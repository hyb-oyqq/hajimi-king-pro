"""
数据迁移工具
负责将文本文件中的密钥迁移到数据库
"""
import os
import re
import shutil
from datetime import datetime
from typing import List, Dict, Tuple
from glob import glob

from common.Logger import logger
from common.translations import get_translator
from utils.db_manager import DatabaseManager

# 获取翻译函数
t = get_translator().t


class KeyMigration:
    """密钥数据迁移工具"""
    
    def __init__(self, data_dir: str, db_manager: DatabaseManager):
        """
        初始化迁移工具
        
        Args:
            data_dir: 数据目录路径
            db_manager: 数据库管理器
        """
        self.data_dir = data_dir
        self.db_manager = db_manager
        self.keys_dir = os.path.join(data_dir, 'keys')
        self.logs_dir = os.path.join(data_dir, 'logs')
        
    def check_need_migration(self) -> bool:
        """
        检查是否需要迁移数据
        
        Returns:
            bool: 是否需要迁移
        """
        # 检查keys文件夹是否存在
        if not os.path.exists(self.keys_dir):
            logger.info(t('migration_keys_dir_not_found'))
            return False
        
        # 检查keys文件夹中是否有密钥文件
        key_files = self._find_key_files()
        
        if not key_files:
            logger.info(t('migration_no_files'))
            return False
        
        logger.info(t('migration_files_found', len(key_files)))
        return True
    
    def migrate(self) -> bool:
        """
        执行数据迁移
        
        Returns:
            bool: 迁移是否成功
        """
        try:
            logger.info("=" * 60)
            logger.info(t('migration_starting'))
            logger.info("=" * 60)
            
            # 1. 查找所有密钥文件
            key_files = self._find_key_files()
            detail_files = self._find_detail_files()
            
            logger.info(t('migration_found_files', len(key_files)))
            logger.info(t('migration_found_detail_files', len(detail_files)))
            
            # 2. 迁移密钥文件
            total_migrated = 0
            for file_path, key_type in key_files:
                count = self._migrate_key_file(file_path, key_type)
                total_migrated += count
            
            # 3. 迁移详细日志文件
            for file_path, key_type in detail_files:
                count = self._migrate_detail_file(file_path, key_type)
                total_migrated += count
            
            logger.info(t('migration_completed', total_migrated))
            
            # 4. 备份原始文件
            self._backup_files()
            
            # 5. 删除keys文件夹
            self._cleanup_keys_folder()
            
            logger.info("=" * 60)
            logger.info(t('migration_completed', total_migrated))
            logger.info("=" * 60)
            
            return True
            
        except Exception as e:
            logger.error(t('migration_failed', e))
            import traceback
            traceback.print_exc()
            return False
    
    def _find_key_files(self) -> List[Tuple[str, str]]:
        """
        查找所有密钥文件
        
        Returns:
            List[Tuple[str, str]]: (文件路径, 密钥类型) 的列表
        """
        files = []
        
        if not os.path.exists(self.keys_dir):
            return files
        
        # 定义文件模式和对应的密钥类型
        patterns = [
            ('keys_valid_*.txt', 'valid'),
            ('key_429_*.txt', 'rate_limited'),
            ('keys_paid_*.txt', 'paid'),
            ('keys_send_*.txt', 'send')
        ]
        
        for pattern, key_type in patterns:
            pattern_path = os.path.join(self.keys_dir, pattern)
            matched_files = glob(pattern_path)
            for file_path in matched_files:
                files.append((file_path, key_type))
                logger.debug(f"  Found {key_type} file: {os.path.basename(file_path)}")
        
        return files
    
    def _find_detail_files(self) -> List[Tuple[str, str]]:
        """
        查找所有详细日志文件
        
        Returns:
            List[Tuple[str, str]]: (文件路径, 密钥类型) 的列表
        """
        files = []
        
        if not os.path.exists(self.logs_dir):
            return files
        
        # 定义文件模式和对应的密钥类型
        patterns = [
            ('keys_valid_detail*.log', 'valid'),
            ('key_429_detail_*.log', 'rate_limited'),
            ('keys_paid_detail_*.log', 'paid'),
            ('keys_send_detail_*.log', 'send')
        ]
        
        for pattern, key_type in patterns:
            pattern_path = os.path.join(self.logs_dir, pattern)
            matched_files = glob(pattern_path)
            for file_path in matched_files:
                files.append((file_path, key_type))
                logger.debug(f"  Found {key_type} detail file: {os.path.basename(file_path)}")
        
        return files
    
    def _migrate_key_file(self, file_path: str, key_type: str) -> int:
        """
        迁移单个密钥文件
        
        Args:
            file_path: 文件路径
            key_type: 密钥类型
        
        Returns:
            int: 迁移的密钥数量
        """
        try:
            logger.info(t('migration_file_processing', key_type, os.path.basename(file_path)))
            
            keys = []
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 提取密钥（可能包含其他信息，用|分隔）
                    parts = line.split('|')
                    key = parts[0].strip()
                    
                    # 验证密钥格式
                    if self._is_valid_key(key):
                        keys.append(key)
            
            if keys:
                # 去重
                keys = list(set(keys))
                
                # 保存到数据库
                success = self.db_manager.save_keys(keys, key_type)
                
                if success:
                    logger.info(t('migration_file_migrated', len(keys), key_type))
                    return len(keys)
                else:
                    logger.warning(t('migration_file_failed', key_type))
                    return 0
            else:
                logger.info(t('migration_file_no_keys'))
                return 0
                
        except Exception as e:
            logger.error(t('migration_file_error', file_path, e))
            return 0
    
    def _migrate_detail_file(self, file_path: str, key_type: str) -> int:
        """
        迁移详细日志文件
        
        Args:
            file_path: 文件路径
            key_type: 密钥类型
        
        Returns:
            int: 迁移的密钥数量
        """
        try:
            logger.info(t('migration_detail_processing', key_type, os.path.basename(file_path)))
            
            keys_with_metadata = []
            current_metadata = {}
            
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 解析TIME行
                    if line.startswith('TIME:'):
                        current_metadata = {}
                        continue
                    
                    # 解析URL行
                    elif line.startswith('URL:'):
                        url = line[4:].strip()
                        current_metadata['file_url'] = url
                        
                        # 尝试从URL提取repo_name和file_path
                        # URL格式: https://github.com/user/repo/blob/branch/path/to/file
                        match = re.match(r'https://github\.com/([^/]+/[^/]+)/blob/[^/]+/(.+)', url)
                        if match:
                            current_metadata['repo_name'] = match.group(1)
                            current_metadata['file_path'] = match.group(2)
                    
                    # 解析KEY行
                    elif line.startswith('KEY:'):
                        key = line[4:].strip()
                        
                        # 验证密钥格式
                        if self._is_valid_key(key):
                            keys_with_metadata.append((key, current_metadata.copy()))
                    
                    # 分隔线，重置元数据
                    elif line.startswith('-' * 10):
                        current_metadata = {}
            
            if keys_with_metadata:
                # 去重（基于密钥）
                unique_keys = {}
                for key, metadata in keys_with_metadata:
                    if key not in unique_keys:
                        unique_keys[key] = metadata
                
                # 保存到数据库
                count = 0
                for key, metadata in unique_keys.items():
                    success = self.db_manager.save_keys([key], key_type, metadata)
                    if success:
                        count += 1
                
                logger.info(t('migration_detail_migrated', count, key_type))
                return count
            else:
                logger.info(t('migration_detail_no_keys'))
                return 0
                
        except Exception as e:
            logger.error(t('migration_detail_error', file_path, e))
            return 0
    
    def _is_valid_key(self, key: str) -> bool:
        """
        验证密钥格式
        
        Args:
            key: 密钥字符串
        
        Returns:
            bool: 是否为有效的Gemini API密钥
        """
        # Gemini API密钥格式: AIzaSy + 33个字符
        pattern = r'^AIzaSy[A-Za-z0-9\-_]{33}$'
        return bool(re.match(pattern, key))
    
    def _backup_files(self):
        """备份原始文件"""
        try:
            # 创建备份目录
            backup_dir = os.path.join(self.data_dir, f'backup_before_migration_{datetime.now().strftime("%Y%m%d_%H%M%S")}')
            os.makedirs(backup_dir, exist_ok=True)
            
            # 备份keys文件夹
            if os.path.exists(self.keys_dir):
                backup_keys_dir = os.path.join(backup_dir, 'keys')
                shutil.copytree(self.keys_dir, backup_keys_dir)
                logger.info(t('migration_backup_keys', backup_keys_dir))
            
            # 备份相关的logs文件
            if os.path.exists(self.logs_dir):
                backup_logs_dir = os.path.join(backup_dir, 'logs')
                os.makedirs(backup_logs_dir, exist_ok=True)
                
                # 只备份密钥相关的日志文件
                log_patterns = [
                    'keys_valid_detail*.log',
                    'key_429_detail_*.log',
                    'keys_paid_detail_*.log',
                    'keys_send_detail_*.log'
                ]
                
                for pattern in log_patterns:
                    pattern_path = os.path.join(self.logs_dir, pattern)
                    matched_files = glob(pattern_path)
                    for file_path in matched_files:
                        dest_path = os.path.join(backup_logs_dir, os.path.basename(file_path))
                        shutil.copy2(file_path, dest_path)
                
                logger.info(t('migration_backup_logs', backup_logs_dir))
            
            logger.info(t('migration_backup_completed', backup_dir))
            
        except Exception as e:
            logger.error(t('migration_backup_failed', e))
    
    def _cleanup_keys_folder(self):
        """删除keys文件夹"""
        try:
            if os.path.exists(self.keys_dir):
                shutil.rmtree(self.keys_dir)
                logger.info(t('migration_cleanup_keys', self.keys_dir))
                
                # 删除相关的日志文件
                if os.path.exists(self.logs_dir):
                    log_patterns = [
                        'keys_valid_detail*.log',
                        'key_429_detail_*.log',
                        'keys_paid_detail_*.log',
                        'keys_send_detail_*.log'
                    ]
                    
                    for pattern in log_patterns:
                        pattern_path = os.path.join(self.logs_dir, pattern)
                        matched_files = glob(pattern_path)
                        for file_path in matched_files:
                            os.remove(file_path)
                            logger.info(t('migration_cleanup_log', os.path.basename(file_path)))
                
                logger.info(t('migration_cleanup_completed'))
            else:
                logger.info(t('migration_keys_already_removed'))
                
        except Exception as e:
            logger.error(t('migration_cleanup_failed', e))

