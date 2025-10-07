"""
Web API 服务
提供面板数据接口
"""
import os
import sys
import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from functools import wraps

# 添加项目根目录到模块搜索路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv, set_key, find_dotenv

try:
    from common.config import Config
    from common.Logger import logger
    from common import state
    from utils.file_manager import file_manager
    from utils.db_manager import create_db_manager
except ImportError as e:
    print("\n" + "=" * 60)
    print("❌ 缺少项目依赖")
    print("=" * 60)
    print(f"\n错误: {e}")
    print("\nWeb 面板需要完整的项目依赖才能运行。")
    print("\n请先安装依赖：")
    print("  方式1: pip install -r requirements.txt")
    print("  方式2: uv sync")
    print("\n或安装最小依赖集：")
    print("  pip install google-generativeai requests beautifulsoup4 lxml psycopg2-binary pymysql")
    print("\n" + "=" * 60)
    sys.exit(1)

# 加载环境变量
load_dotenv()

# 获取web目录的绝对路径
web_dir = os.path.dirname(os.path.abspath(__file__))
dist_folder = os.path.join(web_dir, 'dist')

app = Flask(__name__, static_folder=dist_folder, static_url_path='')
CORS(app)  # 启用CORS支持

# Web面板配置
WEB_PORT = int(os.getenv('WEB_PORT', '5000'))
WEB_HOST = os.getenv('WEB_HOST', '0.0.0.0')
WEB_AUTH_KEY = os.getenv('WEB_AUTH_KEY', '')
WEB_AUTH_ENABLED = os.getenv('WEB_AUTH_ENABLED', 'true').lower() in ('true', '1', 'yes')

# 创建数据库管理器
db_manager = None
if Config.STORAGE_TYPE == 'sql':
    db_config = Config.get_db_config()
    db_manager = create_db_manager(Config.STORAGE_TYPE, Config.DB_TYPE, db_config)
    if db_manager:
        db_manager.connect()
        db_manager.init_tables()


