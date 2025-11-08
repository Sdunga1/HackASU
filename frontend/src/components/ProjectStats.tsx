'use client'

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
  const completionRate = stats.totalIssues > 0 
    ? Math.round((stats.closedIssues / stats.totalIssues) * 100)
    : 0

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Total Issues</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{stats.totalIssues}</p>
          </div>
          <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
            <span className="text-2xl">📋</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Open</p>
            <p className="text-2xl font-bold text-green-600 mt-1">{stats.openIssues}</p>
          </div>
          <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center">
            <span className="text-2xl">🔓</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">In Progress</p>
            <p className="text-2xl font-bold text-blue-600 mt-1">{stats.inProgress}</p>
          </div>
          <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center">
            <span className="text-2xl">⚡</span>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-sm font-medium text-gray-600">Completion</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{completionRate}%</p>
          </div>
          <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center">
            <span className="text-2xl">✅</span>
          </div>
        </div>
      </div>
    </div>
  )
}

