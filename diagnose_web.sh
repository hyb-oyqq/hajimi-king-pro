#!/bin/bash
# Web 面板诊断脚本

echo "========================================"
echo "Hajimi King Web 面板诊断工具"
echo "========================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 获取服务器 IP
SERVER_IP=${1:-localhost}
WEB_PORT=${2:-5000}

echo "📋 诊断信息:"
echo "  服务器: $SERVER_IP"
echo "  端口: $WEB_PORT"
echo ""

# 1. 检查容器状态
echo "1️⃣  检查容器状态..."
if command -v docker &> /dev/null; then
    CONTAINER=$(docker ps --filter "name=hajimi-king" --format "{{.Names}}" | head -n 1)
    if [ -z "$CONTAINER" ]; then
        echo -e "${RED}❌ 未找到运行中的容器${NC}"
        echo "   提示: 运行 'docker-compose up -d' 启动服务"
        exit 1
    else
        echo -e "${GREEN}✅ 容器运行中: $CONTAINER${NC}"
        
        # 检查容器健康状态
        STATUS=$(docker inspect --format='{{.State.Status}}' $CONTAINER)
        echo "   状态: $STATUS"
    fi
else
    echo -e "${YELLOW}⚠️  未安装 docker 命令，跳过容器检查${NC}"
fi
echo ""

# 2. 检查端口监听
echo "2️⃣  检查端口监听..."
if command -v netstat &> /dev/null; then
    if netstat -tunlp 2>/dev/null | grep -q ":$WEB_PORT "; then
        echo -e "${GREEN}✅ 端口 $WEB_PORT 正在监听${NC}"
    else
        echo -e "${RED}❌ 端口 $WEB_PORT 未监听${NC}"
    fi
elif command -v ss &> /dev/null; then
    if ss -tunlp 2>/dev/null | grep -q ":$WEB_PORT "; then
        echo -e "${GREEN}✅ 端口 $WEB_PORT 正在监听${NC}"
    else
        echo -e "${RED}❌ 端口 $WEB_PORT 未监听${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  无法检查端口状态（需要 netstat 或 ss 命令）${NC}"
fi
echo ""

# 3. 健康检查
echo "3️⃣  健康检查..."
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:$WEB_PORT/health 2>/dev/null)
    
    if [ "$HTTP_CODE" = "200" ]; then
        HEALTH_RESPONSE=$(curl -s http://$SERVER_IP:$WEB_PORT/health 2>/dev/null)
        echo -e "${GREEN}✅ 健康检查通过 (HTTP $HTTP_CODE)${NC}"
        echo "   响应: $HEALTH_RESPONSE"
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "${RED}❌ 无法连接到服务${NC}"
        echo "   可能原因:"
        echo "   - 服务未启动"
        echo "   - 防火墙阻止了端口 $WEB_PORT"
        echo "   - IP 地址 $SERVER_IP 不正确"
    else
        echo -e "${RED}❌ 健康检查失败 (HTTP $HTTP_CODE)${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未安装 curl，跳过健康检查${NC}"
    echo "   手动测试: wget -O- http://$SERVER_IP:$WEB_PORT/health"
fi
echo ""

# 4. 检查首页访问
echo "4️⃣  检查 Web 面板首页..."
if command -v curl &> /dev/null; then
    HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://$SERVER_IP:$WEB_PORT/ 2>/dev/null)
    
    if [ "$HTTP_CODE" = "200" ]; then
        echo -e "${GREEN}✅ Web 面板可访问 (HTTP $HTTP_CODE)${NC}"
        echo "   访问地址: http://$SERVER_IP:$WEB_PORT"
    elif [ "$HTTP_CODE" = "503" ]; then
        echo -e "${RED}❌ 服务不可用 (HTTP 503)${NC}"
        echo "   可能原因:"
        echo "   - Gunicorn workers 启动失败"
        echo "   - 应用初始化错误"
        echo "   - 查看容器日志: docker-compose logs -f"
    elif [ "$HTTP_CODE" = "000" ]; then
        echo -e "${RED}❌ 无法连接${NC}"
    else
        echo -e "${YELLOW}⚠️  意外的响应码: HTTP $HTTP_CODE${NC}"
    fi
fi
echo ""

# 5. 检查 Gunicorn 进程
echo "5️⃣  检查 Gunicorn 进程..."
if [ ! -z "$CONTAINER" ]; then
    GUNICORN_COUNT=$(docker exec $CONTAINER ps aux 2>/dev/null | grep -c "[g]unicorn" || echo "0")
    if [ "$GUNICORN_COUNT" -gt "0" ]; then
        echo -e "${GREEN}✅ 找到 $GUNICORN_COUNT 个 Gunicorn 进程${NC}"
        docker exec $CONTAINER ps aux 2>/dev/null | grep "[g]unicorn" | head -n 5
    else
        echo -e "${RED}❌ 未找到 Gunicorn 进程${NC}"
        echo "   可能使用 Flask 开发服务器"
    fi
fi
echo ""

# 6. 查看最近的日志
echo "6️⃣  最近的容器日志（最后 20 行）..."
if [ ! -z "$CONTAINER" ]; then
    echo "----------------------------------------"
    docker logs --tail 20 $CONTAINER 2>&1
    echo "----------------------------------------"
fi
echo ""

# 总结
echo "========================================"
echo "📊 诊断完成"
echo "========================================"
echo ""
echo "💡 下一步建议:"
echo ""

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Web 面板运行正常！${NC}"
    echo "   在浏览器访问: http://$SERVER_IP:$WEB_PORT"
elif [ "$HTTP_CODE" = "503" ]; then
    echo -e "${RED}🔧 需要修复 503 错误：${NC}"
    echo "   1. 查看详细日志: docker-compose logs -f"
    echo "   2. 重启服务: docker-compose restart"
    echo "   3. 如果问题持续，重新构建: docker-compose up -d --build"
    echo "   4. 参考文档: WEB面板503问题修复说明.md"
else
    echo -e "${YELLOW}⚠️  服务可能未正确启动${NC}"
    echo "   1. 启动服务: docker-compose up -d"
    echo "   2. 查看日志: docker-compose logs -f"
    echo "   3. 检查配置: cat .env | grep WEB"
fi
echo ""

