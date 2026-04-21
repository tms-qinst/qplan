import React, { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Button, DatePicker, Card, Table, Tag, Alert, Spin, Typography, message } from 'antd'
import { ThunderboltOutlined } from '@ant-design/icons'
import api from '../services/api'
import dayjs from 'dayjs'

const { Title } = Typography

const SchedulePage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState<any[]>([])
  const [criticalPath, setCriticalPath] = useState<string[]>([])
  const [warnings, setWarnings] = useState<string[]>([])
  const [dataDate, setDataDate] = useState(dayjs())

  const runSchedule = async () => {
    if (!projectId) return
    setLoading(true)
    try {
      const { data } = await api.post(`/projects/${projectId}/schedule`, {
        data_date: dataDate.format('YYYY-MM-DD'),
        mode: 'recalculate',
      })
      setResults(data.activities)
      setCriticalPath(data.critical_path)
      setWarnings(data.warnings)
      message.success(`Schedule calculated: ${data.activities.length} activities, ${data.critical_path.length} critical`)
    } catch (err: any) {
      message.error(err.response?.data?.detail || 'Schedule calculation failed')
    } finally {
      setLoading(false)
    }
  }

  const columns = [
    { title: 'Activity ID', dataIndex: 'activity_id', key: 'id', width: 100, ellipsis: true },
    { title: 'Early Start', dataIndex: 'early_start', key: 'es', width: 120 },
    { title: 'Early Finish', dataIndex: 'early_finish', key: 'ef', width: 120 },
    { title: 'Late Start', dataIndex: 'late_start', key: 'ls', width: 120 },
    { title: 'Late Finish', dataIndex: 'late_finish', key: 'lf', width: 120 },
    { title: 'Total Float', dataIndex: 'total_float', key: 'tf', width: 100,
      render: (v: any) => v !== null ? <Tag color={v <= 0 ? 'red' : 'green'}>{String(v)}</Tag> : '-' },
    { title: 'Critical', dataIndex: 'is_critical', key: 'crit', width: 80,
      render: (v: boolean) => v ? <Tag color="red">Critical</Tag> : <Tag>Normal</Tag> },
    { title: 'Status', dataIndex: 'status', key: 'status', width: 120 },
  ]

  return (
    <div>
      <Title level={3}>Schedule (CPM)</Title>
      <Card style={{ marginBottom: 16 }}>
        <div style={{ display: 'flex', gap: 16, alignItems: 'center' }}>
          <span>Data Date:</span>
          <DatePicker value={dataDate} onChange={(d) => d && setDataDate(d)} />
          <Button type="primary" icon={<ThunderboltOutlined />} onClick={runSchedule} loading={loading}>
            Run Schedule
          </Button>
        </div>
      </Card>

      {warnings.length > 0 && warnings.map((w, i) => <Alert key={i} message={w} type="warning" showIcon style={{ marginBottom: 8 }} />)}

      {results.length > 0 && (
        <Card title={`Results: ${results.length} activities | ${criticalPath.length} on critical path`}>
          <Table dataSource={results} columns={columns} rowKey="activity_id" size="small" scroll={{ x: 1000 }}
            rowClassName={(record) => record.is_critical ? 'critical-row' : ''}
          />
        </Card>
      )}
    </div>
  )
}

export default SchedulePage