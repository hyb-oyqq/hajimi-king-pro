import os
import random
import re
import sys
import time
import traceback
from datetime import datetime, timedelta
from typing import Dict, List, Union, Any

# 添加项目根目录到模块搜索路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

import google.generativeai as genai
from google.api_core import exceptions as google_exceptions

from common.Logger import logger
from common.config import Config
from common.translations import get_translator
from utils.github_client import GitHubClient
from utils.file_manager import file_manager, Checkpoint, checkpoint
from utils.sync_utils import sync_utils

# 获取翻译函数
t = get_translator().t

# 创建GitHub工具实例和文件管理器
github_utils = GitHubClient.create_instance(Config.GITHUB_TOKENS)

# 统计信息
skip_stats = {
    "time_filter": 0,
    "sha_duplicate": 0,
    "age_filter": 0,
    "doc_filter": 0
}


def normalize_query(query: str) -> str:
    query = " ".join(query.split())

    parts = []
    i = 0
    while i < len(query):
        if query[i] == '"':
            end_quote = query.find('"', i + 1)
            if end_quote != -1:
                parts.append(query[i:end_quote + 1])
                i = end_quote + 1
            else:
                parts.append(query[i])
                i += 1
        elif query[i] == ' ':
            i += 1
        else:
            start = i
            while i < len(query) and query[i] != ' ':
                i += 1
            parts.append(query[start:i])

    quoted_strings = []
    language_parts = []
    filename_parts = []
    path_parts = []
    other_parts = []

    for part in parts:
        if part.startswith('"') and part.endswith('"'):
            quoted_strings.append(part)
        elif part.startswith('language:'):
            language_parts.append(part)
        elif part.startswith('filename:'):
            filename_parts.append(part)
        elif part.startswith('path:'):
            path_parts.append(part)
        elif part.strip():
            other_parts.append(part)

    normalized_parts = []
    normalized_parts.extend(sorted(quoted_strings))
    normalized_parts.extend(sorted(other_parts))
    normalized_parts.extend(sorted(language_parts))
    normalized_parts.extend(sorted(filename_parts))
    normalized_parts.extend(sorted(path_parts))

    return " ".join(normalized_parts)


def extract_keys_from_content(content: str) -> List[str]:
    pattern = r'(AIzaSy[A-Za-z0-9\-_]{33})'
    return re.findall(pattern, content)


def should_skip_item(item: Dict[str, Any], checkpoint: Checkpoint) -> tuple[bool, str]:
    """
    检查是否应该跳过处理此item
    
    Returns:
        tuple: (should_skip, reason)
    """
    # 检查增量扫描时间
    if checkpoint.last_scan_time:
        try:
            last_scan_dt = datetime.fromisoformat(checkpoint.last_scan_time)
            repo_pushed_at = item["repository"].get("pushed_at")
            if repo_pushed_at:
                repo_pushed_dt = datetime.strptime(repo_pushed_at, "%Y-%m-%dT%H:%M:%SZ")
                if repo_pushed_dt <= last_scan_dt:
                    skip_stats["time_filter"] += 1
                    return True, "time_filter"
        except Exception as e:
            pass

    # 检查SHA是否已扫描
    if item.get("sha") in checkpoint.scanned_shas:
        skip_stats["sha_duplicate"] += 1
        return True, "sha_duplicate"

    # 检查仓库年龄
    repo_pushed_at = item["repository"].get("pushed_at")
    if repo_pushed_at:
        repo_pushed_dt = datetime.strptime(repo_pushed_at, "%Y-%m-%dT%H:%M:%SZ")
        if repo_pushed_dt < datetime.utcnow() - timedelta(days=Config.DATE_RANGE_DAYS):
            skip_stats["age_filter"] += 1
            return True, "age_filter"

    # 检查文档和示例文件
    lowercase_path = item["path"].lower()
    if any(token in lowercase_path for token in Config.FILE_PATH_BLACKLIST):
        skip_stats["doc_filter"] += 1
        return True, "doc_filter"

    return False, ""


