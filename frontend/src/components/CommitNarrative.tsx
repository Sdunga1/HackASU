'use client'

import { useState, useEffect } from 'react'
import { useTheme } from '@/contexts/ThemeContext'

interface CommitEvent {
  timestamp: string
  type: 'commit' | 'pr' | 'review' | 'status' | 'comment'
  author: string
  title: string
  description: string
  details?: string
}

interface TicketNarrative {
  ticketId: string
  ticketTitle: string
  estimatedDays: number
  actualDays: number
  status: string
  narrative: string
  timeline: CommitEvent[]
  insights: {
    delays: string[]
    blockers: string[]
    resolutions: string[]
  }
}

const mockNarratives: TicketNarrative[] = [
  {
    ticketId: 'PROJ-1234',
    ticketTitle: 'Implement OAuth 2.0 Authentication',
    estimatedDays: 5,
    actualDays: 8,
    status: 'Done',
    narrative: 'This authentication feature took 8 days (3 days longer than estimated). Initial implementation was completed in 4 days, but security review revealed OAuth token handling issues. Developer Sarah Chen submitted fixes after 2 days of back-and-forth in PR #234. Final blocker was integration test failures that took 2 days to resolve due to staging environment issues (mentioned in commit abc123).',
    timeline: [
      {
        timestamp: '2024-01-15 09:00',
        type: 'status',
        author: 'System',
        title: 'Status changed to In Progress',
        description: 'Sarah Chen started working on the ticket'
      },
      {
        timestamp: '2024-01-16 14:30',
        type: 'commit',
        author: 'Sarah Chen',
        title: 'feat: Add OAuth client configuration',
        description: 'Initial setup of OAuth 2.0 client with provider configuration',
        details: 'Commit: a1b2c3d'
      },
      {
        timestamp: '2024-01-17 11:20',
        type: 'commit',
        author: 'Sarah Chen',
        title: 'feat: Implement token exchange flow',
        description: 'Added authorization code exchange and token storage',
        details: 'Commit: e4f5g6h'
      },
      {
        timestamp: '2024-01-19 16:45',
        type: 'pr',
        author: 'Sarah Chen',
        title: 'PR #234 opened',
        description: 'OAuth 2.0 Authentication Implementation',
        details: '234 lines added, 45 lines removed'
      },
      {
        timestamp: '2024-01-20 10:15',
        type: 'review',
        author: 'Mike Johnson',
        title: 'Security review requested changes',
        description: 'Token handling needs improvement - tokens should be encrypted at rest and use secure storage',
        details: 'PR #234'
      },
      {
        timestamp: '2024-01-20 15:30',
        type: 'comment',
        author: 'Sarah Chen',
        title: 'Response to review',
        description: 'Working on implementing secure token storage with encryption'
      },
      {
        timestamp: '2024-01-22 13:00',
        type: 'commit',
        author: 'Sarah Chen',
        title: 'fix: Add token encryption and secure storage',
        description: 'Implemented AES-256 encryption for token storage',
        details: 'Commit: abc123'
      },
      {
        timestamp: '2024-01-22 14:20',
        type: 'review',
        author: 'Mike Johnson',
        title: 'Approved security changes',
        description: 'Token encryption looks good. Ready to merge after tests pass'
      },
      {
        timestamp: '2024-01-23 09:00',
        type: 'comment',
        author: 'Sarah Chen',
        title: 'Integration tests failing',
        description: 'Tests are failing in staging due to environment configuration issues'
      },
      {
        timestamp: '2024-01-24 16:30',
        type: 'commit',
        author: 'Sarah Chen',
        title: 'fix: Update test configuration for staging',
        description: 'Fixed environment variable loading in test suite',
        details: 'Commit: xyz789'
      },
      {
        timestamp: '2024-01-25 11:00',
        type: 'pr',
        author: 'Mike Johnson',
        title: 'PR #234 merged',
        description: 'All checks passed. OAuth implementation merged to main'
      },
      {
        timestamp: '2024-01-25 11:15',
        type: 'status',
        author: 'System',
        title: 'Status changed to Done',
        description: 'Ticket completed and deployed'
      }
    ],
    insights: {
      delays: [
        'Security review added 2 days due to token handling concerns',
        'Staging environment issues caused 2-day delay in final testing',
        'Total delay: 3 days beyond estimate'
      ],
      blockers: [
        'OAuth token encryption requirements not identified during planning',
        'Staging environment configuration mismatch with production',
        'Integration test suite missing environment-specific configurations'
      ],
      resolutions: [
        'Implemented AES-256 encryption for secure token storage',
        'Updated test suite to handle multiple environments',
        'Documented staging environment setup for future reference'
      ]
    }
  },
  {
    ticketId: 'PROJ-1256',
    ticketTitle: 'Database Migration for User Preferences',
    estimatedDays: 3,
    actualDays: 6,
    status: 'Done',
    narrative: 'This database migration took 6 days (double the estimate). The initial migration script was completed in 2 days, but production deployment revealed performance issues with the indexing strategy. The team had to roll back and redesign the migration approach. A second attempt took 3 days and included database partitioning to handle the large dataset. Final deployment succeeded after extensive load testing.',
    timeline: [
      {
        timestamp: '2024-01-10 08:00',
        type: 'status',
        author: 'System',
        title: 'Status changed to In Progress',
        description: 'Alex Kim assigned and started work'
      },
      {
        timestamp: '2024-01-11 15:00',
        type: 'commit',
        author: 'Alex Kim',
        title: 'feat: Add user preferences schema',
        description: 'Created new tables for user preferences with foreign keys',
        details: 'Commit: def456'
      },
      {
        timestamp: '2024-01-12 10:30',
        type: 'pr',
        author: 'Alex Kim',
        title: 'PR #245 opened',
        description: 'Database migration for user preferences',
        details: 'Migration scripts and rollback procedures'
      },
      {
        timestamp: '2024-01-13 14:00',
        type: 'comment',
        author: 'DevOps Bot',
        title: 'Production deployment failed',
        description: 'Migration timeout after 30 minutes. Automatic rollback triggered'
      },
      {
        timestamp: '2024-01-14 09:00',
        type: 'commit',
        author: 'Alex Kim',
        title: 'feat: Add database partitioning',
        description: 'Implemented table partitioning by user_id ranges for better performance',
        details: 'Commit: ghi789'
      },
      {
        timestamp: '2024-01-15 16:00',
        type: 'review',
        author: 'Database Team',
        title: 'Architecture review approved',
        description: 'Partitioning strategy looks solid. Proceed with staged rollout'
      },
      {
        timestamp: '2024-01-16 11:00',
        type: 'status',
        author: 'System',
        title: 'Status changed to Done',
        description: 'Migration completed successfully in production'
      }
    ],
    insights: {
      delays: [
        'Production deployment failure added 3 days',
        'Performance issues required architecture redesign',
        'Total delay: 3 days beyond estimate'
      ],
      blockers: [
        'Initial migration strategy did not account for table size',
        'Missing performance testing in staging environment',
        'Production database had 10x more data than staging'
      ],
      resolutions: [
        'Implemented database partitioning for scalability',
        'Added comprehensive load testing to CI pipeline',
        'Created runbook for large-scale migrations'
      ]
    }
  },
  {
    ticketId: 'PROJ-1289',
    ticketTitle: 'Real-time Notification System',
    estimatedDays: 7,
    actualDays: 7,
    status: 'Done',
    narrative: 'This feature was completed exactly on schedule. The implementation went smoothly with WebSocket infrastructure set up in 3 days, followed by notification logic in 2 days, and UI integration in 2 days. The team proactively identified potential scaling issues during code review and addressed them before deployment. No major blockers encountered.',
    timeline: [
      {
        timestamp: '2024-01-08 09:00',
        type: 'status',
        author: 'System',
        title: 'Status changed to In Progress',
        description: 'Jennifer Lee started implementation'
      },
      {
        timestamp: '2024-01-10 14:00',
        type: 'commit',
        author: 'Jennifer Lee',
        title: 'feat: WebSocket server infrastructure',
        description: 'Set up WebSocket server with connection pooling',
        details: 'Commit: jkl012'
      },
      {
        timestamp: '2024-01-12 11:00',
        type: 'commit',
        author: 'Jennifer Lee',
        title: 'feat: Notification event handlers',
        description: 'Implemented event system for various notification types',
        details: 'Commit: mno345'
      },
      {
        timestamp: '2024-01-13 16:00',
        type: 'pr',
        author: 'Jennifer Lee',
        title: 'PR #267 opened',
        description: 'Real-time notification system implementation'
      },
      {
        timestamp: '2024-01-14 10:00',
        type: 'review',
        author: 'Tech Lead',
        title: 'Suggested optimization',
        description: 'Consider adding Redis pub/sub for horizontal scaling'
      },
      {
        timestamp: '2024-01-14 15:00',
        type: 'commit',
        author: 'Jennifer Lee',
        title: 'feat: Add Redis pub/sub integration',
        description: 'Integrated Redis for distributed notification broadcasting',
        details: 'Commit: pqr678'
      },
      {
        timestamp: '2024-01-15 13:00',
        type: 'status',
        author: 'System',
        title: 'Status changed to Done',
        description: 'Feature deployed and fully operational'
      }
    ],
    insights: {
      delays: [],
      blockers: [],
      resolutions: [
        'Proactively added Redis pub/sub for future scaling',
        'Implemented comprehensive error handling',
        'Added monitoring and alerting for WebSocket health'
      ]
    }
  }
]

