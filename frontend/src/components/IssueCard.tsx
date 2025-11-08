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
    open: 'bg-green-100 text-green-800',
    closed: 'bg-gray-100 text-gray-800',
    'in-progress': 'bg-blue-100 text-blue-800',
    blocked: 'bg-red-100 text-red-800',
  }
  return statusMap[status.toLowerCase()] || 'bg-gray-100 text-gray-800'
}

const getPriorityColor = (priority: string) => {
  const priorityMap: Record<string, string> = {
    high: 'text-red-600',
    medium: 'text-yellow-600',
    low: 'text-gray-600',
  }
  return priorityMap[priority.toLowerCase()] || 'text-gray-600'
}

export default function IssueCard({ issue }: IssueCardProps) {
  return (
    <div className="card hover:shadow-md transition-shadow duration-200">
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold text-gray-900 line-clamp-2">
          {issue.title}
        </h3>
        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(issue.status)}`}>
          {issue.status}
        </span>
      </div>
      
      <div className="space-y-2">
        {issue.assignee && (
          <div className="flex items-center text-sm text-gray-600">
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
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <button className="text-sm text-primary-600 hover:text-primary-700 font-medium">
          View Details →
        </button>
      </div>
    </div>
  )
}

