# 部署脚本使用说明

本文件夹包含在新电脑上部署流水管理系统所需的所有脚本和文档。

## 📁 文件清单

### 🔧 自动化脚本（核心）

| 文件名 | 功能 | 使用场景 |
|--------|------|----------|
| **install.bat** | 一键安装脚本 | 首次部署时安装Python环境和依赖 |
| **start_background.bat** | 后台启动脚本 | 启动后台服务（推荐生产环境使用） |
| **stop.bat** | 停止服务脚本 | 停止运行中的后台服务 |
| **status.bat** | 状态检查脚本 | 查看服务运行状态和日志 |

### 📚 文档说明

| 文件名 | 内容 | 推荐阅读 |
|--------|------|----------|
| **QUICK_START.md** | 快速开始指南 | ⭐ 首次部署必读 |
| **DEPLOYMENT.md** | 详细部署指南 | 需要深入了解时阅读 |
| **production_config.py** | 生产环境配置 | 高级用户自定义配置 |
| **README_DEPLOYMENT.md** | 本文件 | 了解脚本功能 |

---

## 🚀 快速部署流程

### 在新电脑上的操作步骤

```
1. 复制整个项目文件夹到新电脑
   ↓
2. 双击运行 install.bat
   (等待安装完成，首次需要几分钟)
   ↓
3. 双击运行 start_background.bat
   (服务在后台启动)
   ↓
4. 访问 http://localhost:5000 测试
   ↓
5. 配置花生壳内网穿透
   (详见 QUICK_START.md)
```

---

## 💡 脚本功能详解

### 1. install.bat - 环境安装脚本

**功能：**
- ✅ 检查Python环境（3.8+）
- ✅ 检查pip工具
- ✅ 创建必要的目录（data、logs、uploads）
- ✅ 升级pip到最新版本
- ✅ 安装所有项目依赖包
- ✅ 检查数据库文件

**何时使用：**
- 首次在新电脑上部署
- 依赖包缺失或损坏时
- Python环境重装后

**注意事项：**
- 首次运行需要下载依赖，请确保网络连接
- 安装过程可能需要3-5分钟
- 如果报错，请检查Python是否正确安装

---

### 2. start_background.bat - 后台启动脚本

**功能：**
- ✅ 检查Python环境
- ✅ 检测并提示已有进程
- ✅ 设置生产环境变量
- ✅ 使用pythonw启动（无窗口）
- ✅ 日志输出到logs/app.log
- ✅ 自动检测启动状态

**何时使用：**
- 生产环境部署（推荐）
- 需要长期运行服务
- 不需要查看实时日志

**特点：**
- 关闭命令窗口不会停止服务
- 自动设置为生产模式
- 所有日志写入文件

---

### 3. stop.bat - 停止服务脚本

**功能：**
- ✅ 检测后台Python进程
- ✅ 优雅关闭服务
- ✅ 强制结束失败时自动重试
- ✅ 提供清晰的反馈信息

**何时使用：**
- 需要停止后台服务时
- 重启服务前
- 维护或更新系统时

**使用方法：**
```cmd
stop.bat
```

---

### 4. status.bat - 状态检查脚本

**功能：**
- ✅ 显示服务运行状态
- ✅ 列出Python进程信息
- ✅ 检查端口监听状态
- ✅ 显示访问地址（本地+局域网）
- ✅ 显示日志文件信息
- ✅ 显示最近10行日志

**何时使用：**
- 确认服务是否正常运行
- 查看访问地址
- 检查日志输出
- 故障排查

**输出示例：**
```
========================================
  流水管理系统 - 服务状态
========================================

✅ 服务状态: 运行中

进程信息：
pythonw.exe                 12345 Console                    1    150,000 K

端口监听状态：
TCP    0.0.0.0:5000           0.0.0.0:0              LISTENING       12345

访问地址：
  - 本地: http://localhost:5000
  - 局域网: http://192.168.1.100:5000

日志文件：
  - 最新日志: logs\app.log
  - 文件大小: 102400 字节

最近10行日志：
=======================================
[2026-01-29 23:45:00] INFO: 流水管理系统启动
...
=======================================
```

---

## 🔧 高级配置

### production_config.py - 生产环境配置

提供额外的生产环境优化选项：

```python
# 使用方法
from production_config import ExtendedProductionConfig
```

**主要配置项：**
- `HOST`: 监听地址（默认 0.0.0.0）
- `PORT`: 监听端口（默认 5000）
- `SECRET_KEY`: 安全密钥
- `MAX_CONTENT_LENGTH`: 文件上传限制
- `LOG_LEVEL`: 日志级别
- `ENABLE_CACHING`: 启用缓存

