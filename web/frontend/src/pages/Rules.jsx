import React, { useState, useEffect } from 'react'
import { Card, Table, Input, Button, Space, message, Popconfirm, Modal, Tag, Tooltip, theme } from 'antd'
import { PlusOutlined, DeleteOutlined, ReloadOutlined, ThunderboltOutlined, SearchOutlined, CopyOutlined } from '@ant-design/icons'
import api from '../services/api'

function Rules() {
  const { token } = theme.useToken()
  const [rules, setRules] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchText, setSearchText] = useState('')
  const [isModalVisible, setIsModalVisible] = useState(false)
  const [newRule, setNewRule] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [pageSize, setPageSize] = useState(20)

  useEffect(() => {
    loadRules()
  }, [])

  const loadRules = async () => {
    setLoading(true)
    try {
      const data = await api.getRules()
      setRules(data.data || [])
      setLoading(false)
    } catch (error) {
      message.error('加载规则失败: ' + (error.response?.data?.error || error.message))
      setLoading(false)
    }
  }

  const handleAddRule = async () => {
    if (!newRule.trim()) {
      message.warning('规则不能为空')
      return
    }
    
    try {
      await api.addRule(newRule.trim())
      message.success('规则添加成功')
      setNewRule('')
      setIsModalVisible(false)
      loadRules()
    } catch (error) {
      message.error(error.response?.data?.error || '添加规则失败')
    }
  }

  const handleDeleteRule = async (originalIndex, rule) => {
    try {
      await api.deleteRule(originalIndex)
      message.success('规则删除成功')
      loadRules()
    } catch (error) {
      message.error('删除规则失败: ' + (error.response?.data?.error || error.message))
    }
  }

  const handleRestart = async () => {
    try {
      await api.restartSystem()
      message.success('重启信号已发送，系统将在完成当前任务后重启')
    } catch (error) {
      message.error('发送重启信号失败')
    }
  }

  const handleCopyRule = (rule) => {
    navigator.clipboard.writeText(rule)
    message.success('规则已复制到剪贴板')
  }

  // 准备表格数据，保留原始索引
  const dataSource = rules.map((rule, index) => ({
    key: index,
    originalIndex: index,
    ruleNumber: index + 1,
    content: rule
  }))

  // 过滤规则
  const filteredDataSource = searchText 
    ? dataSource.filter(item => 
        item.content.toLowerCase().includes(searchText.toLowerCase())
      )
    : dataSource

  // 表格列定义
  const columns = [
    {
      title: '序号',
      dataIndex: 'ruleNumber',
      key: 'ruleNumber',
      width: 80,
      align: 'center',
      render: (text) => <Tag color="blue">{text}</Tag>
    },
    {
      title: '规则内容',
      dataIndex: 'content',
      key: 'content',
      ellipsis: {
        showTitle: false
      },
      render: (text) => (
        <Tooltip placement="topLeft" title={text}>
          <code style={{ 
            fontSize: 13, 
            background: token.colorBgContainer, 
            border: `1px solid ${token.colorBorder}`,
            color: token.colorText,
            padding: '4px 8px',
            borderRadius: 4,
            display: 'block',
            whiteSpace: 'nowrap',
            overflow: 'hidden',
            textOverflow: 'ellipsis'
          }}>
            {text}
          </code>
        </Tooltip>
      )
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      align: 'center',
      render: (_, record) => (
        <Space>
          <Tooltip title="复制规则">
            <Button 
              type="text" 
              icon={<CopyOutlined />}
              size="small"
              onClick={() => handleCopyRule(record.content)}
            />
          </Tooltip>
          <Popconfirm
            title="确定要删除这条规则吗？"
            description={`规则 ${record.ruleNumber}: ${record.content.substring(0, 50)}...`}
            onConfirm={() => handleDeleteRule(record.originalIndex, record.content)}
            okText="确定"
            cancelText="取消"
          >
            <Button 
              type="text" 
              danger 
              icon={<DeleteOutlined />}
              size="small"
            >
              删除
            </Button>
          </Popconfirm>
        </Space>
      )
    }
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>📋 搜索规则管理</h2>
      
      <Card>
        <Space style={{ marginBottom: 16, width: '100%', justifyContent: 'space-between', flexWrap: 'wrap' }}>
          <Space wrap>
            <Button 
              type="primary" 
              icon={<PlusOutlined />} 
              onClick={() => setIsModalVisible(true)}
            >
              添加规则
            </Button>
            
            <Button 
              icon={<ReloadOutlined />} 
              onClick={loadRules}
              loading={loading}
            >
              刷新
            </Button>
            
            <Popconfirm
              title="确定要重启系统吗？"
              description="系统将在完成当前任务后重启，新增的规则将生效"
              onConfirm={handleRestart}
              okText="确定"
              cancelText="取消"
            >
              <Button 
                type="primary" 
                danger 
                icon={<ThunderboltOutlined />}
              >
                热重启
              </Button>
            </Popconfirm>
          </Space>
          
          <Input
            placeholder="搜索规则..."
            prefix={<SearchOutlined />}
            style={{ width: 300 }}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            allowClear
          />
        </Space>

        <div style={{ 
          background: token.colorBgLayout, 
          padding: 16, 
          borderRadius: 4, 
          marginBottom: 16,
          border: `1px solid ${token.colorBorder}`
        }}>
          <Space size="large">
            <div>
              <span style={{ fontWeight: 'bold', color: token.colorText }}>📊 规则总数：</span>
              <Tag color="blue">{rules.length}</Tag>
            </div>
            {searchText && (
              <div>
                <span style={{ fontWeight: 'bold', color: token.colorText }}>🔍 筛选结果：</span>
                <Tag color="green">{filteredDataSource.length}</Tag>
              </div>
            )}
            <div>
              <span style={{ fontWeight: 'bold', color: token.colorText }}>📄 当前页：</span>
              <Tag color="orange">{currentPage}/{Math.ceil(filteredDataSource.length / pageSize)}</Tag>
            </div>
          </Space>
        </div>

        <Table
          columns={columns}
          dataSource={filteredDataSource}
          loading={loading}
          pagination={{
            current: currentPage,
            pageSize: pageSize,
            total: filteredDataSource.length,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条规则`,
            pageSizeOptions: ['10', '20', '50', '100', '200'],
            onChange: (page, size) => {
              setCurrentPage(page)
              setPageSize(size)
            }
          }}
          scroll={{ y: 600 }}
          size="middle"
        />
      </Card>

      <Modal
        title="添加新规则"
        open={isModalVisible}
        onOk={handleAddRule}
        onCancel={() => {
          setIsModalVisible(false)
          setNewRule('')
        }}
        okText="添加"
        cancelText="取消"
      >
        <Input.TextArea
          rows={4}
          placeholder="请输入GitHub搜索规则，例如：AIzaSy extension:js"
          value={newRule}
          onChange={(e) => setNewRule(e.target.value)}
        />
        <div style={{ marginTop: 8, color: token.colorTextSecondary, fontSize: 12 }}>
          支持GitHub Code Search语法，例如：<br/>
          • AIzaSy language:python<br/>
          • AIzaSy filename:.env<br/>
          • "GOOGLE_API_KEY" in:file
        </div>
      </Modal>

      <Card style={{ marginTop: 16 }} title="💡 规则说明">
        <p>• 规则使用GitHub Code Search语法</p>
        <p>• 添加新规则后需要热重启才能生效</p>
        <p>• 热重启会在完成当前任务后自动重启系统</p>
        <p>• 规则存储在 queries.txt 文件中</p>
      </Card>
    </div>
  )
}

export default Rules

