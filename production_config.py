"""
生产环境配置扩展
提供额外的生产环境优化配置
"""

import os
from config import ProductionConfig


class ExtendedProductionConfig(ProductionConfig):
    """
    扩展的生产环境配置
    包含更多优化选项
    """
    
    # 生产环境密钥 - 请修改为随机字符串
    SECRET_KEY = os.getenv(
        'SECRET_KEY',
        'change-this-to-a-random-secret-key-in-production'
    )
    
    # 服务器配置
    HOST = '0.0.0.0'  # 允许所有IP访问
    PORT = int(os.getenv('PORT', 5000))
    
    # 安全配置
    SESSION_COOKIE_SECURE = True  # 仅HTTPS传输
    SESSION_COOKIE_HTTPONLY = True  # 防止XSS
    SESSION_COOKIE_SAMESITE = 'Lax'  # 防止CSRF
    
    # 文件上传限制
    MAX_CONTENT_LENGTH = 32 * 1024 * 1024  # 32MB
    
    # 日志配置
    LOG_LEVEL = 'INFO'  # 生产环境使用INFO级别
    LOG_FILE = 'logs/app.log'
    LOG_MAX_BYTES = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT = 5  # 保留5个备份
    
    # 数据库配置
    DATABASE_PATH = 'data/flow.db'
    DATABASE_BACKUP_ENABLED = True
    DATABASE_BACKUP_INTERVAL = 86400  # 24小时备份一次
    
    # 性能配置
    ENABLE_CACHING = True
    CACHE_TIMEOUT = 300  # 5分钟缓存
    
    # 维护模式
    MAINTENANCE_MODE = False
    
    # 文件清理配置
    AUTO_CLEAN_UPLOADS = True
    UPLOAD_CLEAN_DAYS = 7  # 清理7天前的上传文件


# 生成随机密钥的辅助函数
def generate_secret_key():
    """
    生成随机的SECRET_KEY
    使用方法：
    from production_config import generate_secret_key
    print(generate_secret_key())
    """
    import secrets
    return secrets.token_hex(32)


# 使用说明
"""
如何在项目中使用此配置：

方法1: 设置环境变量
    set FLASK_CONFIG=production
    set SECRET_KEY=your-random-secret-key

方法2: 在app_new.py中导入使用
    from production_config import ExtendedProductionConfig
    app = create_app()
    app.config.from_object(ExtendedProductionConfig)

方法3: 创建 .env 文件
    FLASK_CONFIG=production
    SECRET_KEY=your-random-secret-key
    PORT=5000
"""
