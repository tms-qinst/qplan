import React, { useEffect, useState } from 'react'
import { Card, Row, Col, Statistic, Typography, List, Tag } from 'antd'
import { ProjectOutlined, AlertOutlined, ClockCircleOutlined } from '@ant-design/icons'
import { useNavigate } from 'react-router-dom'
import api from '../services/api'

const { Title } = Typography

interface Project {
  id: string
  project_code: string
  project_name: string
  project_status: string
  data_date: string
}

const DashboardPage: React.FC = () => {
  const navigate = useNavigate()
  const [projects, setProjects] = useState<Project[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    api.get('/projects').then(({ data }) => {
      setProjects(data)
      setLoading(false)
    }).catch(() => setLoading(false))
  }, [])

  return (
    <div>
      <Title level={3}>Dashboard</Title>
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card><Statistic title="Total Projects" value={projects.length} prefix={<ProjectOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Active" value={projects.filter(p => p.project_status === 'active').length} prefix={<ClockCircleOutlined />} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Planning" value={projects.filter(p => p.project_status === 'planning').length} /></Card>
        </Col>
        <Col span={6}>
          <Card><Statistic title="Completed" value={projects.filter(p => p.project_status === 'completed').length} /></Card>
        </Col>
      </Row>
      <Card title="Recent Projects" loading={loading}>
        <List
          dataSource={projects}
          renderItem={(item) => (
            <List.Item
              style={{ cursor: 'pointer' }}
              onClick={() => navigate(`/project/${item.id}`)}
            >
              <List.Item.Meta
                title={<a>{item.project_name}</a>}
                description={`Code: ${item.project_code} | Data Date: ${item.data_date}`}
              />
              <Tag color={item.project_status === 'active' ? 'green' : 'blue'}>{item.project_status}</Tag>
            </List.Item>
          )}
        />
      </Card>
    </div>
  )
}

export default DashboardPage