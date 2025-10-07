import React, { useState } from 'react'
import { Card, Input, Button, Form, message } from 'antd'
import { LockOutlined } from '@ant-design/icons'

function Login({ onLogin }) {
  const [loading, setLoading] = useState(false)

  const handleSubmit = (values) => {
    setLoading(true)
    // 简单验证，实际验证由API完成
    setTimeout(() => {
      onLogin(values.authKey)
      setLoading(false)
    }, 500)
  }

  return (
    <div style={{
      height: '100vh',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card 
        style={{ width: 400, boxShadow: '0 8px 32px rgba(0,0,0,0.1)' }}
        title={
          <div style={{ textAlign: 'center', fontSize: 24, fontWeight: 'bold' }}>
            🔑 Hajimi King Pro
          </div>
        }
      >
        <Form onFinish={handleSubmit} layout="vertical">
          <Form.Item
            name="authKey"
            rules={[{ required: true, message: '请输入认证密钥' }]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入认证密钥 (WEB_AUTH_KEY)"
              size="large"
            />
          </Form.Item>
          <Form.Item>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              size="large"
              loading={loading}
            >
              登录
            </Button>
          </Form.Item>
        </Form>
        <div style={{ textAlign: 'center', color: '#888', fontSize: 12 }}>
          密钥在 .env 文件的 WEB_AUTH_KEY 中配置
        </div>
      </Card>
    </div>
  )
}

export default Login

