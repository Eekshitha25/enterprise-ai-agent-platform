import { Workflow } from 'lucide-react'

export default function AgentTrace({ trace }) {
  if (!trace || trace.length === 0) return null
  return (
    <details className="mt-2 text-xs">
      <summary className="cursor-pointer text-gray-500 flex items-center gap-1 select-none">
        <Workflow size={12} /> Agent reasoning trace ({trace.length} steps)
      </summary>
      <ol className="mt-1 ml-4 space-y-1 border-l border-gray-200 pl-3">
        {trace.map((step, i) => (
          <li key={i} className="text-gray-500">
            <span className="font-medium text-brand-600">{step.agent}</span>
            {' -> '}
            <span className="text-gray-700">{step.action}</span>
            {step.detail ? <span className="text-gray-400"> ({step.detail})</span> : null}
          </li>
        ))}
      </ol>
    </details>
  )
}
