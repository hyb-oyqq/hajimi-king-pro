import React, { useState, useEffect, useRef } from 'react'
import { Card, Button, Space, message, Switch } from 'antd'
import { ReloadOutlined, DownloadOutlined } from '@ant-design/icons'
import api from '../services/api'

function Logs() {
  const [logs, setLogs] = useState('')
  const [loading, setLoading] = useState(false)
  const [autoRefresh, setAutoRefresh] = useState(false)
  const [autoScroll, setAutoScroll] = useState(true)
  const logViewerRef = useRef(null)

  useEffect(() => {
    loadLogs()
  }, [])

  useEffect(() => {
    if (autoRefresh) {
      const interval = setInterval(loadLogs, 3000)
      return () => clearInterval(interval)
    }
  }, [autoRefresh])

  // 自动滚动到底部
  useEffect(() => {
    if (autoScroll && logViewerRef.current) {
      logViewerRef.current.scrollTop = logViewerRef.current.scrollHeight
    }
  }, [logs, autoScroll])

  const loadLogs = async () => {
    setLoading(true)
    try {
      const data = await api.getLogs(500)
      setLogs(data.logs)
      setLoading(false)
    } catch (error) {
      message.error('加载日志失败')
      setLoading(false)
    }
  }

  const downloadLogs = () => {
    const element = document.createElement('a')
    const file = new Blob([logs], { type: 'text/plain' })
    element.href = URL.createObjectURL(file)
    element.download = `logs-${new Date().toISOString()}.txt`
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  return (
    <div style={{ animation: 'fadeIn 0.6s ease-out' }}>
      <h2 style={{ marginBottom: 24, fontSize: 32 }}>📝 系统日志</h2>
      
      <Card>
        <Space style={{ marginBottom: 16, flexWrap: 'wrap' }}>
          <Button 
            type="primary" 
            icon={<ReloadOutlined />} 
            onClick={loadLogs}
            loading={loading}
          >
            刷新日志
          </Button>
          
          <Button 
            icon={<DownloadOutlined />} 
            onClick={downloadLogs}
          >
            下载日志
          </Button>
          
          <div>
            <Switch 
              checked={autoRefresh} 
              onChange={setAutoRefresh}
            />
            <span style={{ marginLeft: 8 }}>自动刷新（每3秒）</span>
          </div>

          <div>
            <Switch 
              checked={autoScroll} 
              onChange={setAutoScroll}
            />
            <span style={{ marginLeft: 8 }}>自动置底</span>
          </div>
        </Space>

        <div className="log-viewer" ref={logViewerRef}>
          {logs || '暂无日志'}
        </div>
      </Card>

      <Card style={{ marginTop: 16 }} title="💡 日志说明">
        <p>• 显示最近500行日志</p>
        <p>• 日志文件存储在 DATA_PATH/logs 目录</p>
        <p>• 可以启用自动刷新实时查看最新日志</p>
        <p>• 启用自动置底后，日志会自动滚动到最新内容</p>
        <p>• 支持下载日志文件到本地</p>
      </Card>
    </div>
  )
}

export default Logs

