#!/bin/bash

# Hajimi King Pro - Deployment Script
# 用于在外部目录独立部署hajimi-king-Pro项目

set -e  # 遇到错误时停止执行

# 颜色输出函数
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 项目配置
PROJECT_NAME="hajimi-king-pro"
IMAGE_TAG="0.0.1"
IMAGE_NAME="${PROJECT_NAME}:${IMAGE_TAG}"
COMPOSE_FILE="docker-compose.yml"

# 获取脚本所在目录
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
# hajimi-king-pro源码目录（脚本所在目录的hajimi-king-pro子目录）
SOURCE_DIR="${SCRIPT_DIR}/hajimi-king"

# 当前工作目录（部署目录）
DEPLOY_DIR="$(pwd)"

# 打印横幅
print_banner() {
    echo "=================================================="
    echo "🚀 HAJIMI KING Pro - DEPLOYMENT SCRIPT"
    echo "=================================================="
    echo "🏷️  Image: ${IMAGE_NAME}"
    echo "📁 Source: ${SOURCE_DIR}"
    echo "📁 Deploy: ${DEPLOY_DIR}"
    echo "=================================================="
}

# 检查源码目录
check_source_directory() {
    log_info "检查源码目录..."
    
    local required_files=("Dockerfile" "app/hajimi_king.py" "env.example" "queries.example")
    local missing_files=()
    
    for file in "${required_files[@]}"; do
        if [[ ! -f "${SOURCE_DIR}/$file" ]]; then
            missing_files+=("$file")
        fi
    done
    
    if [[ ${#missing_files[@]} -ne 0 ]]; then
        log_error "hajimi-king-pro源码目录缺少必要文件:"
        printf '%s\n' "${missing_files[@]}" | sed 's/^/  - /'
        log_error "请确保hajimi-king-pro源码目录存在且包含所有必要文件"
        log_error "预期源码路径: ${SOURCE_DIR}"
        exit 1
    fi
    
    log_success "源码目录检查通过"
}

# 检查Docker环境
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    if ! docker info &> /dev/null; then
        log_error "Docker守护进程未运行，请启动Docker"
        exit 1
    fi
    
    log_success "Docker环境检查通过"
}

# 创建部署目录结构
setup_deploy_directory() {
    log_info "设置部署目录结构..."
    
    # 1. 创建data文件夹（如果不存在）
    if [[ ! -d "${DEPLOY_DIR}/data" ]]; then
        mkdir -p "${DEPLOY_DIR}/data"
        log_success "创建data目录: ${DEPLOY_DIR}/data"
    else
        log_info "data目录已存在: ${DEPLOY_DIR}/data"
    fi
    
    # 2. 复制env.example到当前目录为.env（如果不存在）
    if [[ ! -f "${DEPLOY_DIR}/.env" ]]; then
        cp "${SOURCE_DIR}/env.example" "${DEPLOY_DIR}/.env"
        log_success "复制配置文件: .env"
    else
        log_info "配置文件已存在: .env"
    fi
    
    # 3. 复制queries.example到data/queries.txt（如果不存在）
    if [[ ! -f "${DEPLOY_DIR}/data/queries.txt" ]]; then
        cp "${SOURCE_DIR}/queries.example" "${DEPLOY_DIR}/data/queries.txt"
        log_success "复制查询文件: data/queries.txt"
    else
        log_info "查询文件已存在: data/queries.txt"
    fi
    
    # 5. 复制docker-compose文件到当前目录
    cp "${SOURCE_DIR}/docker-compose.yml" "${DEPLOY_DIR}/${COMPOSE_FILE}"
    log_success "复制Docker Compose配置: ${COMPOSE_FILE}"
}

# 检查并配置GitHub Token
configure_github_token() {
    log_info "检查GitHub Token配置..."
    
    local env_file="${DEPLOY_DIR}/.env"
    local github_tokens=$(grep "^GITHUB_TOKENS=" "$env_file" 2>/dev/null | cut -d'=' -f2- | tr -d '"' | tr -d "'" || echo "")
    
    # 检查是否包含实际的token（不是示例值）
    if [[ -z "$github_tokens" ]] || [[ "$github_tokens" == "ghp_your_token_here_1,ghp_your_token_here_2" ]] || [[ "$github_tokens" =~ ghp_your_token_here ]]; then
        log_warning "未检测到有效的GitHub Token"
        echo ""
        echo "请输入您的GitHub Personal Access Token(s):"
        echo "- 可以输入多个token，用逗号分隔"
        echo "- 创建token: https://github.com/settings/tokens"
        echo "- 需要 'public_repo' 权限"
        echo ""
        
        while true; do
            read -p "GitHub Token(s): " -r user_tokens
            
            if [[ -z "$user_tokens" ]]; then
                log_error "GitHub Token不能为空，请重新输入"
                continue
            fi
            
            # 简单验证token格式（以ghp_开头）
            if [[ ! "$user_tokens" =~ ^ghp_ ]]; then
                log_warning "Token格式可能不正确（应以ghp_开头），是否继续？(y/N)"
                read -p "" -r confirm
                if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
                    continue
                fi
            fi
            
            # 更新.env文件中的GITHUB_TOKENS
            if grep -q "^GITHUB_TOKENS=" "$env_file"; then
                # 使用sed替换现有行，处理特殊字符
                sed -i.bak "s|^GITHUB_TOKENS=.*|GITHUB_TOKENS=${user_tokens}|" "$env_file"
            else
                # 添加新行
                echo "GITHUB_TOKENS=${user_tokens}" >> "$env_file"
            fi
            
            log_success "GitHub Token已保存到.env文件"
            break
        done
    else
        # 显示现有token（部分遮挩）
        local masked_tokens=$(echo "$github_tokens" | sed 's/ghp_[a-zA-Z0-9]\{10,\}/ghp_*****/g')
        log_success "检测到现有GitHub Token: ${masked_tokens}"
        log_info "如需修改，请直接编辑 .env 文件"
    fi
}

# 构建Docker镜像
build_image() {
    log_info "在源码目录构建Docker镜像: ${IMAGE_NAME}"
    
    # 切换到源码目录进行构建
    cd "${SOURCE_DIR}"
    
    if docker build -t "${IMAGE_NAME}" .; then
        log_success "Docker镜像构建成功: ${IMAGE_NAME}"
    else
        log_error "Docker镜像构建失败"
        exit 1
    fi
    
    # 切换回部署目录
    cd "${DEPLOY_DIR}"
    
    # 显示镜像信息
    log_info "镜像信息:"
    docker images "${PROJECT_NAME}" | head -2
}

# 启动服务
start_services() {
    log_info "在部署目录启动Docker Compose服务..."
    
    # 确保在部署目录
    cd "${DEPLOY_DIR}"
    
    if docker-compose -f "$COMPOSE_FILE" up -d; then
        log_success "服务启动成功"
    else
        log_error "服务启动失败"
        exit 1
    fi
    
    # 等待容器启动
    sleep 3
    
    # 显示服务状态
    log_info "服务状态:"
    docker-compose -f "$COMPOSE_FILE" ps
}

# 停止并清理现有容器
cleanup_existing() {
    log_info "清理现有容器..."
    
    cd "${DEPLOY_DIR}"
    
    if [[ -f "$COMPOSE_FILE" ]] && docker-compose -f "$COMPOSE_FILE" ps -q 2>/dev/null | grep -q .; then
        log_warning "发现运行中的容器，正在停止..."
        docker-compose -f "$COMPOSE_FILE" down
        log_success "容器已停止"
    else
        log_info "没有发现运行中的容器"
    fi
}



# 主函数
main() {
    print_banner
    check_source_directory
    check_docker
    setup_deploy_directory
    configure_github_token
    cleanup_existing
    build_image
    start_services
    echo ""
    log_success "🎉 部署完成!"
    echo ""
    log_info "📁 部署文件位置:"
    echo "  配置文件: ${DEPLOY_DIR}/.env"
    echo "  数据目录: ${DEPLOY_DIR}/data"
    echo "  查询文件: ${DEPLOY_DIR}/data/queries.txt"
    echo ""
    log_info "💡 管理命令:"
    echo "  docker-compose logs -f     - 查看实时日志"
    echo "  docker-compose ps          - 查看服务状态"  
    echo "  docker-compose down        - 停止服务"
    echo "  docker-compose up -d       - 重启服务"
}

# 执行主函数
main 