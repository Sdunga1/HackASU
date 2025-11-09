'use client'

interface Issue {
  id: string
  title: string
  status: string
  assignee?: string
  priority: string
  createdAt: string
}

interface IssueCardProps {
  issue: Issue
}

const getStatusColor = (status: string) => {
  const statusMap: Record<string, string> = {
    open: 'bg-green-900 text-green-300 border-green-700',
    closed: 'bg-gray-700 text-gray-300 border-gray-600',
    'in-progress': 'bg-blue-900 text-blue-300 border-blue-700',
    blocked: 'bg-red-900 text-red-300 border-red-700',
  }
  return statusMap[status.toLowerCase()] || 'bg-gray-700 text-gray-300 border-gray-600'
}

const getPriorityColor = (priority: string) => {
  const priorityMap: Record<string, string> = {
    high: 'text-red-400',
    medium: 'text-yellow-400',
    low: 'text-gray-400',
  }
  return priorityMap[priority.toLowerCase()] || 'text-gray-400'
}

export default function IssueCard({ issue }: IssueCardProps) {
  return (
    <div className="card hover:shadow-xl transition-shadow duration-200">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-100 line-clamp-2">
          {issue.title}
        </h3>
        <span className={`px-2 py-1 text-xs font-medium rounded-full border ${getStatusColor(issue.status)}`}>
          {issue.status}
        </span>
      </div>
      
      <div className="space-y-2">
        {issue.assignee && (
          <div className="flex items-center text-sm text-gray-400">
            <span className="font-medium">Assigned to:</span>
            <span className="ml-2">{issue.assignee}</span>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <span className={`text-sm font-medium ${getPriorityColor(issue.priority)}`}>
            {issue.priority} priority
          </span>
          <span className="text-xs text-gray-500">
            {new Date(issue.createdAt).toLocaleDateString()}
          </span>
        </div>
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-700">
        <button className="text-sm text-blue-400 hover:text-blue-300 font-medium">
          View Details →
        </button>
      </div>
    </div>
  )
}