def process_item(item: Dict[str, Any]) -> tuple:
    """
    处理单个GitHub搜索结果item
    
    Returns:
        tuple: (valid_keys_count, rate_limited_keys_count)
    """
    delay = random.uniform(1, 4)
    file_url = item["html_url"]

    # 简化日志输出，只显示关键信息
    repo_name = item["repository"]["full_name"]
    file_path = item["path"]
    time.sleep(delay)

    content = github_utils.get_file_content(item)
    if not content:
        logger.warning(t('failed_fetch_content', file_url))
        return 0, 0

    keys = extract_keys_from_content(content)

    # 过滤占位符密钥
    filtered_keys = []
    for key in keys:
        context_index = content.find(key)
        if context_index != -1:
            snippet = content[context_index:context_index + 45]
            if "..." in snippet or "YOUR_" in snippet.upper():
                continue
        filtered_keys.append(key)
    
    # 去重处理
    keys = list(set(filtered_keys))

    if not keys:
        return 0, 0

    logger.info(t('found_keys', len(keys)))

    valid_keys = []
    rate_limited_keys = []

    # 验证每个密钥
    for key in keys:
        validation_result = validate_gemini_key(key)
        if validation_result and "ok" in validation_result:
            valid_keys.append(key)
            logger.info(t('valid_key', key))
        elif validation_result == "rate_limited":
            rate_limited_keys.append(key)
            logger.warning(t('rate_limited_key', key, validation_result))
        else:
            logger.info(t('invalid_key', key, validation_result))

    # 保存结果
    if valid_keys:
        file_manager.save_valid_keys(repo_name, file_path, file_url, valid_keys)
        logger.info(t('saved_valid_keys', len(valid_keys)))
        # 添加到同步队列（不阻塞主流程）
        try:
            # 添加到两个队列
            sync_utils.add_keys_to_queue(valid_keys)
            logger.info(t('added_to_queue', len(valid_keys)))
        except Exception as e:
            logger.error(t('error_adding_to_queue', e))

    if rate_limited_keys:
        file_manager.save_rate_limited_keys(repo_name, file_path, file_url, rate_limited_keys)
        logger.info(t('saved_rate_limited_keys', len(rate_limited_keys)))

    return len(valid_keys), len(rate_limited_keys)


def validate_gemini_key(api_key: str) -> Union[bool, str]:
    try:
        time.sleep(random.uniform(0.5, 1.5))

        # 获取随机代理配置
        proxy_config = Config.get_random_proxy()
        
        client_options = {
            "api_endpoint": "generativelanguage.googleapis.com"
        }
        
        # 如果有代理配置，添加到client_options中
        if proxy_config:
            os.environ['grpc_proxy'] = proxy_config.get('http')

        genai.configure(
            api_key=api_key,
            client_options=client_options,
        )

        model = genai.GenerativeModel(Config.HAJIMI_CHECK_MODEL)
        response = model.generate_content("hi")
        return "ok"
    except (google_exceptions.PermissionDenied, google_exceptions.Unauthenticated) as e:
        return "not_authorized_key"
    except google_exceptions.TooManyRequests as e:
        return "rate_limited"
    except Exception as e:
        if "429" in str(e) or "rate limit" in str(e).lower() or "quota" in str(e).lower():
            return "rate_limited:429"
        elif "403" in str(e) or "SERVICE_DISABLED" in str(e) or "API has not been used" in str(e):
            return "disabled"
        else:
            return f"error:{e.__class__.__name__}"


def print_skip_stats():
    """打印跳过统计信息"""
    total_skipped = sum(skip_stats.values())
    if total_skipped > 0:
        logger.info(t('skip_stats', total_skipped, skip_stats['time_filter'], skip_stats['sha_duplicate'], skip_stats['age_filter'], skip_stats['doc_filter']))


def reset_skip_stats():
    """重置跳过统计"""
    global skip_stats
    skip_stats = {"time_filter": 0, "sha_duplicate": 0, "age_filter": 0, "doc_filter": 0}


