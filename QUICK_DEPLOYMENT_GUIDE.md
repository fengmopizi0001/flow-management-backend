# 流水管理系统 - 快速部署指南

## 📋 部署前准备

### ✅ 已完成
- [x] 前端代码已准备（frontend/ 目录）
- [x] Git 仓库已初始化
- [x] 代码已提交到本地仓库
- [x] 后端已配置 CORS 支持

### 📝 需要您准备的信息
1. **GitHub 用户名**：您的 GitHub 账户名
2. **PythonAnywhere 用户名**：您将在 PythonAnywhere 注册的用户名

## 🚀 步骤一：部署前端到 GitHub Pages

### 1.1 在 GitHub 上创建仓库

**方式 A：通过网页创建（推荐）**

1. 访问 https://github.com/new
2. 填写信息：
   - **Repository name**: `flow-management-frontend`
   - **Description**: `流水管理系统 - 前端（前后端分离架构）`
   - **Public**: ✅ 勾选（公开仓库）
   - **Add a README file**: ❌ 不勾选（我们已经有文件了）
3. 点击 **Create repository**

**方式 B：通过命令行创建（需要先配置 git）**

```bash
# 在 frontend 目录执行
git remote add origin https://github.com/YOUR_USERNAME/flow-management-frontend.git
git branch -M main
git push -u origin main
```

### 1.2 推送代码到 GitHub

创建仓库后，GitHub 会显示推送命令，复制并执行：

```bash
cd "c:\Users\Administrator\Desktop\新建文件夹 (3)(1) - 副本\frontend"
git remote add origin https://github.com/YOUR_USERNAME/flow-management-frontend.git
git branch -M main
git push -u origin main
```

**重要**：将 `YOUR_USERNAME` 替换为您的 GitHub 用户名

### 1.3 启用 GitHub Pages

1. 访问您的仓库：https://github.com/YOUR_USERNAME/flow-management-frontend
2. 点击 **Settings** 标签页
3. 向下滚动找到 **Pages** 部分（左侧菜单）
4. 配置：
   - **Source**: 选择 `Deploy from a branch`
   - **Branch**: 选择 `main` 和 `/ (root)`
   - 点击 **Save**
5. 等待 1-3 分钟

### 1.4 获取前端网址

几分钟后，GitHub Pages 会在以下地址部署您的网站：

```
https://YOUR_USERNAME.github.io/flow-management-frontend/
```

访问该地址，应该能看到登录页面。

### 1.5 配置生产环境 API 地址

编辑 `frontend/js/config.js` 文件：

```javascript
const API_CONFIG = {
    development: 'http://localhost:5000/api',
    
    // 修改为您的 PythonAnywhere 地址（部署后端后再修改）
    production: 'https://YOUR_USERNAME.pythonanywhere.com/api'
};
```

修改后：
```bash
cd "c:\Users\Administrator\Desktop\新建文件夹 (3)(1) - 副本\frontend"
git add js/config.js
git commit -m "Update production API URL"
git push
```

## 🚀 步骤二：部署后端到 PythonAnywhere

### 2.1 注册 PythonAnywhere

1. 访问 https://www.pythonanywhere.com
2. 点击右上角 **Sign up**
3. 填写注册信息（免费账户即可）
4. 验证邮箱
5. 登录 PythonAnywhere
6. **记录您的用户名**（例如：`myflowapp`）

### 2.2 创建 Web 应用

1. 登录后，点击顶部的 **Web** 标签
2. 点击 **Add a new web app** 按钮
3. 配置：
   - **Python version**: 选择 `3.8`
   - **Web framework**: 选择 `Flask`
   - 点击 **Next**
4. 配置项目：
   - **Project name**: 输入 `flow-management`
   - 点击 **Use default**
   - 点击 **Next**
5. 记录生成的配置信息

### 2.3 上传后端代码

**方式 A：使用 Git（推荐）**

1. 在 GitHub 创建后端仓库：
   - 访问 https://github.com/new
   - **Repository name**: `flow-management-backend`
   - **Public**: ✅
   - 点击 **Create repository**

2. 在本地初始化并推送：
```bash
cd "c:\Users\Administrator\Desktop\新建文件夹 (3)(1) - 副本"
git init
git add .
git commit -m "Initial commit - Flow Management Backend"
git remote add origin https://github.com/YOUR_USERNAME/flow-management-backend.git
git branch -M main
git push -u origin main
```

**方式 B：直接上传文件**

1. 在本地打包项目：
```bash
# 在项目根目录
tar -czf flow-management.tar.gz --exclude='.venv' --exclude='__pycache__' --exclude='*.pyc' --exclude='frontend' --exclude='.git' .
```

2. 在 PythonAnywhere 的 **Files** 标签上传文件

### 2.4 在 PythonAnywhere 克隆代码

在 PythonAnywhere 控制台（Console）执行：

```bash
cd /home/YOUR_USERNAME
git clone https://github.com/YOUR_USERNAME/flow-management-backend.git flow-management
cd flow-management
```

**重要**：将 `YOUR_USERNAME` 替换为您的 GitHub 用户名

### 2.5 安装依赖

在 PythonAnywhere 控制台：

```bash
cd /home/YOUR_USERNAME/flow-management

# 创建虚拟环境
python3.8 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 升级 pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 2.6 创建生产配置

在 PythonAnywhere 控制台创建配置文件：

```bash
cd /home/YOUR_USERNAME/flow-management

# 创建生产配置文件
cat > production_config.py << 'EOF'
"""
生产环境配置
"""
import os

