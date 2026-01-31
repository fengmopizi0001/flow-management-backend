# 流水管理系统 - 前后端分离部署总结

## 📋 部署概述

本项目已配置为前后端分离架构：
- **前端**：部署到 GitHub Pages（静态网站托管）
- **后端**：部署到 PythonAnywhere（Python Web 应用托管）

## 🎯 当前状态

✅ 本地服务已启动并运行在：http://localhost:5000

✅ 前端代码已准备就绪在：`frontend/` 目录

✅ 后端已配置 CORS 支持跨域请求

## 📁 项目结构

```
流水管理系统/
├── backend/                    # 后端代码（当前目录）
│   ├── app_new.py             # Flask 主应用
│   ├── config.py              # 配置文件
│   ├── database.py            # 数据库操作
│   ├── requirements.txt        # Python 依赖
│   ├── auth/                 # 认证模块
│   ├── admin/                # 管理员模块
│   ├── customer/              # 客户模块
│   ├── data/                 # 数据库文件
│   ├── logs/                 # 日志文件
│   ├── uploads/              # 上传文件
│   └── static/               # 静态资源
├── frontend/                  # 前端代码（新建）
│   ├── index.html            # 主页面
│   ├── css/
│   │   └── style.css       # 样式文件
│   ├── js/
│   │   ├── config.js        # API 配置
│   │   └── app.js          # 应用逻辑
│   └── README.md           # 前端部署指南
├── DEPLOYMENT_PYTHONANYWHERE.md  # PythonAnywhere 部署指南
└── DEPLOYMENT_SUMMARY.md          # 本文档
```

## 🚀 部署步骤

### 第一步：部署前端到 GitHub Pages

#### 1.1 创建 GitHub 仓库

```bash
# 在 frontend 目录初始化 Git
cd frontend
git init
git add .
git commit -m "Initial commit - Flow Management Frontend"

# 创建 GitHub 仓库后，添加远程地址
git remote add origin https://github.com/your-username/flow-management-frontend.git

# 推送代码
git push -u origin main
```

#### 1.2 启用 GitHub Pages

1. 访问你的 GitHub 仓库
2. 点击 **Settings** 标签页
3. 向下滚动找到 **GitHub Pages** 部分
4. 在 **Source** 下选择：
   - **Branch**: `main`
   - **Folder**: `/ (root)`
5. 点击 **Save**

#### 1.3 等待部署完成

几分钟后，你的前端网站将在以下地址可用：

```
https://your-username.github.io/flow-management-frontend/
```

#### 1.4 配置生产环境 API 地址

编辑 `frontend/js/config.js`，修改 `production` 地址：

```javascript
const API_CONFIG = {
    development: 'http://localhost:5000/api',
    
    // 修改为你的 PythonAnywhere 地址
    production: 'https://your-username.pythonanywhere.com/api'
};
```

### 第二步：部署后端到 PythonAnywhere

详细步骤请参考 `DEPLOYMENT_PYTHONANYWHERE.md` 文件。

#### 2.1 快速部署命令

在 PythonAnywhere 控制台执行：

```bash
# 克隆代码（如果使用 Git）
cd /home/your-username
git clone https://github.com/your-username/flow-management-backend.git flow-management

# 或上传代码后解压
cd /home/your-username
unzip flow-management.zip -d flow-management

# 进入项目目录
cd flow-management

# 创建虚拟环境
python3.8 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python -c "from app_new import create_app; app = create_app('production'); print('Database initialized')"
```

#### 2.2 配置 WSGI

编辑 WSGI 配置文件（`/var/www/your-username_pythonanywhere_com_wsgi.py`）：

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

#### 2.3 配置 Web 应用

在 PythonAnywhere 的 **Web** 标签页设置：

- **Virtualenv**: `/home/your-username/flow-management/venv`
- **Working directory**: `/home/your-username/flow-management`

添加环境变量：
```
FLASK_CONFIG=production
FLASK_ENV=production
SECRET_KEY=your-very-secret-key-change-this-in-production
```

点击 **Reload** 重载应用。

### 第三步：配置 CORS（跨域）

#### 3.1 更新生产配置

在 PythonAnywhere 上创建 `production_config.py`：

```python
class ProductionConfig:
    """生产环境配置"""
    
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-very-secret-key-change-this-in-production')
    DEBUG = False
    TESTING = False
    
    # CORS配置 - 重要！
    CORS_ORIGINS = [
        'https://your-username.github.io',
        'https://your-username.github.io/flow-management-frontend'
    ]
```

#### 3.2 更新 config.py

确保 `config.py` 中包含生产配置：

```python
class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SECURE = True
    
    # 从 production_config.py 导入配置
    @staticmethod
    def init_app(app):
        from production_config import ProductionConfig
        app.config.from_object(ProductionConfig)
        Config.init_app(app)
```

