'use client'

import { useTheme } from '@/contexts/ThemeContext'

interface UserStory {
  id: string
  title: string
  description: string
  storyPoints: number
  priority: string
  status: string
  assignee?: string
  acceptanceCriteria?: string[]
}

interface UserStoryCardProps {
  story: UserStory
}

const getStatusColor = (status: string) => {
  const statusMap: Record<string, { border: string; bg: string; text: string }> = {
    todo: {
      border: 'rgba(255, 198, 39, 0.3)',
      bg: 'rgba(255, 198, 39, 0.15)',
      text: '#FFC627'
    },
    'in-progress': {
      border: 'rgba(140, 29, 64, 0.3)',
      bg: 'rgba(140, 29, 64, 0.15)',
      text: '#8C1D40'
    },
    done: {
      border: 'rgba(34, 197, 94, 0.3)',
      bg: 'rgba(34, 197, 94, 0.15)',
      text: '#22C55E'
    },
    backlog: {
      border: 'rgba(100, 100, 100, 0.3)',
      bg: 'rgba(100, 100, 100, 0.15)',
      text: '#aaa'
    }
  }
  const key = status.toLowerCase()
  return statusMap[key] || statusMap.backlog
}

const getPriorityColor = (priority: string) => {
  const priorityMap: Record<string, string> = {
    high: '#8C1D40',
    medium: '#FFC627',
    low: '#888',
  }
  return priorityMap[priority.toLowerCase()] || '#888'
}

export default function UserStoryCard({ story }: UserStoryCardProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const statusColors = getStatusColor(story.status)
  
  return (
    <div className="card hover:shadow-xl transition-shadow duration-200" style={{
      borderColor: 'rgba(140, 29, 64, 0.4)'
    }}>
      <div className="flex items-start justify-between mb-3">
        <h3 className="text-lg font-semibold line-clamp-2 flex-1" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>
          {story.title}
        </h3>
        <span 
          className="px-2 py-1 text-xs font-bold rounded-full ml-2"
          style={{ 
            backgroundColor: isDark ? 'rgba(255, 198, 39, 0.2)' : 'rgba(255, 198, 39, 0.15)',
            color: '#FFC627'
          }}
        >
          {story.storyPoints} SP
        </span>
      </div>
      
      <p className="text-sm mb-3 line-clamp-2" style={{ color: isDark ? '#aaa' : '#666' }}>
        {story.description}
      </p>
      
      <div className="space-y-2">
        <div className="flex items-center justify-between">
          <span 
            className="px-2 py-1 text-xs font-medium rounded-full border"
            style={{ 
              backgroundColor: statusColors.bg,
              borderColor: statusColors.border,
              color: statusColors.text
            }}
          >
            {story.status.replace('-', ' ')}
          </span>
          <span className="text-sm font-medium" style={{ color: getPriorityColor(story.priority) }}>
            {story.priority} priority
          </span>
        </div>
        
        {story.assignee && (
          <div className="flex items-center text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>
            <span className="font-medium">Assigned to:</span>
            <span className="ml-2">{story.assignee}</span>
          </div>
        )}
        
        {story.acceptanceCriteria && story.acceptanceCriteria.length > 0 && (
          <div className="pt-2" style={{ borderTop: '1px solid rgba(140, 29, 64, 0.2)' }}>
            <p className="text-xs font-medium mb-1" style={{ color: isDark ? '#aaa' : '#666' }}>
              Acceptance Criteria:
            </p>
            <ul className="list-disc list-inside text-xs space-y-1" style={{ color: isDark ? '#aaa' : '#666' }}>
              {story.acceptanceCriteria.slice(0, 2).map((criteria, idx) => (
                <li key={idx} className="line-clamp-1">{criteria}</li>
              ))}
              {story.acceptanceCriteria.length > 2 && (
                <li className="text-[#FFC627]">+{story.acceptanceCriteria.length - 2} more</li>
              )}
            </ul>
          </div>
        )}
      </div>
    </div>
  )
}

