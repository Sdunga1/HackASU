'use client'

import { useState } from 'react'
import { useTheme } from '@/contexts/ThemeContext'

interface Anomaly {
  id: string
  type: 'stale_ticket' | 'scope_creep' | 'missing_link' | 'status_mismatch' | 'task_switching'
  severity: 'high' | 'medium' | 'low'
  title: string
  description: string
  affectedItems: {
    tickets?: string[]
    developers?: string[]
    prs?: string[]
    commits?: string[]
  }
  detectedAt: string
  aiAnalysis: string
  suggestedActions: string[]
  metrics?: {
    label: string
    value: string
    trend?: 'up' | 'down' | 'stable'
  }[]
}

const mockAnomalies: Anomaly[] = [
  {
    id: 'ANOM-001',
    type: 'stale_ticket',
    severity: 'high',
    title: 'Ticket in Progress with No Recent Commits',
    description: 'PROJ-1423 has been "In Progress" for 5 days with zero commits',
    affectedItems: {
      tickets: ['PROJ-1423'],
      developers: ['Marcus Rodriguez']
    },
    detectedAt: '2024-01-25 14:30',
    aiAnalysis: 'This ticket shows signs of being blocked or abandoned. The developer Marcus Rodriguez has not made any commits to this ticket in 5 days despite it being marked as "In Progress". This pattern often indicates one of three scenarios: (1) the developer is blocked by external dependencies, (2) the work is more complex than estimated, or (3) the developer has been pulled into other priorities. The lack of activity combined with no status updates or comments suggests poor communication.',
    suggestedActions: [
      'Reach out to Marcus Rodriguez to understand current status',
      'Check if there are blocking dependencies in other tickets',
      'Consider moving ticket back to "To Do" if work hasn\'t started',
      'Update ticket with current blockers or progress notes'
    ],
    metrics: [
      { label: 'Days Inactive', value: '5', trend: 'up' },
      { label: 'Expected Completion', value: '2 days ago', trend: 'down' },
      { label: 'Team Average', value: '1.5 days', trend: 'stable' }
    ]
  },
  {
    id: 'ANOM-002',
    type: 'scope_creep',
    severity: 'high',
    title: 'High Commit Activity on Completed Ticket',
    description: 'PROJ-1389 marked "Done" but has 12 commits in the last 3 days',
    affectedItems: {
      tickets: ['PROJ-1389'],
      developers: ['Sarah Chen', 'Mike Johnson'],
      commits: ['a1b2c3d', 'e4f5g6h', 'i7j8k9l', '+9 more']
    },
    detectedAt: '2024-01-25 11:15',
    aiAnalysis: 'This completed ticket is showing unexpected continued development activity. PROJ-1389 was marked "Done" on January 20th, but has received 12 commits since then from two different developers. This pattern indicates either: (1) significant bugs were discovered post-completion, (2) the scope of the original ticket was incomplete, or (3) new requirements are being added without creating a new ticket. This is a process violation that makes it difficult to track true completion metrics and can hide scope creep.',
    suggestedActions: [
      'Review commits to determine if they are bug fixes or new features',
      'Create new tickets for any new feature work',
      'Consider reopening the ticket if work is substantial',
      'Update ticket documentation to reflect actual work completed'
    ],
    metrics: [
      { label: 'Commits After Done', value: '12', trend: 'up' },
      { label: 'Developers Involved', value: '2', trend: 'up' },
      { label: 'Lines Changed', value: '234', trend: 'up' }
    ]
  },
  {
    id: 'ANOM-003',
    type: 'missing_link',
    severity: 'medium',
    title: 'Pull Request Merged Without Linked Ticket',
    description: 'PR #289 merged with no associated Jira ticket reference',
    affectedItems: {
      prs: ['#289'],
      developers: ['Alex Kim']
    },
    detectedAt: '2024-01-24 16:45',
    aiAnalysis: 'Pull request #289 was merged without any Jira ticket reference in the PR description, branch name, or commit messages. This represents a process compliance issue. While the changes may be legitimate, the lack of ticket tracking makes it impossible to: (1) understand the business context for these changes, (2) track time spent on this work, (3) include this work in sprint metrics, and (4) trace requirements to implementation. The PR title "Update user profile validation" suggests this should have been tracked work.',
    suggestedActions: [
      'Retroactively create a ticket for this work if substantial',
      'Link the PR to the appropriate ticket if one exists',
      'Remind Alex Kim about ticket linking requirements',
      'Consider adding automated PR checks to enforce ticket references'
    ],
    metrics: [
      { label: 'Files Changed', value: '7', trend: 'stable' },
      { label: 'Lines Added', value: '142', trend: 'stable' },
      { label: 'Days Since Merge', value: '1', trend: 'stable' }
    ]
  },
  {
    id: 'ANOM-004',
    type: 'status_mismatch',
    severity: 'high',
    title: 'Ticket in Review with No Open Pull Requests',
    description: 'PROJ-1467 status is "In Review" but no associated PRs are open',
    affectedItems: {
      tickets: ['PROJ-1467'],
      developers: ['Jennifer Lee']
    },
    detectedAt: '2024-01-25 09:00',
    aiAnalysis: 'Ticket PROJ-1467 has been in "In Review" status for 2 days, but there are no open pull requests linked to this ticket. This is a status mismatch that suggests: (1) the PR was created but not properly linked, (2) the ticket status was changed prematurely, or (3) the review process is happening outside of the normal PR workflow. This makes it impossible to track what is actually being reviewed and prevents automated code review workflows from functioning properly.',
    suggestedActions: [
      'Verify if a PR exists and link it to the ticket',
      'Check if review is happening through another channel',
      'Move ticket back to "In Progress" if PR not yet created',
      'Establish clear criteria for moving tickets to "In Review" status'
    ],
    metrics: [
      { label: 'Days in Review', value: '2', trend: 'up' },
      { label: 'Linked PRs', value: '0', trend: 'stable' },
      { label: 'Average Review Time', value: '1.5 days', trend: 'stable' }
    ]
  },
  {
    id: 'ANOM-005',
    type: 'task_switching',
    severity: 'medium',
    title: 'High Task Switching Detected',
    description: 'Marcus Rodriguez has 45 commits across 8 different tickets in the last 5 days',
    affectedItems: {
      developers: ['Marcus Rodriguez'],
      tickets: ['PROJ-1423', 'PROJ-1445', 'PROJ-1467', 'PROJ-1489', 'PROJ-1501', '+3 more']
    },
    detectedAt: '2024-01-25 13:20',
    aiAnalysis: 'Marcus Rodriguez is showing a high degree of task switching, with commits distributed across 8 different tickets in just 5 days. While the commit count (45) seems healthy, the lack of ticket completion suggests fragmented focus. This pattern typically indicates: (1) frequent context switching reducing productivity, (2) being pulled into multiple urgent issues, (3) working on dependencies across multiple features, or (4) helping others with code reviews and debugging. Only 1 of these 8 tickets has been completed, suggesting efficiency concerns.',
    suggestedActions: [
      'Review Marcus\'s workload and help prioritize tasks',
      'Identify if task switching is due to blockers or interruptions',
      'Consider assigning fewer concurrent tickets',
      'Check if Marcus is being pulled into too many support requests',
      'Schedule 1-on-1 to understand context switching drivers'
    ],
    metrics: [
      { label: 'Active Tickets', value: '8', trend: 'up' },
      { label: 'Completed Tickets', value: '1', trend: 'down' },
      { label: 'Avg Focus Time', value: '0.6 days', trend: 'down' },
      { label: 'Team Average', value: '2.3 tickets', trend: 'stable' }
    ]
  },
  {
    id: 'ANOM-006',
    type: 'stale_ticket',
    severity: 'low',
    title: 'Long-Running Feature Branch',
    description: 'Feature branch for PROJ-1398 has been active for 14 days without merge',
    affectedItems: {
      tickets: ['PROJ-1398'],
      developers: ['Sarah Chen'],
      prs: ['#276']
    },
    detectedAt: '2024-01-25 10:30',
    aiAnalysis: 'The feature branch for PROJ-1398 has been open for 14 days with regular commits but no merge to main. This long-running branch pattern can lead to: (1) difficult merge conflicts as main branch evolves, (2) delayed feedback on architectural decisions, (3) integration issues discovered late, and (4) work that may need significant refactoring. The commit history shows steady progress, but the extended timeline suggests either a very large feature or potential scope issues.',
    suggestedActions: [
      'Break down remaining work into smaller, mergeable chunks',
      'Consider feature flags to merge work-in-progress to main',
      'Review if original scope can be split into multiple tickets',
      'Ensure regular rebasing to minimize merge conflict risk'
    ],
    metrics: [
      { label: 'Days Open', value: '14', trend: 'up' },
      { label: 'Commits Behind Main', value: '47', trend: 'up' },
      { label: 'Files Changed', value: '23', trend: 'stable' }
    ]
  }
]

