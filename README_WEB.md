# Hajimi King Pro - Web 管理面板 API 文档

Web 管理面板提供基于 REST API 的可视化管理界面，用于监控和管理 Hajimi King Pro 密钥抓取系统。

## 📋 目录

- [快速开始](#快速开始)
- [环境变量配置](#环境变量配置)
- [API 接口说明](#api-接口说明)
- [认证机制](#认证机制)
- [部署方式](#部署方式)
- [技术栈](#技术栈)

---

## 🚀 快速开始

### 启动方式

**生产环境（推荐）**
```bash
# 同时启动 Web 面板和主程序
python start.py
```

**开发环境（仅 Web 面板）**
```bash
# 单独启动 Web 面板
python web/start.py
```

**访问地址**
```
http://localhost:5000
```

---

## ⚙️ 环境变量配置

在 `.env` 文件中配置以下参数：

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `WEB_PORT` | `5000` | Web 服务监听端口 |
| `WEB_HOST` | `0.0.0.0` | Web 服务监听地址（0.0.0.0=所有网卡，127.0.0.1=仅本地） |
| `WEB_AUTH_KEY` | 空 | Web 面板认证密钥（请设置强密码） |
| `WEB_AUTH_ENABLED` | `true` | 是否启用认证（生产环境必须启用） |

**配置示例**
```env
# ==================== Web面板配置 ====================
WEB_PORT=5000
WEB_HOST=0.0.0.0
WEB_AUTH_KEY=your_secret_key_here
WEB_AUTH_ENABLED=true
```

---

## 🔐 认证机制

### 认证方式

所有需要认证的 API 请求支持以下两种方式：

**方式1：请求头认证（推荐）**
```http
X-Auth-Key: your_secret_key_here
```

**方式2：URL 参数认证**
```http
GET /api/keys?auth_key=your_secret_key_here
```

### 禁用认证（仅开发环境）

```env
WEB_AUTH_ENABLED=false
```

> ⚠️ **警告**：生产环境请务必启用认证！

---

## 📊 API 接口说明

### 1. 仪表盘 API

#### `GET /api/dashboard/stats`
获取仪表盘统计数据

**认证**：需要

**响应示例**
```json
{
  "total": {
    "count": 1250,
    "yesterday_change": 50,
    "last_week_change": 300,
    "last_month_change": 800
  },
  "valid": {
    "count": 850,
    "yesterday_change": 30,
    "last_week_change": 200,
    "last_month_change": 550
  },
  "rate_limited": {
    "count": 300,
    "yesterday_change": 15,
    "last_week_change": 80,
    "last_month_change": 200
  },
  "paid": {
    "count": 100,
    "yesterday_change": 5,
    "last_week_change": 20,
    "last_month_change": 50
  },
  "today": {
    "total": 50,
    "valid": 30,
    "rate_limited": 15,
    "paid": 5
  }
}
```

---

### 2. 密钥管理 API

#### `GET /api/keys`
获取密钥列表（支持分页、搜索、过滤）

**认证**：需要

**查询参数**
| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `type` | string | 密钥类型（valid/rate_limited/paid） | 不过滤 |
| `page` | int | 页码 | 1 |
| `page_size` | int | 每页数量 | 50 |
| `search` | string | 搜索关键词（搜索密钥或仓库名） | 空 |

**请求示例**
```http
GET /api/keys?type=valid&page=1&page_size=50&search=gemini
```

**响应示例**
```json
{
  "total": 850,
  "page": 1,
  "page_size": 50,
  "data": [
    {
      "id": 1,
      "api_key": "AIzaSy***************************",
      "key_type": "valid",
      "repo_name": "username/repo-name",
      "file_path": "config/.env",
      "sha": "abc123...",
      "created_at": "2025-01-06T10:30:00"
    }
  ]
}
```

#### `DELETE /api/keys/<key_id>`
删除指定密钥

**认证**：需要

**路径参数**
- `key_id`: 密钥ID

**响应示例**
```json
{
  "success": true
}
```

---

### 3. 统计分析 API

#### `GET /api/analytics/trend`
获取密钥趋势统计数据

**认证**：需要

**查询参数**
| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `days` | int | 统计天数 | 30 |

**请求示例**
```http
GET /api/analytics/trend?days=30
```

**响应示例**
```json
{
  "data": [
    {
      "date": "2025-01-01",
      "total": 45,
      "valid": 30,
      "rate_limited": 12,
      "paid": 3
    },
    {
      "date": "2025-01-02",
      "total": 52,
      "valid": 35,
      "rate_limited": 14,
      "paid": 3
    }
  ]
}
```

#### `GET /api/analytics/repo-stats`
获取仓库统计数据（Top 50）

**认证**：需要

**响应示例**
```json
{
  "data": [
    {
      "repo": "username/repo-name",
      "total": 150,
      "valid": 100,
      "rate_limited": 40,
      "paid": 10
    }
  ]
}
```

---

### 4. 日志 API

#### `GET /api/logs`
获取主程序日志

**认证**：需要

**查询参数**
| 参数 | 类型 | 说明 | 默认值 |
|------|------|------|--------|
| `lines` | int | 读取行数 | 200 |

**响应示例**
```json
{
  "logs": "2025-01-06 10:30:00 - INFO - 开始搜索...\n...",
  "total_lines": 1500
}
```

#### `GET /api/logs/live`
获取实时日志（最后 100 行）

**认证**：需要

**响应示例**
```json
{
  "logs": [
    "2025-01-06 10:30:00 - INFO - 开始搜索...",
    "2025-01-06 10:30:05 - INFO - 发现新密钥..."
  ]
}
```

---

### 5. 规则管理 API

#### `GET /api/rules`
获取所有搜索规则

**认证**：需要

**响应示例**
```json
{
  "data": [
    "AIzaSy in:file",
    "AizaSy in:file filename:.env"
  ],
  "total": 2
}
```

#### `POST /api/rules`
添加新的搜索规则

**认证**：需要

**请求体**
```json
{
  "rule": "AIzaSy in:file filename:config"
}
```

**响应示例**
```json
{
  "success": true,
  "message": "规则添加成功"
}
```

#### `DELETE /api/rules/<index>`
删除指定索引的规则

**认证**：需要

**路径参数**
- `index`: 规则索引（从 0 开始）

**响应示例**
```json
{
  "success": true,
  "message": "规则删除成功"
}
```

#### `POST /api/system/restart`
重启系统（热重启）

**认证**：需要

**响应示例**
```json
{
  "success": true,
  "message": "重启信号已发送"
}
```

---

### 6. 设置管理 API

#### `GET /api/settings`
获取系统设置

**认证**：需要

**响应示例**
```json
{
  "github_auth_mode": "token",
  "github_tokens": 2,
  "github_sessions": 0,
  "storage_type": "sql",
  "db_type": "sqlite",
  "date_range_days": 730,
  "language": "zh_cn",
  "proxy_count": 0,
  "balancer_enabled": false,
  "gpt_load_enabled": false,
  "forced_cooldown_enabled": false,
  "sha_cleanup_enabled": true,
  "forced_cooldown_hours_per_query": 0,
  "forced_cooldown_hours_per_loop": 0,
  "sha_cleanup_days": 7,
  "sha_cleanup_interval_loops": 10,
  "key_validator_max_workers": 5,
  "rate_limited_handling": "save_only",
  "hajimi_check_model": "gemini-2.5-flash",
  "hajimi_paid_model": "gemini-2.5-pro-preview-03-25",
  "gpt_load_paid_enabled": false,
  "gpt_load_group_name": "",
  "gpt_load_paid_group_name": "",
  "gpt_load_rate_limited_group_name": ""
}
```

#### `GET /api/settings/github-tokens`
获取 GitHub Tokens 列表（脱敏显示）

**认证**：需要

**响应示例**
```json
{
  "data": [
    {
      "index": 0,
      "token": "ghp_xxxx***xxxx",
      "full_length": 40
    }
  ]
}
```

#### `POST /api/settings/github-tokens`
添加 GitHub Token

**认证**：需要

**请求体**
```json
{
  "token": "ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**响应示例**
```json
{
  "success": true,
  "message": "Token添加成功，请重启服务生效"
}
```

#### `DELETE /api/settings/github-tokens/<index>`
删除指定的 GitHub Token

**认证**：需要

**路径参数**
- `index`: Token 索引（从 0 开始）

**响应示例**
```json
{
  "success": true,
  "message": "Token删除成功，请重启服务生效"
}
```

#### `GET /api/settings/github-sessions`
获取 GitHub Sessions 列表（脱敏显示）

**认证**：需要

**响应示例**
```json
{
  "data": [
    {
      "index": 0,
      "session": "session_xx***xx",
      "full_length": 128
    }
  ]
}
```

#### `POST /api/settings/github-sessions`
添加 GitHub Session

**认证**：需要

**请求体**
```json
{
  "session": "user_session_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
}
```

**响应示例**
```json
{
  "success": true,
  "message": "Session添加成功，请重启服务生效"
}
```

#### `DELETE /api/settings/github-sessions/<index>`
删除指定的 GitHub Session

**认证**：需要

**路径参数**
- `index`: Session 索引（从 0 开始）

**响应示例**
```json
{
  "success": true,
  "message": "Session删除成功，请重启服务生效"
}
```

---

### 7. 系统状态 API

#### `GET /health`
健康检查端点

**认证**：❌ 不需要

**响应示例**
```json
{
  "status": "healthy",
  "service": "hajimi-king-web",
  "timestamp": "2025-01-06T10:30:00"
}
```

#### `GET /api/system/status`
获取系统运行状态

**认证**：需要

**响应示例**
```json
{
  "is_running": true,
  "is_in_cooldown": false,
  "db_type": "sqlite",
  "storage_type": "sql",
  "db_connected": true
}
```

---

## 🐳 部署方式

### 方式1: Docker 部署（推荐）

```bash
# 1. 构建镜像
docker build -t hajimi-king-pro:latest .

# 2. 启动容器
docker-compose up -d

# 3. 查看日志
docker logs -f hajimi-king-pro
```

### 方式2: Systemd 服务

```bash
# 1. 创建服务文件
sudo nano /etc/systemd/system/hajimi-king.service

# 2. 启动服务
sudo systemctl enable hajimi-king
sudo systemctl start hajimi-king

# 3. 查看状态
sudo systemctl status hajimi-king
```

### 方式3: 直接运行

```bash
# 生产环境（Web + 主程序）
python start.py

# 开发环境（仅 Web）
python web/start.py
```

---

## 💻 技术栈

### 后端
- **Flask** 3.0+ - Web 框架
- **Flask-CORS** - 跨域支持
- **Python-dotenv** - 环境变量管理

### 前端
- **React** 18 - UI 框架
- **Ant Design** 5 - UI 组件库
- **Recharts** - 数据可视化
- **Axios** - HTTP 客户端
- **React Router** - 路由管理
- **Vite** - 构建工具

---

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
        └── vite.config.js
```

---

## 🐛 常见问题

### 1. 无法访问面板
- 检查防火墙是否开放 `WEB_PORT` 端口
- 确认 `WEB_HOST` 设置正确（0.0.0.0 允许外部访问）

### 2. 认证失败
- 检查 `.env` 中的 `WEB_AUTH_KEY` 是否正确配置
- 确认请求头 `X-Auth-Key` 值正确

### 3. 数据不显示
- 确认 `STORAGE_TYPE=sql` 且数据库配置正确
- 确保主程序已运行并生成了数据

### 4. 端口被占用
```bash
# 修改 .env 中的 WEB_PORT
WEB_PORT=5001
```

---

**文档版本**: v3.0  
**最后更新**: 2025-01-08
