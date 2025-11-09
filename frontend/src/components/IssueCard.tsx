'use client'

import { useTheme } from '@/contexts/ThemeContext'

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

const getStatusColor = (status: string, isDark: boolean) => {
  const key = status.toLowerCase()
  
  if (key === 'open') {
    return {
      border: isDark ? 'rgba(34, 197, 94, 0.4)' : 'rgba(34, 197, 94, 0.3)',
      bg: isDark ? 'rgba(34, 197, 94, 0.15)' : 'rgba(34, 197, 94, 0.1)',
      text: '#22c55e' // Green
    }
  } else if (key === 'in-progress' || key === 'in progress') {
    return {
      border: isDark ? 'rgba(255, 198, 39, 0.4)' : 'rgba(255, 198, 39, 0.3)',
      bg: isDark ? 'rgba(255, 198, 39, 0.15)' : 'rgba(255, 198, 39, 0.1)',
      text: '#FFC627' // Yellow
    }
  } else if (key === 'done' || key === 'closed') {
    return {
      border: isDark ? 'rgba(239, 68, 68, 0.4)' : 'rgba(239, 68, 68, 0.3)',
      bg: isDark ? 'rgba(239, 68, 68, 0.15)' : 'rgba(239, 68, 68, 0.1)',
      text: '#ef4444' // Red
    }
  } else if (key === 'blocked') {
    return {
      border: isDark ? 'rgba(140, 29, 64, 0.4)' : 'rgba(140, 29, 64, 0.3)',
      bg: isDark ? 'rgba(140, 29, 64, 0.15)' : 'rgba(140, 29, 64, 0.1)',
      text: '#8C1D40' // Maroon
    }
  }
  
  // Default
  return {
    border: isDark ? 'rgba(100, 100, 100, 0.4)' : 'rgba(100, 100, 100, 0.3)',
    bg: isDark ? 'rgba(100, 100, 100, 0.15)' : 'rgba(100, 100, 100, 0.1)',
    text: isDark ? '#aaa' : '#666'
  }
}

const getPriorityColor = (priority: string) => {
  const priorityMap: Record<string, string> = {
    high: '#8C1D40',
    medium: '#FFC627',
    low: '#888',
  }
  return priorityMap[priority.toLowerCase()] || '#888'
}

export default function IssueCard({ issue }: IssueCardProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const statusColors = getStatusColor(issue.status, isDark)
  
  return (
    <div className="card hover:shadow-xl transition-shadow duration-200" style={{
      borderColor: 'rgba(140, 29, 64, 0.4)'
    }}>
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold line-clamp-2" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>
          {issue.title}
        </h3>
        <span 
          className="px-2 py-1 text-xs font-medium rounded-full border"
          style={{ 
            backgroundColor: statusColors.bg,
            borderColor: statusColors.border,
            color: statusColors.text
          }}
        >
          {issue.status}
        </span>
      </div>
      
      <div className="space-y-2">
        {issue.assignee && (
          <div className="flex items-center text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>
            <span className="font-medium">Assigned to:</span>
            <span className="ml-2">{issue.assignee}</span>
          </div>
        )}
        
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium" style={{ color: getPriorityColor(issue.priority) }}>
            {issue.priority} priority
          </span>
          <span className="text-xs" style={{ color: isDark ? '#888' : '#999' }}>
            {new Date(issue.createdAt).toLocaleDateString()}
          </span>
        </div>
      </div>
      
      <div className="mt-4 pt-4" style={{ borderTop: '1px solid rgba(140, 29, 64, 0.3)' }}>
        <button className="text-sm font-medium transition-colors" style={{ color: isDark ? '#FFC627' : '#8C1D40' }}
          onMouseEnter={(e) => e.currentTarget.style.color = isDark ? '#FFD757' : '#a02350'}
          onMouseLeave={(e) => e.currentTarget.style.color = isDark ? '#FFC627' : '#8C1D40'}
        >
          View Details →
        </button>
      </div>
    </div>
  )
}

