import React, { useState, useEffect } from 'react'
import { Table, Card, Tag, Input, Select, Button, Space, message, Popconfirm } from 'antd'
import { SearchOutlined, ReloadOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../services/api'

const { Option } = Select

function Keys() {
  const [keys, setKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [pagination, setPagination] = useState({
    current: 1,
    pageSize: 50,
    total: 0
  })
  const [filters, setFilters] = useState({
    type: null,
    search: ''
  })

  useEffect(() => {
    loadKeys()
  }, [pagination.current, pagination.pageSize, filters])

  const loadKeys = async () => {
    setLoading(true)
    try {
      const params = {
        page: pagination.current,
        page_size: pagination.pageSize,
        type: filters.type,
        search: filters.search
      }
      const data = await api.getKeys(params)
      setKeys(data.data)
      setPagination({
        ...pagination,
        total: data.total
      })
      setLoading(false)
    } catch (error) {
      message.error('加载密钥列表失败')
      setLoading(false)
    }
  }

  const handleDelete = async (keyId) => {
    try {
      await api.deleteKey(keyId)
      message.success('删除成功')
      loadKeys()
    } catch (error) {
      message.error('删除失败')
    }
  }

  const columns = [
    {
      title: 'ID',
      dataIndex: 'id',
      key: 'id',
      width: 80
    },
    {
      title: '密钥',
      dataIndex: 'api_key',
      key: 'api_key',
      ellipsis: true,
      render: (text) => (
        <code style={{ fontSize: 12 }}>{text}</code>
      )
    },
    {
      title: '类型',
      dataIndex: 'key_type',
      key: 'key_type',
      width: 120,
      render: (type) => {
        const colorMap = {
          valid: 'green',
          rate_limited: 'orange',
          paid: 'purple',
          send: 'blue'
        }
        const textMap = {
          valid: '有效',
          rate_limited: '限流',
          paid: '付费',
          send: '已发送'
        }
        return <Tag color={colorMap[type]}>{textMap[type] || type}</Tag>
      }
    },
    {
      title: '来源仓库',
      dataIndex: 'repo_name',
      key: 'repo_name',
      ellipsis: true
    },
    {
      title: '文件路径',
      dataIndex: 'file_path',
      key: 'file_path',
      ellipsis: true,
      render: (text) => text || '-'
    },
    {
      title: '创建时间',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 180,
      render: (text) => new Date(text).toLocaleString('zh-CN')
    },
    {
      title: '操作',
      key: 'action',
      width: 100,
      render: (_, record) => (
        <Popconfirm
          title="确定要删除这个密钥吗？"
          onConfirm={() => handleDelete(record.id)}
          okText="确定"
          cancelText="取消"
        >
          <Button type="link" danger icon={<DeleteOutlined />}>
            删除
          </Button>
        </Popconfirm>
      )
    }
  ]

  return (
    <div>
      <h2 style={{ marginBottom: 24 }}>🔑 密钥管理</h2>
      
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16 }}>
          <Select
            style={{ width: 150 }}
            placeholder="选择类型"
            allowClear
            value={filters.type}
            onChange={(value) => setFilters({ ...filters, type: value })}
          >
            <Option value="valid">有效</Option>
            <Option value="rate_limited">限流</Option>
            <Option value="paid">付费</Option>
            <Option value="send">已发送</Option>
          </Select>
          
          <Input
            placeholder="搜索密钥或仓库"
            prefix={<SearchOutlined />}
            style={{ width: 300 }}
            value={filters.search}
            onChange={(e) => setFilters({ ...filters, search: e.target.value })}
            onPressEnter={loadKeys}
          />
          
          <Button type="primary" onClick={loadKeys}>
            搜索
          </Button>
          
          <Button icon={<ReloadOutlined />} onClick={loadKeys}>
            刷新
          </Button>
        </Space>

        <Table
          columns={columns}
          dataSource={keys}
          loading={loading}
          rowKey="id"
          pagination={{
            ...pagination,
            showSizeChanger: true,
            showQuickJumper: true,
            showTotal: (total) => `共 ${total} 条记录`,
            onChange: (page, pageSize) => {
              setPagination({ ...pagination, current: page, pageSize })
            }
          }}
          scroll={{ x: 1200 }}
        />
      </Card>
    </div>
  )
}

export default Keys

