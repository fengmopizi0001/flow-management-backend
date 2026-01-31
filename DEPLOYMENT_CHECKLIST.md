# 流水管理系统 - 部署检查清单

使用此清单确保所有部署步骤正确完成。

---

## 📋 部署前准备

- [ ] 注册 GitHub 账户
- [ ] 注册 PythonAnywhere 账户
- [ ] 本地项目代码已更新到最新版本
- [ ] 数据库文件 `data/flow.db` 已备份（如果有数据）
- [ ] 记录好所有账号密码

---

## 🔧 后端部署（PythonAnywhere）

### 账户和创建
- [ ] 登录 PythonAnywhere
- [ ] 创建 Web App（选择 Flask）
- [ ] 选择 Python 3.x 版本
- [ ] 记录 Web App 路径：`/var/www/你的用户名/mysite`

### 文件上传
- [ ] 上传 `app_new.py`
- [ ] 上传 `config.py`
- [ ] 上传 `database.py`
- [ ] 上传 `utils.py`
- [ ] 上传 `requirements.txt`
- [ ] 创建 `data/` 目录
- [ ] 创建 `logs/` 目录
- [ ] 创建 `uploads/` 目录

### 数据库
- [ ] 上传 `data/flow.db`（如果有数据）或确认将自动创建

### 依赖安装
- [ ] 打开 Bash 终端
- [ ] 运行 `pip3 install -r requirements.txt`
- [ ] 确认所有依赖安装成功

### Web 配置
- [ ] 编辑 WSGI 配置文件
- [ ] 确认导入 `from app_new import app as application`
- [ ] 保存 WSGI 配置

### 环境变量
- [ ] 设置 `FLASK_ENV=production`
- [ ] 设置 `SECRET_KEY`（生成随机字符串）
- [ ] 设置 `CORS_ORIGINS=https://你的用户名.github.io`
- [ ] 保存环境变量

### 重启和测试
- [ ] 点击 "Reload" 重启 Web App
- [ ] 等待 1-2 分钟
- [ ] 记录后端地址：`https://你的用户名.pythonanywhere.com`
- [ ] 在浏览器访问后端地址
- [ ] 确认能看到登录页面

---

## 🌐 前端部署（GitHub Pages）

### 准备文件
- [ ] 创建 `frontend/` 文件夹
- [ ] 复制 `templates/index.html` 到 `frontend/`
- [ ] 复制 `templates/login.html` 到 `frontend/`
- [ ] 复制 `templates/admin/*.html` 到 `frontend/admin/`
- [ ] 复制 `templates/customer/*.html` 到 `frontend/customer/`
- [ ] 复制 `static/css/` 到 `frontend/static/css/`
- [ ] 复制 `static/js/` 到 `frontend/static/js/`

### 修改 HTML 文件
- [ ] 在每个 HTML 中确认 `<script>` 标签顺序正确
- [ ] 确保 `config.js` 在其他 JS 之前加载
- [ ] 修改静态资源路径（如果需要）

### 创建仓库
- [ ] 在 GitHub 创建新仓库 `flow-system-frontend`
- [ ] 设置为 Public（公开）
- [ ] 记录仓库 URL

### 上传文件
- [ ] 方法 A：使用网页上传所有文件
  - [ ] 选择所有前端文件
  - [ ] 填写提交信息
  - [ ] 点击 "Commit changes"
- [ ] 或方法 B：使用 Git 命令上传
  - [ ] `git init`
  - [ ] `git add .`
  - [ ] `git commit -m "Initial commit"`
  - [ ] `git remote add origin ...`
  - [ ] `git push -u origin main`

### 启用 Pages
- [ ] 进入仓库 Settings
- [ ] 找到 Pages 设置
- [ ] 选择 Branch: `main`
- [ ] 选择 Folder: `/ (root)`
- [ ] 点击 Save
- [ ] 等待 1-2 分钟
- [ ] 记录前端地址：`https://你的用户名.github.io/flow-system-frontend/`

### 测试前端
- [ ] 访问前端地址
- [ ] 确认能看到登录页面
- [ ] 按 F12 打开控制台
- [ ] 确认没有错误

---

## 🔗 连接前后端

### 更新前端配置
- [ ] 打开 `static/js/config.js`
- [ ] 修改 `production` API 地址为 PythonAnywhere 地址
- [ ] 保存文件
- [ ] 重新推送到 GitHub
- [ ] 等待 GitHub Pages 重新部署

