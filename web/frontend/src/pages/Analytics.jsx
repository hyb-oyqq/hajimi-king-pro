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
    <div style={{ animation: 'fadeIn 0.6s ease-out' }}>
      <h2 style={{ marginBottom: 24, fontSize: 32 }}>📈 统计分析</h2>

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
      <Card 
        title="📊 密钥获取趋势" 
        style={{ 
          marginBottom: 24,
          animationDelay: '0.2s'
        }}
      >
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={trendData}>
            <defs>
              <linearGradient id="colorTotal" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#1890ff" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#1890ff" stopOpacity={0}/>
              </linearGradient>
              <linearGradient id="colorValid" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#52c41a" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#52c41a" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
            <XAxis dataKey="date" stroke="#888" />
            <YAxis stroke="#888" />
            <Tooltip 
              contentStyle={{ 
                background: 'rgba(255, 255, 255, 0.95)', 
                border: '1px solid #e8e8e8',
                borderRadius: '8px',
                boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
              }} 
            />
            <Legend wrapperStyle={{ paddingTop: '20px' }} />
            <Line 
              type="monotone" 
              dataKey="total" 
              stroke="#1890ff" 
              name="总数" 
              strokeWidth={3}
              dot={{ r: 4, fill: '#1890ff' }}
              activeDot={{ r: 6, fill: '#1890ff' }}
            />
            <Line 
              type="monotone" 
              dataKey="valid" 
              stroke="#52c41a" 
              name="有效" 
              strokeWidth={3}
              dot={{ r: 4, fill: '#52c41a' }}
              activeDot={{ r: 6, fill: '#52c41a' }}
            />
            <Line 
              type="monotone" 
              dataKey="rate_limited" 
              stroke="#fa8c16" 
              name="限流" 
              strokeWidth={3}
              dot={{ r: 4, fill: '#fa8c16' }}
              activeDot={{ r: 6, fill: '#fa8c16' }}
            />
            <Line 
              type="monotone" 
              dataKey="paid" 
              stroke="#722ed1" 
              name="付费" 
              strokeWidth={3}
              dot={{ r: 4, fill: '#722ed1' }}
              activeDot={{ r: 6, fill: '#722ed1' }}
            />
          </LineChart>
        </ResponsiveContainer>
      </Card>

      {/* 类型分布 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} lg={{ span: 12, offset: 6 }}>
          <Card 
            title="🎯 密钥类型分布"
            style={{
              animationDelay: '0.3s'
            }}
          >
            <ResponsiveContainer width="100%" height={400}>
              <PieChart>
                <Pie
                  data={typeDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={130}
                  innerRadius={60}
                  fill="#8884d8"
                  dataKey="value"
                  paddingAngle={5}
                >
                  {typeDistribution.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={COLORS[index % COLORS.length]}
                      style={{ filter: 'drop-shadow(0 2px 4px rgba(0, 0, 0, 0.1))' }}
                    />
                  ))}
                </Pie>
                <Tooltip 
                  contentStyle={{ 
                    background: 'rgba(255, 255, 255, 0.95)', 
                    border: '1px solid #e8e8e8',
                    borderRadius: '8px',
                    boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)'
                  }} 
                />
              </PieChart>
            </ResponsiveContainer>
          </Card>
        </Col>
      </Row>
    </div>
  )
}

export default Analytics

