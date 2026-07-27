import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  timeout: 60000,
})

export async function sendChatMessage(message, conversationId) {
  const { data } = await client.post('/chat', {
    message,
    conversation_id: conversationId || null,
  })
  return data
}

export async function fetchHistory(conversationId) {
  const { data } = await client.get(`/chat/${conversationId}/history`)
  return data
}

export async function uploadDocument(file) {
  const formData = new FormData()
  formData.append('file', file)
  const { data } = await client.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data
}

export async function listDocuments() {
  const { data } = await client.get('/documents')
  return data
}

export default client
