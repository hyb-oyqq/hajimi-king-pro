import React, { useState } from 'react'
import { Card, Input, Button, Form, message } from 'antd'
import { LockOutlined, SafetyOutlined } from '@ant-design/icons'

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
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      position: 'relative',
      overflow: 'hidden'
    }}>
      {/* 背景动画元素 */}
      <div style={{
        position: 'absolute',
        width: '200%',
        height: '200%',
        background: 'radial-gradient(circle, rgba(255,255,255,0.1) 1px, transparent 1px)',
        backgroundSize: '50px 50px',
        animation: 'backgroundMove 20s linear infinite',
        opacity: 0.3
      }} />
      
      {/* 浮动圆形装饰 */}
      <div style={{
        position: 'absolute',
        top: '10%',
        left: '10%',
        width: '300px',
        height: '300px',
        borderRadius: '50%',
        background: 'rgba(255, 255, 255, 0.1)',
        animation: 'float 6s ease-in-out infinite',
        filter: 'blur(60px)'
      }} />
      
      <div style={{
        position: 'absolute',
        bottom: '10%',
        right: '10%',
        width: '400px',
        height: '400px',
        borderRadius: '50%',
        background: 'rgba(255, 255, 255, 0.1)',
        animation: 'float 8s ease-in-out infinite',
        animationDelay: '1s',
        filter: 'blur(80px)'
      }} />
      
      <Card 
        style={{ 
          width: 420, 
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          borderRadius: '16px',
          border: 'none',
          background: 'rgba(255, 255, 255, 0.95)',
          backdropFilter: 'blur(10px)',
          animation: 'cardSlideIn 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
          position: 'relative',
          zIndex: 1
        }}
        title={
          <div style={{ 
            textAlign: 'center', 
            padding: '20px 0 10px',
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            gap: '12px'
          }}>
            <div style={{
              width: '80px',
              height: '80px',
              borderRadius: '50%',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              animation: 'iconPulse 2s ease-in-out infinite',
              boxShadow: '0 8px 24px rgba(102, 126, 234, 0.4)'
            }}>
              <SafetyOutlined style={{ fontSize: 40, color: 'white' }} />
            </div>
            <div style={{ 
              fontSize: 28, 
              fontWeight: 'bold',
              background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundClip: 'text'
            }}>
              Hajimi King Pro
            </div>
            <div style={{
              fontSize: 14,
              color: '#888',
              fontWeight: 'normal'
            }}>
              管理面板
            </div>
          </div>
        }
      >
        <Form onFinish={handleSubmit} layout="vertical" style={{ padding: '10px 0' }}>
          <Form.Item
            name="authKey"
            rules={[{ required: true, message: '请输入认证密钥' }]}
            style={{ marginBottom: 24 }}
          >
            <Input.Password
              prefix={<LockOutlined style={{ color: '#667eea' }} />}
              placeholder="请输入认证密钥 (WEB_AUTH_KEY)"
              size="large"
              style={{
                borderRadius: '8px',
                padding: '12px 16px',
                fontSize: '15px',
                border: '2px solid #e8e8e8',
                transition: 'all 0.3s ease'
              }}
            />
          </Form.Item>
          <Form.Item style={{ marginBottom: 16 }}>
            <Button 
              type="primary" 
              htmlType="submit" 
              block 
              size="large"
              loading={loading}
              style={{
                height: '48px',
                fontSize: '16px',
                fontWeight: 'bold',
                borderRadius: '8px',
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                border: 'none',
                boxShadow: '0 4px 16px rgba(102, 126, 234, 0.4)',
                transition: 'all 0.3s ease'
              }}
            >
              {loading ? '登录中...' : '立即登录'}
            </Button>
          </Form.Item>
        </Form>
        <div style={{ 
          textAlign: 'center', 
          color: '#999', 
          fontSize: 13,
          padding: '16px 0 8px',
          borderTop: '1px solid #f0f0f0',
          marginTop: '8px'
        }}>
          <div style={{ marginBottom: '4px' }}>
            🔐 密钥在 .env 文件的 WEB_AUTH_KEY 中配置
          </div>
          <div style={{ fontSize: 12, color: '#bbb' }}>
            请妥善保管您的认证密钥
          </div>
        </div>
      </Card>
      
      <style>{`
        @keyframes cardSlideIn {
          from {
            opacity: 0;
            transform: translateY(50px) scale(0.9);
          }
          to {
            opacity: 1;
            transform: translateY(0) scale(1);
          }
        }
        
        @keyframes iconPulse {
          0%, 100% {
            transform: scale(1);
            box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
          }
          50% {
            transform: scale(1.05);
            box-shadow: 0 12px 32px rgba(102, 126, 234, 0.6);
          }
        }
        
        @keyframes float {
          0%, 100% {
            transform: translateY(0) translateX(0);
          }
          25% {
            transform: translateY(-20px) translateX(10px);
          }
          50% {
            transform: translateY(-10px) translateX(-10px);
          }
          75% {
            transform: translateY(-30px) translateX(5px);
          }
        }
        
        @keyframes backgroundMove {
          0% {
            transform: translate(0, 0);
          }
          100% {
            transform: translate(50px, 50px);
          }
        }
      `}</style>
    </div>
  )
}

export default Login

