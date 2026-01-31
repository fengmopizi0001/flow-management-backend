"""
配置文件 - 流水管理系统
集中管理所有配置项
"""

import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """基础配置类"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here-change-in-production')
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    TESTING = False
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # 数据库配置
    DATABASE_PATH = os.path.join(basedir, 'data', 'flow.db')
    
    # Session配置
    SESSION_COOKIE_SECURE = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24小时
    
    # CORS配置（跨域支持）
    # 允许的前端域名列表，生产环境需要配置
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        os.makedirs('data', exist_ok=True)
        os.makedirs('logs', exist_ok=True)


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    TESTING = False


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True  # 生产环境启用HTTPS
    
    # 生产环境CORS配置
    # 示例: CORS_ORIGINS = ['https://yourusername.github.io', 'https://your-frontend.com']
    CORS_ORIGINS = os.getenv('CORS_ORIGINS', '').split(',') if os.getenv('CORS_ORIGINS') else []


class TestingConfig(Config):
    """测试环境配置"""
    TESTING = True
    DATABASE_PATH = 'data/test_flow.db'


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}
