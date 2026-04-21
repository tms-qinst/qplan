import React, { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { Table, Button, Modal, Form, Input, InputNumber, Select, DatePicker, Space, Tag, message, Popconfirm } from 'antd'
import { PlusOutlined, DeleteOutlined } from '@ant-design/icons'
import api from '../services/api'
import dayjs from 'dayjs'

const ActivitiesPage: React.FC = () => {
  const { projectId } = useParams<{ projectId: string }>()
  const [activities, setActivities] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [modalOpen, setModalOpen] = useState(false)
  const [form] = Form.useForm()
  const [wbsOptions, setWbsOptions] = useState<any[]>([])

  const loadActivities = () => {
    if (!projectId) return
    setLoading(true)
    Promise.all([
      api.get(`/projects/${projectId}/activities`),
      api.get(`/projects/${projectId}/wbs`),
    ]).then(([actRes, wbsRes]) => {
      setActivities(actRes.data)
      setWbsOptions(wbsRes.data)
    }).finally(() => setLoading(false))
  }

  useEffect(loadActivities, [projectId])

  const handleCreate = async (values: any) => {
    if (!projectId) return
    await api.post(`/projects/${projectId}/activities`, {
      ...values,
      planned_start: values.planned_start?.format('YYYY-MM-DD'),
      planned_finish: values.planned_finish?.format('YYYY-MM-DD'),
    })
    message.success('Activity created')
    setModalOpen(false)
    form.resetFields()
    loadActivities()
  }

  const handleDelete = async (id: string) => {
    if (!projectId) return
    await api.delete(`/projects/${projectId}/activities/${id}`)
    message.success('Activity deleted')
    loadActivities()
  }

  const columns = [
    { title: 'Code', dataIndex: 'activity_code', key: 'code', width: 120 },
    { title: 'Name', dataIndex: 'activity_name', key: 'name' },
    { title: 'Duration', dataIndex: 'duration_days', key: 'duration', width: 100 },
    { title: 'Status', dataIndex: 'status', key: 'status', width: 120, render: (s: string) => <Tag color={s === 'completed' ? 'green' : s === 'in_progress' ? 'blue' : 'default'}>{s}</Tag> },
    { title: 'Early Start', dataIndex: 'early_start', key: 'es', width: 120 },
    { title: 'Early Finish', dataIndex: 'early_finish', key: 'ef', width: 120 },
    { title: 'Total Float', dataIndex: 'total_float', key: 'tf', width: 100,
      render: (v: number) => v !== null && v !== undefined ? <Tag color={v <= 0 ? 'red' : 'green'}>{v}</Tag> : '-' },
    { title: 'Critical', dataIndex: 'is_critical', key: 'crit', width: 80, render: (v: boolean) => v ? <Tag color="red">Yes</Tag> : <Tag>No</Tag> },
    {
      title: 'Action', key: 'action', width: 80,
      render: (_: any, record: any) => (
        <Popconfirm title="Delete?" onConfirm={() => handleDelete(record.id)}>
          <Button icon={<DeleteOutlined />} danger size="small" />
        </Popconfirm>
      ),
    },
  ]

  return (
    <div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 16 }}>
        <h2>Activities</h2>
        <Button type="primary" icon={<PlusOutlined />} onClick={() => setModalOpen(true)}>New Activity</Button>
      </div>
      <Table dataSource={activities} columns={columns} rowKey="id" loading={loading} size="small" scroll={{ x: 1200 }} />

      <Modal title="New Activity" open={modalOpen} onCancel={() => setModalOpen(false)} onOk={() => form.submit()} width={600}>
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item name="wbs_id" label="WBS" rules={[{ required: true }]}>
            <Select options={wbsOptions.map((w: any) => ({ value: w.id, label: `${w.wbs_code} - ${w.wbs_name}` }))} />
          </Form.Item>
          <Form.Item name="activity_code" label="Activity Code" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Form.Item name="activity_name" label="Activity Name" rules={[{ required: true }]}>
            <Input />
          </Form.Item>
          <Space style={{ width: '100%' }} size="large">
            <Form.Item name="duration_days" label="Duration (days)" initialValue={0}>
              <InputNumber min={0} />
            </Form.Item>
            <Form.Item name="status" label="Status" initialValue="not_started">
              <Select options={[
                { value: 'not_started', label: 'Not Started' },
                { value: 'in_progress', label: 'In Progress' },
                { value: 'completed', label: 'Completed' },
              ]} />
            </Form.Item>
            <Form.Item name="is_milestone" label="Milestone" valuePropName="checked">
              <Select options={[{ value: false, label: 'No' }, { value: true, label: 'Yes' }]} />
            </Form.Item>
          </Space>
        </Form>
      </Modal>
    </div>
  )
}

export default ActivitiesPage