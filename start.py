#!/usr/bin/env python
"""
Hajimi King 生产环境启动脚本
同时启动 Web 管理面板和主程序
"""
import os
import sys
import subprocess
import time
import signal
from pathlib import Path

# 添加项目根目录到模块搜索路径
project_root = Path(__file__).parent.absolute()
sys.path.insert(0, str(project_root))

# 全局进程列表
processes = []


def signal_handler(sig, frame):
    """处理 Ctrl+C 信号"""
    print("\n\n🛑 收到停止信号，正在关闭所有服务...")
    for process in processes:
        try:
            process.terminate()
            process.wait(timeout=5)
        except:
            process.kill()
    print("✅ 所有服务已停止")
    sys.exit(0)


def check_dependencies():
    """检查必要的依赖"""
    print("🔍 检查依赖...")
    
    try:
        import flask
        import flask_cors
        import google.generativeai
        print("✅ 所有依赖已安装")
        return True
    except ImportError as e:
        print(f"❌ 缺少依赖: {e}")
        print("\n请先安装依赖:")
        print("  pip install flask flask-cors python-dotenv google-generativeai requests")
        return False


def check_frontend_build():
    """检查前端是否已构建"""
    dist_dir = project_root / "web" / "dist"
    if not dist_dir.exists() or not (dist_dir / "index.html").exists():
        print("⚠️  前端未构建，请先构建前端:")
        print("  cd web/frontend")
        print("  npm install")
        print("  npm run build")
        return False
    print("✅ 前端已构建")
    return True


def start_web_server():
    """启动 Web 管理面板"""
    print("\n🌐 启动 Web 管理面板...")
    web_script = project_root / "web" / "api.py"
    
    if not web_script.exists():
        print("❌ 找不到 web/api.py")
        return None
    
    # 检测是否在 Docker 环境
    in_docker = is_docker_environment()
    
    # 获取配置
    from dotenv import load_dotenv
    load_dotenv()
    web_host = os.getenv('WEB_HOST', '0.0.0.0')
    web_port = os.getenv('WEB_PORT', '5000')
    
    # 在生产环境（Docker）使用 Gunicorn，否则使用开发服务器
    if in_docker:
        try:
            # 使用 Gunicorn 启动（生产环境）
            process = subprocess.Popen(
                [
                    sys.executable, "-m", "gunicorn",
                    "--bind", f"{web_host}:{web_port}",
                    "--workers", "2",  # 减少workers避免初始化冲突
                    "--worker-class", "sync",
                    "--timeout", "300",  # 增加超时时间
                    "--graceful-timeout", "300",
                    "--keep-alive", "5",  # 正确的参数名称
                    "--max-requests", "1000",  # 定期重启worker避免内存泄漏
                    "--max-requests-jitter", "100",
                    "--log-level", "info",
                    "--access-logfile", "-",
                    "--error-logfile", "-",
                    "web.api:app"
                ],
                cwd=str(project_root),
                stdout=sys.stdout,
                stderr=sys.stderr,
                bufsize=0  # 禁用缓冲，实时输出
            )
            print("✅ Web 面板启动中（使用 Gunicorn 生产服务器）...")
            return process
        except Exception as e:
            print(f"⚠️  Gunicorn 启动失败: {e}")
            print("   回退到 Flask 开发服务器...")
    
    # 使用 Flask 开发服务器（开发环境）
    process = subprocess.Popen(
        [sys.executable, str(web_script)],
        cwd=str(project_root),
        stdout=sys.stdout,
        stderr=sys.stderr
    )
    
    print("✅ Web 面板启动中（使用 Flask 开发服务器）...")
    return process


