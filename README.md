# 🎪 Hajimi King Pro 🏆

人人都是【超级】哈基米大王  👑  

## 🙏 特别感谢

本项目基于 [@GakkiNoOne](https://github.com/GakkiNoOne) 的原始项目进行开发和增强。

**原仓库地址**: [https://github.com/GakkiNoOne/hajimi-king](https://github.com/GakkiNoOne/hajimi-king)

感谢原作者的开源贡献！🎉

---

注意： 本项目正处于beta期间，所以功能、结构、接口等等都有可能变化，不保证稳定性，请自行承担风险。

## 🚀 核心功能

1. **GitHub搜索Gemini Key** 🔍 - 基于自定义查询表达式搜索GitHub代码中的API密钥
2. **代理支持** 🌐 - 支持多代理轮换，提高访问稳定性和成功率
3. **增量扫描** 📊 - 支持断点续传，避免重复扫描已处理的文件
4. **智能过滤** 🚫 - 自动过滤文档、示例、测试文件，专注有效代码
5. **外部同步** 🔄 - 支持向[Gemini-Balancer](https://github.com/snailyp/gemini-balance)和[GPT-Load](https://github.com/tbphp/gpt-load)同步发现的密钥
6. **付费key检测** 💰 - 检查到有效key时自动再次检查是否为付费key
7. **数据库存储** 💾 - 支持SQLite/PostgreSQL/MySQL数据库存储，自动从文本文件迁移

### 🔮 待开发功能 (TODO)

- [ ] **API、可视化展示抓取的key列表** 📊 - 提供API接口和可视化界面获取已抓取的密钥列表
- [ ] **多线程支持** 🛠️ - 支持多线程并发处理，提高处理效率


## 📋 部署教程 🗂️

- [本地部署](https://github.com/hyb-oyqq/hajimi-king-pro/wiki/%E6%9C%AC%E5%9C%B0%E9%83%A8%E7%BD%B2%E6%95%99%E7%A8%8B) 🏠
- [Docker部署](https://github.com/hyb-oyqq/hajimi-king-pro/wiki/Docker%E9%83%A8%E7%BD%B2%E6%95%99%E7%A8%8B) 🐳

---

## ⚙️ 配置变量说明 📖

以下是所有可配置的环境变量，在 `.env` 文件中设置：

### 1️⃣ 必填配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `GITHUB_TOKENS` | GitHub API访问令牌，多个用逗号分隔 🎫 | `ghp_token1,ghp_token2` |

### 2️⃣ 基础配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATA_PATH` | `/app/data` | 数据存储目录路径 📂 |
| `QUERIES_FILE` | `queries.txt` | 搜索查询配置文件路径（相对于DATA_PATH）🎯 |
| `LANGUAGE` | `zh_cn` | 界面语言：`zh_cn`=简体中文，`en`=英文 🌐 |
| `PROXY` | 空 | 代理服务器，多个用逗号分隔<br>格式：`http://user:pass@host:port` 🌐 |
| `DATE_RANGE_DAYS` | `730` | 仓库年龄过滤（天数），只扫描N天内有更新的仓库 📅 |
| `FILE_PATH_BLACKLIST` | `readme,docs,...` | 文件路径黑名单，逗号分隔，跳过文档和示例文件 🚫 |

### 3️⃣ 存储配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `STORAGE_TYPE` | `sql` | 存储方式：`sql`=数据库（推荐），`text`=文本文件 💾 |
| `DB_TYPE` | `sqlite` | 数据库类型：`sqlite`/`postgresql`/`mysql` 🗄️ |

**SQLite 配置**（推荐，无需额外安装）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SQLITE_DB_PATH` | `keys.db` | 数据库文件路径（相对于DATA_PATH）📁 |

**PostgreSQL 配置**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `POSTGRESQL_HOST` | `localhost` | 数据库主机地址 🌐 |
| `POSTGRESQL_PORT` | `5432` | 数据库端口 🔌 |
| `POSTGRESQL_DATABASE` | `hajimi_keys` | 数据库名 📊 |
| `POSTGRESQL_USER` | `postgres` | 用户名 👤 |
| `POSTGRESQL_PASSWORD` | 空 | 密码 🔐 |

**MySQL 配置**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `MYSQL_HOST` | `localhost` | 数据库主机地址 🌐 |
| `MYSQL_PORT` | `3306` | 数据库端口 🔌 |
| `MYSQL_DATABASE` | `hajimi_keys` | 数据库名 📊 |
| `MYSQL_USER` | `root` | 用户名 👤 |
| `MYSQL_PASSWORD` | 空 | 密码 🔐 |

> 💡 **数据迁移**：首次启用SQL存储时，系统会自动检测并迁移历史文本文件到数据库，完成后自动备份并删除原文件

### 4️⃣ 模型配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HAJIMI_CHECK_MODEL` | `gemini-2.5-flash` | 用于验证密钥有效性的模型 🤖 |
| `HAJIMI_PAID_MODEL` | `gemini-2.5-pro-preview-03-25` | 用于验证付费密钥的模型 💎 |

### 5️⃣ 密钥同步配置

**Gemini Balancer 同步**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `GEMINI_BALANCER_SYNC_ENABLED` | `false` | 是否启用同步 🔗 |
| `GEMINI_BALANCER_URL` | 空 | 服务地址（如：`http://your-balancer.com`）🌐 |
| `GEMINI_BALANCER_AUTH` | 空 | 认证密码 🔐 |

**GPT-Load 同步**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `GPT_LOAD_SYNC_ENABLED` | `false` | 是否启用密钥同步 🔗 |
| `GPT_LOAD_URL` | 空 | 服务地址（如：`http://your-gpt-load.com`）🌐 |
| `GPT_LOAD_AUTH` | 空 | 认证Token（页面密码）🔐 |
| `GPT_LOAD_GROUP_NAME` | 空 | 目标组名，多个用逗号分隔（如：`group1,group2`）👥 |

**付费密钥同步**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `GPT_LOAD_PAID_SYNC_ENABLED` | `false` | 是否将付费密钥上传到独立分组 💎 |
| `GPT_LOAD_PAID_GROUP_NAME` | 空 | 付费密钥的分组名（如：`paid_group`）💎 |

**429限速密钥处理**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `RATE_LIMITED_HANDLING` | `save_only` | 处理策略：`discard`/`save_only`/`sync`/`sync_separate` ⏰ |
| `GPT_LOAD_RATE_LIMITED_GROUP_NAME` | 空 | 429密钥的分组名（当策略为`sync_separate`时使用）⏰ |

**`RATE_LIMITED_HANDLING` 策略说明：**
- `discard` - 丢弃，不保存不同步
- `save_only` - 仅本地保存
- `sync` - 作为普通密钥同步
- `sync_separate` - 同步到独立分组

### 6️⃣ 高级配置

**文本存储配置**（仅当 `STORAGE_TYPE=text` 时需要）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `VALID_KEY_PREFIX` | `keys/keys_valid_` | 有效密钥文件前缀 🗝️ |
| `RATE_LIMITED_KEY_PREFIX` | `keys/key_429_` | 429密钥文件前缀 ⏰ |
| `PAID_KEY_PREFIX` | `keys/keys_paid_` | 付费密钥文件前缀 💎 |
| `KEYS_SEND_PREFIX` | `keys/keys_send_` | 已发送密钥文件前缀 🚀 |
| `VALID_KEY_DETAIL_PREFIX` | `logs/keys_valid_detail_` | 有效密钥详细日志前缀 📝 |
| `RATE_LIMITED_KEY_DETAIL_PREFIX` | `logs/key_429_detail_` | 429密钥详细日志前缀 📊 |
| `PAID_KEY_DETAIL_PREFIX` | `logs/keys_paid_detail_` | 付费密钥详细日志前缀 💎 |
| `KEYS_SEND_DETAIL_PREFIX` | `logs/keys_send_detail_` | 已发送密钥详细日志前缀 🚀 |

**其他配置**

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SCANNED_SHAS_FILE` | `scanned_shas.txt` | 已扫描文件SHA记录文件名 📋 |

---

### 查询配置文件 🔍

编辑 `queries.txt` 文件自定义搜索规则：

⚠️ **重要提醒**：query 是本项目的核心！好的表达式可以让搜索更高效，需要发挥自己的想象力！🧠💡

```bash
# GitHub搜索查询配置文件
# 每行一个查询语句，支持GitHub搜索语法
# 以#开头的行为注释，空行会被忽略

# 基础搜索
AIzaSy in:file
AizaSy in:file filename:.env
```

> 📖 **搜索语法参考**：[GitHub Code Search Syntax](https://docs.github.com/en/search-github/searching-on-github/searching-code) 📚  
> 🎯 **核心提示**：创造性的查询表达式是成功的关键，多尝试不同的组合！

---

## 💾 数据库存储说明

### 数据库表结构

系统使用单表设计，支持 SQLite/PostgreSQL/MySQL 三种数据库：

**keys 表结构：**

| 字段名 | 类型 | 说明 | 约束 |
|--------|------|------|------|
| `id` | INTEGER | 主键ID | PRIMARY KEY, AUTO_INCREMENT |
| `api_key` | TEXT | Gemini API密钥 | NOT NULL, UNIQUE |
| `key_type` | TEXT | 密钥类型 | NOT NULL |
| `repo_name` | TEXT | GitHub仓库名称 | 可空 |
| `file_path` | TEXT | 文件路径 | 可空 |
| `file_url` | TEXT | GitHub文件URL | 可空 |
| `created_at` | TIMESTAMP | 创建时间 | DEFAULT CURRENT_TIMESTAMP |
| `updated_at` | TIMESTAMP | 更新时间 | DEFAULT CURRENT_TIMESTAMP |

**密钥类型 (key_type)：**
- `valid` - 有效的免费密钥
- `paid` - 付费层级密钥
- `rate_limited` - 被限流的429密钥
- `send` - 已发送的密钥记录

**索引：**
- `idx_key_type` - key_type 字段索引
- `idx_created_at` - created_at 字段索引

### 使用示例

#### SQLite（推荐，无需额外安装）
```bash
STORAGE_TYPE=sql
DB_TYPE=sqlite
SQLITE_DB_PATH=keys.db
```

#### PostgreSQL
```bash
STORAGE_TYPE=sql
DB_TYPE=postgresql
POSTGRESQL_HOST=localhost
POSTGRESQL_PORT=5432
POSTGRESQL_DATABASE=hajimi_keys
POSTGRESQL_USER=postgres
POSTGRESQL_PASSWORD=yourpassword
```

#### MySQL
```bash
STORAGE_TYPE=sql
DB_TYPE=mysql
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=hajimi_keys
MYSQL_USER=root
MYSQL_PASSWORD=yourpassword
```

### 数据迁移

**自动迁移：** 首次启用 SQL 存储时，系统会：
1. 🔍 自动检测 `data/keys/` 目录下的历史文本文件
2. 📦 备份原始文件到 `backup_before_migration_*` 目录
3. 🔄 将所有密钥迁移到数据库（保留元数据）
4. 🗑️ 迁移完成后删除原文本文件

**手动切换回文本存储：**
```bash
STORAGE_TYPE=text
```

---

## 🔒 安全注意事项 🛡️

- ✅ GitHub Token权限最小化（只需`public_repo`读取权限）🔐
- ✅ 定期轮换GitHub Token 🔄
- ✅ 不要将真实的API密钥提交到版本控制 🙈
- ✅ 定期检查和清理发现的密钥（文件或数据库） 🧹
- ✅ 数据库密码使用强密码并妥善保管 🔐

💖 **享受使用 Hajimi King Pro的快乐时光！** 🎉✨🎊

