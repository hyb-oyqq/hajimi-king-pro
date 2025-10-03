import json
import threading
import time
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import List, Dict, Optional

import requests

from common.Logger import logger
from common.config import Config
from common.translations import get_translator
from common import state
from utils.file_manager import file_manager, checkpoint

# 获取翻译函数
t = get_translator().t


class SyncUtils:
    """同步工具类，负责异步发送keys到外部应用"""

    def __init__(self):
        """初始化同步工具"""
        # Gemini Balancer 配置
        self.balancer_url = Config.GEMINI_BALANCER_URL.rstrip('/') if Config.GEMINI_BALANCER_URL else ""
        self.balancer_auth = Config.GEMINI_BALANCER_AUTH
        self.balancer_sync_enabled = Config.parse_bool(Config.GEMINI_BALANCER_SYNC_ENABLED)
        self.balancer_enabled = bool(self.balancer_url and self.balancer_auth and self.balancer_sync_enabled)

        # GPT-load 配置
        self.gpt_load_url = Config.GPT_LOAD_URL.rstrip('/') if Config.GPT_LOAD_URL else ""
        self.gpt_load_auth = Config.GPT_LOAD_AUTH
        # 解析多个group names (逗号分隔)
        self.gpt_load_group_names = [name.strip() for name in Config.GPT_LOAD_GROUP_NAME.split(',') if name.strip()] if Config.GPT_LOAD_GROUP_NAME else []
        self.gpt_load_sync_enabled = Config.parse_bool(Config.GPT_LOAD_SYNC_ENABLED)
        self.gpt_load_enabled = bool(self.gpt_load_url and self.gpt_load_auth and self.gpt_load_group_names and self.gpt_load_sync_enabled)

        # GPT-load - Paid Keys 配置
        self.gpt_load_paid_group_name = Config.GPT_LOAD_PAID_GROUP_NAME.strip() if Config.GPT_LOAD_PAID_GROUP_NAME else ""
        self.gpt_load_paid_sync_enabled = Config.parse_bool(Config.GPT_LOAD_PAID_SYNC_ENABLED)
        self.gpt_load_paid_enabled = bool(self.gpt_load_url and self.gpt_load_auth and self.gpt_load_paid_group_name and self.gpt_load_paid_sync_enabled)

        # GPT-load - Rate Limited Keys 配置
        self.gpt_load_rate_limited_group_name = Config.GPT_LOAD_RATE_LIMITED_GROUP_NAME.strip() if Config.GPT_LOAD_RATE_LIMITED_GROUP_NAME else ""
        self.rate_limited_handling = Config.RATE_LIMITED_HANDLING.strip().lower()
        self.gpt_load_rate_limited_enabled = bool(
            self.gpt_load_url and 
            self.gpt_load_auth and 
            self.gpt_load_rate_limited_group_name and 
            self.rate_limited_handling == "sync_separate"
        )

        # 创建线程池用于异步执行
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix="SyncUtils")
        self.saving_checkpoint = False

        # 周期性发送控制
        self.batch_interval = 60
        self.batch_timer = None
        self.shutdown_flag = False

        # GPT-load group ID 缓存 (15分钟缓存)
        self.group_id_cache: Dict[str, int] = {}
        self.group_id_cache_time: Dict[str, float] = {}
        self.group_id_cache_ttl = 15 * 60  # 15分钟

        if not self.balancer_enabled:
            logger.warning(t('balancer_sync_disabled'))
        else:
            logger.info(t('balancer_enabled_url', self.balancer_url))

        if not self.gpt_load_enabled:
            logger.warning(t('gpt_load_sync_disabled'))
        else:
            logger.info(t('gpt_load_enabled_url', self.gpt_load_url, ', '.join(self.gpt_load_group_names)))

        if not self.gpt_load_paid_enabled:
            logger.warning("💎 付费密钥上传功能未启用")
        else:
            logger.info(f"💎 付费密钥上传已启用: {self.gpt_load_url} -> 分组: {self.gpt_load_paid_group_name}")

        # 429密钥处理策略日志
        logger.info(f"⏰ 429密钥处理策略: {self.rate_limited_handling}")
        if self.gpt_load_rate_limited_enabled:
            logger.info(f"⏰ 429密钥单独分组已启用: {self.gpt_load_url} -> 分组: {self.gpt_load_rate_limited_group_name}")

        # 启动周期性发送线程
        self._start_batch_sender()

    def add_keys_to_queue(self, keys: List[str]):
        """
        将keys同时添加到balancer和GPT load的发送队列
        
        Args:
            keys: API keys列表
        """
        if not keys:
            return

        # Acquire lock for checkpoint saving
        while self.saving_checkpoint:
            logger.info(t('checkpoint_saving_wait', len(keys)))
            time.sleep(0.5)  # Small delay to prevent busy-waiting

        self.saving_checkpoint = True  # Acquire the lock
        try:

            # Gemini Balancer
            if self.balancer_enabled:
                initial_balancer_count = len(checkpoint.wait_send_balancer)
                checkpoint.wait_send_balancer.update(keys)
                new_balancer_count = len(checkpoint.wait_send_balancer)
                added_balancer_count = new_balancer_count - initial_balancer_count
                logger.info(t('added_to_balancer_queue', added_balancer_count, new_balancer_count))
            else:
                logger.info(t('balancer_disabled_skipping', len(keys)))

            # GPT-load
            if self.gpt_load_enabled:
                initial_gpt_count = len(checkpoint.wait_send_gpt_load)
                checkpoint.wait_send_gpt_load.update(keys)
                new_gpt_count = len(checkpoint.wait_send_gpt_load)
                added_gpt_count = new_gpt_count - initial_gpt_count
                logger.info(t('added_to_gpt_load_queue', added_gpt_count, new_gpt_count))
            else:
                logger.info(t('gpt_load_disabled_skipping', len(keys)))

            file_manager.save_checkpoint(checkpoint)
        finally:
            self.saving_checkpoint = False  # Release the lock

    def add_paid_keys_to_queue(self, keys: List[str]):
        """
        将付费密钥添加到GPT-load的独立分组队列
        
        Args:
            keys: 付费API keys列表
        """
        if not keys:
            return

        # Acquire lock for checkpoint saving
        while self.saving_checkpoint:
            logger.info(f"💎 等待checkpoint保存完成... (付费密钥: {len(keys)} 个)")
            time.sleep(0.5)

        self.saving_checkpoint = True  # Acquire the lock
        try:
            # GPT-load - Paid Keys
            if self.gpt_load_paid_enabled:
                initial_paid_count = len(checkpoint.wait_send_gpt_load_paid)
                checkpoint.wait_send_gpt_load_paid.update(keys)
                new_paid_count = len(checkpoint.wait_send_gpt_load_paid)
                added_paid_count = new_paid_count - initial_paid_count
                logger.info(f"💎 已添加 {added_paid_count} 个付费密钥到队列 (总计: {new_paid_count})")
            else:
                logger.info(f"💎 付费密钥上传功能已关闭，跳过 {len(keys)} 个付费密钥")

            file_manager.save_checkpoint(checkpoint)
        finally:
            self.saving_checkpoint = False  # Release the lock

    def add_rate_limited_keys_to_queue(self, keys: List[str]):
        """
        将429限速密钥添加到GPT-load的独立分组队列
        
        Args:
            keys: 429限速API keys列表
        """
        if not keys:
            return

        # Acquire lock for checkpoint saving
        while self.saving_checkpoint:
            logger.info(f"⏰ 等待checkpoint保存完成... (429密钥: {len(keys)} 个)")
            time.sleep(0.5)

        self.saving_checkpoint = True  # Acquire the lock
        try:
            # GPT-load - Rate Limited Keys
            if self.gpt_load_rate_limited_enabled:
                initial_count = len(checkpoint.wait_send_gpt_load_rate_limited)
                checkpoint.wait_send_gpt_load_rate_limited.update(keys)
                new_count = len(checkpoint.wait_send_gpt_load_rate_limited)
                added_count = new_count - initial_count
                logger.info(f"⏰ 已添加 {added_count} 个429密钥到独立队列 (总计: {new_count})")
            else:
                logger.info(f"⏰ 429密钥单独上传功能未启用，跳过 {len(keys)} 个密钥")

            file_manager.save_checkpoint(checkpoint)
        finally:
            self.saving_checkpoint = False  # Release the lock

    def _send_balancer_worker(self, keys: List[str]) -> str:
        """
        实际执行发送到balancer的工作函数（在后台线程中执行）
        
        Args:
            keys: API keys列表
            
        Returns:
            str: "ok" if success, otherwise an error code string.
        """
        try:
            logger.info(t('sending_keys_to_balancer', len(keys)))

            # 1. 获取当前配置
            config_url = f"{self.balancer_url}/api/config"
            headers = {
                'Cookie': f'auth_token={self.balancer_auth}',
                'User-Agent': 'HajimiKing/1.0'
            }

            logger.info(t('fetching_config_from', config_url))

            # 获取当前配置
            response = requests.get(config_url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(t('get_config_failed', response.status_code, response.text))
                return "get_config_failed_not_200"

            # 解析配置
            config_data = response.json()

            # 2. 获取当前的API_KEYS数组
            current_api_keys = config_data.get('API_KEYS', [])

            # 3. 合并新keys（去重）
            existing_keys_set = set(current_api_keys)
            new_add_keys_set = set()
            for key in keys:
                if key not in existing_keys_set:
                    existing_keys_set.add(key)
                    new_add_keys_set.add(key)

            if len(new_add_keys_set) == 0:
                logger.info(t('all_keys_exist', len(keys)))
                # 不需要记录发送结果，因为没有实际发送新密钥
                return "ok"

            # 4. 更新配置中的API_KEYS
            config_data['API_KEYS'] = list(existing_keys_set)

            logger.info(t('updating_balancer_config', len(new_add_keys_set)))

            # 5. 发送更新后的配置到服务器
            update_headers = headers.copy()
            update_headers['Content-Type'] = 'application/json'

            update_response = requests.put(
                config_url,
                headers=update_headers,
                json=config_data,
                timeout=60
            )

            if update_response.status_code != 200:
                logger.error(t('update_config_failed', update_response.status_code, update_response.text))
                return "update_config_failed_not_200"

            # 6. 验证是否添加成功
            updated_config = update_response.json()
            updated_api_keys = updated_config.get('API_KEYS', [])
            updated_keys_set = set(updated_api_keys)

            failed_to_add = [key for key in new_add_keys_set if key not in updated_keys_set]

            if failed_to_add:
                logger.error(t('failed_to_add_keys', len(failed_to_add), [key[:10] + '...' for key in failed_to_add]))
                # 保存发送结果日志 - 部分成功的情况
                send_result = {}
                keys_to_log = []
                for key in new_add_keys_set:  # 只记录尝试新增的密钥
                    if key in failed_to_add:
                        send_result[key] = "update_failed"
                        keys_to_log.append(key)
                    else:
                        send_result[key] = "ok"
                        keys_to_log.append(key)
                if keys_to_log:  # 只有当有需要记录的密钥时才记录
                    file_manager.save_keys_send_result(keys_to_log, send_result)
                return "update_failed"


            logger.info(t('all_keys_added_successfully', len(new_add_keys_set)))
            
            # 保存发送结果日志 - 只记录实际新增的密钥
            send_result = {key: "ok" for key in new_add_keys_set}
            if send_result:  # 只有当有新增密钥时才记录
                file_manager.save_keys_send_result(list(new_add_keys_set), send_result)
            
            return "ok"

        except requests.exceptions.Timeout:
            logger.error(t('request_timeout_balancer'))
            # 保存发送结果日志 - 所有密钥都失败
            send_result = {key: "timeout" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "timeout"
        except requests.exceptions.ConnectionError:
            logger.error(t('connection_failed_balancer'))
            # 保存发送结果日志 - 所有密钥都失败
            send_result = {key: "connection_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "connection_error"
        except json.JSONDecodeError as e:
            logger.error(t('invalid_json_balancer', str(e)))
            # 保存发送结果日志 - 所有密钥都失败
            send_result = {key: "json_decode_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "json_decode_error"
        except Exception as e:
            logger.error(t('failed_send_to_balancer', str(e)))
            traceback.print_exc()
            # 保存发送结果日志 - 所有密钥都失败
            send_result = {key: "exception" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "exception"

    def _get_gpt_load_group_id(self, group_name: str) -> Optional[int]:
        """
        获取GPT-load group ID，带缓存功能
        
        Args:
            group_name: 组名
            
        Returns:
            Optional[int]: 组ID，如果未找到则返回None
        """
        current_time = time.time()
        
        # 检查缓存是否有效
        if (group_name in self.group_id_cache and
            group_name in self.group_id_cache_time and
            current_time - self.group_id_cache_time[group_name] < self.group_id_cache_ttl):
            logger.info(t('using_cached_group_id', group_name, self.group_id_cache[group_name]))
            return self.group_id_cache[group_name]
        
        # 缓存过期或不存在，重新获取
        try:
            groups_url = f"{self.gpt_load_url}/api/groups"
            headers = {
                'Authorization': f'Bearer {self.gpt_load_auth}',
                'User-Agent': 'HajimiKing/1.0'
            }

            logger.info(t('fetching_groups_from', groups_url))

            response = requests.get(groups_url, headers=headers, timeout=30)

            if response.status_code != 200:
                logger.error(t('get_groups_failed', response.status_code, response.text))
                return None

            groups_data = response.json()
            
            if groups_data.get('code') != 0:
                logger.error(t('groups_api_error', groups_data.get('message', 'Unknown error')))
                return None

            # 查找指定group的ID
            groups_list = groups_data.get('data', [])
            for group in groups_list:
                if group.get('name') == group_name:
                    group_id = group.get('id')
                    # 更新缓存
                    self.group_id_cache[group_name] = group_id
                    self.group_id_cache_time[group_name] = current_time
                    logger.info(t('found_and_cached_group', group_name, group_id))
                    return group_id

            logger.error(t('group_not_found', group_name))
            return None

        except Exception as e:
            logger.error(t('failed_get_group_id', group_name, str(e)))
            return None

    def _send_gpt_load_paid_worker(self, keys: List[str]) -> str:
        """
        实际执行发送付费密钥到GPT-load的工作函数（在后台线程中执行）
        
        Args:
            keys: 付费API keys列表
            
        Returns:
            str: "ok" if success, otherwise an error code string.
        """
        try:
            logger.info(f"💎 正在发送 {len(keys)} 个付费密钥到GPT-load分组: {self.gpt_load_paid_group_name}")

            # 1. 获取group ID (使用缓存)
            group_id = self._get_gpt_load_group_id(self.gpt_load_paid_group_name)
            
            if group_id is None:
                logger.error(f"💎 获取付费分组ID失败: {self.gpt_load_paid_group_name}")
                return "failed_get_group_id"

            # 2. 发送keys到指定group
            add_keys_url = f"{self.gpt_load_url}/api/keys/add-async"
            keys_text = ",".join(keys)
            
            add_headers = {
                'Authorization': f'Bearer {self.gpt_load_auth}',
                'Content-Type': 'application/json',
                'User-Agent': 'HajimiKing/1.0'
            }

            payload = {
                "group_id": group_id,
                "keys_text": keys_text
            }

            logger.info(f"💎 添加 {len(keys)} 个付费密钥到分组 [{self.gpt_load_paid_group_name}] (ID: {group_id})")

            # 发送添加keys请求
            add_response = requests.post(
                add_keys_url,
                headers=add_headers,
                json=payload,
                timeout=60
            )

            if add_response.status_code != 200:
                logger.error(f"💎 添加付费密钥失败: HTTP {add_response.status_code} - {add_response.text}")
                return "add_keys_failed"

            # 解析添加keys响应
            add_data = add_response.json()
            
            if add_data.get('code') != 0:
                logger.error(f"💎 添加付费密钥API错误: {add_data.get('message', 'Unknown error')}")
                return "add_keys_api_error"

            # 检查任务状态
            task_data = add_data.get('data', {})
            task_type = task_data.get('task_type')
            is_running = task_data.get('is_running')
            total = task_data.get('total', 0)

            logger.info(f"💎 付费密钥任务已启动 [{self.gpt_load_paid_group_name}]")
            logger.info(f"💎 任务类型: {task_type}, 运行中: {is_running}, 总数: {total}")
            
            # 保存发送结果日志
            send_result = {key: "ok" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            
            return "ok"

        except requests.exceptions.Timeout:
            logger.error("💎 请求超时 - GPT-load (付费密钥)")
            send_result = {key: "timeout" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "timeout"
        except requests.exceptions.ConnectionError:
            logger.error("💎 连接失败 - GPT-load (付费密钥)")
            send_result = {key: "connection_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "connection_error"
        except json.JSONDecodeError as e:
            logger.error(f"💎 JSON解析错误 - GPT-load (付费密钥): {str(e)}")
            send_result = {key: "json_decode_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "json_decode_error"
        except Exception as e:
            logger.error(f"💎 发送付费密钥失败: {str(e)}", exc_info=True)
            send_result = {key: "exception" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "exception"

    def _send_gpt_load_rate_limited_worker(self, keys: List[str]) -> str:
        """
        实际执行发送429限速密钥到GPT-load的工作函数（在后台线程中执行）
        
        Args:
            keys: 429限速API keys列表
            
        Returns:
            str: "ok" if success, otherwise an error code string.
        """
        try:
            logger.info(f"⏰ 正在发送 {len(keys)} 个429密钥到GPT-load分组: {self.gpt_load_rate_limited_group_name}")

            # 1. 获取group ID (使用缓存)
            group_id = self._get_gpt_load_group_id(self.gpt_load_rate_limited_group_name)
            
            if group_id is None:
                logger.error(f"⏰ 获取429分组ID失败: {self.gpt_load_rate_limited_group_name}")
                return "failed_get_group_id"

            # 2. 发送keys到指定group
            add_keys_url = f"{self.gpt_load_url}/api/keys/add-async"
            keys_text = ",".join(keys)
            
            add_headers = {
                'Authorization': f'Bearer {self.gpt_load_auth}',
                'Content-Type': 'application/json',
                'User-Agent': 'HajimiKing/1.0'
            }

            payload = {
                "group_id": group_id,
                "keys_text": keys_text
            }

            logger.info(f"⏰ 添加 {len(keys)} 个429密钥到分组 [{self.gpt_load_rate_limited_group_name}] (ID: {group_id})")

            # 发送添加keys请求
            add_response = requests.post(
                add_keys_url,
                headers=add_headers,
                json=payload,
                timeout=60
            )

            if add_response.status_code != 200:
                logger.error(f"⏰ 添加429密钥失败: HTTP {add_response.status_code} - {add_response.text}")
                return "add_keys_failed"

            # 解析添加keys响应
            add_data = add_response.json()
            
            if add_data.get('code') != 0:
                logger.error(f"⏰ 添加429密钥API错误: {add_data.get('message', 'Unknown error')}")
                return "add_keys_api_error"

            # 检查任务状态
            task_data = add_data.get('data', {})
            task_type = task_data.get('task_type')
            is_running = task_data.get('is_running')
            total = task_data.get('total', 0)

            logger.info(f"⏰ 429密钥任务已启动 [{self.gpt_load_rate_limited_group_name}]")
            logger.info(f"⏰ 任务类型: {task_type}, 运行中: {is_running}, 总数: {total}")
            
            # 保存发送结果日志
            send_result = {key: "ok_rate_limited" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            
            return "ok"

        except requests.exceptions.Timeout:
            logger.error("⏰ 请求超时 - GPT-load (429密钥)")
            send_result = {key: "timeout" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "timeout"
        except requests.exceptions.ConnectionError:
            logger.error("⏰ 连接失败 - GPT-load (429密钥)")
            send_result = {key: "connection_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "connection_error"
        except json.JSONDecodeError as e:
            logger.error(f"⏰ JSON解析错误 - GPT-load (429密钥): {str(e)}")
            send_result = {key: "json_decode_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "json_decode_error"
        except Exception as e:
            logger.error(f"⏰ 发送429密钥失败: {str(e)}", exc_info=True)
            send_result = {key: "exception" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "exception"

    def _send_gpt_load_worker(self, keys: List[str]) -> str:
        """
        实际执行发送到GPT-load的工作函数（在后台线程中执行）
        
        Args:
            keys: API keys列表
            
        Returns:
            str: "ok" if success, otherwise an error code string.
        """
        try:
            logger.info(t('sending_to_gpt_load', len(keys), len(self.gpt_load_group_names)))

            # 遍历所有group names，为每个group发送keys
            all_success = True
            failed_groups = []
            
            for group_name in self.gpt_load_group_names:
                logger.info(t('processing_group', group_name))
                
                # 1. 获取group ID (使用缓存)
                group_id = self._get_gpt_load_group_id(group_name)
                
                if group_id is None:
                    logger.error(t('failed_get_group_id_short', group_name))
                    failed_groups.append(group_name)
                    all_success = False
                    continue

                # 2. 发送keys到指定group
                add_keys_url = f"{self.gpt_load_url}/api/keys/add-async"
                keys_text = ",".join(keys)
                
                add_headers = {
                    'Authorization': f'Bearer {self.gpt_load_auth}',
                    'Content-Type': 'application/json',
                    'User-Agent': 'HajimiKing/1.0'
                }

                payload = {
                    "group_id": group_id,
                    "keys_text": keys_text
                }

                logger.info(t('adding_keys_to_group', len(keys), group_name, group_id))

                try:
                    # 发送添加keys请求
                    add_response = requests.post(
                        add_keys_url,
                        headers=add_headers,
                        json=payload,
                        timeout=60
                    )

                    if add_response.status_code != 200:
                        logger.error(t('failed_add_keys_to_group', group_name, add_response.status_code, add_response.text))
                        failed_groups.append(group_name)
                        all_success = False
                        continue

                    # 解析添加keys响应
                    add_data = add_response.json()
                    
                    if add_data.get('code') != 0:
                        logger.error(t('add_keys_api_error', group_name, add_data.get('message', 'Unknown error')))
                        failed_groups.append(group_name)
                        all_success = False
                        continue

                    # 检查任务状态
                    task_data = add_data.get('data', {})
                    task_type = task_data.get('task_type')
                    is_running = task_data.get('is_running')
                    total = task_data.get('total', 0)
                    response_group_name = task_data.get('group_name')

                    logger.info(t('keys_task_started', group_name))
                    logger.info(t('task_type', task_type))
                    logger.info(t('is_running', is_running))
                    logger.info(t('total_keys', total))
                    logger.info(t('group_name', response_group_name))

                except Exception as e:
                    logger.error(t('exception_adding_to_group', group_name, str(e)))
                    failed_groups.append(group_name)
                    all_success = False
                    continue

            # 根据结果返回状态
            if all_success:
                logger.info(t('sent_to_all_groups', len(self.gpt_load_group_names)))
                # 保存发送结果日志 - 所有密钥都成功
                send_result = {key: "ok" for key in keys}
                file_manager.save_keys_send_result(keys, send_result)
                return "ok"
            else:
                logger.error(t('failed_send_to_groups', len(failed_groups), ', '.join(failed_groups)))
                # 保存发送结果日志 - 部分或全部失败
                send_result = {key: f"partial_failure_{len(failed_groups)}_groups" for key in keys}
                file_manager.save_keys_send_result(keys, send_result)
                return "partial_failure"

        except requests.exceptions.Timeout:
            logger.error(t('request_timeout_gpt_load'))
            send_result = {key: "timeout" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "timeout"
        except requests.exceptions.ConnectionError:
            logger.error(t('connection_failed_gpt_load'))
            send_result = {key: "connection_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "connection_error"
        except json.JSONDecodeError as e:
            logger.error(t('invalid_json_gpt_load', str(e)))
            send_result = {key: "json_decode_error" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "json_decode_error"
        except Exception as e:
            logger.error(t('failed_send_to_gpt_load', str(e)), exc_info=True)
            send_result = {key: "exception" for key in keys}
            file_manager.save_keys_send_result(keys, send_result)
            return "exception"

    def _start_batch_sender(self) -> None:
        """启动批量发送定时器"""
        if self.shutdown_flag:
            return

        # 启动发送任务
        self.executor.submit(self._batch_send_worker)

        # 设置下一次发送定时器
        self.batch_timer = threading.Timer(self.batch_interval, self._start_batch_sender)
        self.batch_timer.daemon = True
        self.batch_timer.start()

    def _batch_send_worker(self) -> None:
        """批量发送worker"""
        # 检查是否处于冷却状态
        if state.is_in_cooldown:
            logger.info("❄️ 主线程正在冷却中，跳过本次批量发送")
            return
        
        while self.saving_checkpoint:
            logger.info(t('checkpoint_saving_batch_wait'))
            time.sleep(0.5)

        self.saving_checkpoint = True
        try:
            # 加载checkpoint
            logger.info(t('starting_batch_send', len(checkpoint.wait_send_balancer), len(checkpoint.wait_send_gpt_load)))
            
            # 发送付费密钥队列
            if checkpoint.wait_send_gpt_load_paid and self.gpt_load_paid_enabled:
                paid_keys = list(checkpoint.wait_send_gpt_load_paid)
                logger.info(f"💎 处理付费密钥队列: {len(paid_keys)} 个")

                result_code = self._send_gpt_load_paid_worker(paid_keys)

                if result_code == 'ok':
                    # 清空队列
                    checkpoint.wait_send_gpt_load_paid.clear()
                    logger.info(f"💎 付费密钥队列已清空: {len(paid_keys)} 个密钥已发送")
                else:
                    logger.error(f"💎 付费密钥队列处理失败: {result_code}")
            
            # 发送429密钥队列
            if checkpoint.wait_send_gpt_load_rate_limited and self.gpt_load_rate_limited_enabled:
                rate_limited_keys = list(checkpoint.wait_send_gpt_load_rate_limited)
                logger.info(f"⏰ 处理429密钥队列: {len(rate_limited_keys)} 个")

                result_code = self._send_gpt_load_rate_limited_worker(rate_limited_keys)

                if result_code == 'ok':
                    # 清空队列
                    checkpoint.wait_send_gpt_load_rate_limited.clear()
                    logger.info(f"⏰ 429密钥队列已清空: {len(rate_limited_keys)} 个密钥已发送")
                else:
                    logger.error(f"⏰ 429密钥队列处理失败: {result_code}")
            
            # 发送gemini balancer队列
            if checkpoint.wait_send_balancer and self.balancer_enabled:
                balancer_keys = list(checkpoint.wait_send_balancer)
                logger.info(t('processing_balancer_queue', len(balancer_keys)))

                result_code = self._send_balancer_worker(balancer_keys)
                if result_code == 'ok':
                    # 清空队列
                    checkpoint.wait_send_balancer.clear()
                    logger.info(t('balancer_queue_cleared', len(balancer_keys)))
                else:
                    logger.error(t('balancer_queue_failed', result_code))

            # 发送gpt_load队列
            if checkpoint.wait_send_gpt_load and self.gpt_load_enabled:
                gpt_load_keys = list(checkpoint.wait_send_gpt_load)
                logger.info(t('processing_gpt_load_queue', len(gpt_load_keys)))

                result_code = self._send_gpt_load_worker(gpt_load_keys)

                if result_code == 'ok':
                    # 清空队列
                    checkpoint.wait_send_gpt_load.clear()
                    logger.info(t('gpt_load_queue_cleared', len(gpt_load_keys)))
                else:
                    logger.error(t('gpt_load_queue_failed', result_code))

            # 保存checkpoint
            file_manager.save_checkpoint(checkpoint)
        except Exception as e:
            stacktrace = traceback.format_exc()
            logger.error(t('batch_send_error', e) + f"\n{stacktrace}")
        finally:
            self.saving_checkpoint = False  # Release the lock

    def shutdown(self) -> None:
        """关闭线程池和定时器"""
        self.shutdown_flag = True

        if self.batch_timer:
            self.batch_timer.cancel()

        self.executor.shutdown(wait=True)
        logger.info(t('syncutils_shutdown_complete'))


# 创建全局实例
sync_utils = SyncUtils()

