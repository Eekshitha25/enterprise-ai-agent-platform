import { Bot, FileText, Upload, Plus } from 'lucide-react'

export default function Sidebar({ documents, onNewChat, onUploadClick }) {
  return (
    <aside className="w-72 shrink-0 bg-brand-900 text-white flex flex-col h-full">
      <div className="p-5 border-b border-brand-700 flex items-center gap-2">
        <Bot size={22} className="text-brand-100" />
        <div>
          <p className="font-semibold leading-tight">Enterprise AI Agent</p>
          <p className="text-xs text-brand-100/70 leading-tight">Knowledge Automation Platform</p>
        </div>
      </div>

      <button
        onClick={onNewChat}
        className="mx-4 mt-4 flex items-center gap-2 bg-brand-600 hover:bg-brand-500 transition rounded-lg px-3 py-2 text-sm font-medium"
      >
        <Plus size={16} /> New conversation
      </button>

      <div className="px-4 mt-6 flex-1 overflow-y-auto">
        <div className="flex items-center justify-between mb-2">
          <p className="text-xs uppercase tracking-wide text-brand-100/60">Knowledge base</p>
          <button onClick={onUploadClick} title="Upload document">
            <Upload size={14} className="text-brand-100/80 hover:text-white" />
          </button>
        </div>
        <ul className="space-y-1">
          {documents.length === 0 && (
            <li className="text-xs text-brand-100/50">No documents indexed yet.</li>
          )}
          {documents.map((doc) => (
            <li key={doc.id} className="flex items-center gap-2 text-sm text-brand-50/90 truncate">
              <FileText size={14} className="shrink-0 text-brand-100/70" />
              <span className="truncate">{doc.filename}</span>
              <span
                className={`ml-auto text-[10px] px-1.5 py-0.5 rounded ${
                  doc.status === 'indexed'
                    ? 'bg-emerald-500/20 text-emerald-300'
                    : doc.status === 'failed'
                    ? 'bg-red-500/20 text-red-300'
                    : 'bg-amber-500/20 text-amber-300'
                }`}
              >
                {doc.status}
              </span>
            </li>
          ))}
        </ul>
      </div>

      <div className="p-4 text-[11px] text-brand-100/50 border-t border-brand-700">
        Multi-agent RAG · LangGraph · Qdrant · PostgreSQL
      </div>
    </aside>
  )
}
