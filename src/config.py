"""
配置文件
集中管理应用的配置参数
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    # Flask配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # 数据库配置
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 3600,
        'pool_pre_ping': True,
    }
    
    # 缓存配置
    CACHE_TYPE = 'SimpleCache'
    CACHE_DEFAULT_TIMEOUT = 300  # 5分钟
    
    # API配置
    DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    DEEPSEEK_API_BASE = os.getenv('DEEPSEEK_API_BASE', 'https://api.deepseek.com/v1')
    
    # 应用配置
    DEFAULT_PROVIDER = 'deepseek'
    DEFAULT_MODEL = 'deepseek-chat'
    DEFAULT_ROUNDS = 3
    DEFAULT_DELAY = 1
    
    # 限制配置
    MAX_TOPIC_LENGTH = 500
    MAX_CONTENT_LENGTH = 10000
    MIN_ROUNDS = 1
    MAX_ROUNDS = 10
    
    # 历史记录配置
    HISTORY_CACHE_TIMEOUT = 60  # 1分钟
    SESSION_DETAIL_CACHE_TIMEOUT = 120  # 2分钟
    MAX_HISTORY_ITEMS = 100


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True  # 打印SQL语句


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config(env=None):
    """获取配置对象"""
    if env is None:
        env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
