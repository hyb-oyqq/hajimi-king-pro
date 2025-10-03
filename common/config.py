import os
import random
from typing import Dict, Optional, Any

from dotenv import load_dotenv

from common.Logger import logger
from common.translations import get_translator

# 只在环境变量不存在时才从.env加载值
load_dotenv(override=False)


class Config:
    GITHUB_TOKENS_STR = os.getenv("GITHUB_TOKENS", "")

    # 获取GitHub tokens列表
    GITHUB_TOKENS = [token.strip() for token in GITHUB_TOKENS_STR.split(',') if token.strip()]
    DATA_PATH = os.getenv('DATA_PATH', '/app/data')
    PROXY_LIST_STR = os.getenv("PROXY", "")
    
    # 解析代理列表，支持格式：http://user:pass@host:port,http://host:port,socks5://user:pass@host:port
    PROXY_LIST = []
    if PROXY_LIST_STR:
        for proxy_str in PROXY_LIST_STR.split(','):
            proxy_str = proxy_str.strip()
            if proxy_str:
                PROXY_LIST.append(proxy_str)
    
    # Gemini Balancer配置
    GEMINI_BALANCER_SYNC_ENABLED = os.getenv("GEMINI_BALANCER_SYNC_ENABLED", "false")
    GEMINI_BALANCER_URL = os.getenv("GEMINI_BALANCER_URL", "")
    GEMINI_BALANCER_AUTH = os.getenv("GEMINI_BALANCER_AUTH", "")

    # GPT-load Configuration
    GPT_LOAD_SYNC_ENABLED = os.getenv("GPT_LOAD_SYNC_ENABLED", "false")
    GPT_LOAD_URL = os.getenv('GPT_LOAD_URL', '')
    GPT_LOAD_AUTH = os.getenv('GPT_LOAD_AUTH', '')
    GPT_LOAD_GROUP_NAME = os.getenv('GPT_LOAD_GROUP_NAME', '')
    
    # GPT-load - Paid Keys Configuration
    GPT_LOAD_PAID_SYNC_ENABLED = os.getenv("GPT_LOAD_PAID_SYNC_ENABLED", "false")
    GPT_LOAD_PAID_GROUP_NAME = os.getenv('GPT_LOAD_PAID_GROUP_NAME', '')
    
    # 429限速密钥处理策略
    # 可选值: discard, save_only, sync, sync_separate
    RATE_LIMITED_HANDLING = os.getenv("RATE_LIMITED_HANDLING", "save_only")
    GPT_LOAD_RATE_LIMITED_GROUP_NAME = os.getenv('GPT_LOAD_RATE_LIMITED_GROUP_NAME', '')

    # 文件前缀配置
    VALID_KEY_PREFIX = os.getenv("VALID_KEY_PREFIX", "keys/keys_valid_")
    RATE_LIMITED_KEY_PREFIX = os.getenv("RATE_LIMITED_KEY_PREFIX", "keys/key_429_")
    KEYS_SEND_PREFIX = os.getenv("KEYS_SEND_PREFIX", "keys/keys_send_")
    PAID_KEY_PREFIX = os.getenv("PAID_KEY_PREFIX", "keys/keys_paid_")

    VALID_KEY_DETAIL_PREFIX = os.getenv("VALID_KEY_DETAIL_PREFIX", "logs/keys_valid_detail_")
    RATE_LIMITED_KEY_DETAIL_PREFIX = os.getenv("RATE_LIMITED_KEY_DETAIL_PREFIX", "logs/key_429_detail_")
    KEYS_SEND_DETAIL_PREFIX = os.getenv("KEYS_SEND_DETAIL_PREFIX", "logs/keys_send_detail_")
    PAID_KEY_DETAIL_PREFIX = os.getenv("PAID_KEY_DETAIL_PREFIX", "logs/keys_paid_detail_")
    
    # 日期范围过滤器配置 (单位：天)
    DATE_RANGE_DAYS = int(os.getenv("DATE_RANGE_DAYS", "730"))  # 默认730天 (约2年)

    # 查询文件路径配置
    QUERIES_FILE = os.getenv("QUERIES_FILE", "queries.txt")

    # 已扫描SHA文件配置
    SCANNED_SHAS_FILE = os.getenv("SCANNED_SHAS_FILE", "scanned_shas.txt")

    # Gemini模型配置
    HAJIMI_CHECK_MODEL = os.getenv("HAJIMI_CHECK_MODEL", "gemini-2.5-flash")
    HAJIMI_PAID_MODEL = os.getenv("HAJIMI_PAID_MODEL", "gemini-2.0-flash-thinking-exp-01-21")

    # 文件路径黑名单配置
    FILE_PATH_BLACKLIST_STR = os.getenv("FILE_PATH_BLACKLIST", "readme,docs,doc/,.md,sample,tutorial")
    FILE_PATH_BLACKLIST = [token.strip().lower() for token in FILE_PATH_BLACKLIST_STR.split(',') if token.strip()]

    # 语言配置
    LANGUAGE = os.getenv("LANGUAGE", "zh_cn").lower()

    # 存储配置
    STORAGE_TYPE = os.getenv("STORAGE_TYPE", "sql").lower()  # text 或 sql，默认sql
    DB_TYPE = os.getenv("DB_TYPE", "sqlite").lower()  # sqlite, postgresql, mysql，默认sqlite
    
    # SQLite配置
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", "keys.db")
    
    # PostgreSQL配置
    POSTGRESQL_HOST = os.getenv("POSTGRESQL_HOST", "localhost")
    POSTGRESQL_PORT = int(os.getenv("POSTGRESQL_PORT", "5432"))
    POSTGRESQL_DATABASE = os.getenv("POSTGRESQL_DATABASE", "hajimi_keys")
    POSTGRESQL_USER = os.getenv("POSTGRESQL_USER", "postgres")
    POSTGRESQL_PASSWORD = os.getenv("POSTGRESQL_PASSWORD", "")
    
    # MySQL配置
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "hajimi_keys")
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "")
    
    # 强制冷却配置（支持固定值或范围，如 "1" 或 "1-3"）
    FORCED_COOLDOWN_ENABLED = os.getenv("FORCED_COOLDOWN_ENABLED", "false")
    FORCED_COOLDOWN_HOURS_PER_QUERY = os.getenv("FORCED_COOLDOWN_HOURS_PER_QUERY", "0")
    FORCED_COOLDOWN_HOURS_PER_LOOP = os.getenv("FORCED_COOLDOWN_HOURS_PER_LOOP", "0")

    @classmethod
    def parse_bool(cls, value: str) -> bool:
        """
        解析布尔值配置，支持多种格式
        
        Args:
            value: 配置值字符串
            
        Returns:
            bool: 解析后的布尔值
        """
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            value = value.strip().lower()
            return value in ('true', '1', 'yes', 'on', 'enabled')
        
        if isinstance(value, int):
            return bool(value)
        
        return False
    
    @classmethod
    def parse_cooldown_hours(cls, value: str) -> float:
        """
        解析冷却时间配置，支持固定值或范围
        
        格式：
        - 固定值：如 "1" 或 "1.5"
        - 范围值：如 "1-3" 或 "0.5-1.5"
        
        Args:
            value: 配置值字符串
            
        Returns:
            float: 解析后的冷却时间（小时），如果是范围则返回随机值
        """
        if not value:
            return 0.0
        
        value = str(value).strip()
        
        # 检查是否为范围格式 (如 "1-3")
        if '-' in value:
            parts = value.split('-')
            if len(parts) == 2:
                try:
                    min_hours = float(parts[0].strip())
                    max_hours = float(parts[1].strip())
                    
                    # 确保最小值不大于最大值
                    if min_hours > max_hours:
                        min_hours, max_hours = max_hours, min_hours
                    
                    # 返回范围内的随机值
                    return random.uniform(min_hours, max_hours)
                except ValueError:
                    logger.warning(f"⚠️ 无法解析冷却时间范围: {value}，使用默认值 0")
                    return 0.0
        
        # 固定值格式
        try:
            return float(value)
        except ValueError:
            logger.warning(f"⚠️ 无法解析冷却时间: {value}，使用默认值 0")
            return 0.0

    @classmethod
    def get_random_proxy(cls) -> Optional[Dict[str, str]]:
        """
        随机获取一个代理配置
        
        Returns:
            Optional[Dict[str, str]]: requests格式的proxies字典，如果未配置则返回None
        """
        if not cls.PROXY_LIST:
            return None
        
        # 随机选择一个代理
        proxy_url = random.choice(cls.PROXY_LIST).strip()
        
        # 返回requests格式的proxies字典
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    
    @classmethod
    def get_db_config(cls) -> Dict[str, Any]:
        """
        获取数据库配置
        
        Returns:
            Dict[str, Any]: 数据库配置字典
        """
        if cls.DB_TYPE == 'sqlite':
            db_path = cls.SQLITE_DB_PATH
            # 如果是相对路径，则相对于DATA_PATH
            if not os.path.isabs(db_path):
                db_path = os.path.join(cls.DATA_PATH, db_path)
            
            return {
                'db_path': db_path
            }
        elif cls.DB_TYPE == 'postgresql':
            return {
                'host': cls.POSTGRESQL_HOST,
                'port': cls.POSTGRESQL_PORT,
                'database': cls.POSTGRESQL_DATABASE,
                'user': cls.POSTGRESQL_USER,
                'password': cls.POSTGRESQL_PASSWORD
            }
        elif cls.DB_TYPE == 'mysql':
            return {
                'host': cls.MYSQL_HOST,
                'port': cls.MYSQL_PORT,
                'database': cls.MYSQL_DATABASE,
                'user': cls.MYSQL_USER,
                'password': cls.MYSQL_PASSWORD
            }
        else:
            return {}

    @classmethod
    def check(cls) -> bool:
        """
        检查必要的配置是否完整
        
        Returns:
            bool: 配置是否完整
        """
        t = get_translator(cls.LANGUAGE).t
        logger.info(t('checking_config'))
        
        errors = []
        
        # 检查GitHub tokens
        if not cls.GITHUB_TOKENS:
            errors.append(t('github_tokens_missing'))
            logger.error(t('github_tokens_missing_short'))
        else:
            logger.info(t('github_tokens_ok', len(cls.GITHUB_TOKENS)))
        
        # 检查Gemini Balancer配置
        if cls.GEMINI_BALANCER_SYNC_ENABLED:
            logger.info(t('balancer_enabled', cls.GEMINI_BALANCER_URL))
            if not cls.GEMINI_BALANCER_AUTH or not cls.GEMINI_BALANCER_URL:
                logger.warning(t('balancer_missing'))
            else:
                logger.info(t('balancer_ok'))
        else:
            logger.info(t('balancer_not_configured'))

        # 检查GPT-load配置
        if cls.parse_bool(cls.GPT_LOAD_SYNC_ENABLED):
            logger.info(t('gpt_load_enabled', cls.GPT_LOAD_URL))
            if not cls.GPT_LOAD_AUTH or not cls.GPT_LOAD_URL or not cls.GPT_LOAD_GROUP_NAME:
                logger.warning(t('gpt_load_missing'))
            else:
                logger.info(t('gpt_load_ok'))
                logger.info(t('gpt_load_group_name', cls.GPT_LOAD_GROUP_NAME))
        else:
            logger.info(t('gpt_load_not_configured'))

        if errors:
            logger.error(t('config_check_failed_details'))
            logger.info(t('check_env_file'))
            return False
        
        logger.info(t('all_config_valid'))
        return True


