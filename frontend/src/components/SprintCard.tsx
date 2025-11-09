'use client'

import { useTheme } from '@/contexts/ThemeContext'

interface UserStory {
  id: string
  title: string
  storyPoints: number
}

interface Sprint {
  id: string
  name: string
  goal: string
  startDate: string
  endDate: string
  totalStoryPoints: number
  completedStoryPoints: number
  progress: number
  userStories: UserStory[]
}

interface SprintCardProps {
  sprint: Sprint
  isSelected?: boolean
}

export default function SprintCard({ sprint, isSelected = false }: SprintCardProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  
  return (
    <div 
      className="card hover:shadow-lg transition-all duration-200 relative" 
      style={{
        borderColor: isSelected 
          ? '#8C1D40' 
          : isDark 
          ? 'rgba(140, 29, 64, 0.3)' 
          : 'rgba(140, 29, 64, 0.2)',
        backgroundColor: isSelected
          ? isDark
            ? 'rgba(140, 29, 64, 0.12)'
            : 'rgba(140, 29, 64, 0.08)'
          : isDark
          ? '#1a1a1a'
          : '#ffffff',
        borderWidth: isSelected ? '2px' : '1px',
        boxShadow: isSelected
          ? isDark
            ? '0 4px 12px rgba(140, 29, 64, 0.25)'
            : '0 4px 12px rgba(140, 29, 64, 0.2)'
          : '0 2px 8px rgba(0, 0, 0, 0.1)',
      }}
    >
      {/* Clean Selection Indicator */}
      {isSelected && (
        <div
          className="absolute top-0 left-0 w-1 h-full"
          style={{ backgroundColor: '#8C1D40' }}
        />
      )}
      <div className="flex items-start justify-between mb-3">
        <h3 
          className="text-lg font-semibold flex-1" 
          style={{ 
            color: isDark 
              ? '#f5f5f5' 
              : '#1a1a1a' 
          }}
        >
          {sprint.name}
        </h3>
        <span 
          className="px-2 py-1 text-xs font-medium rounded-full"
          style={{ 
            backgroundColor: isDark ? 'rgba(34, 197, 94, 0.15)' : 'rgba(34, 197, 94, 0.1)',
            border: `1px solid ${isDark ? 'rgba(34, 197, 94, 0.3)' : 'rgba(34, 197, 94, 0.2)'}`,
            color: '#22C55E'
          }}
        >
          {sprint.userStories.length} stories
        </span>
      </div>
      
      <p className="text-sm mb-4 line-clamp-2" style={{ color: isDark ? '#aaa' : '#666' }}>
        {sprint.goal}
      </p>
      
      <div className="space-y-3">
        <div>
          <div className="flex items-center justify-between text-sm mb-1">
            <span style={{ color: isDark ? '#aaa' : '#666' }}>Progress</span>
            <span style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>
              {sprint.completedStoryPoints}/{sprint.totalStoryPoints} SP
            </span>
          </div>
          <div
            className="w-full h-2 rounded-full overflow-hidden"
            style={{
              backgroundColor: isDark ? '#2a2a2a' : '#f5f5f5',
            }}
          >
            <div
              className="h-full transition-all duration-300"
              style={{
                width: `${sprint.progress}%`,
                backgroundColor: isSelected ? '#8C1D40' : '#FFC627',
              }}
            />
          </div>
        </div>
        
        <div className="flex items-center justify-between text-sm">
          <span style={{ color: isDark ? '#aaa' : '#666' }}>
            {new Date(sprint.startDate).toLocaleDateString()} - {new Date(sprint.endDate).toLocaleDateString()}
          </span>
          <span 
            className="px-2 py-1 text-xs font-bold rounded-full"
            style={{
              backgroundColor: isDark ? 'rgba(255, 198, 39, 0.2)' : 'rgba(255, 198, 39, 0.15)',
              color: '#FFC627'
            }}
          >
            {sprint.totalStoryPoints} SP
          </span>
        </div>
      </div>
    </div>
  )
}

