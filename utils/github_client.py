import base64
import random
import time
from typing import Dict, List, Optional, Any

import requests

from common.Logger import logger
from common.config import Config
from common.translations import get_translator

# 获取翻译函数
t = get_translator().t


class GitHubClient:
    GITHUB_API_URL = "https://api.github.com/search/code"

    def __init__(self, tokens: List[str]):
        self.tokens = [token.strip() for token in tokens if token.strip()]
        self._token_ptr = 0

    def _next_token(self) -> Optional[str]:
        if not self.tokens:
            return None

        token = self.tokens[self._token_ptr % len(self.tokens)]
        self._token_ptr += 1

        return token.strip() if isinstance(token, str) else token

    def search_for_keys(self, query: str, max_retries: int = 5) -> Dict[str, Any]:
        all_items = []
        total_count = 0
        expected_total = None
        pages_processed = 0

        # 统计信息
        total_requests = 0
        failed_requests = 0
        rate_limit_hits = 0
        failed_pages = []  # 记录失败的页码

        for page in range(1, 11):
            page_result = None
            page_success = False

            for attempt in range(1, max_retries + 1):
                current_token = self._next_token()

                headers = {
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/138.0.0.0 Safari/537.36"
                }

                if current_token:
                    current_token = current_token.strip()
                    headers["Authorization"] = f"token {current_token}"

                params = {
                    "q": query,
                    "per_page": 100,
                    "page": page
                }

                try:
                    total_requests += 1
                    # 获取随机proxy配置
                    proxies = Config.get_random_proxy()
                    
                    if proxies:
                        response = requests.get(self.GITHUB_API_URL, headers=headers, params=params, timeout=30, proxies=proxies)
                    else:
                        response = requests.get(self.GITHUB_API_URL, headers=headers, params=params, timeout=30)
                    rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
                    # 只在剩余次数很少时警告
                    if rate_limit_remaining and int(rate_limit_remaining) < 3:
                        logger.warning(t('rate_limit_low', rate_limit_remaining, current_token))
                    response.raise_for_status()
                    page_result = response.json()
                    
                    page_success = True
                    break

                except requests.exceptions.HTTPError as e:
                    status = e.response.status_code if e.response else None
                    failed_requests += 1
                    
                    # 获取token显示（脱敏处理）
                    token_display = current_token[:20] if current_token else "None"
                    
                    # 尝试从响应中提取详细错误信息
                    error_message = "Unknown error"
                    try:
                        if e.response is not None:
                            error_json = e.response.json()
                            error_message = error_json.get('message', str(e))
                        else:
                            error_message = str(e)
                    except:
                        error_message = str(e)
                    
                    # 根据不同的状态码提供详细的错误信息
                    if status == 401:
                        # Token 无效
                        logger.error(t('token_invalid', token_display, error_message))
                        time.sleep(2 ** attempt)
                        continue
                    elif status == 403:
                        # Token 被禁止或权限不足，可能是速率限制
                        rate_limit_hits += 1
                        rate_limit_remaining = e.response.headers.get('X-RateLimit-Remaining', 'N/A')
                        rate_limit_reset = e.response.headers.get('X-RateLimit-Reset', 'N/A')
                        
                        # 转换重置时间为可读格式
                        if rate_limit_reset != 'N/A':
                            try:
                                from datetime import datetime
                                reset_time = datetime.fromtimestamp(int(rate_limit_reset)).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                reset_time = rate_limit_reset
                        else:
                            reset_time = 'N/A'
                        
                        # 判断是否是速率限制
                        if 'rate limit' in error_message.lower() or rate_limit_remaining == '0':
                            logger.warning(t('token_rate_limited', token_display, rate_limit_remaining, reset_time))
                        else:
                            logger.error(t('token_forbidden', token_display, error_message))
                        
                        wait = min(2 ** attempt + random.uniform(0, 1), 60)
                        if attempt >= 3:
                            logger.warning(t('rate_limit_hit', status, attempt, max_retries, wait))
                        time.sleep(wait)
                        continue
                    elif status == 422:
                        # 查询语法错误（Unprocessable Entity）
                        logger.error(t('query_syntax_error', query[:80], error_message))
                        # 查询语法错误不需要重试，返回特殊标记
                        return {"items": [], "total_count": 0, "query_syntax_error": True}
                    elif status == 429:
                        # 明确的速率限制
                        rate_limit_hits += 1
                        rate_limit_remaining = e.response.headers.get('X-RateLimit-Remaining', '0')
                        rate_limit_reset = e.response.headers.get('X-RateLimit-Reset', 'N/A')
                        
                        # 转换重置时间
                        if rate_limit_reset != 'N/A':
                            try:
                                from datetime import datetime
                                reset_time = datetime.fromtimestamp(int(rate_limit_reset)).strftime('%Y-%m-%d %H:%M:%S')
                            except:
                                reset_time = rate_limit_reset
                        else:
                            reset_time = 'N/A'
                        
                        logger.warning(t('token_rate_limited', token_display, rate_limit_remaining, reset_time))
                        wait = min(2 ** attempt + random.uniform(0, 1), 60)
                        time.sleep(wait)
                        continue
                    else:
                        # 其他HTTP错误
                        if attempt == max_retries:
                            logger.error(t('token_error_detail', status or 'None', token_display, error_message))
                        time.sleep(2 ** attempt)
                        continue

                except requests.exceptions.RequestException as e:
                    failed_requests += 1
                    wait = min(2 ** attempt, 30)

                    # 只在最后一次尝试时记录网络错误
                    if attempt == max_retries:
                        logger.error(t('network_error', max_retries, page, type(e).__name__))

                    time.sleep(wait)
                    continue

            if not page_success or not page_result:
                if page == 1:
                    # 第一页失败是严重问题
                    logger.error(t('first_page_failed', query[:50]))
                    break
                # 记录失败页面信息，便于诊断
                failed_pages.append(page)
                logger.warning(f"⚠️ 第 {page} 页请求失败，已跳过（可能导致数据丢失）")
                continue

            pages_processed += 1

            if page == 1:
                total_count = page_result.get("total_count", 0)
                expected_total = min(total_count, 1000)
                
                if total_count > 0:
                    logger.info(f"   🔢 GitHub返回总数: {total_count} (预期获取: {expected_total})")

            items = page_result.get("items", [])
            current_page_count = len(items)

            if current_page_count == 0:
                if expected_total and len(all_items) < expected_total:
                    continue
                else:
                    break

            all_items.extend(items)

            if expected_total and len(all_items) >= expected_total:
                break

            if page < 10:
                sleep_time = random.uniform(0.5, 1.5)
                logger.info(t('processing_query', query, page, current_page_count, expected_total, total_count, sleep_time))
                time.sleep(sleep_time)

        final_count = len(all_items)

        # 检查数据完整性
        if expected_total and final_count < expected_total:
            discrepancy = expected_total - final_count
            if discrepancy > expected_total * 0.1:  # 超过10%数据丢失
                warning_msg = t('data_loss_warning', discrepancy, expected_total, discrepancy / expected_total * 100)
                if failed_pages:
                    warning_msg += f" | 失败页面: {failed_pages}"
                logger.warning(warning_msg)

        # 主要成功日志 - 一条日志包含所有关键信息
        logger.info(t('search_complete', query, pages_processed, final_count, expected_total or '?', total_requests))

        result = {
            "total_count": total_count,
            "incomplete_results": final_count < expected_total if expected_total else False,
            "items": all_items
        }

        return result

    def get_file_content(self, item: Dict[str, Any]) -> Optional[str]:
        repo_full_name = item["repository"]["full_name"]
        file_path = item["path"]

        metadata_url = f"https://api.github.com/repos/{repo_full_name}/contents/{file_path}"
        headers = {
            "Accept": "application/vnd.github.v3+json",
        }

        token = self._next_token()
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            # 获取proxy配置
            proxies = Config.get_random_proxy()

            logger.info(t('processing_file', metadata_url))
            if proxies:
                metadata_response = requests.get(metadata_url, headers=headers, proxies=proxies)
            else:
                metadata_response = requests.get(metadata_url, headers=headers)

            metadata_response.raise_for_status()
            file_metadata = metadata_response.json()

            # 检查返回的是否为列表（目录内容）而非单个文件
            if isinstance(file_metadata, list):
                logger.warning(t('unexpected_list_response', metadata_url))
                return None

            # 检查是否有base64编码的内容
            encoding = file_metadata.get("encoding")
            content = file_metadata.get("content")
            
            if encoding == "base64" and content:
                try:
                    # 解码base64内容
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    return decoded_content
                except Exception as e:
                    logger.warning(t('decode_failed', e))
            
            # 如果没有base64内容或解码失败，使用原有的download_url逻辑
            download_url = file_metadata.get("download_url")
            if not download_url:
                logger.warning(t('no_download_url', metadata_url))
                return None

            if proxies:
                content_response = requests.get(download_url, headers=headers, proxies=proxies)
            else:
                content_response = requests.get(download_url, headers=headers)
            logger.info(t('checking_keys_from', download_url, content_response.status_code))
            content_response.raise_for_status()
            return content_response.text

        except requests.exceptions.HTTPError as e:
            status = e.response.status_code if e.response else None
            token_display = token[:20] if token else "None"
            
            # 尝试从响应中提取详细错误信息
            error_message = "Unknown error"
            try:
                if e.response is not None:
                    error_json = e.response.json()
                    error_message = error_json.get('message', str(e))
                else:
                    error_message = str(e)
            except:
                error_message = str(e)
            
            # 根据不同的状态码提供详细的错误信息
            if status == 401:
                logger.error(t('token_invalid', token_display, error_message))
            elif status == 403:
                rate_limit_remaining = e.response.headers.get('X-RateLimit-Remaining', 'N/A')
                rate_limit_reset = e.response.headers.get('X-RateLimit-Reset', 'N/A')
                
                if rate_limit_reset != 'N/A':
                    try:
                        from datetime import datetime
                        reset_time = datetime.fromtimestamp(int(rate_limit_reset)).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        reset_time = rate_limit_reset
                else:
                    reset_time = 'N/A'
                
                if 'rate limit' in error_message.lower() or rate_limit_remaining == '0':
                    logger.warning(t('token_rate_limited', token_display, rate_limit_remaining, reset_time))
                else:
                    logger.error(t('token_forbidden', token_display, error_message))
            elif status == 429:
                rate_limit_remaining = e.response.headers.get('X-RateLimit-Remaining', '0')
                rate_limit_reset = e.response.headers.get('X-RateLimit-Reset', 'N/A')
                
                if rate_limit_reset != 'N/A':
                    try:
                        from datetime import datetime
                        reset_time = datetime.fromtimestamp(int(rate_limit_reset)).strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        reset_time = rate_limit_reset
                else:
                    reset_time = 'N/A'
                
                logger.warning(t('token_rate_limited', token_display, rate_limit_remaining, reset_time))
            else:
                logger.error(t('token_error_detail', status or 'None', token_display, error_message))
            
            return None
        except requests.exceptions.RequestException as e:
            logger.error(t('fetch_file_failed', metadata_url, type(e).__name__))
            return None

    @staticmethod
    def create_instance(tokens: List[str]) -> 'GitHubClient':
        return GitHubClient(tokens)
