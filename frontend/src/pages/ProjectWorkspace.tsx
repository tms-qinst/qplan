import React, { useEffect, useState } from 'react'
import { useParams, useNavigate, Outlet, NavLink } from 'react-router-dom'
import { Layout, Menu, Typography, Button, Spin, message } from 'antd'
import { useAuth } from '../contexts/AuthContext'
import api from '../services/api'

const { Header, Sider, Content } = Layout
const { Title } = Typography

const ProjectWorkspace: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const navigate = useNavigate()
  const { signOut, user } = useAuth()
  const [project, setProject] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (projectId) {
      api.get(`/projects/${projectId}`)
        .then(({ data }) => setProject(data))
        .catch(() => message.error('Failed to load project'))
        .finally(() => setLoading(false))
    }
  }, [projectId])

  const menuItems = [
    { key: 'activities', label: 'Activities', path: 'activities' },
    { key: 'wbs', label: 'WBS', path: 'wbs' },
    { key: 'gantt', label: 'Gantt Chart', path: 'gantt' },
    { key: 'relationships', label: 'Relationships', path: 'relationships' },
    { key: 'baselines', label: 'Baselines', path: 'baselines' },
    { key: 'schedule', label: 'Schedule (CPM)', path: 'schedule' },
  ]

  if (loading) return <Spin size="large" style={{ display: 'block', margin: '100px auto' }} />

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', background: '#001529' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <Title level={4} style={{ color: 'white', margin: 0, cursor: 'pointer' }} onClick={() => navigate('/')}>
            Qplan
          </Title>
          <span style={{ color: '#aaa' }}>{project?.project_name || 'Project'}</span>
        </div>
        <div>
          <span style={{ color: '#ddd', marginRight: 16 }}>{user?.email}</span>
          <Button type="text" style={{ color: '#ddd' }} onClick={signOut}>Logout</Button>
        </div>
      </Header>
      <Layout>
        <Sider width={220} theme="light">
          <Menu mode="inline" style={{ height: '100%' }}>
            {menuItems.map(item => (
              <Menu.Item key={item.key}>
                <NavLink to={`/project/${projectId}/${item.path}`}>{item.label}</NavLink>
              </Menu.Item>
            ))}
          </Menu>
        </Sider>
        <Content style={{ padding: 24, background: '#fff', overflow: 'auto' }}>
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  )
}

export default ProjectWorkspace