export default function CommitNarrative() {
  const { theme } = useTheme()
  const isDark = theme === 'dark'
  const [selectedTicket, setSelectedTicket] = useState<TicketNarrative>(mockNarratives[0])
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(['timeline']))
  const [dataSource, setDataSource] = useState<'mock' | 'real'>('mock')
  const [realNarratives, setRealNarratives] = useState<TicketNarrative[]>([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  
  // Get current narratives based on data source
  const currentNarratives = dataSource === 'mock' ? mockNarratives : realNarratives

  // Fetch real-time narratives from backend
  const fetchRealNarratives = async () => {
    setLoading(true)
    setError(null)
    
    try {
      const response = await fetch('http://localhost:8000/api/narratives/list')
      const data = await response.json()
      
      if (data.status === 'success' && data.narratives.length > 0) {
        setRealNarratives(data.narratives)
        setDataSource('real')
        setSelectedTicket(data.narratives[0])
      } else {
        setError('No real-time narratives available. Generate narratives using the MCP tool.')
      }
    } catch (err) {
      console.error('Failed to fetch narratives:', err)
      setError('Failed to fetch real-time data. Make sure the backend is running.')
    } finally {
      setLoading(false)
    }
  }
  
  // Switch to mock data
  const switchToMock = () => {
    setDataSource('mock')
    setSelectedTicket(mockNarratives[0])
    setError(null)
  }
  
  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections)
    if (newExpanded.has(section)) {
      newExpanded.delete(section)
    } else {
      newExpanded.add(section)
    }
    setExpandedSections(newExpanded)
  }

  const getEventIcon = (type: string) => {
    switch (type) {
      case 'commit':
        return (
          <div 
            className="w-8 h-8 rounded-full flex items-center justify-center border" 
            style={{
              backgroundColor: isDark ? '#1e3a8a' : '#dbeafe',
              borderColor: isDark ? '#3b82f6' : '#3b82f6',
            }}
          >
            <svg className="w-4 h-4" style={{ color: isDark ? '#60a5fa' : '#2563eb' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
            </svg>
          </div>
        )
      case 'pr':
        return (
          <div 
            className="w-8 h-8 rounded-full flex items-center justify-center border"
            style={{
              backgroundColor: isDark ? '#581c87' : '#f3e8ff',
              borderColor: isDark ? '#a855f7' : '#9333ea',
            }}
          >
            <svg className="w-4 h-4" style={{ color: isDark ? '#c084fc' : '#9333ea' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7h12m0 0l-4-4m4 4l-4 4m0 6H4m0 0l4 4m-4-4l4-4" />
            </svg>
          </div>
        )
      case 'review':
        return (
          <div 
            className="w-8 h-8 rounded-full flex items-center justify-center border"
            style={{
              backgroundColor: isDark ? '#78350f' : '#fef3c7',
              borderColor: isDark ? '#f59e0b' : '#f59e0b',
            }}
          >
            <svg className="w-4 h-4" style={{ color: isDark ? '#fbbf24' : '#d97706' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
            </svg>
          </div>
        )
      case 'status':
        return (
          <div 
            className="w-8 h-8 rounded-full flex items-center justify-center border"
            style={{
              backgroundColor: isDark ? '#14532d' : '#dcfce7',
              borderColor: isDark ? '#22c55e' : '#16a34a',
            }}
          >
            <svg className="w-4 h-4" style={{ color: isDark ? '#4ade80' : '#16a34a' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
        )
      case 'comment':
        return (
          <div 
            className="w-8 h-8 rounded-full flex items-center justify-center border"
            style={{
              backgroundColor: isDark ? '#374151' : '#f3f4f6',
              borderColor: isDark ? '#6b7280' : '#9ca3af',
            }}
          >
            <svg className="w-4 h-4" style={{ color: isDark ? '#d1d5db' : '#6b7280' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
            </svg>
          </div>
        )
      default:
        return null
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'Done':
        return { bg: 'rgba(255, 198, 39, 0.15)', text: '#FFC627', border: 'rgba(255, 198, 39, 0.3)' }
      case 'In Progress':
        return { bg: 'rgba(140, 29, 64, 0.15)', text: '#FFC627', border: 'rgba(140, 29, 64, 0.5)' }
      default:
        return { bg: 'rgba(100, 100, 100, 0.15)', text: '#888', border: 'rgba(100, 100, 100, 0.3)' }
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Commit-to-Ticket Narratives</h2>
          <p className="mt-1" style={{ color: isDark ? '#aaa' : '#666' }}>AI-generated summaries of ticket progress and blockers</p>
        </div>
        
        <div className="flex items-center gap-3">
          <span className="text-sm" style={{ color: isDark ? '#aaa' : '#666' }}>Data Source:</span>
          <div className="flex gap-2">
            <button
              onClick={switchToMock}
              disabled={loading}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={{
                backgroundColor: dataSource === 'mock' 
                  ? (isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)')
                  : (isDark ? '#1a1a1a' : '#f5f5f5'),
                color: dataSource === 'mock' ? '#FFC627' : (isDark ? '#aaa' : '#666'),
                border: `1px solid ${dataSource === 'mock' ? '#8C1D40' : (isDark ? '#3a3a3a' : '#e5e5e5')}`
              }}
            >
              Mock Data
            </button>
            <button
              onClick={fetchRealNarratives}
              disabled={loading}
              className="px-4 py-2 rounded-lg text-sm font-medium transition-all"
              style={{
                backgroundColor: dataSource === 'real' 
                  ? (isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)')
                  : (isDark ? '#1a1a1a' : '#f5f5f5'),
                color: dataSource === 'real' ? '#FFC627' : (isDark ? '#aaa' : '#666'),
                border: `1px solid ${dataSource === 'real' ? '#8C1D40' : (isDark ? '#3a3a3a' : '#e5e5e5')}`
              }}
            >
              {loading ? 'Loading...' : 'Real-Time Data'}
            </button>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="p-4 rounded-lg" style={{
          backgroundColor: isDark ? 'rgba(239, 68, 68, 0.1)' : 'rgba(239, 68, 68, 0.05)',
          border: `1px solid ${isDark ? 'rgba(239, 68, 68, 0.3)' : 'rgba(239, 68, 68, 0.2)'}`,
          color: isDark ? '#fca5a5' : '#dc2626'
        }}>
          <div className="flex items-start gap-2">
            <svg className="w-5 h-5 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <div>
              <p className="font-medium">Error loading real-time data</p>
              <p className="text-sm mt-1">{error}</p>
            </div>
          </div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-1">
          <div className="p-0 rounded-lg overflow-hidden" style={{
            backgroundColor: isDark ? '#252525' : '#ffffff',
            border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
            boxShadow: isDark ? '0 2px 8px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.1)',
          }}>
            <div className="p-4" style={{ borderBottom: isDark ? '1px solid #3a3a3a' : '1px solid #e5e5e5' }}>
              <h3 className="font-semibold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Recent Tickets</h3>
            </div>
            <div style={{ borderTop: isDark ? '1px solid #3a3a3a' : '1px solid #e5e5e5' }}>
              {currentNarratives.length === 0 ? (
                <div className="p-8 text-center" style={{ color: isDark ? '#aaa' : '#666' }}>
                  <p>No narratives available</p>
                  <p className="text-sm mt-2">Click "Real-Time Data" to load from backend</p>
                </div>
              ) : (
                currentNarratives.map((ticket, index) => (
                <button
                  key={ticket.ticketId}
                  onClick={() => setSelectedTicket(ticket)}
                  className="w-full text-left p-4 transition-colors"
                  style={{
                    backgroundColor: selectedTicket.ticketId === ticket.ticketId
                      ? isDark
                        ? 'rgba(140, 29, 64, 0.3)'
                        : 'rgba(140, 29, 64, 0.15)'
                      : 'transparent',
                    borderTop: index > 0 ? (isDark ? '1px solid #3a3a3a' : '1px solid #e5e5e5') : 'none',
                  }}
                  onMouseEnter={(e) => {
                    if (selectedTicket.ticketId !== ticket.ticketId) {
                      e.currentTarget.style.backgroundColor = isDark 
                        ? 'rgba(140, 29, 64, 0.15)' 
                        : 'rgba(140, 29, 64, 0.08)';
                    }
                  }}
                  onMouseLeave={(e) => {
                    if (selectedTicket.ticketId !== ticket.ticketId) {
                      e.currentTarget.style.backgroundColor = 'transparent';
                    }
                  }}
                >
                  <div className="flex items-start justify-between mb-2">
                    <span className="text-sm font-mono" style={{ color: isDark ? '#aaa' : '#666' }}>{ticket.ticketId}</span>
                    <span className="text-xs px-2 py-1 rounded-full border" style={{
                      backgroundColor: getStatusColor(ticket.status).bg,
                      color: getStatusColor(ticket.status).text,
                      borderColor: getStatusColor(ticket.status).border
                    }}>
                      {ticket.status}
                    </span>
                  </div>
                  <p className="text-sm font-medium mb-2" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{ticket.ticketTitle}</p>
                  <div className="flex items-center gap-4 text-xs" style={{ color: isDark ? '#aaa' : '#666' }}>
                    <span>Est: {ticket.estimatedDays}d</span>
                    <span>Act: {ticket.actualDays}d</span>
                    {ticket.actualDays > ticket.estimatedDays && (
                      <span className="font-medium" style={{ color: isDark ? '#ef4444' : '#dc2626' }}>
                        +{ticket.actualDays - ticket.estimatedDays}d
                      </span>
                    )}
                  </div>
                </button>
              )))}
            </div>
          </div>
        </div>

        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-lg p-6" style={{
            backgroundColor: isDark ? '#252525' : '#ffffff',
            border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
            boxShadow: isDark ? '0 2px 8px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.1)',
          }}>
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className="flex items-center gap-3 mb-2">
                  <h3 className="text-xl font-bold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{selectedTicket.ticketId}</h3>
                  <span className="text-sm px-3 py-1 rounded-full border" style={{
                    backgroundColor: getStatusColor(selectedTicket.status).bg,
                    color: getStatusColor(selectedTicket.status).text,
                    borderColor: getStatusColor(selectedTicket.status).border
                  }}>
                    {selectedTicket.status}
                  </span>
                </div>
                <p className="font-medium" style={{ color: isDark ? '#e5e5e5' : '#333' }}>{selectedTicket.ticketTitle}</p>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-4 p-4 rounded-lg" style={{
              backgroundColor: isDark ? 'rgba(140, 29, 64, 0.25)' : 'rgba(140, 29, 64, 0.15)',
              border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.4)' : 'rgba(140, 29, 64, 0.3)'}`,
            }}>
              <div>
                <p className="text-xs mb-1" style={{ color: isDark ? '#aaa' : '#666' }}>Estimated</p>
                <p className="text-2xl font-bold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{selectedTicket.estimatedDays}d</p>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: isDark ? '#aaa' : '#666' }}>Actual</p>
                <p className="text-2xl font-bold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{selectedTicket.actualDays}d</p>
              </div>
              <div>
                <p className="text-xs mb-1" style={{ color: isDark ? '#aaa' : '#666' }}>Variance</p>
                <p className="text-2xl font-bold" style={{
                  color: selectedTicket.actualDays > selectedTicket.estimatedDays 
                    ? (isDark ? '#ef4444' : '#dc2626')
                    : (isDark ? '#22c55e' : '#16a34a')
                }}>
                  {selectedTicket.actualDays > selectedTicket.estimatedDays ? '+' : ''}
                  {selectedTicket.actualDays - selectedTicket.estimatedDays}d
                </p>
              </div>
            </div>

            <div className="mt-6">
              <h4 className="text-sm font-semibold mb-2" style={{ color: isDark ? '#e5e5e5' : '#333' }}>AI-Generated Narrative</h4>
              <div className="p-4 rounded" style={{
                backgroundColor: isDark ? 'rgba(140, 29, 64, 0.25)' : 'rgba(140, 29, 64, 0.12)',
                borderLeft: '4px solid #8C1D40'
              }}>
                <p className="leading-relaxed" style={{ color: isDark ? '#e5e5e5' : '#1a1a1a' }}>{selectedTicket.narrative}</p>
              </div>
            </div>
          </div>

          <div className="rounded-lg p-6" style={{
            backgroundColor: isDark ? '#252525' : '#ffffff',
            border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
            boxShadow: isDark ? '0 2px 8px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.1)',
          }}>
            <button
              onClick={() => toggleSection('timeline')}
              className="w-full flex items-center justify-between mb-4"
            >
              <h4 className="text-lg font-semibold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>Timeline</h4>
              <svg
                className={`w-5 h-5 transform transition-transform ${
                  expandedSections.has('timeline') ? 'rotate-180' : ''
                }`}
                style={{ color: isDark ? '#aaa' : '#666' }}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {expandedSections.has('timeline') && (
              <div className="space-y-4">
                {selectedTicket.timeline.map((event, index) => (
                  <div key={index} className="flex gap-4">
                    <div className="flex flex-col items-center">
                      {getEventIcon(event.type)}
                      {index < selectedTicket.timeline.length - 1 && (
                        <div className="w-0.5 h-full mt-2" style={{ backgroundColor: isDark ? '#444' : '#d1d5db' }}></div>
                      )}
                    </div>
                    <div className="flex-1 pb-6">
                      <div className="flex items-start justify-between mb-1">
                        <p className="font-medium" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>{event.title}</p>
                        <span className="text-xs" style={{ color: isDark ? '#888' : '#999' }}>{event.timestamp}</span>
                      </div>
                      <p className="text-sm mb-1" style={{ color: isDark ? '#aaa' : '#666' }}>{event.description}</p>
                      {event.details && (
                        <p className="text-xs font-mono" style={{ color: isDark ? '#888' : '#999' }}>{event.details}</p>
                      )}
                      <p className="text-xs mt-1" style={{ color: isDark ? '#888' : '#999' }}>{event.author}</p>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="rounded-lg p-6" style={{
            backgroundColor: isDark ? '#252525' : '#ffffff',
            border: `1px solid ${isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'}`,
            boxShadow: isDark ? '0 2px 8px rgba(0, 0, 0, 0.3)' : '0 2px 8px rgba(0, 0, 0, 0.1)',
          }}>
            <button
              onClick={() => toggleSection('insights')}
              className="w-full flex items-center justify-between mb-4"
            >
              <h4 className="text-lg font-semibold" style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>AI Insights</h4>
              <svg
                className={`w-5 h-5 transform transition-transform ${
                  expandedSections.has('insights') ? 'rotate-180' : ''
                }`}
                style={{ color: isDark ? '#aaa' : '#666' }}
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
              </svg>
            </button>

            {expandedSections.has('insights') && (
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {selectedTicket.insights.delays.length > 0 && (
                  <div>
                    <h5 className="text-sm font-semibold mb-2" style={{ color: '#8C1D40' }}>Delays</h5>
                    <ul className="space-y-2">
                      {selectedTicket.insights.delays.map((delay, index) => (
                        <li key={index} className="text-sm pl-4" style={{ 
                          color: isDark ? '#e5e5e5' : '#333',
                          borderLeft: '2px solid #8C1D40' 
                        }}>
                          {delay}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {selectedTicket.insights.blockers.length > 0 && (
                  <div>
                    <h5 className="text-sm font-semibold mb-2" style={{ color: '#FFC627' }}>Blockers</h5>
                    <ul className="space-y-2">
                      {selectedTicket.insights.blockers.map((blocker, index) => (
                        <li key={index} className="text-sm pl-4" style={{ 
                          color: isDark ? '#e5e5e5' : '#333',
                          borderLeft: '2px solid #FFC627' 
                        }}>
                          {blocker}
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                <div>
                  <h5 className="text-sm font-semibold mb-2" style={{ color: '#FFC627' }}>Resolutions</h5>
                  <ul className="space-y-2">
                    {selectedTicket.insights.resolutions.map((resolution, index) => (
                      <li key={index} className="text-sm pl-4" style={{ 
                        color: isDark ? '#e5e5e5' : '#333',
                        borderLeft: '2px solid #FFC627' 
                      }}>
                        {resolution}
                      </li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