def require_auth(f):
    """认证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not WEB_AUTH_ENABLED:
            return f(*args, **kwargs)
        
        auth_key = request.headers.get('X-Auth-Key') or request.args.get('auth_key')
        if not auth_key or auth_key != WEB_AUTH_KEY:
            return jsonify({'error': '未授权访问'}), 401
        return f(*args, **kwargs)
    return decorated_function


# ==================== 仪表盘 API ====================

@app.route('/api/dashboard/stats', methods=['GET'])
@require_auth
def get_dashboard_stats():
    """获取仪表盘统计数据"""
    try:
        if not db_manager:
            return jsonify({'error': '数据库未启用'}), 500
        
        # 获取所有密钥
        all_keys = db_manager.get_keys()
        
        # 统计各类密钥数量
        total_keys = len(all_keys)
        valid_keys = len([k for k in all_keys if k['key_type'] == 'valid'])
        rate_limited_keys = len([k for k in all_keys if k['key_type'] == 'rate_limited'])
        paid_keys = len([k for k in all_keys if k['key_type'] == 'paid'])
        
        # 计算时间范围
        now = datetime.now()
        yesterday = now - timedelta(days=1)
        last_week = now - timedelta(days=7)
        last_month = now - timedelta(days=30)
        
        # 今日数据
        today_keys = [k for k in all_keys if datetime.fromisoformat(k['created_at']) >= yesterday]
        today_total = len(today_keys)
        today_valid = len([k for k in today_keys if k['key_type'] == 'valid'])
        today_rate_limited = len([k for k in today_keys if k['key_type'] == 'rate_limited'])
        today_paid = len([k for k in today_keys if k['key_type'] == 'paid'])
        
        # 昨日数据
        yesterday_keys = [k for k in all_keys if yesterday - timedelta(days=1) <= datetime.fromisoformat(k['created_at']) < yesterday]
        yesterday_total = len(yesterday_keys)
        yesterday_valid = len([k for k in yesterday_keys if k['key_type'] == 'valid'])
        yesterday_rate_limited = len([k for k in yesterday_keys if k['key_type'] == 'rate_limited'])
        yesterday_paid = len([k for k in yesterday_keys if k['key_type'] == 'paid'])
        
        # 上周数据
        last_week_keys = [k for k in all_keys if last_week <= datetime.fromisoformat(k['created_at']) < last_week + timedelta(days=1)]
        last_week_total = len(last_week_keys)
        last_week_valid = len([k for k in last_week_keys if k['key_type'] == 'valid'])
        last_week_rate_limited = len([k for k in last_week_keys if k['key_type'] == 'rate_limited'])
        last_week_paid = len([k for k in last_week_keys if k['key_type'] == 'paid'])
        
        # 上月数据
        last_month_keys = [k for k in all_keys if last_month <= datetime.fromisoformat(k['created_at']) < last_month + timedelta(days=1)]
        last_month_total = len(last_month_keys)
        last_month_valid = len([k for k in last_month_keys if k['key_type'] == 'valid'])
        last_month_rate_limited = len([k for k in last_month_keys if k['key_type'] == 'rate_limited'])
        last_month_paid = len([k for k in last_month_keys if k['key_type'] == 'paid'])
        
        return jsonify({
            'total': {
                'count': total_keys,
                'yesterday_change': total_keys - yesterday_total,
                'last_week_change': total_keys - last_week_total,
                'last_month_change': total_keys - last_month_total
            },
            'valid': {
                'count': valid_keys,
                'yesterday_change': valid_keys - yesterday_valid,
                'last_week_change': valid_keys - last_week_valid,
                'last_month_change': valid_keys - last_month_valid
            },
            'rate_limited': {
                'count': rate_limited_keys,
                'yesterday_change': rate_limited_keys - yesterday_rate_limited,
                'last_week_change': rate_limited_keys - last_week_rate_limited,
                'last_month_change': rate_limited_keys - last_month_rate_limited
            },
            'paid': {
                'count': paid_keys,
                'yesterday_change': paid_keys - yesterday_paid,
                'last_week_change': paid_keys - last_week_paid,
                'last_month_change': paid_keys - last_month_paid
            },
            'today': {
                'total': today_total,
                'valid': today_valid,
                'rate_limited': today_rate_limited,
                'paid': today_paid
            }
        })
    except Exception as e:
        logger.error(f"获取仪表盘统计失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 密钥管理 API ====================

@app.route('/api/keys', methods=['GET'])
@require_auth
def get_keys():
    """获取密钥列表"""
    try:
        if not db_manager:
            return jsonify({'error': '数据库未启用'}), 500
        
        # 获取查询参数
        key_type = request.args.get('type', None)
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('page_size', 50))
        search = request.args.get('search', '')
        
        # 获取所有密钥
        all_keys = db_manager.get_keys(key_type=key_type)
        
        # 搜索过滤
        if search:
            all_keys = [k for k in all_keys if search.lower() in k['api_key'].lower() 
                       or search.lower() in (k.get('repo_name', '') or '').lower()]
        
        # 分页
        total = len(all_keys)
        start = (page - 1) * page_size
        end = start + page_size
        keys = all_keys[start:end]
        
        return jsonify({
            'total': total,
            'page': page,
            'page_size': page_size,
            'data': keys
        })
    except Exception as e:
        logger.error(f"获取密钥列表失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/keys/<int:key_id>', methods=['DELETE'])
@require_auth
def delete_key(key_id):
    """删除密钥"""
    try:
        if not db_manager:
            return jsonify({'error': '数据库未启用'}), 500
        
        # 这里需要在db_manager中添加删除方法
        # 暂时返回成功
        return jsonify({'success': True})
    except Exception as e:
        logger.error(f"删除密钥失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 统计分析 API ====================

@app.route('/api/analytics/trend', methods=['GET'])
@require_auth
def get_analytics_trend():
    """获取趋势统计数据"""
    try:
        if not db_manager:
            return jsonify({'error': '数据库未启用'}), 500
        
        days = int(request.args.get('days', 30))
        all_keys = db_manager.get_keys()
        
        # 按天统计
        now = datetime.now()
        trend_data = []
        
        for i in range(days, 0, -1):
            date = now - timedelta(days=i)
            date_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
            date_end = date_start + timedelta(days=1)
            
            day_keys = [k for k in all_keys if date_start <= datetime.fromisoformat(k['created_at']) < date_end]
            
            trend_data.append({
                'date': date_start.strftime('%Y-%m-%d'),
                'total': len(day_keys),
                'valid': len([k for k in day_keys if k['key_type'] == 'valid']),
                'rate_limited': len([k for k in day_keys if k['key_type'] == 'rate_limited']),
                'paid': len([k for k in day_keys if k['key_type'] == 'paid'])
            })
        
        return jsonify({'data': trend_data})
    except Exception as e:
        logger.error(f"获取趋势统计失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/analytics/repo-stats', methods=['GET'])
@require_auth
def get_repo_stats():
    """获取仓库统计数据"""
    try:
        if not db_manager:
            return jsonify({'error': '数据库未启用'}), 500
        
        all_keys = db_manager.get_keys()
        
        # 按仓库统计
        repo_stats = {}
        for key in all_keys:
            repo = key.get('repo_name', '未知')
            if repo not in repo_stats:
                repo_stats[repo] = {'total': 0, 'valid': 0, 'rate_limited': 0, 'paid': 0}
            
            repo_stats[repo]['total'] += 1
            if key['key_type'] == 'valid':
                repo_stats[repo]['valid'] += 1
            elif key['key_type'] == 'rate_limited':
                repo_stats[repo]['rate_limited'] += 1
            elif key['key_type'] == 'paid':
                repo_stats[repo]['paid'] += 1
        
        # 转换为列表并排序
        data = [{'repo': k, **v} for k, v in repo_stats.items()]
        data.sort(key=lambda x: x['total'], reverse=True)
        
        return jsonify({'data': data[:50]})  # 返回前50个仓库
    except Exception as e:
        logger.error(f"获取仓库统计失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 日志 API ====================

@app.route('/api/logs', methods=['GET'])
@require_auth
def get_logs():
    """获取日志"""
    try:
        # 读取最新的日志文件
        log_dir = os.path.join(Config.DATA_PATH, 'logs')
        log_files = []
        
        if os.path.exists(log_dir):
            for filename in os.listdir(log_dir):
                if filename.endswith('.log'):
                    file_path = os.path.join(log_dir, filename)
                    log_files.append((file_path, os.path.getmtime(file_path)))
        
        # 获取最新的日志文件
        if log_files:
            log_files.sort(key=lambda x: x[1], reverse=True)
            latest_log = log_files[0][0]
            
            # 读取最后N行
            lines = int(request.args.get('lines', 200))
            with open(latest_log, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                recent_lines = all_lines[-lines:]
            
            return jsonify({
                'logs': ''.join(recent_lines),
                'total_lines': len(all_lines)
            })
        else:
            return jsonify({'logs': '暂无日志', 'total_lines': 0})
    except Exception as e:
        logger.error(f"获取日志失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/logs/live', methods=['GET'])
@require_auth
def get_live_logs():
    """获取实时日志（最后100行）"""
    try:
        log_dir = os.path.join(Config.DATA_PATH, 'logs')
        if not os.path.exists(log_dir):
            return jsonify({'logs': []})
        
        log_files = [(os.path.join(log_dir, f), os.path.getmtime(os.path.join(log_dir, f))) 
                     for f in os.listdir(log_dir) if f.endswith('.log')]
        
        if not log_files:
            return jsonify({'logs': []})
        
        latest_log = max(log_files, key=lambda x: x[1])[0]
        
        with open(latest_log, 'r', encoding='utf-8') as f:
            lines = f.readlines()[-100:]
        
        return jsonify({'logs': [line.strip() for line in lines]})
    except Exception as e:
        logger.error(f"获取实时日志失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 规则管理 API ====================

@app.route('/api/rules', methods=['GET'])
@require_auth
def get_rules():
    """获取搜索规则"""
    try:
        queries = file_manager.get_search_queries()
        return jsonify({'data': queries, 'total': len(queries)})
    except Exception as e:
        logger.error(f"获取规则失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rules', methods=['POST'])
@require_auth
def add_rule():
    """添加搜索规则"""
    try:
        data = request.json
        rule = data.get('rule', '').strip()
        
        if not rule:
            return jsonify({'error': '规则不能为空'}), 400
        
        # 读取现有规则
        queries = file_manager.get_search_queries()
        
        # 检查是否已存在
        if rule in queries:
            return jsonify({'error': '规则已存在'}), 400
        
        # 添加新规则到data目录下的queries.txt
        queries_file = os.path.join(Config.DATA_PATH, Config.QUERIES_FILE)
        with open(queries_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{rule}")
        
        return jsonify({'success': True, 'message': '规则添加成功'})
    except Exception as e:
        logger.error(f"添加规则失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/rules/<int:index>', methods=['DELETE'])
@require_auth
def delete_rule(index):
    """删除搜索规则"""
    try:
        queries = file_manager.get_search_queries()
        
        if index < 0 or index >= len(queries):
            return jsonify({'error': '规则索引无效'}), 400
        
        # 删除规则
        deleted_rule = queries.pop(index)
        logger.info(f"删除规则 #{index}: {deleted_rule}")
        
        # 保存更新后的规则到data目录下的queries.txt
        queries_file = os.path.join(Config.DATA_PATH, Config.QUERIES_FILE)
        with open(queries_file, 'w', encoding='utf-8') as f:
            # 保留注释头
            f.write("# GitHub搜索查询配置文件\n")
            f.write("# 每行一个查询语句，支持GitHub搜索语法\n")
            f.write("# 以#开头的行为注释，空行会被忽略\n\n")
            if queries:
                f.write('\n'.join(queries) + '\n')
        
        return jsonify({'success': True, 'message': '规则删除成功'})
    except Exception as e:
        logger.error(f"删除规则失败: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500


@app.route('/api/system/restart', methods=['POST'])
@require_auth
def restart_system():
    """重启系统（热重启）"""
    try:
        # 这里可以实现重启逻辑
        # 例如：触发supervisord重启、systemd重启等
        # 或者设置一个标志文件，让主程序检测并重启
        
        restart_flag = os.path.join(Config.DATA_PATH, '.restart_flag')
        with open(restart_flag, 'w') as f:
            f.write(str(datetime.now()))
        
        return jsonify({'success': True, 'message': '重启信号已发送'})
    except Exception as e:
        logger.error(f"重启系统失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 设置管理 API ====================

@app.route('/api/settings', methods=['GET'])
@require_auth
def get_settings():
    """获取设置"""
    try:
        settings = {
            'github_auth_mode': Config.GITHUB_AUTH_MODE,
            'github_tokens': len(Config.GITHUB_TOKENS),
            'github_sessions': len(Config.GITHUB_SESSIONS),
            'storage_type': Config.STORAGE_TYPE,
            'db_type': Config.DB_TYPE,
            'date_range_days': Config.DATE_RANGE_DAYS,
            'language': Config.LANGUAGE,
            'proxy_count': len(Config.PROXY_LIST),
            'balancer_enabled': Config.parse_bool(Config.GEMINI_BALANCER_SYNC_ENABLED),
            'gpt_load_enabled': Config.parse_bool(Config.GPT_LOAD_SYNC_ENABLED),
            'forced_cooldown_enabled': Config.parse_bool(Config.FORCED_COOLDOWN_ENABLED),
            'sha_cleanup_enabled': Config.parse_bool(Config.SHA_CLEANUP_ENABLED),
            # 新增配置项
            'forced_cooldown_hours_per_query': Config.FORCED_COOLDOWN_HOURS_PER_QUERY,
            'forced_cooldown_hours_per_loop': Config.FORCED_COOLDOWN_HOURS_PER_LOOP,
            'sha_cleanup_days': Config.SHA_CLEANUP_DAYS,
            'sha_cleanup_interval_loops': Config.SHA_CLEANUP_INTERVAL_LOOPS,
            'key_validator_max_workers': Config.KEY_VALIDATOR_MAX_WORKERS,
            'rate_limited_handling': Config.RATE_LIMITED_HANDLING,
            'hajimi_check_model': Config.HAJIMI_CHECK_MODEL,
            'hajimi_paid_model': Config.HAJIMI_PAID_MODEL,
            'gpt_load_paid_enabled': Config.parse_bool(Config.GPT_LOAD_PAID_SYNC_ENABLED),
            'gpt_load_group_name': Config.GPT_LOAD_GROUP_NAME,
            'gpt_load_paid_group_name': Config.GPT_LOAD_PAID_GROUP_NAME,
            'gpt_load_rate_limited_group_name': Config.GPT_LOAD_RATE_LIMITED_GROUP_NAME
        }
        return jsonify(settings)
    except Exception as e:
        logger.error(f"获取设置失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/github-tokens', methods=['GET'])
@require_auth
def get_github_tokens():
    """获取GitHub Tokens列表（隐藏部分内容）"""
    try:
        tokens = []
        for i, token in enumerate(Config.GITHUB_TOKENS):
            masked_token = token[:10] + '***' + token[-10:] if len(token) > 20 else '***'
            tokens.append({
                'index': i,
                'token': masked_token,
                'full_length': len(token)
            })
        return jsonify({'data': tokens})
    except Exception as e:
        logger.error(f"获取GitHub Tokens失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/github-tokens', methods=['POST'])
@require_auth
def add_github_token():
    """添加GitHub Token"""
    try:
        data = request.json
        token = data.get('token', '').strip()
        
        if not token:
            return jsonify({'error': 'Token不能为空'}), 400
        
        # 更新.env文件
        env_file = find_dotenv()
        if not env_file:
            return jsonify({'error': '.env文件不存在'}), 500
        
        # 添加token
        current_tokens = os.getenv('GITHUB_TOKENS', '')
        new_tokens = f"{current_tokens},{token}" if current_tokens else token
        set_key(env_file, 'GITHUB_TOKENS', new_tokens)
        
        return jsonify({'success': True, 'message': 'Token添加成功，请重启服务生效'})
    except Exception as e:
        logger.error(f"添加GitHub Token失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/github-tokens/<int:index>', methods=['DELETE'])
@require_auth
def delete_github_token(index):
    """删除GitHub Token"""
    try:
        tokens = Config.GITHUB_TOKENS.copy()
        
        if index < 0 or index >= len(tokens):
            return jsonify({'error': 'Token索引无效'}), 400
        
        tokens.pop(index)
        
        # 更新.env文件
        env_file = find_dotenv()
        if not env_file:
            return jsonify({'error': '.env文件不存在'}), 500
        
        new_tokens = ','.join(tokens)
        set_key(env_file, 'GITHUB_TOKENS', new_tokens)
        
        return jsonify({'success': True, 'message': 'Token删除成功，请重启服务生效'})
    except Exception as e:
        logger.error(f"删除GitHub Token失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/github-sessions', methods=['GET'])
@require_auth
def get_github_sessions():
    """获取GitHub Sessions列表（隐藏部分内容）"""
    try:
        sessions = []
        for i, session in enumerate(Config.GITHUB_SESSIONS):
            masked_session = session[:10] + '***' + session[-10:] if len(session) > 20 else '***'
            sessions.append({
                'index': i,
                'session': masked_session,
                'full_length': len(session)
            })
        return jsonify({'data': sessions})
    except Exception as e:
        logger.error(f"获取GitHub Sessions失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/github-sessions', methods=['POST'])
@require_auth
def add_github_session():
    """添加GitHub Session"""
    try:
        data = request.json
        session = data.get('session', '').strip()
        
        if not session:
            return jsonify({'error': 'Session不能为空'}), 400
        
        # 更新.env文件
        env_file = find_dotenv()
        if not env_file:
            return jsonify({'error': '.env文件不存在'}), 500
        
        current_sessions = os.getenv('GITHUB_SESSION', '')
        new_sessions = f"{current_sessions},{session}" if current_sessions else session
        set_key(env_file, 'GITHUB_SESSION', new_sessions)
        
        return jsonify({'success': True, 'message': 'Session添加成功，请重启服务生效'})
    except Exception as e:
        logger.error(f"添加GitHub Session失败: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/settings/github-sessions/<int:index>', methods=['DELETE'])
@require_auth
def delete_github_session(index):
    """删除GitHub Session"""
    try:
        sessions = Config.GITHUB_SESSIONS.copy()
        
        if index < 0 or index >= len(sessions):
            return jsonify({'error': 'Session索引无效'}), 400
        
        sessions.pop(index)
        
        # 更新.env文件
        env_file = find_dotenv()
        if not env_file:
            return jsonify({'error': '.env文件不存在'}), 500
        
        new_sessions = ','.join(sessions)
        set_key(env_file, 'GITHUB_SESSION', new_sessions)
        
        return jsonify({'success': True, 'message': 'Session删除成功，请重启服务生效'})
    except Exception as e:
        logger.error(f"删除GitHub Session失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 系统状态 API ====================

@app.route('/api/system/status', methods=['GET'])
@require_auth
def get_system_status():
    """获取系统状态"""
    try:
        return jsonify({
            'is_running': True,  # 如果API可访问说明系统在运行
            'is_in_cooldown': state.is_in_cooldown,
            'db_type': Config.DB_TYPE,
            'storage_type': Config.STORAGE_TYPE
        })
    except Exception as e:
        logger.error(f"获取系统状态失败: {e}")
        return jsonify({'error': str(e)}), 500


# ==================== 前端路由 ====================

@app.route('/')
def index():
    """提供React前端首页"""
    return send_from_directory(app.static_folder, 'index.html')

# 404错误处理器 - 用于SPA路由
@app.errorhandler(404)
def not_found(e):
    """处理404错误 - 对于前端路由返回index.html"""
    # 如果请求的是API，返回JSON错误
    if request.path.startswith('/api/'):
        return jsonify({'error': 'Not found'}), 404
    
    # 如果请求的是静态文件但不存在，返回404
    if '.' in request.path:
        return jsonify({'error': 'File not found'}), 404
    
    # 其他所有路径（前端路由）返回index.html
    return send_from_directory(app.static_folder, 'index.html')


if __name__ == '__main__':
    logger.info(f"🌐 Web面板启动在 http://{WEB_HOST}:{WEB_PORT}")
    if WEB_AUTH_ENABLED:
        logger.info(f"🔒 认证已启用，请使用 X-Auth-Key: {WEB_AUTH_KEY}")
    else:
        logger.warning("⚠️ 认证未启用，建议在生产环境启用认证")
    
    app.run(host=WEB_HOST, port=WEB_PORT, debug=False)