**生成随机密钥：**
```python
from production_config import generate_secret_key
print(generate_secret_key())
```

---

## 📊 服务管理最佳实践

### 日常运维

**启动服务：**
```cmd
start_background.bat
```

**检查状态：**
```cmd
status.bat
```

**停止服务：**
```cmd
stop.bat
```

**查看日志：**
```cmd
# 方法1：使用status.bat查看最新日志
status.bat

# 方法2：直接打开日志文件
notepad logs\app.log

# 方法3：使用PowerShell查看最后50行
powershell -Command "Get-Content logs\app.log -Tail 50"
```

### 设置开机自启动

**方法1：启动文件夹（简单）**
1. Win+R → 输入 `shell:startup`
2. 创建 `start_background.bat` 的快捷方式
3. 复制到打开的文件夹

**方法2：任务计划程序（推荐）**
1. 打开"任务计划程序"
2. 创建基本任务
3. 触发器：计算机启动时
4. 操作：启动 `start_background.bat`

### 数据备份

**备份数据库：**
```cmd
# 创建带日期的备份
copy data\flow.db data\backup_%date:~0,10%.db

# 或使用xcopy
xcopy data\flow.db data\backup_%date:~0,10%.db /Y
```

**自动备份脚本（可选）：**
创建 `backup.bat`：
```cmd
@echo off
set BACKUP_DIR=data\backups
if not exist "%BACKUP_DIR%" mkdir "%BACKUP_DIR%"
copy data\flow.db "%BACKUP_DIR%\flow_backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%.db"
echo 备份完成
```

---

## ⚠️ 故障排查

### 常见问题及解决方案

#### 问题1：install.bat 提示"未检测到Python环境"

**原因：** Python未安装或未添加到PATH

**解决方案：**
1. 确认Python已安装：`python --version`
2. 如果未安装，访问 https://www.python.org/downloads/ 下载
3. 重新安装时**务必勾选** "Add Python to PATH"
4. 安装后重启命令行窗口

---

#### 问题2：start_background.bat 启动失败

**检查步骤：**
1. 运行 `status.bat` 查看错误
2. 打开 `logs\app.log` 查看详细日志
3. 检查5000端口是否被占用：
   ```cmd
   netstat -ano | findstr :5000
   ```

**常见原因：**
- 端口被占用 → 修改config.py中的PORT或关闭占用进程
- 依赖缺失 → 重新运行 `install.bat`
- 数据库损坏 → 删除data/flow.db，重启自动重建

---

#### 问题3：服务无法访问

**本地无法访问：**
1. 确认服务正在运行：`status.bat`
2. 检查防火墙设置
3. 尝试使用IP访问：`http://127.0.0.1:5000`

**外网无法访问（花生壳）：**
1. 确认本地服务正常
2. 检查花生壳客户端是否在线
3. 检查映射配置是否正确
4. 查看花生壳客户端的连接状态

---

#### 问题4：日志文件过大

**解决方案：**
```cmd
# 删除旧日志备份
del logs\app.log.*

# 或配置日志轮转（已在app_new.py中配置）
# maxBytes=10MB, backupCount=10
```

---

## 📞 获取帮助

### 遇到问题时提供的信息

为了快速解决问题，请提供：
1. 错误截图
2. `logs/app.log` 的内容（特别是错误部分）
3. 操作系统版本
4. Python版本：`python --version`
5. 详细的复现步骤

### 文档参考

- **快速开始**：`QUICK_START.md`
- **详细部署**：`DEPLOYMENT.md`
- **功能说明**：`NEW_FEATURES.md`
- **项目说明**：`README.md`

---

## ✅ 部署检查清单

部署完成后，请确认：

- [ ] Python 3.8+ 已安装
- [ ] 运行 `install.bat` 成功
- [ ] 运行 `start_background.bat` 成功
- [ ] 访问 `http://localhost:5000` 正常
- [ ] 可以登录系统（admin/admin123）
- [ ] 花生壳映射配置完成
- [ ] 外网地址可以访问
- [ ] 默认密码已修改
- [ ] 数据库备份策略已制定
- [ ] 运行 `status.bat` 显示正常

---

## 🎯 总结

这套自动化脚本让在新电脑上部署变得非常简单：

**3个步骤完成部署：**
1. 复制项目文件夹
2. 运行 `install.bat`
3. 运行 `start_background.bat`

**4个脚本管理服务：**
- `install.bat` - 安装环境
- `start_background.bat` - 启动服务
- `stop.bat` - 停止服务
- `status.bat` - 查看状态

**2份文档供参考：**
- `QUICK_START.md` - 快速开始
- `DEPLOYMENT.md` - 详细说明

**祝部署顺利！** 🎉
