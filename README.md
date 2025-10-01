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
6. **付费key检测**💰 - 检查到有效key时自动再次检查是否为付费key

### 🔮 待开发功能 (TODO)

- [ ] **数据库支持保存key** 💾 - 支持将发现的API密钥持久化存储到数据库中
- [ ] **API、可视化展示抓取的key列表** 📊 - 提供API接口和可视化界面获取已抓取的密钥列表
- [x] **付费key检测** 💰 - 额外check下付费key

## 📋 目录 🗂️

- [本地部署](#-本地部署) 🏠
- [Docker部署](#-docker部署) 🐳
- [配置变量说明](#-配置变量说明) ⚙️

---

## 🖥️ 本地部署 🚀

### 1. 环境准备 🔧

```bash
# 确保已安装Python
python --version

# 安装uv包管理器（如果未安装）
pip install uv
```

### 2. 项目设置 📁

```bash
# 克隆项目
git clone <repository-url>
cd hajimi-king

# 复制配置文件
cp env.example .env

# 复制查询文件
cp queries.example queries.txt
```

### 3. 配置环境变量 🔑

编辑 `.env` 文件，**必须**配置GitHub Token：

```bash
# 必填：GitHub访问令牌
GITHUB_TOKENS=ghp1,ghp2,ghp3

# 可选：其他配置保持默认值即可
```

> 💡 **获取GitHub Token**：访问 [GitHub Settings > Tokens](https://github.com/settings/tokens)，创建具有 `public_repo` 权限的访问令牌 🎫

### 4. 安装依赖并运行 ⚡

```bash
# 安装项目依赖
uv pip install -r pyproject.toml

# 创建数据目录
mkdir -p data

# 运行程序
python app/hajimi_king.py
```

### 5. 本地运行管理 🎮

```bash
# 查看日志文件
tail -f data/keys/keys_valid_detail_*.log

# 查看找到的有效密钥
cat data/keys/keys_valid_*.txt

# 停止程序
Ctrl + C
```

---

## 🐳 Docker部署 🌊

### 方式一：使用环境变量

```yaml
version: '3.8'
services:
  hajimi-king:
    image: ghcr.io/hyb-oyqq/hajimi-king-pro:latest
    container_name: hajimi-king-pro
    restart: unless-stopped
    environment:
      # 必填：GitHub访问令牌
      - GITHUB_TOKENS=ghp_your_token_here_1,ghp_your_token_here_2
      # 可选配置
      - HAJIMI_CHECK_MODEL=gemini-2.5-flash
      - QUERIES_FILE=queries.txt
    volumes:
      - ./data:/app/data
    working_dir: /app
```

### 方式二：使用.env文件

```yaml
version: '3.8'
services:
  hajimi-king:
    image: ghcr.io/hyb-oyqq/hajimi-king-pro:latest
    container_name: hajimi-king-pro
    restart: unless-stopped
    env_file:
      - .env
    volumes:
      - ./data:/app/data
    working_dir: /app
```

创建 `.env` 文件（参考 `env.example`）：
```bash
# 复制示例配置文件
cp env.example .env
# 编辑配置文件，填入你的GitHub Token
```

### 启动服务

```bash
# 创建数据目录和查询文件
mkdir -p data
echo "AIzaSy in:file" > data/queries.txt

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```

### 代理配置

强烈建议使用！GITHUB、GEMINI 访问长时间高频都会BAN IP

如果需要使用代理访问GitHub或Gemini API，推荐使用本地WARP代理：

> 🌐 **代理方案**：[warp-docker](https://github.com/cmj2002/warp-docker) - 本地WARP代理解决方案

在 `.env` 文件中配置：
```bash
# 多个代理使用逗号分隔
PROXY=http://localhost:1080
```

---

## ⚙️ 配置变量说明 📖

以下是所有可配置的环境变量，在 `.env` 文件中设置：

### 🔴 必填配置 ⚠️

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `GITHUB_TOKENS` | GitHub API访问令牌，多个用逗号分隔 🎫 | `ghp_token1,ghp_token2` |

### 🟡 重要配置（建议了解）🤓

| 变量名 | 默认值                | 说明                                              |
|--------|--------------------|-------------------------------------------------|
| `PROXY` | 空 | 代理服务器地址，支持多个（逗号分隔）和账密认证，格式：`http://user:pass@proxy:port` 🌐 |
| `DATA_PATH` | `/app/data`        | 数据存储目录路径 📂                                     |
| `DATE_RANGE_DAYS` | `730`              | 仓库年龄过滤（天数），只扫描指定天数内的仓库 📅                       |
| `QUERIES_FILE` | `queries.txt`      | 搜索查询配置文件路径（表达式严重影响搜索的高效性) 🎯                    |
| `HAJIMI_CHECK_MODEL` | `gemini-2.5-flash` | 用于验证key有效的模型 🤖                                 |
| `GEMINI_BALANCER_SYNC_ENABLED` | `false` | 是否启用Gemini Balancer同步 🔗                        |
| `GEMINI_BALANCER_URL` | 空 | Gemini Balancer服务地址（http://your-gemini-balancer.com） 🌐 |
| `GEMINI_BALANCER_AUTH` | 空 | Gemini Balancer认证信息(密码） 🔐                      |
| `GPT_LOAD_SYNC_ENABLED` | `false` | 是否启用GPT-load同步 🔗                      |
| `GPT_LOAD_URL` | 空 | GPT Load 服务地址（http://your-gpt-load.com） 🌐      |
| `GPT_LOAD_AUTH` | 空 | GPT Load 认证Token（页面密码） 🔐                       |
| `GPT_LOAD_GROUP_NAME` | 空 | GPT Load 组名，多个用逗号分隔（group1,group2） 👥           |
| `GPT_LOAD_PAID_SYNC_ENABLED` | `false` | 是否将付费密钥上传到独立分组 💎                         |
| `GPT_LOAD_PAID_GROUP_NAME` | 空 | GPT Load 付费密钥的独立分组名（如：paid_group） 💎          |
| `RATE_LIMITED_HANDLING` | `save_only` | 429密钥处理策略：`discard`/`save_only`/`sync`/`sync_separate` ⏰ |
| `GPT_LOAD_RATE_LIMITED_GROUP_NAME` | 空 | 429密钥独立分组名（当`RATE_LIMITED_HANDLING=sync_separate`时使用） ⏰ |

#### 💡 关于 `RATE_LIMITED_HANDLING` 配置说明

此配置用于控制429限速密钥的处理策略，提供4种选项：

- **`discard`**：丢弃，视为无效密钥，不做任何保存或同步
- **`save_only`**（默认）：仅保存到本地专用文件（`key_429_*.txt`），不同步到外部系统
- **`sync`**：视为正常密钥，与有效密钥一起同步到正常分组
- **`sync_separate`**：同步到独立的429专用分组（需配置`GPT_LOAD_RATE_LIMITED_GROUP_NAME`）

### 🟢 可选配置（不懂就别动）😅

| 变量名                              | 默认值                                        | 说明 |
|----------------------------------|----------------------------------------------|------|
| `HAJIMI_PAID_MODEL`              | `gemini-2.5-pro-preview-03-25`       | 用于验证付费密钥的模型 💎 |
| `VALID_KEY_PREFIX`               | `keys/keys_valid_`                           | 有效密钥文件名前缀 🗝️ |
| `RATE_LIMITED_KEY_PREFIX`        | `keys/key_429_`                              | 频率限制密钥文件名前缀 ⏰ |
| `KEYS_SEND_PREFIX`               | `keys/keys_send_`                            | 发送到外部应用的密钥文件名前缀 🚀 |
| `PAID_KEY_PREFIX`                | `keys/keys_paid_`                            | 付费密钥文件名前缀 💎 |
| `VALID_KEY_DETAIL_PREFIX`        | `logs/keys_valid_detail_`                    | 有效密钥详细日志文件名前缀 📝 |
| `RATE_LIMITED_KEY_DETAIL_PREFIX` | `logs/key_429_detail_`                       | 频率限制详细日志文件名前缀 📊 |
| `KEYS_SEND_DETAIL_PREFIX`        | `logs/keys_send_detail_`                     | 发送密钥详细日志文件名前缀 🚀 |
| `PAID_KEY_DETAIL_PREFIX`         | `logs/keys_paid_detail_`                     | 付费密钥详细日志文件名前缀 💎 |
| `SCANNED_SHAS_FILE`              | `scanned_shas.txt`                           | 已扫描文件SHA记录文件名 📋 |
| `FILE_PATH_BLACKLIST`            | `readme,docs,doc/,.md,example,...`           | 文件路径黑名单，逗号分隔 🚫 |
| `LANGUAGE`                       | `zh_cn`                                      | 语言配置（zh_cn=简体中文, en=英文） 🌐 |

### 配置文件示例 💫

完整的 `.env` 文件示例：

```bash
# 必填配置
GITHUB_TOKENS=ghp_your_token_here_1,ghp_your_token_here_2

# 重要配置（可选修改）
DATA_PATH=/app/data
DATE_RANGE_DAYS=730
QUERIES_FILE=queries.txt
HAJIMI_CHECK_MODEL=gemini-2.5-flash
PROXY=

# Gemini Balancer同步配置
GEMINI_BALANCER_SYNC_ENABLED=false
GEMINI_BALANCER_URL=
GEMINI_BALANCER_AUTH=

# GPT-load同步配置
GPT_LOAD_SYNC_ENABLED=false
GPT_LOAD_URL=
GPT_LOAD_AUTH=
GPT_LOAD_GROUP_NAME=group1,group2,group3

# GPT-load - 付费密钥配置
GPT_LOAD_PAID_SYNC_ENABLED=false
GPT_LOAD_PAID_GROUP_NAME=paid_group

# 429限速密钥处理策略
RATE_LIMITED_HANDLING=save_only
GPT_LOAD_RATE_LIMITED_GROUP_NAME=rate_limited_group

# 高级配置（建议保持默认）
HAJIMI_PAID_MODEL=gemini-2.0-flash-thinking-exp-01-21
VALID_KEY_PREFIX=keys/keys_valid_
RATE_LIMITED_KEY_PREFIX=keys/key_429_
KEYS_SEND_PREFIX=keys/keys_send_
PAID_KEY_PREFIX=keys/keys_paid_
VALID_KEY_DETAIL_PREFIX=logs/keys_valid_detail_
RATE_LIMITED_KEY_DETAIL_PREFIX=logs/key_429_detail_
KEYS_SEND_DETAIL_PREFIX=logs/keys_send_detail_
PAID_KEY_DETAIL_PREFIX=logs/keys_paid_detail_
SCANNED_SHAS_FILE=scanned_shas.txt
FILE_PATH_BLACKLIST=readme,docs,doc/,.md,example,sample,tutorial,test,spec,demo,mock
LANGUAGE=zh_cn
```

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

## 🔒 安全注意事项 🛡️

- ✅ GitHub Token权限最小化（只需`public_repo`读取权限）🔐
- ✅ 定期轮换GitHub Token 🔄
- ✅ 不要将真实的API密钥提交到版本控制 🙈
- ✅ 定期检查和清理发现的密钥文件 🧹

💖 **享受使用 Hajimi King 的快乐时光！** 🎉✨🎊

