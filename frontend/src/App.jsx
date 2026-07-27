import { useState, useEffect, useRef } from 'react'
import Sidebar from './components/Sidebar.jsx'
import ChatWindow from './components/ChatWindow.jsx'
import { listDocuments, uploadDocument } from './api/client.js'

export default function App() {
  const [conversationId, setConversationId] = useState(null)
  const [chatKey, setChatKey] = useState(0)
  const [documents, setDocuments] = useState([])
  const fileInputRef = useRef(null)

  const refreshDocuments = async () => {
    try {
      const docs = await listDocuments()
      setDocuments(docs)
    } catch {
      // backend not reachable yet; ignore in dev
    }
  }

  useEffect(() => {
    refreshDocuments()
  }, [])

  const handleNewChat = () => {
    setConversationId(null)
    setChatKey((k) => k + 1)
  }

  const handleUploadClick = () => fileInputRef.current?.click()

  const handleFileChange = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    await uploadDocument(file)
    refreshDocuments()
    e.target.value = ''
  }

  return (
    <div className="flex h-screen">
      <Sidebar documents={documents} onNewChat={handleNewChat} onUploadClick={handleUploadClick} />
      <input type="file" ref={fileInputRef} onChange={handleFileChange} className="hidden" accept=".pdf" />
      <main className="flex-1 flex flex-col bg-gray-50">
        <ChatWindow key={chatKey} conversationId={conversationId} setConversationId={setConversationId} />
      </main>
    </div>
  )
}
