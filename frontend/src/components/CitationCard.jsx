import { BookOpen } from 'lucide-react'

export default function CitationCard({ citation }) {
  return (
    <div className="border border-gray-200 rounded-md p-2 bg-gray-50 text-xs">
      <div className="flex items-center gap-1 text-brand-600 font-medium mb-1">
        <BookOpen size={12} />
        {citation.source}
      </div>
      <p className="text-gray-600 line-clamp-3">{citation.snippet}</p>
    </div>
  )
}
