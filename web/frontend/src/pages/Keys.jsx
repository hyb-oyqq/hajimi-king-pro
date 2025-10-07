import React, { useState, useEffect } from 'react'
import { Table, Card, Tag, Input, Select, Button, Space, message, Popconfirm, Alert, Dropdown } from 'antd'
import { SearchOutlined, ReloadOutlined, DeleteOutlined, DownloadOutlined, ClearOutlined, ThunderboltOutlined } from '@ant-design/icons'
import api from '../services/api'

const { Option } = Select

function Keys() {
  const [keys, setKeys] = useState([])
  const [loading, setLoading] = useState(true)
  const [selectedRowKeys, setSelectedRowKeys] = useState([])
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

  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要删除的密钥')
      return
    }
    
    try {
      // 批量删除
      const promises = selectedRowKeys.map(id => api.deleteKey(id))
      await Promise.all(promises)
      message.success(`成功删除 ${selectedRowKeys.length} 个密钥`)
      setSelectedRowKeys([])
      loadKeys()
    } catch (error) {
      message.error('批量删除失败')
    }
  }

  const handleExport = (format = 'csv') => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择要导出的密钥')
      return
    }

    // 获取选中的密钥数据
    const selectedKeys = keys.filter(key => selectedRowKeys.includes(key.id))
    
    if (format === 'csv') {
      exportToCSV(selectedKeys)
    } else if (format === 'json') {
      exportToJSON(selectedKeys)
    } else if (format === 'txt') {
      exportToTXT(selectedKeys)
    }
  }

  const handleQuickExport = async (keyType) => {
    try {
      // 获取特定类型的所有密钥（不分页）
      const params = {
        page: 1,
        page_size: 10000, // 大数字获取所有
        type: keyType
      }
      const data = await api.getKeys(params)
      
      if (data.data.length === 0) {
        message.warning(`没有找到${getTypeText(keyType)}密钥`)
        return
      }

      // 导出为TXT（仅密钥）
      exportToTXT(data.data)
    } catch (error) {
      message.error('快速导出失败')
    }
  }

  const getTypeText = (type) => {
    const typeMap = {
      'valid': '有效',
      'rate_limited': '限流',
      'paid': '付费',
      'send': '待验证'
    }
    return typeMap[type] || type
  }

  const exportToCSV = (data) => {
    // CSV头部
    const headers = ['ID', '密钥', '类型', '来源仓库', '文件路径', '创建时间']
    const csvContent = [
      headers.join(','),
      ...data.map(item => [
        item.id,
        `"${item.api_key}"`,
        item.key_type,
        `"${item.repo_name || ''}"`,
        `"${item.file_path || ''}"`,
        `"${new Date(item.created_at).toLocaleString('zh-CN')}"`
      ].join(','))
    ].join('\n')

    // 添加BOM以支持中文
    const BOM = '\uFEFF'
    const blob = new Blob([BOM + csvContent], { type: 'text/csv;charset=utf-8;' })
    downloadFile(blob, `keys_export_${Date.now()}.csv`)
    message.success(`成功导出 ${data.length} 个密钥到CSV`)
  }

  const exportToJSON = (data) => {
    const jsonContent = JSON.stringify(data, null, 2)
    const blob = new Blob([jsonContent], { type: 'application/json;charset=utf-8;' })
    downloadFile(blob, `keys_export_${Date.now()}.json`)
    message.success(`成功导出 ${data.length} 个密钥到JSON`)
  }

  const exportToTXT = (data) => {
    // 仅导出密钥，每行一个
    const txtContent = data.map(item => item.api_key).join('\n')
    const blob = new Blob([txtContent], { type: 'text/plain;charset=utf-8;' })
    downloadFile(blob, `keys_export_${Date.now()}.txt`)
    message.success(`成功导出 ${data.length} 个密钥到TXT`)
  }

  const downloadFile = (blob, filename) => {
    const link = document.createElement('a')
    const url = URL.createObjectURL(blob)
    link.href = url
    link.download = filename
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
  }

  const rowSelection = {
    selectedRowKeys,
    onChange: (selectedKeys) => {
      setSelectedRowKeys(selectedKeys)
    },
    selections: [
      Table.SELECTION_ALL,
      Table.SELECTION_INVERT,
      Table.SELECTION_NONE,
    ],
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
          send: '待验证'
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
    <div style={{ animation: 'fadeIn 0.6s ease-out' }}>
      <h2 style={{ marginBottom: 24, fontSize: 32 }}>🔑 密钥管理</h2>
      
      <Card style={{ marginBottom: 16 }}>
        <Space style={{ marginBottom: 16, flexWrap: 'wrap' }}>
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
            <Option value="send">待验证</Option>
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

          <Dropdown
            menu={{
              items: [
                {
                  key: 'valid',
                  label: '快速导出有效密钥',
                  onClick: () => handleQuickExport('valid')
                },
                {
                  key: 'rate_limited',
                  label: '快速导出限流密钥',
                  onClick: () => handleQuickExport('rate_limited')
                },
                {
                  key: 'paid',
                  label: '快速导出付费密钥',
                  onClick: () => handleQuickExport('paid')
                },
                {
                  key: 'send',
                  label: '快速导出待验证密钥',
                  onClick: () => handleQuickExport('send')
                }
              ]
            }}
            placement="bottomLeft"
          >
            <Button icon={<ThunderboltOutlined />}>
              快速导出密钥
            </Button>
          </Dropdown>
        </Space>

        {selectedRowKeys.length > 0 && (
          <Alert
            message={
              <Space>
                <span>已选择 <strong>{selectedRowKeys.length}</strong> 项</span>
                <Button 
                  type="link" 
                  size="small"
                  icon={<ClearOutlined />}
                  onClick={() => setSelectedRowKeys([])}
                >
                  清空选择
                </Button>
              </Space>
            }
            type="info"
            showIcon
            style={{ marginBottom: 16 }}
            action={
              <Space wrap>
                <Button 
                  size="small" 
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport('txt')}
                >
                  仅导出密钥
                </Button>
                <Button 
                  size="small" 
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport('csv')}
                >
                  导出CSV
                </Button>
                <Button 
                  size="small" 
                  icon={<DownloadOutlined />}
                  onClick={() => handleExport('json')}
                >
                  导出JSON
                </Button>
                <Popconfirm
                  title="批量删除确认"
                  description={`确定要删除选中的 ${selectedRowKeys.length} 个密钥吗？`}
                  onConfirm={handleBatchDelete}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button 
                    size="small" 
                    danger 
                    icon={<DeleteOutlined />}
                  >
                    批量删除
                  </Button>
                </Popconfirm>
              </Space>
            }
          />
        )}

        <Table
          columns={columns}
          dataSource={keys}
          loading={loading}
          rowKey="id"
          rowSelection={rowSelection}
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

