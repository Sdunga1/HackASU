'use client'

import { useEffect, useState } from 'react'
import Header from './Header'
import IssueCard from './IssueCard'
import ProjectStats from './ProjectStats'
import { fetchIssues, fetchProjectStats } from '@/lib/api'

interface Issue {
  id: string
  title: string
  status: string
  assignee?: string
  priority: string
  createdAt: string
}

interface ProjectStats {
  totalIssues: number
  openIssues: number
  closedIssues: number
  inProgress: number
}

export default function Dashboard() {
  const [issues, setIssues] = useState<Issue[]>([])
  const [stats, setStats] = useState<ProjectStats | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    loadDashboardData()
  }, [])

  const loadDashboardData = async () => {
    try {
      setLoading(true)
      const [issuesData, statsData] = await Promise.all([
        fetchIssues(),
        fetchProjectStats(),
      ])
      setIssues(issuesData)
      setStats(statsData)
    } catch (err) {
      setError('Failed to load dashboard data')
      console.error('Dashboard load error:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button onClick={loadDashboardData} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {stats && <ProjectStats stats={stats} />}
        
        <div className="mt-8">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Issues</h2>
            <button onClick={loadDashboardData} className="btn-secondary">
              Refresh
            </button>
          </div>
          
          {issues.length === 0 ? (
            <div className="card text-center py-12">
              <p className="text-gray-500">No issues found. Connect your repositories to get started.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {issues.map((issue) => (
                <IssueCard key={issue.id} issue={issue} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

