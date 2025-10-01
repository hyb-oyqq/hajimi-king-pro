"""
多语言翻译模块
Multilingual Translation Module
"""

import os
from typing import Dict


class Translations:
    """多语言翻译类"""
    
    # 所有支持的语言
    SUPPORTED_LANGUAGES = ['zh_cn', 'en']
    
    # 翻译字典
    TRANSLATIONS = {
        'zh_cn': {
            # 系统启动相关
            'system_starting': '🚀 HAJIMI KING 启动中',
            'started_at': '⏰ 启动时间: {}',
            'config_check_failed': '❌ 配置检查失败。退出中...',
            'filemanager_check_failed': '❌ 文件管理器检查失败。退出中...',
            'syncutils_ready': '🔗 同步工具已就绪，准备异步同步密钥',
            'queue_status': '📊 队列状态 - Balancer: {}, GPT Load: {}',
            'system_information': '📋 系统信息:',
            'github_tokens_count': '🔑 GitHub tokens: 已配置 {} 个',
            'search_queries_count': '🔍 搜索查询: 已加载 {} 个',
            'date_filter': '📅 日期过滤器: {} 天',
            'proxy_configured': '🌐 代理: 已配置 {} 个代理',
            'checkpoint_found': '💾 发现检查点 - 增量扫描模式',
            'last_scan': '   上次扫描: {}',
            'scanned_files': '   已扫描文件: {}',
            'processed_queries': '   已处理查询: {}',
            'no_checkpoint': '💾 无检查点 - 全量扫描模式',
            'system_ready': '✅ 系统就绪 - 开始运行',
            
            # 循环和进度相关
            'loop_start': '🔄 循环 #{} - {}',
            'cleared_queries': '🔄 已清除上一轮的已处理查询',
            'skipping_query': '🔍 跳过已处理查询: [{}],索引:#{}',
            'progress': '📈 进度: {}/{} | 查询: {} | 当前有效: {} | 当前限速: {} | 总有效: {} | 总限速: {}',
            'skipping_item': '🚫 跳过项目,名称: {},索引:{} - 原因: {}',
            'query_complete': '✅ 查询 {}/{} 完成 - 已处理: {}, 有效: +{}, 限速: +{}',
            'query_all_skipped': '⏭️ 查询 {}/{} 完成 - 所有项目已跳过',
            'query_no_items': '📭 查询 {}/{} - 未找到项目',
            'query_failed': '❌ 查询 {}/{} 失败',
            'taking_break': '⏸️ 已处理 {} 个查询，休息一下...',
            'loop_complete': '🏁 循环 #{} 完成 - 处理了 {} 个文件 | 总有效: {} | 总限速: {}',
            'sleeping': '💤 休眠 10 秒...',
            
            # 文件处理相关
            'failed_fetch_content': '⚠️ 获取文件内容失败: {}',
            'found_keys': '🔑 找到 {} 个疑似密钥，正在验证...',
            'valid_key': '✅ 有效: {}',
            'rate_limited_key': '⚠️ 限速: {}, 检查结果: {}',
            'invalid_key': '❌ 无效: {}, 检查结果: {}',
            'saved_valid_keys': '💾 已保存 {} 个有效密钥',
            'added_to_queue': '📥 已将 {} 个密钥添加到同步队列',
            'error_adding_to_queue': '📥 添加密钥到同步队列时出错: {}',
            'saved_rate_limited_keys': '💾 已保存 {} 个限速密钥',
            
            # 统计相关
            'skip_stats': '📊 跳过 {} 个项目 - 时间: {}, 重复: {}, 年龄: {}, 文档: {}',
            'final_stats': '📊 最终统计 - 有效密钥: {}, 限速密钥: {}',
            
            # 错误和中断
            'interrupted': '⛔ 用户中断',
            'shutting_down': '🔚 关闭同步工具...',
            'unexpected_error': '💥 意外错误: {}',
            'continuing': '🔄 继续中...',
            
            # 配置检查
            'checking_config': '🔍 检查必要配置...',
            'github_tokens_missing': '未找到 GitHub tokens。请设置 GITHUB_TOKENS 环境变量。',
            'github_tokens_missing_short': '❌ GitHub tokens: 缺失',
            'github_tokens_ok': '✅ GitHub tokens: 已配置 {} 个',
            'balancer_enabled': '✅ Gemini Balancer 已启用, URL: {}',
            'balancer_missing': '⚠️ Gemini Balancer Auth 或 URL 缺失 (Balancer功能将被禁用)',
            'balancer_ok': '✅ Gemini Balancer Auth: ****',
            'balancer_not_configured': 'ℹ️ Gemini Balancer URL: 未配置 (Balancer功能将被禁用)',
            'gpt_load_enabled': '✅ GPT-load 已启用, URL: {}',
            'gpt_load_missing': '⚠️ GPT-load Auth, URL 或 Group Name 缺失 (GPT-load功能将被禁用)',
            'gpt_load_ok': '✅ GPT-load Auth: ****',
            'gpt_load_group_name': '✅ GPT-load Group Name: {}',
            'gpt_load_not_configured': 'ℹ️ GPT-load: 未配置 (GPT-load功能将被禁用)',
            'config_check_failed_details': '❌ 配置检查失败:',
            'check_env_file': '请检查您的 .env 文件和配置。',
            'all_config_valid': '✅ 所有必要配置均有效',
            
            # GitHub客户端相关
            'rate_limit_low': '⚠️ 速率限制较低: 剩余 {} 次, token: {}',
            'rate_limit_hit': '❌ 遇到速率限制, 状态码:{} (尝试 {}/{}) - 等待 {:.1f}秒',
            'http_error': '❌ HTTP {} 错误，已尝试 {} 次，第 {} 页',
            'network_error': '❌ 网络错误，已尝试 {} 次，第 {} 页: {}',
            'first_page_failed': '❌ 查询第一页失败: {}...',
            'processing_query': '⏳ 处理查询: 【{}】,第 {} 页,项目数: {},预期总数: {},总数: {},随机休眠: {:.1f}秒',
            'data_loss_warning': '⚠️ 显著数据丢失: {}/{} 个项目丢失 ({:.1f}%)',
            'search_complete': '🔍 GitHub 搜索完成: 查询:【{}】 | 成功页数:{} | 项目数:{}/{} | 总请求数:{} ',
            'processing_file': '🔍 处理文件: {}',
            'decode_failed': '⚠️ 解码 base64 内容失败: {}, 回退到 download_url',
            'no_download_url': '⚠️ 未找到文件下载 URL: {}',
            'unexpected_list_response': '⚠️ API 返回列表格式而非文件内容（可能是目录）: {}',
            'checking_keys_from': '⏳ 从以下位置检查密钥: {},状态: {}',
            'fetch_file_failed': '❌ 获取文件内容失败: {}, {}',
            
            # 同步工具相关
            'balancer_sync_disabled': '🚫 Gemini Balancer 同步已禁用 - URL 或 AUTH 未配置',
            'balancer_enabled_url': '🔗 Gemini Balancer 已启用 - URL: {}',
            'gpt_load_sync_disabled': '🚫 GPT-load 同步已禁用 - URL、AUTH、GROUP_NAME 未配置或同步已禁用',
            'gpt_load_enabled_url': '🔗 GPT-load 已启用 - URL: {}, 组: {}',
            'checkpoint_saving_wait': '📥 检查点正在保存中，在添加 {} 个密钥到队列前等待...',
            'added_to_balancer_queue': '📥 已添加 {} 个密钥到 gemini balancer 队列 (总数: {})',
            'balancer_disabled_skipping': '🚫 Gemini Balancer 已禁用，跳过 {} 个密钥',
            'added_to_gpt_load_queue': '📥 已添加 {} 个密钥到 GPT-load 队列 (总数: {})',
            'gpt_load_disabled_skipping': '🚫 GPT-load 已禁用，跳过 {} 个密钥',
            'sending_keys_to_balancer': '🔄 正在发送 {} 个密钥到 balancer...',
            'fetching_config_from': '📥 从以下位置获取当前配置: {}',
            'get_config_failed': '获取配置失败: HTTP {} - {}',
            'all_keys_exist': 'ℹ️ 所有 {} 个密钥已存在于 balancer 中',
            'updating_balancer_config': '📝 正在使用 {} 个新密钥更新 gemini balancer 配置...',
            'update_config_failed': '更新配置失败: HTTP {} - {}',
            'failed_to_add_keys': '❌ 添加 {} 个密钥失败: {}',
            'all_keys_added_successfully': '✅ 所有 {} 个新密钥已成功添加到 balancer。',
            'request_timeout_balancer': '❌ 连接到 balancer 时请求超时',
            'connection_failed_balancer': '❌ 连接到 balancer 失败',
            'invalid_json_balancer': '❌ balancer 返回的 JSON 无效: {}',
            'failed_send_to_balancer': '❌ 发送密钥到 balancer 失败: {}',
            'using_cached_group_id': '📋 使用 \'{}\' 的缓存组 ID: {}',
            'fetching_groups_from': '📥 从以下位置获取组: {}',
            'get_groups_failed': '获取组失败: HTTP {} - {}',
            'groups_api_error': '组 API 返回错误: {}',
            'found_and_cached_group': '✅ 找到并缓存组 \'{}\' ID: {}',
            'group_not_found': '在组列表中未找到组 \'{}\'',
            'failed_get_group_id': '❌ 获取组 \'{}\' 的 ID 失败: {}',
            'sending_to_gpt_load': '🔄 正在为 {} 个组发送 {} 个密钥到 GPT-load...',
            'processing_group': '📝 处理组: {}',
            'failed_get_group_id_short': '获取组 \'{}\' 的 ID 失败',
            'adding_keys_to_group': '📝 正在添加 {} 个密钥到组 \'{}\' (ID: {})...',
            'failed_add_keys_to_group': '添加密钥到组 \'{}\' 失败: HTTP {} - {}',
            'add_keys_api_error': '组 \'{}\' 的添加密钥 API 返回错误: {}',
            'keys_task_started': '✅ 组 \'{}\' 的密钥添加任务已成功启动:',
            'task_type': '   任务类型: {}',
            'is_running': '   运行中: {}',
            'total_keys': '   总密钥数: {}',
            'group_name': '   组名: {}',
            'exception_adding_to_group': '❌ 添加密钥到组 \'{}\' 时发生异常: {}',
            'sent_to_all_groups': '✅ 已成功发送密钥到所有 {} 个组',
            'failed_send_to_groups': '❌ 发送密钥到 {} 个组失败: {}',
            'request_timeout_gpt_load': '❌ 连接到 GPT-load 时请求超时',
            'connection_failed_gpt_load': '❌ 连接到 GPT-load 失败',
            'invalid_json_gpt_load': '❌ GPT-load 返回的 JSON 无效: {}',
            'failed_send_to_gpt_load': '❌ 发送密钥到 GPT-load 失败: {}',
            'checkpoint_saving_batch_wait': '📥 检查点正在保存中，批量发送前等待...',
            'starting_batch_send': '📥 开始批量发送，wait_send_balancer 长度: {}，wait_send_gpt_load 长度: {}',
            'processing_balancer_queue': '🔄 正在处理 gemini balancer 队列中的 {} 个密钥',
            'balancer_queue_cleared': '✅ Gemini balancer 队列处理成功，已清除 {} 个密钥',
            'balancer_queue_failed': '❌ Gemini balancer 队列处理失败，代码: {}',
            'processing_gpt_load_queue': '🔄 正在处理 GPT-load 队列中的 {} 个密钥',
            'gpt_load_queue_cleared': '✅ GPT-load 队列处理成功，已清除 {} 个密钥',
            'gpt_load_queue_failed': '❌ GPT-load 队列处理失败，代码: {}',
            'batch_send_error': '❌ 批量发送 worker 错误: {}',
            'syncutils_shutdown_complete': '🔚 SyncUtils 关闭完成',
        },
        'en': {
            # System startup
            'system_starting': '🚀 HAJIMI KING STARTING',
            'started_at': '⏰ Started at: {}',
            'config_check_failed': '❌ Config check failed. Exiting...',
            'filemanager_check_failed': '❌ FileManager check failed. Exiting...',
            'syncutils_ready': '🔗 SyncUtils ready for async key syncing',
            'queue_status': '📊 Queue status - Balancer: {}, GPT Load: {}',
            'system_information': '📋 SYSTEM INFORMATION:',
            'github_tokens_count': '🔑 GitHub tokens: {} configured',
            'search_queries_count': '🔍 Search queries: {} loaded',
            'date_filter': '📅 Date filter: {} days',
            'proxy_configured': '🌐 Proxy: {} proxies configured',
            'checkpoint_found': '💾 Checkpoint found - Incremental scan mode',
            'last_scan': '   Last scan: {}',
            'scanned_files': '   Scanned files: {}',
            'processed_queries': '   Processed queries: {}',
            'no_checkpoint': '💾 No checkpoint - Full scan mode',
            'system_ready': '✅ System ready - Starting king',
            
            # Loop and progress
            'loop_start': '🔄 Loop #{} - {}',
            'cleared_queries': '🔄 Cleared processed queries from previous loop',
            'skipping_query': '🔍 Skipping already processed query: [{}],index:#{}',
            'progress': '📈 Progress: {}/{} | query: {} | current valid: {} | current rate limited: {} | total valid: {} | total rate limited: {}',
            'skipping_item': '🚫 Skipping item,name: {},index:{} - reason: {}',
            'query_complete': '✅ Query {}/{} complete - Processed: {}, Valid: +{}, Rate limited: +{}',
            'query_all_skipped': '⏭️ Query {}/{} complete - All items skipped',
            'query_no_items': '📭 Query {}/{} - No items found',
            'query_failed': '❌ Query {}/{} failed',
            'taking_break': '⏸️ Processed {} queries, taking a break...',
            'loop_complete': '🏁 Loop #{} complete - Processed {} files | Total valid: {} | Total rate limited: {}',
            'sleeping': '💤 Sleeping for 10 seconds...',
            
            # File processing
            'failed_fetch_content': '⚠️ Failed to fetch content for file: {}',
            'found_keys': '🔑 Found {} suspected key(s), validating...',
            'valid_key': '✅ VALID: {}',
            'rate_limited_key': '⚠️ RATE LIMITED: {}, check result: {}',
            'invalid_key': '❌ INVALID: {}, check result: {}',
            'saved_valid_keys': '💾 Saved {} valid key(s)',
            'added_to_queue': '📥 Added {} key(s) to sync queues',
            'error_adding_to_queue': '📥 Error adding keys to sync queues: {}',
            'saved_rate_limited_keys': '💾 Saved {} rate limited key(s)',
            
            # Statistics
            'skip_stats': '📊 Skipped {} items - Time: {}, Duplicate: {}, Age: {}, Docs: {}',
            'final_stats': '📊 Final stats - Valid keys: {}, Rate limited: {}',
            
            # Errors and interrupts
            'interrupted': '⛔ Interrupted by user',
            'shutting_down': '🔚 Shutting down sync utils...',
            'unexpected_error': '💥 Unexpected error: {}',
            'continuing': '🔄 Continuing...',
            
            # Config check
            'checking_config': '🔍 Checking required configurations...',
            'github_tokens_missing': 'GitHub tokens not found. Please set GITHUB_TOKENS environment variable.',
            'github_tokens_missing_short': '❌ GitHub tokens: Missing',
            'github_tokens_ok': '✅ GitHub tokens: {} configured',
            'balancer_enabled': '✅ Gemini Balancer enabled, URL: {}',
            'balancer_missing': '⚠️ Gemini Balancer Auth or URL Missing (Balancer disabled)',
            'balancer_ok': '✅ Gemini Balancer Auth: ****',
            'balancer_not_configured': 'ℹ️ Gemini Balancer URL: Not configured (Balancer disabled)',
            'gpt_load_enabled': '✅ GPT-load enabled, URL: {}',
            'gpt_load_missing': '⚠️ GPT-load Auth, URL or Group Name Missing (GPT-load disabled)',
            'gpt_load_ok': '✅ GPT-load Auth: ****',
            'gpt_load_group_name': '✅ GPT-load Group Name: {}',
            'gpt_load_not_configured': 'ℹ️ GPT-load: Not configured (GPT-load disabled)',
            'config_check_failed_details': '❌ Configuration check failed:',
            'check_env_file': 'Please check your .env file and configuration.',
            'all_config_valid': '✅ All required configurations are valid',
            
            # GitHub client related
            'rate_limit_low': '⚠️ Rate limit low: {} remaining, token: {}',
            'rate_limit_hit': '❌ Rate limit hit, status:{} (attempt {}/{}) - waiting {:.1f}s',
            'http_error': '❌ HTTP {} error after {} attempts on page {}',
            'network_error': '❌ Network error after {} attempts on page {}: {}',
            'first_page_failed': '❌ First page failed for query: {}...',
            'processing_query': '⏳ Processing query: 【{}】,page {},item count: {},expected total: {},total count: {},random sleep: {:.1f}s',
            'data_loss_warning': '⚠️ Significant data loss: {}/{} items missing ({:.1f}%)',
            'search_complete': '🔍 GitHub search complete: query:【{}】 | page success count:{} | items count:{}/{} | total requests:{} ',
            'processing_file': '🔍 Processing file: {}',
            'decode_failed': '⚠️ Failed to decode base64 content: {}, falling back to download_url',
            'no_download_url': '⚠️ No download URL found for file: {}',
            'unexpected_list_response': '⚠️ API returned list instead of file content (possibly a directory): {}',
            'checking_keys_from': '⏳ checking for keys from: {},status: {}',
            'fetch_file_failed': '❌ Failed to fetch file content: {}, {}',
            
            # Sync utils related
            'balancer_sync_disabled': '🚫 Gemini Balancer sync disabled - URL or AUTH not configured',
            'balancer_enabled_url': '🔗 Gemini Balancer enabled - URL: {}',
            'gpt_load_sync_disabled': '🚫 GPT-load sync disabled - URL, AUTH, GROUP_NAME not configured or sync disabled',
            'gpt_load_enabled_url': '🔗 GPT-load enabled - URL: {}, Groups: {}',
            'checkpoint_saving_wait': '📥 Checkpoint is currently being saved, waiting before adding {} key(s) to queues...',
            'added_to_balancer_queue': '📥 Added {} key(s) to gemini balancer queue (total: {})',
            'balancer_disabled_skipping': '🚫 Gemini Balancer disabled, skipping {} key(s) for gemini balancer queue',
            'added_to_gpt_load_queue': '📥 Added {} key(s) to GPT-load queue (total: {})',
            'gpt_load_disabled_skipping': '🚫 GPT-load disabled, skipping {} key(s) for GPT-load queue',
            'sending_keys_to_balancer': '🔄 Sending {} key(s) to balancer...',
            'fetching_config_from': '📥 Fetching current config from: {}',
            'get_config_failed': 'Failed to get config: HTTP {} - {}',
            'all_keys_exist': 'ℹ️ All {} key(s) already exist in balancer',
            'updating_balancer_config': '📝 Updating gemini balancer config with {} new key(s)...',
            'update_config_failed': 'Failed to update config: HTTP {} - {}',
            'failed_to_add_keys': '❌ Failed to add {} key(s): {}',
            'all_keys_added_successfully': '✅ All {} new key(s) successfully added to balancer.',
            'request_timeout_balancer': '❌ Request timeout when connecting to balancer',
            'connection_failed_balancer': '❌ Connection failed to balancer',
            'invalid_json_balancer': '❌ Invalid JSON response from balancer: {}',
            'failed_send_to_balancer': '❌ Failed to send keys to balancer: {}',
            'using_cached_group_id': '📋 Using cached group ID for \'{}\': {}',
            'fetching_groups_from': '📥 Fetching groups from: {}',
            'get_groups_failed': 'Failed to get groups: HTTP {} - {}',
            'groups_api_error': 'Groups API returned error: {}',
            'found_and_cached_group': '✅ Found and cached group \'{}\' with ID: {}',
            'group_not_found': 'Group \'{}\' not found in groups list',
            'failed_get_group_id': '❌ Failed to get group ID for \'{}\': {}',
            'sending_to_gpt_load': '🔄 Sending {} key(s) to GPT-load for {} group(s)...',
            'processing_group': '📝 Processing group: {}',
            'failed_get_group_id_short': 'Failed to get group ID for \'{}\'',
            'adding_keys_to_group': '📝 Adding {} key(s) to group \'{}\' (ID: {})...',
            'failed_add_keys_to_group': 'Failed to add keys to group \'{}\': HTTP {} - {}',
            'add_keys_api_error': 'Add keys API returned error for group \'{}\': {}',
            'keys_task_started': '✅ Keys addition task started successfully for group \'{}\'',
            'task_type': '   Task Type: {}',
            'is_running': '   Is Running: {}',
            'total_keys': '   Total Keys: {}',
            'group_name': '   Group Name: {}',
            'exception_adding_to_group': '❌ Exception when adding keys to group \'{}\': {}',
            'sent_to_all_groups': '✅ Successfully sent keys to all {} group(s)',
            'failed_send_to_groups': '❌ Failed to send keys to {} group(s): {}',
            'request_timeout_gpt_load': '❌ Request timeout when connecting to GPT-load',
            'connection_failed_gpt_load': '❌ Connection failed to GPT-load',
            'invalid_json_gpt_load': '❌ Invalid JSON response from GPT-load: {}',
            'failed_send_to_gpt_load': '❌ Failed to send keys to GPT-load: {}',
            'checkpoint_saving_batch_wait': '📥 Checkpoint is currently being saving, waiting before batch sending...',
            'starting_batch_send': '📥 Starting batch sending, wait_send_balancer length: {}, wait_send_gpt_load length: {}',
            'processing_balancer_queue': '🔄 Processing {} key(s) from gemini balancer queue',
            'balancer_queue_cleared': '✅ Gemini balancer queue processed successfully, cleared {} key(s)',
            'balancer_queue_failed': '❌ Gemini balancer queue processing failed with code: {}',
            'processing_gpt_load_queue': '🔄 Processing {} key(s) from GPT-load queue',
            'gpt_load_queue_cleared': '✅ GPT-load queue processed successfully, cleared {} key(s)',
            'gpt_load_queue_failed': '❌ GPT-load queue processing failed with code: {}',
            'batch_send_error': '❌ Batch send worker error: {}',
            'syncutils_shutdown_complete': '🔚 SyncUtils shutdown complete',
        }
    }
    
    def __init__(self, language: str = 'zh_cn'):
        """
        初始化翻译类
        
        Args:
            language: 语言代码，默认为zh_cn（简体中文）
        """
        if language not in self.SUPPORTED_LANGUAGES:
            print(f"Warning: Unsupported language '{language}', falling back to 'zh_cn'")
            language = 'zh_cn'
        
        self.current_language = language
        self.current_translations = self.TRANSLATIONS[language]
    
    def t(self, key: str, *args, **kwargs) -> str:
        """
        获取翻译文本
        
        Args:
            key: 翻译键
            *args: 格式化参数（位置参数）
            **kwargs: 格式化参数（关键字参数）
        
        Returns:
            str: 翻译后的文本
        """
        text = self.current_translations.get(key, f'[Missing translation: {key}]')
        
        # 如果有格式化参数，进行格式化
        if args:
            try:
                text = text.format(*args)
            except (IndexError, KeyError) as e:
                print(f"Warning: Failed to format translation '{key}': {e}")
        elif kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"Warning: Failed to format translation '{key}': {e}")
        
        return text
    
    def set_language(self, language: str):
        """
        设置当前语言
        
        Args:
            language: 语言代码
        """
        if language not in self.SUPPORTED_LANGUAGES:
            print(f"Warning: Unsupported language '{language}', keeping current language '{self.current_language}'")
            return
        
        self.current_language = language
        self.current_translations = self.TRANSLATIONS[language]


# 创建全局翻译实例（默认中文）
# 注意：实际的语言将在config.py中通过环境变量设置后更新
_translator = None


def get_translator(language: str = None) -> Translations:
    """
    获取全局翻译实例
    
    Args:
        language: 语言代码，如果为None则使用已存在的实例
    
    Returns:
        Translations: 翻译实例
    """
    global _translator
    
    if _translator is None or language is not None:
        if language is None:
            language = os.getenv('LANGUAGE', 'zh_cn').lower()
        _translator = Translations(language)
    
    return _translator


def t(key: str, *args, **kwargs) -> str:
    """
    快捷翻译函数
    
    Args:
        key: 翻译键
        *args: 格式化参数（位置参数）
        **kwargs: 格式化参数（关键字参数）
    
    Returns:
        str: 翻译后的文本
    """
    translator = get_translator()
    return translator.t(key, *args, **kwargs)