def main():
    start_time = datetime.now()

    # 打印系统启动信息
    logger.info("=" * 60)
    logger.info(t('system_starting'))
    logger.info("=" * 60)
    logger.info(t('started_at', start_time.strftime('%Y-%m-%d %H:%M:%S')))

    # 1. 检查配置
    if not Config.check():
        logger.info(t('config_check_failed'))
        sys.exit(1)
    # 2. 检查文件管理器
    if not file_manager.check():
        logger.error(t('filemanager_check_failed'))
        sys.exit(1)

    # 2.5. 显示SyncUtils状态和队列信息
    if sync_utils.balancer_enabled:
        logger.info(t('syncutils_ready'))
        
    # 显示队列状态
    balancer_queue_count = len(checkpoint.wait_send_balancer)
    gpt_load_queue_count = len(checkpoint.wait_send_gpt_load)
    logger.info(t('queue_status', balancer_queue_count, gpt_load_queue_count))

    # 3. 显示系统信息
    search_queries = file_manager.get_search_queries()
    logger.info(t('system_information'))
    logger.info(t('github_tokens_count', len(Config.GITHUB_TOKENS)))
    logger.info(t('search_queries_count', len(search_queries)))
    logger.info(t('date_filter', Config.DATE_RANGE_DAYS))
    if Config.PROXY_LIST:
        logger.info(t('proxy_configured', len(Config.PROXY_LIST)))

    if checkpoint.last_scan_time:
        logger.info(t('checkpoint_found'))
        logger.info(t('last_scan', checkpoint.last_scan_time))
        logger.info(t('scanned_files', len(checkpoint.scanned_shas)))
        logger.info(t('processed_queries', len(checkpoint.processed_queries)))
    else:
        logger.info(t('no_checkpoint'))


    logger.info(t('system_ready'))
    logger.info("=" * 60)

    total_keys_found = 0
    total_rate_limited_keys = 0
    loop_count = 0

    while True:
        try:
            loop_count += 1
            logger.info(t('loop_start', loop_count, datetime.now().strftime('%H:%M:%S')))

            # 清空上一轮的已处理查询，准备新一轮搜索
            if loop_count > 1:
                checkpoint.processed_queries.clear()
                file_manager.save_checkpoint(checkpoint)
                logger.info(t('cleared_queries'))

            query_count = 0
            loop_processed_files = 0
            reset_skip_stats()

            for i, q in enumerate(search_queries, 1):
                normalized_q = normalize_query(q)
                if normalized_q in checkpoint.processed_queries:
                    logger.info(t('skipping_query', q, i))
                    continue

                res = github_utils.search_for_keys(q)

                if res and "items" in res:
                    items = res["items"]
                    if items:
                        query_valid_keys = 0
                        query_rate_limited_keys = 0
                        query_processed = 0

                        for item_index, item in enumerate(items, 1):

                            # 每20个item保存checkpoint并显示进度
                            if item_index % 20 == 0:
                                logger.info(t('progress', item_index, len(items), q, query_valid_keys, query_rate_limited_keys, total_keys_found, total_rate_limited_keys))
                                file_manager.save_checkpoint(checkpoint)
                                file_manager.update_dynamic_filenames()

                            # 检查是否应该跳过此item
                            should_skip, skip_reason = should_skip_item(item, checkpoint)
                            if should_skip:
                                logger.info(t('skipping_item', item.get('path','').lower(), item_index, skip_reason))
                                continue

                            # 处理单个item
                            valid_count, rate_limited_count = process_item(item)

                            query_valid_keys += valid_count
                            query_rate_limited_keys += rate_limited_count
                            query_processed += 1

                            # 记录已扫描的SHA
                            checkpoint.add_scanned_sha(item.get("sha"))

                            loop_processed_files += 1



                        total_keys_found += query_valid_keys
                        total_rate_limited_keys += query_rate_limited_keys

                        if query_processed > 0:
                            logger.info(t('query_complete', i, len(search_queries), query_processed, query_valid_keys, query_rate_limited_keys))
                        else:
                            logger.info(t('query_all_skipped', i, len(search_queries)))

                        print_skip_stats()
                    else:
                        logger.info(t('query_no_items', i, len(search_queries)))
                else:
                    logger.warning(t('query_failed', i, len(search_queries)))

                checkpoint.add_processed_query(normalized_q)
                query_count += 1

                checkpoint.update_scan_time()
                file_manager.save_checkpoint(checkpoint)
                file_manager.update_dynamic_filenames()

                if query_count % 5 == 0:
                    logger.info(t('taking_break', query_count))
                    time.sleep(1)

            logger.info(t('loop_complete', loop_count, loop_processed_files, total_keys_found, total_rate_limited_keys))

            logger.info(t('sleeping'))
            time.sleep(10)

        except KeyboardInterrupt:
            logger.info(t('interrupted'))
            checkpoint.update_scan_time()
            file_manager.save_checkpoint(checkpoint)
            logger.info(t('final_stats', total_keys_found, total_rate_limited_keys))
            logger.info(t('shutting_down'))
            sync_utils.shutdown()
            break
        except Exception as e:
            logger.error(t('unexpected_error', e))
            traceback.print_exc()
            logger.info(t('continuing'))
            continue


if __name__ == "__main__":
    main()
