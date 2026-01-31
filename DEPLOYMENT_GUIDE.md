# 流水管理系统 - 前后端分离部署指南

本指南将帮助您将流水管理系统部署到免费平台：
- **前端**：GitHub Pages（免费、永久）
- **后端**：PythonAnywhere（免费账户）

---

## 📋 部署前准备

### 必需账户
1. [GitHub 账户](https://github.com/signup) - 用于前端托管
2. [PythonAnywhere 账户](https://www.pythonanywhere.com/) - 用于后端API

### 本地准备
- 确保项目代码已更新到最新版本
- 数据库文件：`data/flow.db`（如果已有数据）

---

## 🎯 第一部分：后端部署（PythonAnywhere）

### 步骤1：注册 PythonAnywhere

1. 访问 https://www.pythonanywhere.com
2. 点击 "Sign up"
3. 选择 "Free account"（免费账户）
4. 填写信息并注册
5. 验证邮箱

### 步骤2：创建 Web App

1. 登录后，点击顶部 "Web" 标签
2. 点击 "Add a new web app"
3. 选择 "Flask"
4. Python版本：选择 "Python 3.x"（推荐 3.10 或更高）
5. 输入路径：`/var/www/你的用户名/mysite`
6. 点击 "Next" 继续

### 步骤3：上传代码文件

#### 方式A：使用 Web 界面上传（推荐新手）

1. 点击顶部 "Files" 标签
2. 进入 `mysite` 目录
3. 点击 "Upload files" 按钮
4. 上传以下文件：
   ```
   app_new.py
   config.py
   database.py
   utils.py
   requirements.txt
   ```

5. 创建必要的目录：
   - 在 `mysite` 目录下创建 `data` 文件夹
   - 在 `mysite` 目录下创建 `logs` 文件夹
   - 在 `mysite` 目录下创建 `uploads` 文件夹

#### 方式B：使用 Git（推荐）

如果您的代码在 Git 仓库：

1. 在 PythonAnywhere 的 "Consoles" 标签下，打开 "Bash"
2. 运行：
```bash
cd /var/www/你的用户名/mysite
git clone https://github.com/你的用户名/你的仓库.git .
```

### 步骤4：上传数据库

**重要**：如果您有现有数据：

1. 在本地找到 `data/flow.db` 文件
2. 在 PythonAnywhere 的 "Files" 标签下
3. 进入 `mysite/data` 目录
4. 上传 `flow.db` 文件

如果是新部署，数据库会在首次运行时自动创建。

### 步骤5：安装依赖

1. 在 PythonAnywhere 点击 "Consoles" 标签
2. 点击 "Bash" 打开终端
3. 运行以下命令：
```bash
pip3 install -r /var/www/你的用户名/mysite/requirements.txt
```

### 步骤6：配置 Web App

1. 回到 "Web" 标签
2. 找到 "Code" 部分
3. 点击 "WSGI configuration file" 链接
4. 编辑文件内容为：

```python
import sys
import os

# 添加项目路径
project_home = u'/var/www/你的用户名/mysite'
if project_home not in sys.path:
    sys.path = [project_home] + sys.path

# 导入Flask应用
from app_new import app as application
```

5. 点击 "Save" 保存

### 步骤7：配置环境变量

1. 在 "Web" 标签下
2. 找到 "Environment variables" 部分
3. 添加以下变量：

| 变量名 | 值 |
|--------|-----|
| `FLASK_ENV` | `production` |
| `SECRET_KEY` | `生成一个随机字符串` |
| `CORS_ORIGINS` | `https://你的用户名.github.io` |

**生成 SECRET_KEY**：
- 访问 https://www.random.org/strings/
- 生成一个长随机字符串

### 步骤8：重启 Web App

1. 在 "Web" 标签顶部
2. 点击绿色的 "Reload" 按钮
3. 等待 1-2 分钟

### 步骤9：获取 API 地址

在 "Web" 标签顶部，你会看到：
```
Configuration: /var/www/你的用户名/mysite/mysite_wsgi.py
Running on: https://你的用户名.pythonanywhere.com
```

**记录这个地址**，这是你的后端API地址。

### 步骤10：测试 API

在浏览器中访问：
```
https://你的用户名.pythonanywhere.com/
```

应该能看到页面重定向到登录页。

---

## 🌐 第二部分：前端部署（GitHub Pages）

### 步骤1：准备前端文件

在本地创建一个新的文件夹结构：

```
frontend/
├── index.html          # 从 templates/ 复制并修改
├── login.html          # 从 templates/ 复制并修改
├── static/
│   ├── css/
│   │   └── *.css      # 所有CSS文件
│   └── js/
│       ├── config.js   # 已创建
│       ├── script.js   # 已修改
│       └── operator-selector.js  # 已修改
└── README.md
```

### 步骤2：修改 HTML 文件

在每个 HTML 文件的 `<head>` 部分，确保按以下顺序加载 JavaScript：

```html
<!-- 先加载配置文件 -->
<script src="/static/js/config.js"></script>
<!-- 再加载其他JS文件 -->
<script src="/static/js/script.js"></script>
<script src="/static/js/operator-selector.js"></script>
```

### 步骤3：创建 GitHub 仓库

1. 访问 https://github.com
2. 登录后点击右上角 "+"
3. 选择 "New repository"
4. 仓库名：`flow-system-frontend`
5. 选择 "Public"（公开仓库才能用 GitHub Pages）
6. 点击 "Create repository"

### 步骤4：上传前端文件

#### 方式A：使用网页上传（适合少量文件）

1. 进入新创建的仓库
2. 点击 "Upload files"
3. 拖拽或选择所有前端文件
4. 在底部填写提交信息：
   - Add files via upload
5. 点击 "Commit changes"

#### 方式B：使用 Git 命令（推荐）

在本地前端目录打开终端：

```bash
# 初始化 Git
git init

# 添加所有文件
git add .

# 提交
git commit -m "Initial commit"

# 添加远程仓库
git remote add origin https://github.com/你的用户名/flow-system-frontend.git

# 推送到 GitHub
git branch -M main
git push -u origin main
```

### 步骤5：启用 GitHub Pages

1. 进入仓库页面
2. 点击 "Settings" 标签
3. 在左侧菜单找到 "Pages"
4. 在 "Source" 部分：
   - Branch: 选择 `main`
   - Folder: 选择 `/ (root)`
5. 点击 "Save"

### 步骤6：等待部署

- 等待 1-2 分钟
- 刷新页面
- 在顶部会看到：
  ```
  Your site is live at https://你的用户名.github.io/flow-system-frontend/
  ```

### 步骤7：测试前端

访问：
```
https://你的用户名.github.io/flow-system-frontend/
```

应该能看到登录页面。

---

## 🔗 第三部分：连接前后端

### 步骤1：更新前端 API 配置

在 `static/js/config.js` 文件中，修改生产环境 API 地址：

```javascript
const API_CONFIG = {
    // 开发环境
    development: 'http://localhost:5000/api',
    
    // 生产环境 - 修改这里！
    production: 'https://你的用户名.pythonanywhere.com/api'
};
```

### 步骤2：重新上传前端

更新 `config.js` 后，重新推送到 GitHub：

```bash
git add static/js/config.js
git commit -m "Update API URL"
git push
```

GitHub Pages 会自动重新部署（约1-2分钟）。

### 步骤3：配置后端 CORS

在 PythonAnywhere：

1. 回到 "Web" 标签
2. 在 "Environment variables" 部分
3. 确保 `CORS_ORIGINS` 包含你的前端地址：
   ```
   https://你的用户名.github.io
   ```
4. 点击 "Save"
5. 点击 "Reload" 重启 Web App

---

## ✅ 第四部分：测试部署

### 测试步骤

1. **访问前端**
   - 打开：`https://你的用户名.github.io/flow-system-frontend/`

2. **打开浏览器控制台**
   - 按 F12 打开开发者工具
   - 查看 Console 标签
   - 应该看到：
     ```
     当前API地址: https://你的用户名.pythonanywhere.com/api
     环境: 生产环境
     ```

3. **测试登录**
   - 使用默认管理员账户：`admin / admin123`
   - 点击登录
   - 应该成功登录并跳转到仪表盘

4. **测试功能**
   - 查看统计数据
   - 标记流水记录
   - 所有功能应该正常工作

---

## 📊 架构图

```
用户浏览器
    ↓
    ↓ HTTPS
    ↓
┌─────────────────────────────────┐
│   GitHub Pages (前端)          │
│   https://xxx.github.io        │
│   - HTML/CSS/JS 静态文件       │
│   - 通过 API 调用后端          │
└─────────────────────────────────┘
         ↓ JSON API 调用
         ↓
┌─────────────────────────────────┐
│   PythonAnywhere (后端)        │
│   https://xxx.pythonanywhere.com│
│   - Flask API                  │
│   - SQLite 数据库              │
│   - 业务逻辑处理               │
└─────────────────────────────────┘
```

---

## 🔧 常见问题

### 1. CORS 错误

**问题**：浏览器控制台显示 CORS 相关错误

**解决**：
- 检查 PythonAnywhere 的 `CORS_ORIGINS` 环境变量
- 确保地址完全匹配（包括 https://）
- 重启 PythonAnywhere Web App

### 2. API 404 错误

**问题**：API 请求返回 404

**解决**：
- 检查 `config.js` 中的 `API_URL` 是否正确
- 确保以 `/api` 结尾
- 检查 PythonAnywhere 的路由配置

### 3. 登录失败

**问题**：无法登录或登录后立即退出

**解决**：
- 检查 `SECRET_KEY` 是否设置
- 确保前后端的 Cookie 配置一致
- 检查浏览器是否阻止了 Cookie

### 4. 数据库连接失败

**问题**：数据库相关错误

**解决**：
- 确保 `data/flow.db` 文件存在
- 检查文件权限
- 查看 PythonAnywhere 的错误日志

### 5. GitHub Pages 部署失败

**问题**：GitHub Pages 显示部署错误

**解决**：
- 确保 HTML 文件在仓库根目录
- 检查文件名是否正确（index.html）
- 查看 GitHub Pages 的部署日志

---

## 📝 维护和更新

### 更新后端

1. 修改代码
2. 在 PythonAnywhere 的 "Files" 标签上传新文件
3. 点击 "Web" → "Reload"

或使用 Git：
```bash
cd /var/www/你的用户名/mysite
git pull
```

### 更新前端

1. 修改本地文件
2. Git 提交并推送：
```bash
git add .
git commit -m "Update"
git push
```
GitHub Pages 会自动部署。

---

## 🔒 安全建议

1. **修改默认密码**
   - 登录后立即修改管理员密码
   - 为客户账户设置强密码

2. **定期备份数据库**
   - 定期下载 `data/flow.db` 文件
   - 保存到本地或云存储

3. **监控日志**
   - 定期查看 PythonAnywhere 的日志
   - 注意异常访问

4. **限制访问**（可选）
   - 可以在前端添加访问密码
   - 或使用 GitHub Pages 的访问限制

---

## 💰 费用总结

| 项目 | 平台 | 费用 |
|------|------|------|
| 前端托管 | GitHub Pages | **免费** |
| 后端托管 | PythonAnywhere | **免费** |
| 域名 | GitHub Pages | **免费** (xxx.github.io) |
| SSL证书 | 自动配置 | **免费** |
| 数据库 | SQLite | **免费** |
| **总计** | | **$0 / 永久免费** |

---

## 🎉 完成部署

恭喜！您已成功将流水管理系统部署到免费平台！

### 访问地址
- **前端**：`https://你的用户名.github.io/flow-system-frontend/`
- **后端**：`https://你的用户名.pythonanywhere.com/`

### 下一步
1. 修改默认管理员密码
2. 导入或创建客户数据
3. 开始使用系统！

---

## 📞 获取帮助

如遇问题：
1. 检查浏览器控制台的错误信息
2. 查看 PythonAnywhere 的错误日志
3. 查看 GitHub Pages 的部署日志
4. 参考本文档的"常见问题"部分

---

**祝您使用愉快！** 🚀
