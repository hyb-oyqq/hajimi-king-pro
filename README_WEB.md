# Hajimi King Pro - Web 管理面板

这是一个基于 React + Flask 的 Web 管理面板，用于管理和监控 Hajimi King Pro 密钥抓取系统。

## 📋 目录

- [功能特性](#功能特性)
- [快速开始](#快速开始)
- [配置说明](#配置说明)
- [开发模式](#开发模式)
- [生产部署](#生产部署)
- [API 接口说明](#api-接口说明)
- [技术栈](#技术栈)
- [故障排除](#故障排除)

## 功能特性

### 1. 仪表盘 (Dashboard)
- 📊 显示密钥总数、有效数、限流数、付费数
- 📈 展示相较于昨日、上周、上月的增长/降低数据
- 📅 单独展示今日密钥统计（总数、有效、限流、付费）
- 🔄 数据每30秒自动刷新

### 2. 密钥管理 (Keys Management)
- 🔍 查看所有已获取的密钥
- 🔎 按类型、关键词搜索密钥
- 📄 分页显示，支持每页50/100/200条
- 🗑️ 删除指定密钥
- 📋 查看密钥详细信息（来源仓库、文件路径等）

### 3. 统计分析 (Analytics)
- 📉 密钥获取趋势图（可选7/14/30/60/90天）
- 📊 Top仓库统计柱状图
- 🎯 密钥类型分布饼图
- 📈 多维度数据可视化

### 4. 日志 (Logs)
- 📝 查看实时抓取日志
- 🔄 自动刷新（每3秒）
- 💾 下载日志到本地
- 📄 显示最近500行日志

### 5. 规则编辑 (Rules)
- ➕ 添加新的搜索规则
- 🗑️ 删除现有规则
- 🔍 搜索规则
- ⚡ 热重启功能（新规则即时生效）

### 6. 设置 (Settings)
- 🔧 查看系统配置
- 🔑 管理 GitHub Tokens
- 🌐 管理 GitHub Sessions
- ➕ 添加/删除 Token 和 Session

## ✅ 已完成的重构

### 1. 创建了统一的启动脚本

#### 📦 `start.py` (项目根目录)
**用途**: 生产环境，同时启动 Web 面板和主程序

```bash
python start.py
```

**功能**:
- ✅ 自动检查依赖
- ✅ 同时启动 Web 服务器和主程序
- ✅ 统一的进程管理
- ✅ 优雅的停止机制（Ctrl+C）
- ✅ 进程监控和自动重启

#### 🔧 `web/start.py`
**用途**: 开发环境，单独启动 Web 面板测试

```bash
python web/start.py
```

**功能**:
- ✅ 自动检查并安装 Python 依赖
- ✅ 自动检查并安装前端依赖
- ✅ 自动构建前端（如果需要）
- ✅ 启动 Web 服务器
- ✅ 跨平台支持（Windows/Linux/Mac）

### 2. 删除了旧脚本

- ❌ `start_web.sh` - 已删除
- ❌ `start_web.bat` - 已删除  
- ❌ `install_web_deps.bat` - 已删除

### 3. 精简了文档

**已合并文档**:
- ✅ 所有 Web 面板文档已整合到本文件

## 🚀 快速开始

### 准备工作

首次使用需要安装依赖：

```bash
# 方式1: 使用 pip（推荐）
pip install -r requirements.txt

# 方式2: 使用 uv（更快）
uv sync
```

### 方式1: 生产环境（推荐）

同时启动 Web 面板和主程序：

```bash
# 1. 确保已安装依赖
# 2. 配置 .env 文件（添加 Web 配置）
# 3. 运行启动脚本
python start.py

# 访问 Web 面板: http://localhost:5000
```

脚本会自动：
- ✅ 检查 Python 依赖
- ✅ 同时启动 Web 服务器和主程序
- ✅ 统一的进程管理
- ✅ 优雅的停止机制（Ctrl+C）

### 方式2: 开发环境（仅 Web 面板）

单独启动 Web 面板进行测试：

```bash
# 安装依赖后运行
python web/start.py

# 访问 Web 面板: http://localhost:5000
```

脚本会自动：
- ✅ 检查 Python 依赖
- ✅ 检查并安装前端依赖  
- ✅ 构建前端（如果需要）
- ✅ 启动 Web 服务器

## 📋 配置说明

在项目根目录的 `.env` 文件中添加以下配置：

```env
# ==================== Web面板配置 ====================
# Web服务端口
WEB_PORT=5000

# Web服务监听地址 (0.0.0.0表示所有网卡，127.0.0.1仅本地访问)
WEB_HOST=0.0.0.0

# Web认证密钥 (用于访问面板，请设置一个强密码)
WEB_AUTH_KEY=your_secret_key_here

# 是否启用认证 (生产环境建议设置为true)
WEB_AUTH_ENABLED=true
```

### 认证说明

#### 启用认证
在 `.env` 中设置：
```env
WEB_AUTH_ENABLED=true
WEB_AUTH_KEY=your_secret_key_here
```

#### 禁用认证（仅开发环境）
```env
WEB_AUTH_ENABLED=false
```

**警告：** 生产环境请务必启用认证！

## 🔧 开发模式

如果需要开发和调试前端：

### 1. 启动后端 API
```bash
python web/api.py
```

### 2. 启动前端开发服务器
```bash
cd web/frontend
npm run dev
```

前端开发服务器会在 http://localhost:3000 启动，并自动代理 API 请求到后端。

## 📊 API 接口说明

所有 API 请求需要在 Header 中携带认证密钥：
```
X-Auth-Key: your_secret_key_here
```

### 主要接口

- `GET /api/dashboard/stats` - 获取仪表盘统计
- `GET /api/keys` - 获取密钥列表
- `GET /api/analytics/trend` - 获取趋势数据
- `GET /api/logs` - 获取日志
- `GET /api/rules` - 获取搜索规则
- `POST /api/rules` - 添加搜索规则
- `GET /api/settings` - 获取系统设置
- `POST /api/settings/github-tokens` - 添加 GitHub Token

完整 API 文档请查看 `web/api.py` 源码。

## 💻 技术栈

### 后端
- Flask 3.0+ - Web框架
- Flask-CORS - 跨域支持
- Python-dotenv - 环境变量管理

### 前端
- React 18 - UI框架
- Ant Design 5 - UI组件库
- Recharts - 数据可视化
- Axios - HTTP客户端
- React Router - 路由管理
- Vite - 构建工具

## 🎯 脚本对比

| 功能 | `start.py` | `web/start.py` |
|------|-----------|---------------|
| 启动位置 | 项目根目录 | web 目录 |
| 用途 | 生产环境 | 开发环境 |
| Web 面板 | ✅ | ✅ |
| 主程序 | ✅ | ❌ |
| 自动安装依赖 | ❌ | ✅ |
| 自动构建前端 | ❌ | ✅ |
| 进程监控 | ✅ | ❌ |

## 🔧 系统服务配置

### Systemd 服务文件

创建 `/etc/systemd/system/hajimi-king.service`:

```ini
[Unit]
Description=Hajimi King (Web Panel + Main App)
After=network.target

[Service]
Type=simple
User=your-user
WorkingDirectory=/path/to/hajimi-king
Environment="PATH=/path/to/hajimi-king/.venv/bin"
ExecStart=/path/to/hajimi-king/.venv/bin/python start.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

启动服务:
```bash
sudo systemctl enable hajimi-king
sudo systemctl start hajimi-king
sudo systemctl status hajimi-king
```

查看日志:
```bash
sudo journalctl -u hajimi-king -f
```

### 使用 Nginx 反向代理

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_cache_bypass $http_upgrade;
    }
}
```

## 📦 目录结构

```
hajimi-king/
├── start.py              # 生产环境启动脚本（Web + 主程序）
├── .env                  # 配置文件
├── app/
│   └── hajimi_king.py    # 主程序
└── web/
    ├── api.py            # Flask API 后端
    ├── start.py          # 开发环境启动脚本（仅 Web）
    ├── dist/             # 前端构建输出目录
    └── frontend/         # React 前端源码
        ├── src/
        │   ├── pages/      # 页面组件
        │   ├── services/   # API 服务
        │   ├── App.jsx     # 主应用组件
        │   └── main.jsx    # 入口文件
        ├── index.html
        ├── package.json
        └── vite.config.js
```

## 🐛 故障排除

### 1. 无法访问面板
- 检查防火墙是否开放了 WEB_PORT 端口
- 确认 WEB_HOST 设置正确（0.0.0.0 允许外部访问）

### 2. 认证失败
- 确认 WEB_AUTH_KEY 设置正确
- 检查浏览器是否保存了正确的认证密钥
- 检查 `.env` 中的 `WEB_AUTH_KEY` 是否正确配置

### 3. 数据不显示
- 确认数据库配置正确
- 检查 STORAGE_TYPE 是否设置为 sql
- 确保主程序已运行并生成了数据

### 4. 提示缺少模块

```bash
ModuleNotFoundError: No module named 'flask_cors'
```

**解决**: 安装依赖
```bash
pip install -r requirements.txt
# 或
pip install flask flask-cors python-dotenv
```

### 5. 前端未构建

```bash
⚠️ 前端未构建
```

**解决**: 使用 `web/start.py` 会自动构建，或手动构建：
```bash
cd web/frontend
npm install
npm run build
```

### 6. 端口被占用

```bash
Address already in use
```

**解决**: 修改 `.env` 中的 `WEB_PORT`，或停止占用端口的进程

## 📝 注意事项

1. **生产环境**: 必须启用认证 (`WEB_AUTH_ENABLED=true`)
2. **密钥安全**: `WEB_AUTH_KEY` 应设置强密码
3. **依赖安装**: 首次运行建议使用 `web/start.py` 自动安装依赖
4. **前端构建**: 生产环境需要先构建前端才能使用 `start.py`

## 🎉 优势

相比旧的脚本方案：

✅ **统一体验** - 一个 Python 脚本替代多个 shell/bat 脚本  
✅ **跨平台** - Windows/Linux/Mac 都可以使用相同命令  
✅ **自动化** - 自动安装依赖、构建前端  
✅ **容错性** - 更好的错误提示和处理  
✅ **可维护** - 代码更清晰，更容易维护

## 更新日志

### v1.0.0 (2025-01-06)
- ✨ 初始版本发布
- 🎨 实现所有核心功能
- 📊 支持实时数据监控
- 🔐 添加认证机制

## 许可证

与主项目保持一致。

---

**文档版本**: v2.0  
**最后更新**: 2025-01-06

