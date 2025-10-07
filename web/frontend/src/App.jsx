import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { ConfigProvider, theme, Layout, Menu, message, Drawer } from 'antd'
import {
  DashboardOutlined,
  KeyOutlined,
  BarChartOutlined,
  FileTextOutlined,
  EditOutlined,
  SettingOutlined,
  MenuOutlined
} from '@ant-design/icons'
import Dashboard from './pages/Dashboard'
import Keys from './pages/Keys'
import Analytics from './pages/Analytics'
import Logs from './pages/Logs'
import Rules from './pages/Rules'
import Settings from './pages/Settings'
import Login from './pages/Login'
import api from './services/api'
import './App.css'

const { Header, Sider, Content } = Layout

function AppContent() {
  const navigate = useNavigate()
  const location = useLocation()
  const [authKey, setAuthKey] = useState(localStorage.getItem('authKey') || '')
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [darkMode, setDarkMode] = useState(false)
  const [mobileMenuVisible, setMobileMenuVisible] = useState(false)
  
  // 从当前路由获取selectedKey
  const getSelectedKey = () => {
    const path = location.pathname.split('/')[1] || 'dashboard'
    return path
  }
  
  const [selectedKey, setSelectedKey] = useState(getSelectedKey())

  useEffect(() => {
    // 检查认证
    if (authKey) {
      api.setAuthKey(authKey)
      checkAuth()
    }
  }, [authKey])

  useEffect(() => {
    // 路由变化时更新selectedKey
    setSelectedKey(getSelectedKey())
  }, [location])

  const checkAuth = async () => {
    try {
      await api.getSystemStatus()
      setIsAuthenticated(true)
    } catch (error) {
      if (error.response?.status === 401) {
        setIsAuthenticated(false)
        localStorage.removeItem('authKey')
        setAuthKey('')
        message.error('认证失败，请重新登录')
      }
    }
  }

  const handleLogin = (key) => {
    setAuthKey(key)
    localStorage.setItem('authKey', key)
    api.setAuthKey(key)
    setIsAuthenticated(true)
  }

  const handleLogout = () => {
    setAuthKey('')
    setIsAuthenticated(false)
    localStorage.removeItem('authKey')
    message.success('已退出登录')
  }

  const menuItems = [
    {
      key: 'dashboard',
      icon: <DashboardOutlined />,
      label: '仪表盘'
    },
    {
      key: 'keys',
      icon: <KeyOutlined />,
      label: '密钥管理'
    },
    {
      key: 'analytics',
      icon: <BarChartOutlined />,
      label: '统计分析'
    },
    {
      key: 'logs',
      icon: <FileTextOutlined />,
      label: '日志'
    },
    {
      key: 'rules',
      icon: <EditOutlined />,
      label: '规则编辑'
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '设置'
    }
  ]

  const handleMenuClick = ({ key }) => {
    setSelectedKey(key)
    navigate(`/${key}`)
    setMobileMenuVisible(false) // 移动端点击后关闭菜单
  }

  if (!isAuthenticated) {
    return (
      <ConfigProvider
        theme={{
          algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm
        }}
      >
        <Login onLogin={handleLogin} />
      </ConfigProvider>
    )
  }

  return (
    <ConfigProvider
      theme={{
        algorithm: darkMode ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff'
        }
      }}
    >
      <Layout style={{ minHeight: '100vh' }}>
        {/* 桌面端侧边栏 */}
        <Sider 
          theme={darkMode ? 'dark' : 'light'} 
          breakpoint="lg" 
          collapsedWidth="0"
          className="desktop-sider"
        >
          <div style={{ 
            height: 64, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            fontSize: 20,
            fontWeight: 'bold',
            color: darkMode ? '#fff' : '#1890ff'
          }}>
            Hajimi King Pro
          </div>
          <Menu
            theme={darkMode ? 'dark' : 'light'}
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={handleMenuClick}
          />
        </Sider>

        {/* 移动端抽屉菜单 */}
        <Drawer
          placement="left"
          onClose={() => setMobileMenuVisible(false)}
          open={mobileMenuVisible}
          className="mobile-drawer"
          styles={{ body: { padding: 0 } }}
          width={250}
        >
          <div style={{ 
            height: 64, 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center',
            fontSize: 20,
            fontWeight: 'bold',
            color: darkMode ? '#fff' : '#1890ff',
            borderBottom: darkMode ? '1px solid #303030' : '1px solid #f0f0f0'
          }}>
            Hajimi King Pro
          </div>
          <Menu
            theme={darkMode ? 'dark' : 'light'}
            mode="inline"
            selectedKeys={[selectedKey]}
            items={menuItems}
            onClick={handleMenuClick}
            style={{ border: 'none' }}
          />
        </Drawer>

        <Layout>
          <Header style={{ 
            padding: '0 16px', 
            background: darkMode ? '#001529' : '#fff',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: darkMode ? '1px solid #303030' : '1px solid #f0f0f0'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {/* 移动端菜单按钮 */}
              <MenuOutlined 
                className="mobile-menu-button"
                onClick={() => setMobileMenuVisible(true)}
                style={{ fontSize: 20, cursor: 'pointer' }}
              />
              <div style={{ fontSize: 18, fontWeight: 500 }}>
                密钥管理系统
              </div>
            </div>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <a 
                onClick={() => setDarkMode(!darkMode)}
                style={{ cursor: 'pointer', whiteSpace: 'nowrap' }}
              >
                {darkMode ? '🌞 浅色' : '🌙 深色'}
              </a>
              <a onClick={handleLogout} style={{ cursor: 'pointer', whiteSpace: 'nowrap' }}>
                退出
              </a>
            </div>
          </Header>
          <Content style={{ margin: '16px', padding: 16, minHeight: 280 }}>
            <Routes>
              <Route path="/" element={<Navigate to="/dashboard" replace />} />
              <Route path="/dashboard" element={<Dashboard />} />
              <Route path="/keys" element={<Keys />} />
              <Route path="/analytics" element={<Analytics />} />
              <Route path="/logs" element={<Logs />} />
              <Route path="/rules" element={<Rules />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </ConfigProvider>
  )
}

function App() {
  return (
    <Router>
      <AppContent />
    </Router>
  )
}

export default App