export default function AnomalyDetector() {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const [selectedAnomaly, setSelectedAnomaly] = useState<Anomaly | null>(null)
  const [filterSeverity, setFilterSeverity] = useState<'all' | 'high' | 'medium' | 'low'>('all')
  const [filterType, setFilterType] = useState<string>('all')

  const filteredAnomalies = mockAnomalies.filter(anomaly => {
    const severityMatch = filterSeverity === 'all' || anomaly.severity === filterSeverity
    const typeMatch = filterType === 'all' || anomaly.type === filterType
    return severityMatch && typeMatch
  })

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return { bg: 'rgba(239, 68, 68, 0.2)', text: '#ef4444', border: 'rgba(239, 68, 68, 0.5)' }
      case 'medium':
        return { bg: 'rgba(255, 198, 39, 0.15)', text: '#FFC627', border: 'rgba(255, 198, 39, 0.4)' }
      case 'low':
        return { bg: 'rgba(140, 29, 64, 0.1)', text: '#aaa', border: 'rgba(140, 29, 64, 0.3)' }
      default:
        return { bg: 'rgba(100, 100, 100, 0.15)', text: '#888', border: 'rgba(100, 100, 100, 0.3)' }
    }
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return (
          <svg className="w-5 h-5" style={{ color: '#ef4444' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      case 'medium':
        return (
          <svg className="w-5 h-5" style={{ color: '#FFC627' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      case 'low':
        return (
          <svg className="w-5 h-5" style={{ color: '#888' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      default:
        return null
    }
  }

  const getTypeLabel = (type: string) => {
    const labels: Record<string, string> = {
      stale_ticket: 'Stale Ticket',
      scope_creep: 'Scope Creep',
      missing_link: 'Missing Link',
      status_mismatch: 'Status Mismatch',
      task_switching: 'Task Switching'
    }
    return labels[type] || type
  }

  const anomalyTypeCount = mockAnomalies.reduce((acc, anomaly) => {
    acc[anomaly.type] = (acc[anomaly.type] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  const severityCount = mockAnomalies.reduce((acc, anomaly) => {
    acc[anomaly.severity] = (acc[anomaly.severity] || 0) + 1
    return acc
  }, {} as Record<string, number>)

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Cross-Platform Anomaly Detection</h2>
          <p className="mt-1" style={{ color: isDark ? '#aaa' : '#666' }}>AI-powered detection of workflow issues across GitHub and Jira</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>Total Anomalies</p>
              <p className="text-3xl font-bold mt-1" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{mockAnomalies.length}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
              backgroundColor: isDark ? 'rgba(100, 100, 100, 0.2)' : 'rgba(100, 100, 100, 0.1)',
              border: `1px solid ${isDark ? 'rgba(100, 100, 100, 0.3)' : 'rgba(100, 100, 100, 0.2)'}`
            }}>
              <svg className="w-6 h-6" style={{ color: isDark ? '#aaa' : '#666' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>High Severity</p>
              <p className="text-3xl font-bold mt-1" style={{ color: '#ef4444' }}>{severityCount.high || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
              backgroundColor: 'rgba(239, 68, 68, 0.3)',
              border: '1px solid rgba(239, 68, 68, 0.5)'
            }}>
              <svg className="w-6 h-6" style={{ color: '#ef4444' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>Medium Severity</p>
              <p className="text-3xl font-bold mt-1" style={{ color: '#FFC627' }}>{severityCount.medium || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
              backgroundColor: 'rgba(255, 198, 39, 0.15)',
              border: '1px solid rgba(255, 198, 39, 0.4)'
            }}>
              <svg className="w-6 h-6" style={{ color: '#FFC627' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>Low Severity</p>
              <p className="text-3xl font-bold mt-1" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{severityCount.low || 0}</p>
            </div>
            <div className="w-12 h-12 rounded-lg flex items-center justify-center" style={{
              backgroundColor: 'rgba(140, 29, 64, 0.15)',
              border: '1px solid rgba(140, 29, 64, 0.3)'
            }}>
              <svg className="w-6 h-6" style={{ color: '#888' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div className="card">
        <div className="flex items-center gap-4 mb-6">
          <div>
            <label className="text-sm font-medium mb-1 block" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Severity</label>
            <select
              value={filterSeverity}
              onChange={(e) => setFilterSeverity(e.target.value as any)}
              className="px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              style={{
                backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
                border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
                color: isDark ? '#f5f5f5' : '#1a1a1a'
              }}
            >
              <option value="all">All Severities</option>
              <option value="high">High</option>
              <option value="medium">Medium</option>
              <option value="low">Low</option>
            </select>
          </div>

          <div>
            <label className="text-sm font-medium mb-1 block" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Type</label>
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="px-4 py-2 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              style={{
                backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
                border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
                color: isDark ? '#f5f5f5' : '#1a1a1a'
              }}
            >
              <option value="all">All Types</option>
              <option value="stale_ticket">Stale Tickets</option>
              <option value="scope_creep">Scope Creep</option>
              <option value="missing_link">Missing Links</option>
              <option value="status_mismatch">Status Mismatch</option>
              <option value="task_switching">Task Switching</option>
            </select>
          </div>
        </div>

        <div className="space-y-3">
          {filteredAnomalies.map((anomaly) => (
            <div
              key={anomaly.id}
              className="rounded-lg p-4 hover:shadow-xl transition-all cursor-pointer"
              style={{
                border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
                backgroundColor: isDark ? '#252525' : '#ffffff',
              }}
              onClick={() => setSelectedAnomaly(anomaly)}
              onMouseEnter={(e) => {
                e.currentTarget.style.borderColor = isDark ? 'rgba(140, 29, 64, 0.5)' : 'rgba(140, 29, 64, 0.4)'
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.borderColor = isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'
              }}
            >
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-start gap-3 flex-1">
                  {getSeverityIcon(anomaly.severity)}
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{anomaly.title}</h3>
                      <span className="text-xs px-2 py-1 rounded-full border" style={{
                        backgroundColor: getSeverityColor(anomaly.severity).bg,
                        color: getSeverityColor(anomaly.severity).text,
                        borderColor: getSeverityColor(anomaly.severity).border
                      }}>
                        {anomaly.severity.toUpperCase()}
                      </span>
                      <span className="text-xs px-2 py-1 rounded-full border" style={{
                        backgroundColor: isDark ? 'rgba(100, 100, 100, 0.15)' : 'rgba(100, 100, 100, 0.1)',
                        color: isDark ? '#aaa' : '#666',
                        borderColor: isDark ? 'rgba(100, 100, 100, 0.3)' : 'rgba(100, 100, 100, 0.2)'
                      }}>
                        {getTypeLabel(anomaly.type)}
                      </span>
                    </div>
                    <p className="text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>{anomaly.description}</p>
                  </div>
                </div>
                <span className="text-xs whitespace-nowrap ml-4" style={{ color: isDark ? '#888' : '#999' }}>{anomaly.detectedAt}</span>
              </div>

              <div className="flex flex-wrap gap-2 text-xs">
                {anomaly.affectedItems.tickets && (
                  <div className="flex items-center gap-1" style={{ color: isDark ? '#aaa' : '#666' }}>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z" />
                    </svg>
                    <span>{anomaly.affectedItems.tickets.join(', ')}</span>
                  </div>
                )}
                {anomaly.affectedItems.developers && (
                  <div className="flex items-center gap-1" style={{ color: isDark ? '#aaa' : '#666' }}>
                    <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                    <span>{anomaly.affectedItems.developers.join(', ')}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {selectedAnomaly && (
        <div 
          className="fixed inset-0 flex items-center justify-center p-4 z-50" 
          style={{ backgroundColor: isDark ? 'rgba(0, 0, 0, 0.75)' : 'rgba(0, 0, 0, 0.5)' }}
          onClick={() => setSelectedAnomaly(null)}
        >
          <div 
            className="rounded-lg max-w-4xl w-full max-h-[90vh] overflow-y-auto" 
            style={{
              backgroundColor: isDark ? '#252525' : '#ffffff',
              border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
            }}
            onClick={(e) => e.stopPropagation()}
          >
            <div 
              className="sticky top-0 p-6 flex items-start justify-between"
              style={{
                backgroundColor: isDark ? '#252525' : '#ffffff',
                borderBottom: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
              }}
            >
              <div className="flex-1">
                <div className="flex items-center gap-3 mb-2">
                  {getSeverityIcon(selectedAnomaly.severity)}
                  <h2 className="text-2xl font-bold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{selectedAnomaly.title}</h2>
                </div>
                <div className="flex items-center gap-2">
                  <span className="text-sm px-3 py-1 rounded-full border" style={{
                    backgroundColor: getSeverityColor(selectedAnomaly.severity).bg,
                    color: getSeverityColor(selectedAnomaly.severity).text,
                    borderColor: getSeverityColor(selectedAnomaly.severity).border
                  }}>
                    {selectedAnomaly.severity.toUpperCase()}
                  </span>
                  <span className="text-sm px-3 py-1 rounded-full border" style={{
                    backgroundColor: isDark ? 'rgba(100, 100, 100, 0.15)' : 'rgba(100, 100, 100, 0.1)',
                    color: isDark ? '#aaa' : '#666',
                    borderColor: isDark ? 'rgba(100, 100, 100, 0.3)' : 'rgba(100, 100, 100, 0.2)'
                  }}>
                    {getTypeLabel(selectedAnomaly.type)}
                  </span>
                  <span className="text-sm" style={{ color: isDark ? '#888' : '#999' }}>{selectedAnomaly.detectedAt}</span>
                </div>
              </div>
              <button
                onClick={() => setSelectedAnomaly(null)}
                style={{ color: isDark ? '#aaa' : '#666' }}
                className="transition-colors hover:opacity-70"
                onMouseEnter={(e) => e.currentTarget.style.color = isDark ? '#f5f5f5' : '#1a1a1a'}
                onMouseLeave={(e) => e.currentTarget.style.color = isDark ? '#aaa' : '#666'}
              >
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <div className="p-6 space-y-6">
              <div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Description</h3>
                <p style={{ color: isDark ? '#aaa' : '#666' }}>{selectedAnomaly.description}</p>
              </div>

              {selectedAnomaly.metrics && selectedAnomaly.metrics.length > 0 && (
                <div>
                  <h3 className="text-lg font-semibold mb-3" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Metrics</h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                    {selectedAnomaly.metrics.map((metric, index) => (
                      <div 
                        key={index} 
                        className="p-4 rounded-lg"
                        style={{
                          backgroundColor: isDark ? '#1a1a1a' : '#f5f5f5',
                          border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`
                        }}
                      >
                        <p className="text-sm mb-1" style={{ color: isDark ? '#aaa' : '#666' }}>{metric.label}</p>
                        <div className="flex items-center gap-2">
                          <p className="text-2xl font-bold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{metric.value}</p>
                          {metric.trend === 'up' && (
                            <svg className="w-5 h-5" style={{ color: '#ef4444' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" />
                            </svg>
                          )}
                          {metric.trend === 'down' && (
                            <svg className="w-5 h-5" style={{ color: '#22c55e' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 17h8m0 0V9m0 8l-8-8-4 4-6-6" />
                            </svg>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <h3 className="text-lg font-semibold mb-2" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>AI Analysis</h3>
                <div 
                  className="p-4 rounded"
                  style={{
                    backgroundColor: isDark ? 'rgba(140, 29, 64, 0.2)' : 'rgba(140, 29, 64, 0.1)',
                    borderLeft: '4px solid #8C1D40'
                  }}
                >
                  <p className="leading-relaxed" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{selectedAnomaly.aiAnalysis}</p>
                </div>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Suggested Actions</h3>
                <ul className="space-y-2">
                  {selectedAnomaly.suggestedActions.map((action, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <svg className="w-5 h-5 mt-0.5 flex-shrink-0" style={{ color: '#FFC627' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                      <span style={{ color: isDark ? '#aaa' : '#666' }}>{action}</span>
                    </li>
                  ))}
                </ul>
              </div>

              <div>
                <h3 className="text-lg font-semibold mb-3" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Affected Items</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {selectedAnomaly.affectedItems.tickets && (
                    <div>
                      <h4 className="text-sm font-medium mb-2" style={{ color: isDark ? '#aaa' : '#666' }}>Tickets</h4>
                      <div className="space-y-1">
                        {selectedAnomaly.affectedItems.tickets.map((ticket, index) => (
                          <div 
                            key={index} 
                            className="text-sm font-mono px-3 py-1 rounded"
                            style={{
                              backgroundColor: isDark ? '#1a1a1a' : '#f5f5f5',
                              color: isDark ? '#f5f5f5' : '#1a1a1a',
                              border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`
                            }}
                          >
                            {ticket}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedAnomaly.affectedItems.developers && (
                    <div>
                      <h4 className="text-sm font-medium mb-2" style={{ color: isDark ? '#aaa' : '#666' }}>Developers</h4>
                      <div className="space-y-1">
                        {selectedAnomaly.affectedItems.developers.map((dev, index) => (
                          <div 
                            key={index} 
                            className="text-sm px-3 py-1 rounded"
                            style={{
                              backgroundColor: isDark ? '#1a1a1a' : '#f5f5f5',
                              color: isDark ? '#f5f5f5' : '#1a1a1a',
                              border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`
                            }}
                          >
                            {dev}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedAnomaly.affectedItems.prs && (
                    <div>
                      <h4 className="text-sm font-medium mb-2" style={{ color: isDark ? '#aaa' : '#666' }}>Pull Requests</h4>
                      <div className="space-y-1">
                        {selectedAnomaly.affectedItems.prs.map((pr, index) => (
                          <div 
                            key={index} 
                            className="text-sm font-mono px-3 py-1 rounded"
                            style={{
                              backgroundColor: isDark ? '#1a1a1a' : '#f5f5f5',
                              color: isDark ? '#f5f5f5' : '#1a1a1a',
                              border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`
                            }}
                          >
                            {pr}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                  {selectedAnomaly.affectedItems.commits && (
                    <div>
                      <h4 className="text-sm font-medium mb-2" style={{ color: isDark ? '#aaa' : '#666' }}>Commits</h4>
                      <div className="space-y-1">
                        {selectedAnomaly.affectedItems.commits.map((commit, index) => (
                          <div 
                            key={index} 
                            className="text-sm font-mono px-3 py-1 rounded"
                            style={{
                              backgroundColor: isDark ? '#1a1a1a' : '#f5f5f5',
                              color: isDark ? '#f5f5f5' : '#1a1a1a',
                              border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`
                            }}
                          >
                            {commit}
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

