import React, { useState, useEffect } from 'react'
import { Card, Row, Col, Select, message, Spin } from 'antd'
import { LineChart, Line, PieChart, Pie, Cell, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import api from '../services/api'

const { Option } = Select

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8', '#82CA9D']

function Analytics() {
  const [trendData, setTrendData] = useState([])
  const [loading, setLoading] = useState(true)
  const [days, setDays] = useState(30)

  useEffect(() => {
    loadData()
  }, [days])

  const loadData = async () => {
    setLoading(true)
    try {
      const trend = await api.getAnalyticsTrend(days)
      setTrendData(trend.data)
      setLoading(false)
    } catch (error) {
      message.error('加载统计数据失败')
      setLoading(false)
    }
  }

  // 准备类型分布数据
  const typeDistribution = trendData.length > 0 ? [
    { name: '有效', value: trendData.reduce((sum, item) => sum + item.valid, 0) },
    { name: '限流', value: trendData.reduce((sum, item) => sum + item.rate_limited, 0) },
    { name: '付费', value: trendData.reduce((sum, item) => sum + item.paid, 0) }
  ] : []

  if (loading) {
    return <div style={{ textAlign: 'center', padding: 100 }}><Spin size="large" /></div>
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>📈 统计分析</h2>

      <Card style={{ marginBottom: 24 }}>
        <div style={{ marginBottom: 16 }}>
          <span style={{ marginRight: 8 }}>时间范围：</span>
          <Select value={days} onChange={setDays} style={{ width: 150 }}>
            <Option value={7}>最近 7 天</Option>
            <Option value={14}>最近 14 天</Option>
            <Option value={30}>最近 30 天</Option>
            <Option value={60}>最近 60 天</Option>
            <Option value={90}>最近 90 天</Option>
          </Select>
        </div>
      </Card>

      {/* 趋势图 */}
      <Card title="📊 密钥获取趋势" style={{ marginBottom: 24 }}>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="total" stroke="#1890ff" name="总数" />
            <Line type="monotone" dataKey="valid" stroke="#52c41a" name="有效" />
            <Line type="monotone" dataKey="rate_limited" stroke="#fa8c16" name="限流" />
            <Line type="monotone" dataKey="paid" stroke="#722ed1" name="付费" />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* 类型分布 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={{ span: 12, offset: 6 }}>
          <Card title="🎯 密钥类型分布">
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={typeDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={120}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {typeDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Analytics