def start_main_app():
    """启动主程序"""
    print("\n🚀 启动主程序...")
    app_script = project_root / "app" / "hajimi_king.py"
    
    if not app_script.exists():
        print("❌ 找不到 app/hajimi_king.py")
        return None
    
    # 统一使用 /.env 作为配置文件路径（本地和容器环境一致）
    env_file = Path("/.env")
    in_docker = is_docker_environment()
    
    if env_file.exists():
        print(f"✅ 找到配置文件: {env_file}")
    else:
        # Docker/K8s 环境：通过环境变量注入
        if in_docker:
            print("🐳 容器环境：使用环境变量配置")
        else:
            print("⚠️  未找到配置文件: /.env")
            print("   请将 env.example 复制为 /.env 并配置必要参数")
            return None
    
    # 主程序日志只写入文件，不输出到控制台
    # 使用 DEVNULL 抑制标准输出和标准错误
    process = subprocess.Popen(
        [sys.executable, str(app_script)],
        cwd=str(project_root),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    
    print("✅ 主程序启动中（日志已重定向到文件，请在 Web 面板查看）...")
    return process
def check_process_startup(process, name, timeout=3):
    """检查进程启动是否成功"""
    import time
    start_time = time.time()
    
    # 给进程一点启动时间
    time.sleep(timeout)
    
    # 检查进程是否还在运行
    if process.poll() is not None:
        print(f"\n❌ {name}启动失败，退出码: {process.returncode}")
        return False
    
    return True


def is_docker_environment():
    """检测是否在 Docker 环境中运行"""
    return os.path.exists('/.dockerenv') or os.environ.get('DOCKER_ENVIRONMENT') == 'true'


def main():
    """主函数"""
    print("=" * 60)
    print("🔑 Hajimi King Pro - 生产环境启动器")
    print("=" * 60)
    print()
    
    # 检测环境
    in_docker = is_docker_environment()
    if in_docker:
        print("🐳 检测到 Docker 环境")
    
    # 注册信号处理
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 检查依赖
    if not check_dependencies():
        sys.exit(1)
    
    # 检查前端构建
    if not check_frontend_build():
        sys.exit(1)
    
    # 启动 Web 服务器
    web_process = start_web_server()
    if web_process:
        processes.append(web_process)
        if not check_process_startup(web_process, "Web服务器", timeout=3):
            signal_handler(None, None)
            sys.exit(1)
    else:
        print("❌ Web 服务器启动失败")
        sys.exit(1)
    
    # 启动主程序
    app_process = start_main_app()
    if app_process:
        processes.append(app_process)
        if not check_process_startup(app_process, "主程序", timeout=5):
            print("\n❌ 主程序启动失败")
            print("\n" + "=" * 60)
            print("⚠️  主程序启动失败，但 Web 面板仍在运行")
            print("=" * 60)
            
            # 在 Docker 环境中自动继续，不等待用户输入
            if in_docker:
                # 移除失败的主程序进程
                processes.pop()
                print("\n✅ Docker 环境：自动继续运行 Web 面板...")
            else:
                print("\n💡 选项:")
                print("   1. 按 Enter 继续（仅运行 Web 面板）")
                print("   2. 按 Ctrl+C 停止所有服务")
                print()
                
                try:
                    input("请选择操作: ")
                    # 移除失败的主程序进程
                    processes.pop()
                    print("\n✅ 继续运行 Web 面板...")
                except KeyboardInterrupt:
                    print("\n")
                    signal_handler(None, None)
                    sys.exit(1)
    else:
        print("\n❌ 主程序无法启动（配置问题或其他错误）")
        print("\n" + "=" * 60)
        print("⚠️  主程序启动失败，但 Web 面板仍在运行")
        print("=" * 60)
        print("\n💡 调试建议:")
        print("   1. 确保 .env 文件存在且配置正确")
        print("   2. 单独运行主程序查看详细错误: python app/hajimi_king.py")
        print("   3. 检查 GITHUB_TOKENS 或 GITHUB_SESSION 是否配置")
        
        # 在 Docker 环境中自动继续，不等待用户输入
        if in_docker:
            print("\n✅ Docker 环境：自动继续运行 Web 面板...")
        else:
            print("\n💡 选项:")
            print("   1. 按 Enter 继续（仅运行 Web 面板）")
            print("   2. 按 Ctrl+C 停止所有服务")
            print()
            
            try:
                input("请选择操作: ")
                print("\n✅ 继续运行 Web 面板...")
            except KeyboardInterrupt:
                print("\n")
                signal_handler(None, None)
                sys.exit(1)
    
        print("\n" + "=" * 60)
        if len(processes) == 2:
            print("✅ 所有服务已启动！")
            print("=" * 60)
            print("\n📊 Web 面板: http://localhost:5000")
            print("🔑 主程序: 正在后台运行")
            print("\n💡 提示:")
            print("   • Web 面板日志会显示在此控制台")
            print("   • 主程序日志已写入文件，请在 Web 面板的「日志」页面查看")
        else:
            print("✅ Web 面板已启动！")
            print("=" * 60)
            print("\n📊 Web 面板: http://localhost:5000")
            print("⚠️  主程序: 未运行")
        print("\n按 Ctrl+C 停止所有服务")
        print("=" * 60)
        print()
    
    # 监控进程
    try:
        while True:
            # 检查进程是否还在运行
            for i, process in enumerate(processes):
                if process.poll() is not None:
                    service_name = "Web服务器" if i == 0 else "主程序"
                    print(f"\n⚠️  {service_name} 意外退出，退出码: {process.returncode}")
                    
                    # 如果是 Web 服务器退出，停止所有
                    if i == 0:
                        signal_handler(None, None)
                        sys.exit(1)
                    # 如果是主程序退出，只提示但继续运行 Web
                    else:
                        print("   Web 面板仍在运行，按 Ctrl+C 停止")
                        processes.pop(i)
                        break
            
            time.sleep(1)
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    main()

