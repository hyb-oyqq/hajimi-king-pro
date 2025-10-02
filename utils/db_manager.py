"""
数据库管理器
支持SQLite、PostgreSQL和MySQL数据库
"""
import os
import sqlite3
from datetime import datetime
from typing import List, Optional, Dict, Any
from contextlib import contextmanager

from common.Logger import logger
from common.translations import get_translator

# 获取翻译函数
t = get_translator().t


class DatabaseManager:
    """数据库管理器基类"""
    
    def __init__(self, db_type: str, config: Dict[str, Any]):
        """
        初始化数据库管理器
        
        Args:
            db_type: 数据库类型 (sqlite, postgresql, mysql)
            config: 数据库配置
        """
        self.db_type = db_type.lower()
        self.config = config
        self.conn = None
        
    def connect(self):
        """连接数据库"""
        raise NotImplementedError
    
    def close(self):
        """关闭数据库连接"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    @contextmanager
    def get_cursor(self):
        """获取数据库游标的上下文管理器"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        try:
            yield cursor
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
            raise e
        finally:
            cursor.close()
    
    def init_tables(self):
        """初始化数据库表"""
        raise NotImplementedError
    
    def save_keys(self, keys: List[str], key_type: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        """
        保存密钥到数据库
        
        Args:
            keys: 密钥列表
            key_type: 密钥类型 (valid, rate_limited, paid, send)
            metadata: 元数据 (repo_name, file_path, file_url等)
        
        Returns:
            bool: 是否保存成功
        """
        raise NotImplementedError
    
    def get_keys(self, key_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        获取密钥
        
        Args:
            key_type: 密钥类型，None表示获取所有类型
            limit: 限制返回数量
        
        Returns:
            List[Dict]: 密钥列表，每个元素包含key, key_type, created_at等字段
        """
        raise NotImplementedError


class SQLiteManager(DatabaseManager):
    """SQLite数据库管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('sqlite', config)
        self.db_path = config.get('db_path', 'data/keys.db')
        
    def connect(self):
        """连接SQLite数据库"""
        try:
            # 确保数据库目录存在
            db_dir = os.path.dirname(self.db_path)
            if db_dir and not os.path.exists(db_dir):
                os.makedirs(db_dir, exist_ok=True)
            
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
            logger.info(t('db_connected', 'SQLite', self.db_path))
        except Exception as e:
            logger.error(t('db_connect_failed', 'SQLite', e))
            raise
    
    def init_tables(self):
        """初始化SQLite表"""
        try:
            with self.get_cursor() as cursor:
                # 创建keys表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS keys (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        api_key TEXT NOT NULL UNIQUE,
                        key_type TEXT NOT NULL,
                        repo_name TEXT,
                        file_path TEXT,
                        file_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_key_type ON keys(key_type)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at ON keys(created_at)
                ''')
                
            logger.info(t('db_tables_initialized', 'SQLite'))
        except Exception as e:
            logger.error(t('db_tables_init_failed', 'SQLite', e))
            raise
    
    def save_keys(self, keys: List[str], key_type: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        """保存密钥到SQLite"""
        if not keys:
            return True
        
        metadata = metadata or {}
        repo_name = metadata.get('repo_name', '')
        file_path = metadata.get('file_path', '')
        file_url = metadata.get('file_url', '')
        
        try:
            with self.get_cursor() as cursor:
                for key in keys:
                    # 使用INSERT OR REPLACE来处理重复密钥
                    cursor.execute('''
                        INSERT OR REPLACE INTO keys 
                        (api_key, key_type, repo_name, file_path, file_url, updated_at)
                        VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ''', (key, key_type, repo_name, file_path, file_url))
                
            logger.info(t('db_keys_saved', len(keys), key_type, 'SQLite'))
            return True
        except Exception as e:
            logger.error(t('db_keys_save_failed', 'SQLite', e))
            return False
    
    def get_keys(self, key_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """从SQLite获取密钥"""
        try:
            with self.get_cursor() as cursor:
                if key_type:
                    query = "SELECT * FROM keys WHERE key_type = ? ORDER BY created_at DESC"
                    params = (key_type,)
                else:
                    query = "SELECT * FROM keys ORDER BY created_at DESC"
                    params = ()
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # 转换为字典列表
                result = []
                for row in rows:
                    result.append({
                        'id': row['id'],
                        'api_key': row['api_key'],
                        'key_type': row['key_type'],
                        'repo_name': row['repo_name'],
                        'file_path': row['file_path'],
                        'file_url': row['file_url'],
                        'created_at': row['created_at'],
                        'updated_at': row['updated_at']
                    })
                
                return result
        except Exception as e:
            logger.error(t('db_keys_get_failed', 'SQLite', e))
            return []


class PostgreSQLManager(DatabaseManager):
    """PostgreSQL数据库管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('postgresql', config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 5432)
        self.database = config.get('database', 'hajimi_keys')
        self.user = config.get('user', 'postgres')
        self.password = config.get('password', '')
        
    def connect(self):
        """连接PostgreSQL数据库"""
        try:
            import psycopg2
            from psycopg2.extras import RealDictCursor
            
            self.conn = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursor_factory=RealDictCursor
            )
            logger.info(t('db_connected', 'PostgreSQL', self.database))
        except ImportError:
            logger.error(t('db_driver_missing', 'psycopg2', 'psycopg2-binary'))
            raise
        except Exception as e:
            logger.error(t('db_connect_failed', 'PostgreSQL', e))
            raise
    
    def init_tables(self):
        """初始化PostgreSQL表"""
        try:
            with self.get_cursor() as cursor:
                # 创建keys表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS keys (
                        id SERIAL PRIMARY KEY,
                        api_key TEXT NOT NULL UNIQUE,
                        key_type TEXT NOT NULL,
                        repo_name TEXT,
                        file_path TEXT,
                        file_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
                
                # 创建索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_key_type ON keys(key_type)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at ON keys(created_at)
                ''')
                
            logger.info(t('db_tables_initialized', 'PostgreSQL'))
        except Exception as e:
            logger.error(t('db_tables_init_failed', 'PostgreSQL', e))
            raise
    
    def save_keys(self, keys: List[str], key_type: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        """保存密钥到PostgreSQL"""
        if not keys:
            return True
        
        metadata = metadata or {}
        repo_name = metadata.get('repo_name', '')
        file_path = metadata.get('file_path', '')
        file_url = metadata.get('file_url', '')
        
        try:
            with self.get_cursor() as cursor:
                for key in keys:
                    # 使用ON CONFLICT来处理重复密钥
                    cursor.execute('''
                        INSERT INTO keys 
                        (api_key, key_type, repo_name, file_path, file_url, updated_at)
                        VALUES (%s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
                        ON CONFLICT (api_key) DO UPDATE 
                        SET key_type = EXCLUDED.key_type,
                            repo_name = EXCLUDED.repo_name,
                            file_path = EXCLUDED.file_path,
                            file_url = EXCLUDED.file_url,
                            updated_at = CURRENT_TIMESTAMP
                    ''', (key, key_type, repo_name, file_path, file_url))
                
            logger.info(t('db_keys_saved', len(keys), key_type, 'PostgreSQL'))
            return True
        except Exception as e:
            logger.error(t('db_keys_save_failed', 'PostgreSQL', e))
            return False
    
    def get_keys(self, key_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """从PostgreSQL获取密钥"""
        try:
            with self.get_cursor() as cursor:
                if key_type:
                    query = "SELECT * FROM keys WHERE key_type = %s ORDER BY created_at DESC"
                    params = (key_type,)
                else:
                    query = "SELECT * FROM keys ORDER BY created_at DESC"
                    params = ()
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                # RealDictCursor已经返回字典
                return [dict(row) for row in rows]
        except Exception as e:
            logger.error(t('db_keys_get_failed', 'PostgreSQL', e))
            return []


class MySQLManager(DatabaseManager):
    """MySQL数据库管理器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__('mysql', config)
        self.host = config.get('host', 'localhost')
        self.port = config.get('port', 3306)
        self.database = config.get('database', 'hajimi_keys')
        self.user = config.get('user', 'root')
        self.password = config.get('password', '')
        
    def connect(self):
        """连接MySQL数据库"""
        try:
            import pymysql
            from pymysql.cursors import DictCursor
            
            self.conn = pymysql.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password,
                cursorclass=DictCursor
            )
            logger.info(t('db_connected', 'MySQL', self.database))
        except ImportError:
            logger.error(t('db_driver_missing', 'pymysql', 'pymysql'))
            raise
        except Exception as e:
            logger.error(t('db_connect_failed', 'MySQL', e))
            raise
    
    def init_tables(self):
        """初始化MySQL表"""
        try:
            with self.get_cursor() as cursor:
                # 创建keys表
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS `keys` (
                        id INT AUTO_INCREMENT PRIMARY KEY,
                        api_key TEXT NOT NULL,
                        key_type VARCHAR(50) NOT NULL,
                        repo_name TEXT,
                        file_path TEXT,
                        file_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                        UNIQUE KEY unique_api_key (api_key(255))
                    )
                ''')
                
                # 创建索引
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_key_type ON `keys`(key_type)
                ''')
                cursor.execute('''
                    CREATE INDEX IF NOT EXISTS idx_created_at ON `keys`(created_at)
                ''')
                
            logger.info(t('db_tables_initialized', 'MySQL'))
        except Exception as e:
            logger.error(t('db_tables_init_failed', 'MySQL', e))
            raise
    
    def save_keys(self, keys: List[str], key_type: str, metadata: Optional[Dict[str, str]] = None) -> bool:
        """保存密钥到MySQL"""
        if not keys:
            return True
        
        metadata = metadata or {}
        repo_name = metadata.get('repo_name', '')
        file_path = metadata.get('file_path', '')
        file_url = metadata.get('file_url', '')
        
        try:
            with self.get_cursor() as cursor:
                for key in keys:
                    # 使用ON DUPLICATE KEY UPDATE来处理重复密钥
                    cursor.execute('''
                        INSERT INTO `keys` 
                        (api_key, key_type, repo_name, file_path, file_url)
                        VALUES (%s, %s, %s, %s, %s)
                        ON DUPLICATE KEY UPDATE 
                            key_type = VALUES(key_type),
                            repo_name = VALUES(repo_name),
                            file_path = VALUES(file_path),
                            file_url = VALUES(file_url),
                            updated_at = CURRENT_TIMESTAMP
                    ''', (key, key_type, repo_name, file_path, file_url))
                
            logger.info(t('db_keys_saved', len(keys), key_type, 'MySQL'))
            return True
        except Exception as e:
            logger.error(t('db_keys_save_failed', 'MySQL', e))
            return False
    
    def get_keys(self, key_type: Optional[str] = None, limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """从MySQL获取密钥"""
        try:
            with self.get_cursor() as cursor:
                if key_type:
                    query = "SELECT * FROM `keys` WHERE key_type = %s ORDER BY created_at DESC"
                    params = (key_type,)
                else:
                    query = "SELECT * FROM `keys` ORDER BY created_at DESC"
                    params = ()
                
                if limit:
                    query += f" LIMIT {limit}"
                
                cursor.execute(query, params)
                rows = cursor.fetchall()
                
                return rows
        except Exception as e:
            logger.error(t('db_keys_get_failed', 'MySQL', e))
            return []


def create_db_manager(storage_type: str, db_type: str, db_config: Dict[str, Any]) -> Optional[DatabaseManager]:
    """
    创建数据库管理器工厂函数
    
    Args:
        storage_type: 存储类型 (text或sql)
        db_type: 数据库类型 (sqlite, postgresql, mysql)
        db_config: 数据库配置
    
    Returns:
        DatabaseManager实例，如果storage_type为text则返回None
    """
    if storage_type.lower() != 'sql':
        return None
    
    db_type = db_type.lower()
    
    if db_type == 'sqlite':
        return SQLiteManager(db_config)
    elif db_type == 'postgresql':
        return PostgreSQLManager(db_config)
    elif db_type == 'mysql':
        return MySQLManager(db_config)
    else:
        logger.error(t('db_type_unsupported', db_type))
        return None

