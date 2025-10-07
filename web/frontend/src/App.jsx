import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate, useLocation } from 'react-router-dom'
import { ConfigProvider, theme, Layout, Menu, message, Drawer, Button } from 'antd'
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
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem('authKey'))
  const [authChecking, setAuthChecking] = useState(!!localStorage.getItem('authKey'))
  // 主题模式: 'light' | 'dark' | 'auto'
  const [themeMode, setThemeMode] = useState(localStorage.getItem('themeMode') || 'auto')
  const [systemDark, setSystemDark] = useState(false)
  const [mobileMenuVisible, setMobileMenuVisible] = useState(false)
  
  // 计算实际使用的深色模式
  const darkMode = themeMode === 'auto' ? systemDark : themeMode === 'dark'
  
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
    } else {
      setAuthChecking(false)
    }
  }, [authKey])

  useEffect(() => {
    // 路由变化时更新selectedKey
    setSelectedKey(getSelectedKey())
  }, [location])

  useEffect(() => {
    // 检测系统主题偏好
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)')
    setSystemDark(mediaQuery.matches)
    
    // 监听系统主题变化
    const handler = (e) => setSystemDark(e.matches)
    mediaQuery.addEventListener('change', handler)
    
    return () => mediaQuery.removeEventListener('change', handler)
  }, [])

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
    } finally {
      setAuthChecking(false)
    }
  }

  const handleLogin = (key) => {
    setAuthKey(key)
    localStorage.setItem('authKey', key)
    api.setAuthKey(key)
    setIsAuthenticated(true)
    // 登录成功后跳转到仪表盘
    navigate('/dashboard')
  }

  const handleLogout = () => {
    setAuthKey('')
    setIsAuthenticated(false)
    localStorage.removeItem('authKey')
    message.success('已退出登录')
    // 退出后跳转到根路径（会显示登录页）
    navigate('/')
  }

  const handleThemeChange = () => {
    const modes = ['light', 'dark', 'auto']
    const currentIndex = modes.indexOf(themeMode)
    const nextMode = modes[(currentIndex + 1) % modes.length]
    setThemeMode(nextMode)
    localStorage.setItem('themeMode', nextMode)
  }

  const getThemeIcon = () => {
    if (themeMode === 'light') return '🌞 浅色模式'
    if (themeMode === 'dark') return '🌙 深色模式'
    return '🌓 自动模式'
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

  // 正在检查认证状态时，显示空白页面避免闪烁
  if (authChecking) {
    return null
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
      <MainLayout 
        darkMode={darkMode}
        selectedKey={selectedKey}
        menuItems={menuItems}
        handleMenuClick={handleMenuClick}
        handleThemeChange={handleThemeChange}
        getThemeIcon={getThemeIcon}
        handleLogout={handleLogout}
        mobileMenuVisible={mobileMenuVisible}
        setMobileMenuVisible={setMobileMenuVisible}
      />
    </ConfigProvider>
  )
}

function MainLayout({ 
  darkMode, 
  selectedKey, 
  menuItems, 
  handleMenuClick,
  handleThemeChange,
  getThemeIcon,
  handleLogout,
  mobileMenuVisible,
  setMobileMenuVisible
}) {
  // 直接根据darkMode计算背景色，不依赖theme.useToken()
  const headerBg = darkMode ? '#141414' : '#ffffff'
  const contentBg = darkMode ? '#141414' : '#ffffff'
  
  // 调试：打印darkMode值
  console.log('MainLayout darkMode:', darkMode, 'headerBg:', headerBg, 'contentBg:', contentBg)
  
  return (
    <Layout style={{ minHeight: '100vh' }} className={darkMode ? 'dark-mode' : ''}>
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
            background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
            backgroundClip: 'text',
            padding: '0 16px'
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
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            borderBottom: darkMode ? '1px solid #303030' : '1px solid #f0f0f0',
            background: headerBg
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
              {/* 移动端菜单按钮 */}
              <MenuOutlined 
                className="mobile-menu-button"
                onClick={() => setMobileMenuVisible(true)}
                style={{ 
                  fontSize: 20, 
                  cursor: 'pointer',
                  color: darkMode ? '#fff' : '#667eea',
                  transition: 'all 0.3s ease'
                }}
              />
              <div style={{ 
                fontSize: 18, 
                fontWeight: 600,
                background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                管理面板
              </div>
            </div>
            <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
              <Button
                type="text"
                onClick={handleThemeChange}
                style={{ 
                  cursor: 'pointer', 
                  whiteSpace: 'nowrap',
                  borderRadius: '6px',
                  transition: 'all 0.3s ease',
                  fontWeight: 500
                }}
                title={`当前: ${getThemeIcon()} (点击切换)`}
              >
                {getThemeIcon()}
              </Button>
              <Button
                type="primary"
                onClick={handleLogout}
                style={{ 
                  cursor: 'pointer', 
                  whiteSpace: 'nowrap',
                  borderRadius: '6px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  border: 'none',
                  boxShadow: '0 2px 8px rgba(102, 126, 234, 0.3)'
                }}
              >
                退出登录
              </Button>
            </div>
          </Header>
          <Content style={{ 
            margin: '24px', 
            padding: 24, 
            minHeight: 280,
            borderRadius: '12px',
            background: contentBg
          }}>
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