class ProductionConfig:
    """生产环境配置"""
    
    # Flask基础配置
    SECRET_KEY = os.getenv('SECRET_KEY', 'CHANGE-THIS-TO-A-RANDOM-STRING')
    DEBUG = False
    TESTING = False
    
    # 文件上传配置
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    UPLOAD_FOLDER = '/home/YOUR_USERNAME/flow-management/uploads'
    ALLOWED_EXTENSIONS = {'xlsx', 'xls'}
    
    # 数据库配置
    DATABASE_PATH = '/home/YOUR_USERNAME/flow-management/data/flow.db'
    
    # Session配置
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 86400
    
    # CORS配置 - 重要！
    CORS_ORIGINS = [
        'https://YOUR_USERNAME.github.io',
        'https://YOUR_USERNAME.github.io/flow-management-frontend'
    ]
    
    @staticmethod
    def init_app(app):
        """初始化应用配置"""
        os.makedirs('/home/YOUR_USERNAME/flow-management/data', exist_ok=True)
        os.makedirs('/home/YOUR_USERNAME/flow-management/logs', exist_ok=True)
        os.makedirs('/home/YOUR_USERNAME/flow-management/uploads', exist_ok=True)
EOF
```

**重要**：
- 将 `YOUR_USERNAME` 替换为您的 PythonAnywhere 用户名
- 将第二个 `YOUR_USERNAME` 替换为您的 GitHub 用户名

### 2.7 配置 WSGI

在 PythonAnywhere 的 **Web** 标签页：

1. 找到 **WSGI configuration file** 部分
2. 点击文件链接（例如：`/var/www/your-username_pythonanywhere_com_wsgi.py`）
3. 编辑文件内容：

```python
import sys
import os

# 添加项目路径
path = '/home/YOUR_USERNAME/flow-management'
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

4. 点击 **Save**

**重要**：将 `YOUR_USERNAME` 替换为您的 PythonAnywhere 用户名

### 2.8 配置 Web 应用

在 PythonAnywhere 的 **Web** 标签页：

1. **Virtualenv**: 输入 `/home/YOUR_USERNAME/flow-management/venv`
2. **Working directory**: 输入 `/home/YOUR_USERNAME/flow-management`
3. 向下滚动到 **Environment variables** 部分
4. 添加以下变量：

```
FLASK_CONFIG = production
FLASK_ENV = production
SECRET_KEY = your-very-secret-key-change-this-in-production
```

5. 点击页面底部的 **Reload** 按钮

### 2.9 初始化数据库

在 PythonAnywhere 控制台：

```bash
cd /home/YOUR_USERNAME/flow-management
source venv/bin/activate

# 初始化数据库
python -c "from app_new import create_app; app = create_app('production'); print('Database initialized')"
```

## 🧪 步骤三：测试部署

### 3.1 测试前端

1. 访问您的 GitHub Pages 地址：
   ```
   https://YOUR_USERNAME.github.io/flow-management-frontend/
   ```

2. 应该看到登录页面

3. 尝试登录：
   - 用户名：`admin`
   - 密码：`admin123`

4. 如果登录成功，说明前端部署正常

### 3.2 测试后端 API

在浏览器访问：
```
https://YOUR_USERNAME.pythonanywhere.com/api/auth/status
```

应该返回 JSON 格式的状态信息。

### 3.3 测试跨域连接

1. 打开浏览器开发者工具（F12）
2. 访问前端网站并登录
3. 查看 Console 标签
4. 应该没有 CORS 错误

## 🔧 故障排查

### 问题 1：GitHub Pages 显示 404

**解决方案**：
- 等待 1-3 分钟让 GitHub 部署
- 检查仓库的 Settings -> Pages 配置
- 确认文件在仓库的根目录

### 问题 2：PythonAnywhere 500 错误

**解决方案**：
- 查看 Web -> Error log
- 检查虚拟环境是否正确
- 确认依赖都已安装
- 检查数据库路径

### 问题 3：CORS 错误

**解决方案**：
- 检查 `production_config.py` 的 `CORS_ORIGINS`
- 确保包含您的 GitHub Pages 地址
- 点击 PythonAnywhere 的 Reload 按钮
- 清除浏览器缓存

### 问题 4：登录失败

**解决方案**：
- 检查 `SECRET_KEY` 是否配置
- 确认 `SESSION_COOKIE_SECURE` 设置
- 检查后端日志
- 验证数据库是否初始化

## 📱 移动端测试

使用手机访问您的 GitHub Pages 地址，测试：
- 登录功能
- 仪表盘显示
- 流水明细
- 底部导航栏
- 响应式布局

## 🎉 部署完成检查清单

- [ ] GitHub Pages 网站可访问
- [ ] PythonAnywhere API 可访问
- [ ] 登录功能正常
- [ ] 数据加载正常
- [ ] 无 CORS 错误
- [ ] 移动端显示正常
- [ ] 文件上传功能正常
- [ ] Session 保持正常

## 📞 需要帮助？

- 查看 `DEPLOYMENT_PYTHONANYWHERE.md` 获取详细的后端部署说明
- 查看 `frontend/README.md` 获取前端部署说明
- 查看 `DEPLOYMENT_SUMMARY.md` 获取完整的部署总结

## 🔄 更新部署

### 更新前端

```bash
cd frontend
# 修改代码
git add .
git commit -m "Update frontend"
git push
```

GitHub Pages 会自动重新部署。

### 更新后端

```bash
# 在本地修改代码
git add .
git commit -m "Update backend"
git push

# 在 PythonAnywhere 控制台
cd /home/YOUR_USERNAME/flow-management
git pull origin main
```

然后在 PythonAnywhere 的 Web 标签点击 **Reload**。

---

**祝您部署成功！** 🎊
