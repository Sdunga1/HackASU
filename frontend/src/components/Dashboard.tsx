'use client';

import { useEffect, useState } from 'react';
import Header from './Header';
import IssueCard from './IssueCard';
import ProjectStats from './ProjectStats';
import CommitNarrative from './CommitNarrative';
import AnomalyDetector from './AnomalyDetector';
import { Chatbot } from './Chatbot';
import { fetchIssues, fetchProjectStats } from '@/lib/api';
import { useTheme } from '@/contexts/ThemeContext';

interface Issue {
  id: string;
  title: string;
  status: string;
  assignee?: string;
  priority: string;
  createdAt: string;
}

interface ProjectStats {
  totalIssues: number;
  openIssues: number;
  closedIssues: number;
  inProgress: number;
}

type TabType = 'overview' | 'narratives' | 'anomalies';

export default function Dashboard() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [issues, setIssues] = useState<Issue[]>([]);
  const [stats, setStats] = useState<ProjectStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isChatOpen, setIsChatOpen] = useState(false);

  useEffect(() => {
    loadDashboardData();

    // Setup WebSocket for real-time updates
    const wsUrl =
      process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') ||
      'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/dashboard/ws`);

    const messageHandler = (event: MessageEvent) => {
      const message = JSON.parse(event.data);
      if (message.type === 'issues_update' || message.type === 'initial_data') {
        if (message.data.issues && message.data.issues.length > 0) {
          setIssues(message.data.issues);
          console.log(
            'Real-time update received:',
            message.data.issues.length,
            'issues'
          );
        }
      }
    };

    const errorHandler = (error: Event) => {
      console.log(
        'WebSocket error (this is normal if backend is not running):',
        error
      );
    };

    ws.addEventListener('message', messageHandler);
    ws.addEventListener('error', errorHandler);

    return () => {
      // Proper cleanup: remove event listeners before closing
      ws.removeEventListener('message', messageHandler);
      ws.removeEventListener('error', errorHandler);

      // Close WebSocket connection
      if (
        ws.readyState === WebSocket.OPEN ||
        ws.readyState === WebSocket.CONNECTING
      ) {
        ws.close(1000, 'Component unmounting');
      }
    };
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      const [issuesData, statsData] = await Promise.all([
        fetchIssues(),
        fetchProjectStats(),
      ]);
      setIssues(issuesData);
      setStats(statsData);
    } catch (err) {
      setError('Failed to load dashboard data');
      console.error('Dashboard load error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div
        className="flex items-center justify-center min-h-screen"
        style={{ backgroundColor: isDark ? '#0a0a0a' : '#f5f5f5' }}
      >
        <div className="text-center">
          <div
            className="animate-spin rounded-full h-12 w-12 border-b-2 mx-auto"
            style={{ borderColor: '#FFC627' }}
          ></div>
          <p className="mt-4" style={{ color: isDark ? '#aaa' : '#666' }}>
            Loading dashboard...
          </p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div
        className="flex items-center justify-center min-h-screen"
        style={{ backgroundColor: isDark ? '#0a0a0a' : '#f5f5f5' }}
      >
        <div className="text-center">
          <p className="mb-4" style={{ color: '#FFC627' }}>
            {error}
          </p>
          <button onClick={loadDashboardData} className="btn-primary">
            Retry
          </button>
        </div>
      </div>
    );
  }

  const tabs = [
    {
      id: 'overview' as TabType,
      name: 'Overview',
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
          />
        </svg>
      ),
    },
    {
      id: 'narratives' as TabType,
      name: 'Commit Narratives',
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
          />
        </svg>
      ),
    },
    {
      id: 'anomalies' as TabType,
      name: 'Anomaly Detection',
      icon: (
        <svg
          className="w-5 h-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
          />
        </svg>
      ),
    },
  ];

  return (
    <div
      className="min-h-screen"
      style={{
        backgroundColor: isDark ? '#0a0a0a' : '#f5f5f5',
        transition: 'background-color 0.3s ease',
      }}
    >
      <Header />

      <div
        style={{
          borderBottom: '1px solid rgba(140, 29, 64, 0.3)',
          backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
          transition: 'background-color 0.3s ease',
        }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map(tab => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className="flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm transition-colors"
                style={
                  activeTab === tab.id
                    ? { borderColor: '#FFC627', color: '#FFC627' }
                    : {
                        borderColor: 'transparent',
                        color: isDark ? '#888' : '#666',
                      }
                }
                onMouseEnter={e => {
                  if (activeTab !== tab.id) {
                    e.currentTarget.style.color = '#FFC627';
                    e.currentTarget.style.borderColor =
                      'rgba(255, 198, 39, 0.3)';
                  }
                }}
                onMouseLeave={e => {
                  if (activeTab !== tab.id) {
                    e.currentTarget.style.color = isDark ? '#888' : '#666';
                    e.currentTarget.style.borderColor = 'transparent';
                  }
                }}
              >
                {tab.icon}
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'overview' && (
          <>
            {stats && <ProjectStats stats={stats} />}

            <div className="mt-8">
              <div className="flex justify-between items-center mb-6">
                <h2
                  className="text-2xl font-bold"
                  style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                >
                  Issues
                </h2>
                <button onClick={loadDashboardData} className="btn-secondary">
                  Refresh
                </button>
              </div>

              {issues.length === 0 ? (
                <div className="card text-center py-12">
                  <p style={{ color: isDark ? '#aaa' : '#666' }}>
                    No issues found. Connect your repositories to get started.
                  </p>
                </div>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {issues.map(issue => (
                    <IssueCard key={issue.id} issue={issue} />
                  ))}
                </div>
              )}
            </div>
          </>
        )}

        {activeTab === 'narratives' && <CommitNarrative />}

        {activeTab === 'anomalies' && <AnomalyDetector />}
      </div>

      {/* Floating Chat Button */}
      <button
        onClick={() => setIsChatOpen(!isChatOpen)}
        className="fixed bottom-4 right-4 md:bottom-6 md:right-6 z-50 w-14 h-14 rounded-full shadow-lg flex items-center justify-center transition-all duration-300 hover:scale-110 hover:shadow-xl"
        style={{
          backgroundColor: '#8C1D40',
          color: '#FFFFFF',
        }}
        aria-label={isChatOpen ? 'Close chat' : 'Open chat'}
      >
        {isChatOpen ? (
          <svg
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        ) : (
          <svg
            className="w-6 h-6"
            fill="none"
            viewBox="0 0 24 24"
            stroke="currentColor"
            strokeWidth={2}
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            />
          </svg>
        )}
        {!isChatOpen && (
          <span
            className="absolute -top-1 -right-1 w-4 h-4 rounded-full animate-pulse"
            style={{ backgroundColor: '#FFC627' }}
          />
        )}
      </button>

      {/* Floating Chat Window */}
      {isChatOpen && (
        <div
          className={`fixed bottom-20 right-4 left-4 md:bottom-24 md:right-6 md:left-auto z-40 md:w-96 h-[500px] md:h-[600px] rounded-lg shadow-2xl transition-all duration-300 animate-slide-up flex flex-col overflow-hidden ${
            isDark ? 'dark-chat-container' : ''
          }`}
          style={{
            backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
            border: `1px solid ${
              isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)'
            }`,
            maxHeight: 'calc(100vh - 5rem)',
          }}
        >
          <Chatbot
            apiUrl={
              process.env.NEXT_PUBLIC_API_URL
                ? `${process.env.NEXT_PUBLIC_API_URL}/api/chat`
                : 'http://localhost:8000/api/chat'
            }
            heading="Claude Assistant"
            tagline="Your AI partner for hackathon success."
            introMessage="Welcome! How can I help you?"
            className="h-full"
          />
        </div>
      )}
    </div>
  );
}
