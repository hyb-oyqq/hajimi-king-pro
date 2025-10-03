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

### 必填配置

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `GITHUB_TOKENS` | GitHub API令牌（多个用逗号分隔） | `ghp_token1,ghp_token2` |

### 基础配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `DATA_PATH` | `/app/data` | 数据存储目录 |
| `QUERIES_FILE` | `queries.txt` | 搜索查询配置文件（相对于DATA_PATH） |
| `LANGUAGE` | `zh_cn` | 界面语言（`zh_cn`/`en`） |
| `PROXY` | 空 | 代理服务器（多个用逗号分隔） |
| `DATE_RANGE_DAYS` | `730` | 仓库年龄过滤（天数） |
| `FILE_PATH_BLACKLIST` | `readme,docs,...` | 文件路径黑名单（逗号分隔） |

### 存储配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `STORAGE_TYPE` | `sql` | 存储方式（`sql`/`text`，推荐sql） |
| `DB_TYPE` | `sqlite` | 数据库类型（`sqlite`/`postgresql`/`mysql`） |
| `SQLITE_DB_PATH` | `keys.db` | SQLite数据库文件路径 |
| `POSTGRESQL_HOST` | `localhost` | PostgreSQL主机 |
| `POSTGRESQL_PORT` | `5432` | PostgreSQL端口 |
| `POSTGRESQL_DATABASE` | `hajimi_keys` | PostgreSQL数据库名 |
| `POSTGRESQL_USER` | `postgres` | PostgreSQL用户名 |
| `POSTGRESQL_PASSWORD` | 空 | PostgreSQL密码 |
| `MYSQL_HOST` | `localhost` | MySQL主机 |
| `MYSQL_PORT` | `3306` | MySQL端口 |
| `MYSQL_DATABASE` | `hajimi_keys` | MySQL数据库名 |
| `MYSQL_USER` | `root` | MySQL用户名 |
| `MYSQL_PASSWORD` | 空 | MySQL密码 |

> 💡 首次启用SQL存储时，系统会自动迁移历史文本文件到数据库

### 模型配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `HAJIMI_CHECK_MODEL` | `gemini-2.5-flash` | 密钥验证模型 |
| `HAJIMI_PAID_MODEL` | `gemini-2.5-pro-preview-03-25` | 付费密钥验证模型 |

### 密钥同步配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `GEMINI_BALANCER_SYNC_ENABLED` | `false` | Gemini Balancer同步开关 |
| `GEMINI_BALANCER_URL` | 空 | Gemini Balancer服务地址 |
| `GEMINI_BALANCER_AUTH` | 空 | Gemini Balancer认证密码 |
| `GPT_LOAD_SYNC_ENABLED` | `false` | GPT-Load同步开关 |
| `GPT_LOAD_URL` | 空 | GPT-Load服务地址 |
| `GPT_LOAD_AUTH` | 空 | GPT-Load认证Token |
| `GPT_LOAD_GROUP_NAME` | 空 | GPT-Load目标组名（多个用逗号分隔） |
| `GPT_LOAD_PAID_SYNC_ENABLED` | `false` | 付费密钥独立同步开关 |
| `GPT_LOAD_PAID_GROUP_NAME` | 空 | 付费密钥分组名 |
| `RATE_LIMITED_HANDLING` | `save_only` | 429密钥处理策略 |
| `GPT_LOAD_RATE_LIMITED_GROUP_NAME` | 空 | 429密钥分组名 |

> **429密钥处理策略：** `discard`=丢弃 / `save_only`=仅保存 / `sync`=正常同步 / `sync_separate`=单独分组

### SHA清理配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `SHA_CLEANUP_ENABLED` | `true` | 是否启用自动清理 |
| `SHA_CLEANUP_DAYS` | `7` | 清理N天前的SHA记录 |
| `SHA_CLEANUP_INTERVAL_LOOPS` | `10` | 每N轮执行一次清理 |

> 💡 定期清理旧SHA记录可以重新扫描仓库，避免错过新密钥

### 强制冷却配置

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `FORCED_COOLDOWN_ENABLED` | `false` | 是否启用强制冷却 |
| `FORCED_COOLDOWN_HOURS_PER_QUERY` | `0` | 每个查询后冷却时间（小时） |
| `FORCED_COOLDOWN_HOURS_PER_LOOP` | `0` | 每轮搜索后冷却时间（小时） |

> 💡 支持固定值（如`1`）或范围（如`1-3`或`0.5-1.5`）

### 文本存储配置（仅STORAGE_TYPE=text）

| 变量名 | 默认值 | 说明 |
|--------|--------|------|
| `VALID_KEY_PREFIX` | `keys/keys_valid_` | 有效密钥文件前缀 |
| `RATE_LIMITED_KEY_PREFIX` | `keys/key_429_` | 429密钥文件前缀 |
| `PAID_KEY_PREFIX` | `keys/keys_paid_` | 付费密钥文件前缀 |
| `KEYS_SEND_PREFIX` | `keys/keys_send_` | 已发送密钥文件前缀 |
| `VALID_KEY_DETAIL_PREFIX` | `logs/keys_valid_detail_` | 有效密钥日志前缀 |
| `RATE_LIMITED_KEY_DETAIL_PREFIX` | `logs/key_429_detail_` | 429密钥日志前缀 |
| `PAID_KEY_DETAIL_PREFIX` | `logs/keys_paid_detail_` | 付费密钥日志前缀 |
| `KEYS_SEND_DETAIL_PREFIX` | `logs/keys_send_detail_` | 已发送密钥日志前缀 |

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

## 🔒 安全注意事项

- GitHub Token权限最小化（只需`public_repo`读取权限）
- 定期轮换GitHub Token
- 不要将真实的API密钥提交到版本控制
- 定期检查和清理发现的密钥（文件或数据库）
- 数据库密码使用强密码并妥善保管

---

💖 **享受使用 Hajimi King Pro的快乐时光！** 🎉

