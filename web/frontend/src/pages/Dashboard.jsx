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
    <div style={{ animation: 'fadeIn 0.6s ease-out' }}>
      <h2 style={{ marginBottom: 24, fontSize: 32 }}>📊 仪表盘</h2>
      
      {/* 总体统计 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card" style={{ 
            animationDelay: '0.1s',
            borderTop: '4px solid #1890ff'
          }}>
            <Statistic
              title="密钥总数"
              value={stats?.total?.count || 0}
              prefix={<KeyOutlined style={{ fontSize: 24 }} />}
              valueStyle={{ color: '#1890ff', fontWeight: 'bold', fontSize: 32 }}
            />
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较昨日: {renderChangeBadge(stats?.total?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较上周: {renderChangeBadge(stats?.total?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.total?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card" style={{ 
            animationDelay: '0.2s',
            borderTop: '4px solid #52c41a'
          }}>
            <Statistic
              title="有效密钥"
              value={stats?.valid?.count || 0}
              prefix={<CheckCircleOutlined style={{ fontSize: 24 }} />}
              valueStyle={{ color: '#52c41a', fontWeight: 'bold', fontSize: 32 }}
            />
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较昨日: {renderChangeBadge(stats?.valid?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较上周: {renderChangeBadge(stats?.valid?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.valid?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card" style={{ 
            animationDelay: '0.3s',
            borderTop: '4px solid #fa8c16'
          }}>
            <Statistic
              title="限流密钥"
              value={stats?.rate_limited?.count || 0}
              prefix={<ClockCircleOutlined style={{ fontSize: 24 }} />}
              valueStyle={{ color: '#fa8c16', fontWeight: 'bold', fontSize: 32 }}
            />
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较昨日: {renderChangeBadge(stats?.rate_limited?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较上周: {renderChangeBadge(stats?.rate_limited?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.rate_limited?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card className="stat-card" style={{ 
            animationDelay: '0.4s',
            borderTop: '4px solid #722ed1'
          }}>
            <Statistic
              title="付费密钥"
              value={stats?.paid?.count || 0}
              prefix={<CrownOutlined style={{ fontSize: 24 }} />}
              valueStyle={{ color: '#722ed1', fontWeight: 'bold', fontSize: 32 }}
            />
            <div style={{ marginTop: 12 }}>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较昨日: {renderChangeBadge(stats?.paid?.yesterday_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary, marginBottom: 4 }}>相较上周: {renderChangeBadge(stats?.paid?.last_week_change || 0)}</div>
              <div style={{ fontSize: 12, color: token.colorTextSecondary }}>相较上月: {renderChangeBadge(stats?.paid?.last_month_change || 0)}</div>
            </div>
          </Card>
        </Col>
      </Row>

      {/* 今日统计 */}
      <Card 
        title="📅 今日统计" 
        style={{ 
          marginBottom: 24,
          animationDelay: '0.5s'
        }}
      >
        <Row gutter={[16, 16]}>
          <Col xs={12} sm={6}>
            <div style={{ 
              padding: '16px', 
              borderRadius: '8px', 
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              background: token.colorBgContainer,
              border: `1px solid ${token.colorBorder}`
            }}>
              <Statistic
                title="今日总数"
                value={stats?.today?.total || 0}
                valueStyle={{ color: '#1890ff', fontWeight: 'bold', fontSize: 24 }}
              />
            </div>
          </Col>
          <Col xs={12} sm={6}>
            <div style={{ 
              padding: '16px', 
              borderRadius: '8px', 
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              background: token.colorBgContainer,
              border: `1px solid ${token.colorBorder}`
            }}>
              <Statistic
                title="今日有效"
                value={stats?.today?.valid || 0}
                valueStyle={{ color: '#52c41a', fontWeight: 'bold', fontSize: 24 }}
              />
            </div>
          </Col>
          <Col xs={12} sm={6}>
            <div style={{ 
              padding: '16px', 
              borderRadius: '8px', 
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              background: token.colorBgContainer,
              border: `1px solid ${token.colorBorder}`
            }}>
              <Statistic
                title="今日限流"
                value={stats?.today?.rate_limited || 0}
                valueStyle={{ color: '#fa8c16', fontWeight: 'bold', fontSize: 24 }}
              />
            </div>
          </Col>
          <Col xs={12} sm={6}>
            <div style={{ 
              padding: '16px', 
              borderRadius: '8px', 
              transition: 'all 0.3s ease',
              cursor: 'pointer',
              background: token.colorBgContainer,
              border: `1px solid ${token.colorBorder}`
            }}>
              <Statistic
                title="今日付费"
                value={stats?.today?.paid || 0}
                valueStyle={{ color: '#722ed1', fontWeight: 'bold', fontSize: 24 }}
              />
            </div>
          </Col>
        </Row>
      </Card>
    </div>
  )
}

export default Dashboard