# 初始化翻译器
get_translator(Config.LANGUAGE)

logger.info(f"*" * 30 + " CONFIG START " + "*" * 30)
logger.info(f"LANGUAGE: {Config.LANGUAGE}")
logger.info(f"GITHUB_TOKENS: {len(Config.GITHUB_TOKENS)} tokens")
logger.info(f"DATA_PATH: {Config.DATA_PATH}")
logger.info(f"PROXY_LIST: {len(Config.PROXY_LIST)} proxies configured")
logger.info(f"GEMINI_BALANCER_URL: {Config.GEMINI_BALANCER_URL or 'Not configured'}")
logger.info(f"GEMINI_BALANCER_AUTH: {'Configured' if Config.GEMINI_BALANCER_AUTH else 'Not configured'}")
logger.info(f"GEMINI_BALANCER_SYNC_ENABLED: {Config.parse_bool(Config.GEMINI_BALANCER_SYNC_ENABLED)}")
logger.info(f"GPT_LOAD_SYNC_ENABLED: {Config.parse_bool(Config.GPT_LOAD_SYNC_ENABLED)}")
logger.info(f"GPT_LOAD_URL: {Config.GPT_LOAD_URL or 'Not configured'}")
logger.info(f"GPT_LOAD_AUTH: {'Configured' if Config.GPT_LOAD_AUTH else 'Not configured'}")
logger.info(f"GPT_LOAD_GROUP_NAME: {Config.GPT_LOAD_GROUP_NAME or 'Not configured'}")
logger.info(f"GPT_LOAD_PAID_SYNC_ENABLED: {Config.parse_bool(Config.GPT_LOAD_PAID_SYNC_ENABLED)}")
logger.info(f"GPT_LOAD_PAID_GROUP_NAME: {Config.GPT_LOAD_PAID_GROUP_NAME or 'Not configured'}")
logger.info(f"RATE_LIMITED_HANDLING: {Config.RATE_LIMITED_HANDLING}")
logger.info(f"GPT_LOAD_RATE_LIMITED_GROUP_NAME: {Config.GPT_LOAD_RATE_LIMITED_GROUP_NAME or 'Not configured'}")
logger.info(f"VALID_KEY_PREFIX: {Config.VALID_KEY_PREFIX}")
logger.info(f"RATE_LIMITED_KEY_PREFIX: {Config.RATE_LIMITED_KEY_PREFIX}")
logger.info(f"KEYS_SEND_PREFIX: {Config.KEYS_SEND_PREFIX}")
logger.info(f"PAID_KEY_PREFIX: {Config.PAID_KEY_PREFIX}")
logger.info(f"VALID_KEY_DETAIL_PREFIX: {Config.VALID_KEY_DETAIL_PREFIX}")
logger.info(f"RATE_LIMITED_KEY_DETAIL_PREFIX: {Config.RATE_LIMITED_KEY_DETAIL_PREFIX}")
logger.info(f"KEYS_SEND_DETAIL_PREFIX: {Config.KEYS_SEND_DETAIL_PREFIX}")
logger.info(f"PAID_KEY_DETAIL_PREFIX: {Config.PAID_KEY_DETAIL_PREFIX}")
logger.info(f"DATE_RANGE_DAYS: {Config.DATE_RANGE_DAYS} days")
logger.info(f"QUERIES_FILE: {Config.QUERIES_FILE}")
logger.info(f"SCANNED_SHAS_FILE: {Config.SCANNED_SHAS_FILE}")
logger.info(f"HAJIMI_CHECK_MODEL: {Config.HAJIMI_CHECK_MODEL}")
logger.info(f"HAJIMI_PAID_MODEL: {Config.HAJIMI_PAID_MODEL}")
logger.info(f"FILE_PATH_BLACKLIST: {len(Config.FILE_PATH_BLACKLIST)} items")
logger.info(f"FORCED_COOLDOWN_ENABLED: {Config.parse_bool(Config.FORCED_COOLDOWN_ENABLED)}")
logger.info(f"FORCED_COOLDOWN_HOURS_PER_QUERY: {Config.FORCED_COOLDOWN_HOURS_PER_QUERY}")
logger.info(f"FORCED_COOLDOWN_HOURS_PER_LOOP: {Config.FORCED_COOLDOWN_HOURS_PER_LOOP}")
logger.info(f"STORAGE_TYPE: {Config.STORAGE_TYPE}")
logger.info(f"DB_TYPE: {Config.DB_TYPE}")
if Config.STORAGE_TYPE == 'sql':
    if Config.DB_TYPE == 'sqlite':
        logger.info(f"SQLITE_DB_PATH: {Config.SQLITE_DB_PATH}")
    elif Config.DB_TYPE == 'postgresql':
        logger.info(f"POSTGRESQL_HOST: {Config.POSTGRESQL_HOST}")
        logger.info(f"POSTGRESQL_PORT: {Config.POSTGRESQL_PORT}")
        logger.info(f"POSTGRESQL_DATABASE: {Config.POSTGRESQL_DATABASE}")
        logger.info(f"POSTGRESQL_USER: {Config.POSTGRESQL_USER}")
    elif Config.DB_TYPE == 'mysql':
        logger.info(f"MYSQL_HOST: {Config.MYSQL_HOST}")
        logger.info(f"MYSQL_PORT: {Config.MYSQL_PORT}")
        logger.info(f"MYSQL_DATABASE: {Config.MYSQL_DATABASE}")
        logger.info(f"MYSQL_USER: {Config.MYSQL_USER}")
logger.info(f"*" * 30 + " CONFIG END " + "*" * 30)

# 创建全局配置实例
config = Config()
