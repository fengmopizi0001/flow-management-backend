# 流水管理系统 - PythonAnywhere 部署指南

## 准备工作

### 1. 注册 PythonAnywhere

1. 访问 [https://www.pythonanywhere.com](https://www.pythonanywhere.com)
2. 注册一个免费账户（或者付费账户以获得更好性能）
3. 记录你的用户名

### 2. 创建 Web 应用

1. 登录 PythonAnywhere
2. 点击 "Web" 标签页
3. 点击 "Add a new web app"
4. 选择配置：
   - **Python version**: Python 3.8
   - **Web framework**: Flask
5. 点击 Next
6. 配置项目路径：
   - **Project name**: `flow-management`
   - **Python path**: 点击 "Use default"
7. 点击 Next

### 3. 配置 WSGI

在 Web 配置页面，找到 "WSGI configuration file" 部分：

1. 点击 `/var/www/your-username_pythonanywhere_com_wsgi.py` 链接
2. 编辑文件内容如下：

```python
import sys
import os

# 添加项目路径
path = '/home/your-username/flow-management'
if path not in sys.path:
    sys.path.append(path)

# 切换到项目目录
os.chdir(path)

# 导入 Flask 应用
from app_new import app as application

# 配置日志
import logging
logging.basicConfig(stream=sys.stderr)
```

**重要**：将 `your-username` 替换为你的 PythonAnywhere 用户名。

## 上传代码

### 方法 1: 使用 Git（推荐）

#### 1. 在本地初始化 Git 仓库

```bash
cd "c:\Users\Administrator\Desktop\新建文件夹 (3)(1) - 副本"
git init
git add .
git commit -m "Initial commit"
```

#### 2. 推送到 GitHub

```bash
# 添加远程仓库
git remote add origin https://github.com/your-username/flow-management-backend.git

# 推送到 GitHub
git push -u origin main
```

#### 3. 在 PythonAnywhere 上克隆

在 PythonAnywhere 控制台（Console）：

```bash
cd /home/your-username
git clone https://github.com/your-username/flow-management-backend.git flow-management
cd flow-management
```

### 方法 2: 直接上传

1. 在本地将项目打包为 zip 文件
2. 在 PythonAnywhere 的 "Files" 标签页上传 zip 文件
3. 使用控制台解压：

```bash
cd /home/your-username
unzip flow-management.zip -d flow-management
```

## 安装依赖

在 PythonAnywhere 控制台：

```bash
cd /home/your-username/flow-management

# 创建虚拟环境
python3.8 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

## 配置生产环境

### 1. 创建生产配置文件

在项目目录创建 `production_config.py`：

```python
"""
生产环境配置
"""
import os

class ProductionConfig:
    """生产环境配置"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secret-key-change-this-in-production')
    DEBUG = False
    TESTING = False
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = '/home/your-username/flow-management/uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # 数据库配置
    DATABASE_PATH = '/home/your-username/flow-management/data/flow.db'
    
    # Session配置
    SESSION_COOKIE_SECURE = True  # 启用HTTPS
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400  # 24小时
    
    # CORS配置
    # 替换为你的 GitHub Pages 地址
    CORS_ORIGINS = [
        'https://your-username.github.io',
        'https://your-username.github.io/flow-management-frontend'
    ]
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        # 创建必要的目录
        os.makedirs('/home/your-username/flow-management/data', exist_ok=True)
        os.makedirs('/home/your-username/flow-management/logs', exist_ok=True)
        os.makedirs('/home/your-username/flow-management/uploads', exist_ok=True)
```

**重要**：
- 将 `your-username` 替换为你的 PythonAnywhere 用户名
- 修改 `SECRET_KEY` 为随机字符串
- 修改 `CORS_ORIGINS` 为你的 GitHub Pages 地址

### 2. 更新 app_new.py

在项目目录，编辑 `app_new.py`，修改最后一行：

```python
# 创建应用实例
# 使用生产环境配置
app = create_app('production')

if __name__ == '__main__':
    print("=" * 60)
    print("流水管理系统 - 生产环境")
    print("=" * 60)
    print(f"运行模式: production")
    print(f"数据库路径: {app.config['DATABASE_PATH']}")
    print("=" * 60)
    
    # 生产环境不直接运行，由 PythonAnywhere WSGI 处理
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=False
    )
```

### 3. 初始化数据库

在 PythonAnywhere 控制台：

```bash
cd /home/your-username/flow-management
source venv/bin/activate
python -c "from app_new import create_app; app = create_app('production'); print('Database initialized')"
```

## 配置 Web 应用

在 PythonAnywhere 的 "Web" 标签页：

### 1. 修改虚拟环境路径

- **Virtualenv**: `/home/your-username/flow-management/venv`

### 2. 修改工作目录

- **Working directory**: `/home/your-username/flow-management`

### 3. 修改 WSGI 配置文件

确保 WSGI 文件路径为：
```
/var/www/your-username_pythonanywhere_com_wsgi.py
```

### 4. 设置环境变量

在 "Web" 标签页找到 "Environment variables" 部分：

添加以下变量：
```
FLASK_CONFIG=production
FLASK_ENV=production
SECRET_KEY=your-very-secret-key-change-this-in-production
```

### 5. 重载 Web 应用

点击页面底部的 "Reload" 按钮。

## 测试部署

### 1. 检查日志

在 "Web" 标签页，查看：
- **Error log**: 错误日志
- **Access log**: 访问日志

### 2. 测试访问

访问你的 PythonAnywhere 地址：
```
https://your-username.pythonanywhere.com
```

### 3. 测试 API

```bash
# 测试登录状态检查
curl https://your-username.pythonanywhere.com/api/auth/status

# 测试登录
curl -X POST https://your-username.pythonanywhere.com/api/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
```

## 更新代码

### 方法 1: Git 拉取

```bash
cd /home/your-username/flow-management
git pull origin main
```

### 方法 2: 重新上传

1. 修改本地代码
2. 打包上传到 PythonAnywhere
3. 解压覆盖旧文件

### 更新后重载

每次更新代码后，在 PythonAnywhere 的 "Web" 标签页点击 "Reload"。

## 数据库管理

### 备份数据库

```bash
cd /home/your-username/flow-management/data
cp flow.db flow_backup_$(date +%Y%m%d_%H%M%S).db
```

### 导出数据

```bash
sqlite3 /home/your-username/flow-management/data/flow.db .dump > backup.sql
```

### 导入数据

```bash
sqlite3 /home/your-username/flow-management/data/flow.db < backup.sql
```

## 常见问题

### 1. 500 Internal Server Error

检查：
- 错误日志（Web -> Error log）
- 虚拟环境是否正确配置
- 依赖是否全部安装
- 数据库是否正确初始化

### 2. CORS 错误

检查：
- `production_config.py` 中的 `CORS_ORIGINS` 配置
- 前端的 API 地址是否正确

### 3. 文件上传失败

检查：
- `uploads` 目录权限
- 文件大小限制（`MAX_CONTENT_LENGTH`）
- 磁盘空间是否充足

### 4. Session 失效

检查：
- `SECRET_KEY` 是否配置
- HTTPS 是否启用
- Cookie 配置是否正确

### 5. 数据库错误

检查：
- 数据库文件路径是否正确
- 数据库文件权限
- 是否已初始化数据库

## 性能优化

### 1. 使用静态文件服务

在 "Web" 标签页的 "Static files" 部分，添加：

- **URL**: `/static/`
- **Directory**: `/home/your-username/flow-management/static`

### 2. 启用压缩

在 WSGI 配置文件中添加：

```python
from whitenoise import WhiteNoise

# 在导入 application 后
application.wsgi_app = WhiteNoise(
    application.wsgi_app,
    root='/home/your-username/flow-management/static',
    prefix='/static/'
)
```

安装 whitenoise：

```bash
pip install whitenoise
```

### 3. 使用数据库连接池

对于高并发场景，考虑使用 PostgreSQL 替代 SQLite。

## 安全建议

1. **修改默认密码**：首次登录后修改 admin 密码
2. **使用 HTTPS**：PythonAnywhere 免费账户支持 HTTPS
3. **定期备份**：定期备份数据库
4. **监控日志**：定期检查错误日志
5. **限制访问**：如需要，可在 Web 配置中添加 IP 白名单

## 支持与联系

如有问题，请查看：
- PythonAnywhere 文档：https://help.pythonanywhere.com/
- Flask 文档：https://flask.palletsprojects.com/
- 项目 GitHub 仓库
