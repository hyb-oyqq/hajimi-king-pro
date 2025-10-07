import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Statistic, Tag, Spin, message, theme } from 'antd'
import { 
  KeyOutlined, 
  CheckCircleOutlined, 
  ClockCircleOutlined, 
  CrownOutlined,
  ArrowUpOutlined,
  ArrowDownOutlined
} from '@ant-design/icons'
import api from '../services/api'

function Dashboard() {
  const { token } = theme.useToken()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
    // 每30秒刷新一次
    const interval = setInterval(loadStats, 30000)
    return () => clearInterval(interval)
  }, [])

  const loadStats = async () => {
    try {
      const data = await api.getDashboardStats()
      setStats(data)
      setLoading(false)
    } catch (error) {
      message.error('加载统计数据失败')
      setLoading(false)
    }
  }

  const renderChangeBadge = (change) => {
    if (change > 0) {
      return (
        <Tag color="success" icon={<ArrowUpOutlined />}>
          +{change}
        </Tag>
      )
    } else if (change < 0) {
      return (
        <Tag color="warning" icon={<ArrowDownOutlined />}>
          {change}
        </Tag>
      )
    }
    return <Tag>无变化</Tag>
  }

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>📊 仪表盘</h2>
      
      {/* 总体统计 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="密钥总数"
              value={stats?.total?.count || 0}
              prefix={<KeyOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较昨日: {renderChangeBadge(stats?.total?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上周: {renderChangeBadge(stats?.total?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.total?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="有效密钥"
              value={stats?.valid?.count || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较昨日: {renderChangeBadge(stats?.valid?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上周: {renderChangeBadge(stats?.valid?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.valid?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="限流密钥"
              value={stats?.rate_limited?.count || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较昨日: {renderChangeBadge(stats?.rate_limited?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上周: {renderChangeBadge(stats?.rate_limited?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.rate_limited?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card">
            <Statistic
              title="付费密钥"
              value={stats?.paid?.count || 0}
              prefix={<CrownOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
            <div style={{ marginTop: 8 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较昨日: {renderChangeBadge(stats?.paid?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上周: {renderChangeBadge(stats?.paid?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.paid?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 今日统计 */}
      <Card title="📅 今日统计" style={{ marginBottom: 24 }}>
        <Row gutter={[16, 16]}>
          <Col xs={12} sm={6}>
            <Statistic
              title="今日总数"
              value={stats?.today?.total || 0}
              valueStyle={{ color: '#1890ff' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="今日有效"
              value={stats?.today?.valid || 0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="今日限流"
              value={stats?.today?.rate_limited || 0}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Col>
          <Col xs={12} sm={6}>
            <Statistic
              title="今日付费"
              value={stats?.today?.paid || 0}
              valueStyle={{ color: '#722ed1' }}
            />
          </Col>
        </Row>
      </Card>

      <Card title="💡 系统提示">
        <p>• 数据每30秒自动刷新</p>
        <p>• 密钥数据来自数据库实时统计</p>
        <p>• 可在"密钥管理"页面查看详细信息</p>
      </Card>
    </div>
  )
}

export default Dashboard