### 配置后端 CORS
- [ ] 回到 PythonAnywhere
- [ ] 确认 `CORS_ORIGINS` 包含前端地址
- [ ] 点击 "Reload" 重启后端

### 测试连接
- [ ] 清除浏览器缓存
- [ ] 重新访问前端地址
- [ ] 打开浏览器控制台
- [ ] 确认显示：`环境: 生产环境`
- [ ] 确认 API 地址正确

---

## ✅ 功能测试

### 登录测试
- [ ] 使用管理员账户登录（admin / admin123）
- [ ] 确认成功登录
- [ ] 确认跳转到仪表盘
- [ ] 登出功能正常

### 管理员功能测试
- [ ] 查看仪表盘统计数据
- [ ] 导入 Excel 文件（如果有）
- [ ] 添加目标
- [ ] 录入流水
- [ ] 查看记录
- [ ] 对账报表

### 客户功能测试
- [ ] 使用客户账户登录
- [ ] 查看客户仪表盘
- [ ] 查看流水明细
- [ ] 标记流水记录
- [ ] 选择操作人
- [ ] 确认统计更新

### API 测试
- [ ] 打开浏览器控制台 Network 标签
- [ ] 执行操作时查看 API 请求
- [ ] 确认所有 API 请求返回 200 状态
- [ ] 确认没有 CORS 错误
- [ ] 确认数据正确返回

---

## 🔒 安全配置

- [ ] 修改管理员密码
- [ ] 修改所有客户默认密码
- [ ] 确认 `SECRET_KEY` 已修改
- [ ] 确认 `DEBUG=False`（生产环境）
- [ ] 确认 HTTPS 正常工作
- [ ] 检查日志文件 `logs/app.log`
- [ ] 备份数据库 `data/flow.db`

---

## 📝 记录信息

### 重要地址和凭据

**GitHub**
- 账户：`______________________`
- 邮箱：`______________________`
- 前端地址：`https://______________________.github.io/flow-system-frontend/`

**PythonAnywhere**
- 账户：`______________________`
- 邮箱：`______________________`
- 后端地址：`https://______________________.pythonanywhere.com`
- Web App 路径：`/var/www/______________________/mysite`

**系统账户**
- 管理员用户名：`admin`
- 管理员密码：`______________________`（修改后填写）

**环境变量**
- SECRET_KEY：`______________________`（请妥善保管）
- CORS_ORIGINS：`https://______________________.github.io`

---

## 🚨 故障排查

### 如果遇到问题，按以下步骤检查：

1. **CORS 错误**
   - [ ] 检查 PythonAnywhere 的 `CORS_ORIGINS` 设置
   - [ ] 确认地址完全匹配（包括 https://）
   - [ ] 重启 PythonAnywhere Web App

2. **API 404 错误**
   - [ ] 检查 `config.js` 中的 `API_URL`
   - [ ] 确认以 `/api` 结尾
   - [ ] 检查 PythonAnywhere 路由

3. **登录失败**
   - [ ] 检查 `SECRET_KEY` 是否设置
   - [ ] 检查 Cookie 是否被阻止
   - [ ] 查看浏览器控制台错误

4. **数据库错误**
   - [ ] 确认 `data/flow.db` 存在
   - [ ] 检查文件权限
   - [ ] 查看 PythonAnywhere 日志

5. **GitHub Pages 部署失败**
   - [ ] 确认仓库是 Public
   - [ ] 检查文件在根目录
   - [ ] 查看 GitHub Pages 日志

---

## 📊 部署总结

完成所有检查项后，您应该：

✅ 前端在 GitHub Pages 上运行
✅ 后端在 PythonAnywhere 上运行
✅ 前后端通过 API 正常通信
✅ 所有功能正常工作
✅ 安全配置已完成
✅ 备份数据已保存

**恭喜！您的系统已成功部署到免费平台！** 🎉

---

## 📞 需要帮助？

1. 查看 `DEPLOYMENT_GUIDE.md` 获取详细步骤
2. 检查浏览器控制台错误信息
3. 查看 PythonAnywhere 日志
4. 查看 GitHub Pages 部署日志
5. 参考本文档的"故障排查"部分

---

**祝您使用愉快！** 🚀
