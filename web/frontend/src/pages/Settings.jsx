import React, { useState, useEffect } from 'react'
import { Card, Descriptions, Tag, Button, List, Space, message, Modal, Input, Popconfirm } from 'antd'
import { PlusOutlined, DeleteOutlined, ReloadOutlined } from '@ant-design/icons'
import api from '../services/api'

function Settings() {
  const [settings, setSettings] = useState({})
  const [tokens, setTokens] = useState([])
  const [sessions, setSessions] = useState([])
  const [loading, setLoading] = useState(true)
  const [isTokenModalVisible, setIsTokenModalVisible] = useState(false)
  const [isSessionModalVisible, setIsSessionModalVisible] = useState(false)
  const [newToken, setNewToken] = useState('')
  const [newSession, setNewSession] = useState('')

  useEffect(() => {
    loadData()
  }, [])

  const loadData = async () => {
    setLoading(true)
    try {
      const [settingsData, tokensData, sessionsData] = await Promise.all([
        api.getSettings(),
        api.getGithubTokens(),
        api.getGithubSessions()
      ])
      setSettings(settingsData)
      setTokens(tokensData.data)
      setSessions(sessionsData.data)
      setLoading(false)
    } catch (error) {
      message.error('加载设置失败')
      setLoading(false)
    }
  }

  const handleAddToken = async () => {
    if (!newToken.trim()) {
      message.warning('Token不能为空')
      return
    }
    
    try {
      await api.addGithubToken(newToken.trim())
      message.success('Token添加成功，请重启服务生效')
      setNewToken('')
      setIsTokenModalVisible(false)
      loadData()
    } catch (error) {
      message.error(error.response?.data?.error || '添加Token失败')
    }
  }

  const handleDeleteToken = async (index) => {
    try {
      await api.deleteGithubToken(index)
      message.success('Token删除成功，请重启服务生效')
      loadData()
    } catch (error) {
      message.error('删除Token失败')
    }
  }

  const handleAddSession = async () => {
    if (!newSession.trim()) {
      message.warning('Session不能为空')
      return
    }
    
    try {
      await api.addGithubSession(newSession.trim())
      message.success('Session添加成功，请重启服务生效')
      setNewSession('')
      setIsSessionModalVisible(false)
      loadData()
    } catch (error) {
      message.error(error.response?.data?.error || '添加Session失败')
    }
  }

  const handleDeleteSession = async (index) => {
    try {
      await api.deleteGithubSession(index)
      message.success('Session删除成功，请重启服务生效')
      loadData()
    } catch (error) {
      message.error('删除Session失败')
    }
  }

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>⚙️ 系统设置</h2>
      
      {/* 系统配置 */}
      <Card title="🔧 基础配置" style={{ marginBottom: 24 }} loading={loading}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="认证模式">
            <Tag color={settings.github_auth_mode === 'token' ? 'blue' : 'green'}>
              {settings.github_auth_mode === 'token' ? 'Token 模式' : 'Web 模式'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="存储类型">
            <Tag color="purple">{settings.storage_type?.toUpperCase()}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="数据库类型">
            <Tag>{settings.db_type?.toUpperCase()}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="日期范围">
            {settings.date_range_days} 天
          </Descriptions.Item>
          <Descriptions.Item label="语言">
            {settings.language}
          </Descriptions.Item>
          <Descriptions.Item label="代理数量">
            {settings.proxy_count} 个
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* Gemini模型配置 */}
      <Card title="🤖 Gemini模型配置" style={{ marginBottom: 24 }} loading={loading}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="基础验证模型">
            <Tag color="blue">{settings.hajimi_check_model}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="付费验证模型">
            <Tag color="purple">{settings.hajimi_paid_model}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="异步验证并发数">
            {settings.key_validator_max_workers} 个
          </Descriptions.Item>
          <Descriptions.Item label="429限速处理">
            <Tag>{settings.rate_limited_handling}</Tag>
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 同步配置 */}
      <Card title="🔄 同步配置" style={{ marginBottom: 24 }} loading={loading}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="Balancer同步">
            {settings.balancer_enabled ? 
              <Tag color="green">已启用</Tag> : 
              <Tag color="default">未启用</Tag>
            }
          </Descriptions.Item>
          <Descriptions.Item label="GPT-load同步">
            {settings.gpt_load_enabled ? 
              <Tag color="green">已启用</Tag> : 
              <Tag color="default">未启用</Tag>
            }
          </Descriptions.Item>
          {settings.gpt_load_enabled && (
            <>
              <Descriptions.Item label="GPT-load分组" span={2}>
                {settings.gpt_load_group_name || '未设置'}
              </Descriptions.Item>
            </>
          )}
          <Descriptions.Item label="GPT-load付费同步">
            {settings.gpt_load_paid_enabled ? 
              <Tag color="green">已启用</Tag> : 
              <Tag color="default">未启用</Tag>
            }
          </Descriptions.Item>
          {settings.gpt_load_paid_enabled && (
            <Descriptions.Item label="付费分组">
              {settings.gpt_load_paid_group_name || '未设置'}
            </Descriptions.Item>
          )}
          {settings.gpt_load_rate_limited_group_name && (
            <Descriptions.Item label="限速分组" span={2}>
              {settings.gpt_load_rate_limited_group_name}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      {/* 强制冷却配置 */}
      <Card title="⏰ 强制冷却配置" style={{ marginBottom: 24 }} loading={loading}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="强制冷却">
            {settings.forced_cooldown_enabled ? 
              <Tag color="orange">已启用</Tag> : 
              <Tag color="default">未启用</Tag>
            }
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            {settings.forced_cooldown_enabled ? '系统将在查询间隔进行冷却' : '关闭'}
          </Descriptions.Item>
          <Descriptions.Item label="每查询后冷却">
            {settings.forced_cooldown_hours_per_query || '0'} 小时
          </Descriptions.Item>
          <Descriptions.Item label="每轮后冷却">
            {settings.forced_cooldown_hours_per_loop || '0'} 小时
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* SHA清理配置 */}
      <Card title="🧹 SHA清理配置" style={{ marginBottom: 24 }} loading={loading}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="SHA清理">
            {settings.sha_cleanup_enabled ? 
              <Tag color="green">已启用</Tag> : 
              <Tag color="default">未启用</Tag>
            }
          </Descriptions.Item>
          <Descriptions.Item label="状态">
            {settings.sha_cleanup_enabled ? '自动清理过期SHA记录' : '关闭'}
          </Descriptions.Item>
          <Descriptions.Item label="清理天数">
            {settings.sha_cleanup_days} 天
          </Descriptions.Item>
          <Descriptions.Item label="清理间隔">
            每 {settings.sha_cleanup_interval_loops} 轮循环
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* GitHub Tokens */}
      <Card 
        title="🔑 GitHub Tokens" 
        style={{ marginBottom: 24 }}
        extra={
          <Space>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setIsTokenModalVisible(true)}
            >
              添加
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={loadData}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <div style={{ marginBottom: 16 }}>
          共 {tokens.length} 个 Token
        </div>
        <List
          loading={loading}
          dataSource={tokens}
          renderItem={(token) => (
            <List.Item
              actions={[
                <Popconfirm
                  title="确定要删除这个Token吗？"
                  description="删除后需要重启服务生效"
                  onConfirm={() => handleDeleteToken(token.index)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button 
                    type="link" 
                    danger 
                    icon={<DeleteOutlined />}
                  >
                    删除
                  </Button>
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                title={`Token ${token.index + 1}`}
                description={
                  <code style={{ fontSize: 12 }}>
                    {token.token}
                  </code>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      {/* GitHub Sessions */}
      <Card 
        title="🌐 GitHub Sessions" 
        style={{ marginBottom: 24 }}
        extra={
          <Space>
            <Button 
              type="primary" 
              icon={<PlusOutlined />}
              onClick={() => setIsSessionModalVisible(true)}
            >
              添加
            </Button>
            <Button 
              icon={<ReloadOutlined />}
              onClick={loadData}
            >
              刷新
            </Button>
          </Space>
        }
      >
        <div style={{ marginBottom: 16 }}>
          共 {sessions.length} 个 Session
        </div>
        <List
          loading={loading}
          dataSource={sessions}
          renderItem={(session) => (
            <List.Item
              actions={[
                <Popconfirm
                  title="确定要删除这个Session吗？"
                  description="删除后需要重启服务生效"
                  onConfirm={() => handleDeleteSession(session.index)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button 
                    type="link" 
                    danger 
                    icon={<DeleteOutlined />}
                  >
                    删除
                  </Button>
                </Popconfirm>
              ]}
            >
              <List.Item.Meta
                title={`Session ${session.index + 1}`}
                description={
                  <code style={{ fontSize: 12 }}>
                    {session.session}
                  </code>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      {/* Token Modal */}
      <Modal
        title="添加 GitHub Token"
        open={isTokenModalVisible}
        onOk={handleAddToken}
        onCancel={() => {
          setIsTokenModalVisible(false)
          setNewToken('')
        }}
        okText="添加"
        cancelText="取消"
      >
        <Input.TextArea
          rows={3}
          placeholder="请输入GitHub Token"
          value={newToken}
          onChange={(e) => setNewToken(e.target.value)}
        />
        <div style={{ marginTop: 8, color: '#888', fontSize: 12 }}>
          • 在 https://github.com/settings/tokens 创建Token<br/>
          • 需要 repo 和 read:user 权限<br/>
          • 添加后需要重启服务生效
        </div>
      </Modal>

      {/* Session Modal */}
      <Modal
        title="添加 GitHub Session"
        open={isSessionModalVisible}
        onOk={handleAddSession}
        onCancel={() => {
          setIsSessionModalVisible(false)
          setNewSession('')
        }}
        okText="添加"
        cancelText="取消"
      >
        <Input.TextArea
          rows={3}
          placeholder="请输入GitHub Session (user_session cookie)"
          value={newSession}
          onChange={(e) => setNewSession(e.target.value)}
        />
        <div style={{ marginTop: 8, color: '#888', fontSize: 12 }}>
          • 登录GitHub后，打开浏览器开发者工具<br/>
          • Application &gt; Cookies &gt; user_session<br/>
          • 复制cookie值并粘贴到这里<br/>
          • 添加后需要重启服务生效
        </div>
      </Modal>

      <Card title="💡 设置说明">
        <p>• 修改GitHub Tokens或Sessions后需要重启服务才能生效</p>
        <p>• 其他配置项请直接修改 .env 文件并重启服务</p>
        <p>• Token和Session信息部分隐藏，仅显示前后部分字符</p>
      </Card>
    </div>
  )
}

export default Settings