## 🔧 配置说明

### API 地址配置

前端 `js/config.js` 会自动检测环境：

- **开发环境**：`http://localhost:5000/api`（本地开发）
- **生产环境**：`https://your-username.pythonanywhere.com/api`（线上部署）

### CORS 配置

后端已配置支持跨域请求：

- 开发环境：允许所有来源（`*`）
- 生产环境：仅允许配置的来源（GitHub Pages 地址）

## 📝 部署清单

### 前端部署到 GitHub Pages

- [ ] 创建 GitHub 仓库
- [ ] 推送前端代码
- [ ] 启用 GitHub Pages
- [ ] 等待部署完成
- [ ] 测试访问前端网站
- [ ] 更新 `frontend/js/config.js` 中的生产 API 地址

### 后端部署到 PythonAnywhere

- [ ] 注册 PythonAnywhere 账户
- [ ] 创建 Web 应用
- [ ] 上传后端代码
- [ ] 创建虚拟环境
- [ ] 安装依赖
- [ ] 配置 WSGI
- [ ] 配置环境变量
- [ ] 初始化数据库
- [ ] 重载应用
- [ ] 测试 API 访问

### 集成测试

- [ ] 测试前端登录功能
- [ ] 测试数据加载
- [ ] 测试表单提交
- [ ] 测试文件上传
- [ ] 测试 Session 管理
- [ ] 测试 CORS 配置

## 🔍 测试验证

### 1. 本地测试（开发环境）

```bash
# 本地服务已在运行
# 访问: http://localhost:5000
```

### 2. 前端独立测试

直接在浏览器打开 `frontend/index.html`：
- 本地：直接打开文件
- 或使用本地服务器：`python -m http.server 8000`

### 3. 生产环境测试

1. 访问 GitHub Pages：`https://your-username.github.io/flow-management-frontend/`
2. 尝试登录（admin / admin123）
3. 检查是否能正常加载数据
4. 检查浏览器控制台是否有 CORS 错误

## 🐛 故障排查

### 问题 1：CORS 错误

**症状**：浏览器控制台显示跨域错误

**解决方案**：
1. 检查 `production_config.py` 中的 `CORS_ORIGINS` 配置
2. 确保包含你的 GitHub Pages 地址
3. 重载 PythonAnywhere 应用
4. 清除浏览器缓存

### 问题 2：API 请求失败

**症状**：前端无法连接后端 API

**解决方案**：
1. 检查 `frontend/js/config.js` 中的 API 地址
2. 确保后端服务正常运行
3. 检查 PythonAnywhere 日志
4. 验证网络连接

### 问题 3：Session 失效

**症状**：登录后立即退出或无法保持登录状态

**解决方案**：
1. 检查 `SECRET_KEY` 是否配置
2. 确保 HTTPS 已启用
3. 检查 Cookie 设置（`SESSION_COOKIE_SECURE`, `SESSION_COOKIE_SAMESITE`）
4. 验证 CORS 的 `supports_credentials: True` 配置

### 问题 4：数据库错误

**症状**：无法访问或操作数据库

**解决方案**：
1. 检查数据库文件路径是否正确
2. 确保数据库文件权限正确
3. 验证数据库是否已初始化
4. 检查磁盘空间是否充足

## 📚 相关文档

- `frontend/README.md` - 前端详细部署指南
- `DEPLOYMENT_PYTHONANYWHERE.md` - PythonAnywhere 详细部署指南
- `README.md` - 项目使用说明

## 🎉 部署完成检查

部署完成后，请确认：

✅ 前端网站可正常访问
✅ 后端 API 可正常响应
✅ 登录功能正常
✅ 数据加载正常
✅ 无 CORS 错误
✅ Session 管理正常
✅ 移动端显示正常

## 📞 技术支持

如遇到问题：

1. 查看 GitHub 仓库的 Issues
2. 检查 PythonAnywhere 日志
3. 查看浏览器开发者工具控制台
4. 联系后端管理员

## 🔐 安全建议

1. **修改默认密码**：首次登录后修改 admin 密码
2. **使用强密码**：客户账户使用强密码
3. **定期备份数据库**：定期导出数据库备份
4. **监控日志**：定期检查错误日志
5. **更新依赖**：及时更新 Python 包

## 📈 性能优化建议

1. **静态文件缓存**：配置浏览器缓存策略
2. **数据库优化**：考虑使用 PostgreSQL 替代 SQLite
3. **CDN 加速**：为静态资源使用 CDN
4. **压缩资源**：启用 Gzip 压缩
5. **负载均衡**：高并发时使用负载均衡

---

**部署日期**：2026-01-31  
**版本**：v1.0  
**架构**：前后端分离
