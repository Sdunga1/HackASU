'use client'

import { useTheme } from '@/contexts/ThemeContext'

interface ProjectStats {
  totalIssues: number
  openIssues: number
  closedIssues: number
  inProgress: number
}

interface ProjectStatsProps {
  stats: ProjectStats
}

export default function ProjectStats({ stats }: ProjectStatsProps) {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const completionRate = stats.totalIssues > 0 
    ? Math.round((stats.closedIssues / stats.totalIssues) * 100)
    : 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium" style={{ color: isDark ? '#aaa' : '#666' }}>Total Issues</p>
            <p className="text-2xl font-bold mt-1" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{stats.totalIssues}</p>
          </div>
          <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
            backgroundColor: isDark ? 'rgba(255, 198, 39, 0.15)' : 'rgba(255, 198, 39, 0.2)',
            border: isDark ? '1px solid rgba(255, 198, 39, 0.3)' : '1px solid rgba(255, 198, 39, 0.4)'
          }}>
            <svg className="w-6 h-6" style={{ color: isDark ? '#FFC627' : '#8C1D40' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
            </svg>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium" style={{ color: isDark ? '#aaa' : '#666' }}>Open</p>
            <p className="text-2xl font-bold mt-1" style={{ color: isDark ? '#FFC627' : '#8C1D40' }}>{stats.openIssues}</p>
          </div>
          <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
            backgroundColor: isDark ? 'rgba(255, 198, 39, 0.15)' : 'rgba(255, 198, 39, 0.2)',
            border: isDark ? '1px solid rgba(255, 198, 39, 0.3)' : '1px solid rgba(255, 198, 39, 0.4)'
          }}>
            <svg className="w-6 h-6" style={{ color: isDark ? '#FFC627' : '#8C1D40' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 11V7a4 4 0 118 0m-4 8v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2z" />
            </svg>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium" style={{ color: isDark ? '#aaa' : '#666' }}>In Progress</p>
            <p className="text-2xl font-bold mt-1" style={{ color: isDark ? '#FFC627' : '#8C1D40' }}>{stats.inProgress}</p>
          </div>
          <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
            backgroundColor: isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.15)',
            border: isDark ? '1px solid rgba(140, 29, 64, 0.5)' : '1px solid rgba(140, 29, 64, 0.3)'
          }}>
            <svg className="w-6 h-6" style={{ color: isDark ? '#FFC627' : '#8C1D40' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium" style={{ color: isDark ? '#aaa' : '#666' }}>Completion</p>
            <p className="text-2xl font-bold mt-1" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{completionRate}%</p>
          </div>
          <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
            backgroundColor: isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.15)',
            border: isDark ? '1px solid rgba(140, 29, 64, 0.5)' : '1px solid rgba(140, 29, 64, 0.3)'
          }}>
            <svg className="w-6 h-6" style={{ color: isDark ? '#FFC627' : '#8C1D40' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        </div>
      </div>
    </div>
  )
}

