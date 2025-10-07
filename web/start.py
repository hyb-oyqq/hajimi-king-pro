#!/usr/bin/env python
"""
Web 管理面板开发环境启动脚本
用于单独启动和测试 Web 面板
"""
import os
import sys
import subprocess
from pathlib import Path

# 项目根目录
project_root = Path(__file__).parent.parent.absolute()
web_root = Path(__file__).parent.absolute()
frontend_root = web_root / "frontend"


def print_header():
    """打印标题"""
    print("=" * 60)
    print("🌐 Hajimi King Pro Web 管理面板 - 开发环境启动器")
    print("=" * 60)
    print()


def check_python_env():
    """检查 Python 环境"""
    print("🐍 检查 Python 环境...")
    print(f"   Python 版本: {sys.version}")
    print(f"   Python 路径: {sys.executable}")
    
    # 检查虚拟环境
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("   ✅ 虚拟环境: 已激活")
    else:
        print("   ⚠️  虚拟环境: 未激活 (建议使用虚拟环境)")
    print()


def install_python_deps():
    """安装 Python 依赖"""
    print("📦 检查 Python 依赖...")
    
    # Web 面板基础依赖
    web_deps = ["flask", "flask-cors", "python-dotenv"]
    
    # 项目完整依赖（用于访问 common 模块等）
    project_deps = [
        "google-generativeai>=0.8.5",
        "requests>=2.32.4",
        "beautifulsoup4>=4.12.3",
        "lxml>=5.1.0"
    ]
    
    try:
        # 检查 Web 基础依赖
        import flask
        import flask_cors
        
        # 检查项目依赖
        try:
            import google.generativeai
            import requests
            import bs4
            import lxml
            print("   ✅ 所有依赖已安装")
            return True
        except ImportError as e:
            print(f"   ⚠️  缺少项目依赖: {e}")
            print("\n   Web 面板需要完整的项目依赖才能运行。")
            print("   请先安装项目依赖：")
            print("   方式1: pip install -r requirements.txt")
            print("   方式2: uv sync")
            print("\n   或安装最小依赖集：")
            all_deps = web_deps + project_deps
            print(f"   pip install {' '.join(all_deps)}")
            
            # 询问是否自动安装
            try:
                choice = input("\n   是否自动安装? (y/n): ").lower()
                if choice == 'y':
                    print("\n   正在安装依赖...")
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install"] + all_deps,
                        check=True
                    )
                    print("   ✅ 依赖安装成功")
                    return True
                else:
                    return False
            except KeyboardInterrupt:
                print("\n   已取消")
                return False
            
    except ImportError:
        print("   ⚠️  检测到缺少依赖")
        print("\n   正在安装 Web 基础依赖...")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install"] + web_deps,
                check=True,
                capture_output=True
            )
            print("   ✅ Web 基础依赖安装成功")
            print("\n   还需要安装项目依赖，请运行:")
            print("   pip install google-generativeai requests beautifulsoup4 lxml")
            return False
        except subprocess.CalledProcessError as e:
            print(f"   ❌ 依赖安装失败: {e}")
            return False


def check_frontend():
    """检查前端构建"""
    dist_dir = web_root / "dist"
    
    print("🎨 检查前端构建...")
    
    if dist_dir.exists() and (dist_dir / "index.html").exists():
        print("   ✅ 前端已构建")
        return True
    else:
        print("   ⚠️  前端未构建")
        return False


def install_frontend_deps():
    """安装前端依赖"""
    print("\n📦 安装前端依赖...")
    
    if not frontend_root.exists():
        print("   ❌ 找不到 frontend 目录")
        return False
    
    node_modules = frontend_root / "node_modules"
    
    if node_modules.exists():
        print("   ✅ 前端依赖已安装")
        return True
    
    print("   正在安装前端依赖（这可能需要几分钟）...")
    try:
        result = subprocess.run(
            ["npm", "install"],
            cwd=str(frontend_root),
            check=True,
            capture_output=True,
            text=True
        )
        print("   ✅ 前端依赖安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 前端依赖安装失败")
        print(f"   错误: {e.stderr}")
        return False
    except FileNotFoundError:
        print("   ❌ 找不到 npm 命令，请先安装 Node.js")
        return False


def build_frontend():
    """构建前端"""
    print("\n🔨 构建前端...")
    
    try:
        result = subprocess.run(
            ["npm", "run", "build"],
            cwd=str(frontend_root),
            check=True,
            capture_output=True,
            text=True
        )
        print("   ✅ 前端构建成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ 前端构建失败")
        print(f"   错误: {e.stderr}")
        return False
    except FileNotFoundError:
        print("   ❌ 找不到 npm 命令")
        return False


def start_web_server():
    """启动 Web 服务器"""
    print("\n🚀 启动 Web 服务器...")
    print("=" * 60)
    
    api_script = web_root / "api.py"
    
    if not api_script.exists():
        print("❌ 找不到 api.py")
        return False
    
    try:
        # 设置工作目录为项目根目录
        os.chdir(str(project_root))
        
        # 启动服务器
        subprocess.run([sys.executable, str(api_script)])
        return True
    except KeyboardInterrupt:
        print("\n\n🛑 服务器已停止")
        return True
    except Exception as e:
        print(f"\n❌ 启动失败: {e}")
        return False


def main():
    """主函数"""
    print_header()
    
    # 检查 Python 环境
    check_python_env()
    
    # 安装 Python 依赖
    if not install_python_deps():
        sys.exit(1)
    
    # 检查前端
    frontend_ready = check_frontend()
    
    if not frontend_ready:
        print("\n" + "=" * 60)
        print("需要构建前端")
        print("=" * 60)
        
        # 安装前端依赖
        if not install_frontend_deps():
            print("\n❌ 无法安装前端依赖")
            print("\n请手动执行:")
            print(f"  cd {frontend_root}")
            print("  npm install")
            print("  npm run build")
            sys.exit(1)
        
        # 构建前端
        if not build_frontend():
            print("\n❌ 无法构建前端")
            sys.exit(1)
    
    # 启动 Web 服务器
    print("\n" + "=" * 60)
    print("准备启动 Web 服务器")
    print("=" * 60)
    print("\n💡 提示:")
    print("  - 访问地址: http://localhost:5000")
    print("  - 按 Ctrl+C 停止服务器")
    print("  - 认证密钥在 .env 文件的 WEB_AUTH_KEY 中配置")
    print()
    
    if not start_web_server():
        sys.exit(1)


if __name__ == "__main__":
    main()

