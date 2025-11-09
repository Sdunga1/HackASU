'use client';

import { useState, useEffect } from 'react';
import { useTheme } from '@/contexts/ThemeContext';
import {
  getSRSDocument,
  getSprints,
  type SRSDocument,
  type Sprint,
  type UserStory,
} from '@/lib/api';

// Types are imported from api.ts

export default function SrsSprintPlanner() {
  const { theme } = useTheme();
  const isDark = theme === 'dark';
  const [selectedSprint, setSelectedSprint] = useState<Sprint | null>(null);
  const [srsDocument, setSrsDocument] = useState<SRSDocument | null>(null);
  const [sprints, setSprints] = useState<Sprint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSRSData();

    // Setup WebSocket listener for real-time sprint updates
    const wsUrl =
      process.env.NEXT_PUBLIC_API_URL?.replace('http', 'ws') ||
      'ws://localhost:8000';
    const ws = new WebSocket(`${wsUrl}/api/dashboard/ws`);

    const messageHandler = (event: MessageEvent) => {
      const message = JSON.parse(event.data);
      if (
        message.type === 'sprints_update' ||
        message.type === 'initial_data'
      ) {
        if (message.data.sprints) {
          console.log('WebSocket sprints update:', message.data.sprints);
          message.data.sprints.forEach((sprint: Sprint, idx: number) => {
            console.log(`Sprint ${idx + 1} (${sprint.name}):`, {
              userStoriesCount: sprint.userStories?.length || 0,
              hasUserStories: !!sprint.userStories,
              userStories: sprint.userStories,
            });
          });
          setSprints(message.data.sprints);
        }
        if (message.data.srs_document) {
          setSrsDocument(message.data.srs_document);
        }
      }
    };

    ws.addEventListener('message', messageHandler);

    return () => {
      ws.removeEventListener('message', messageHandler);
      if (
        ws.readyState === WebSocket.OPEN ||
        ws.readyState === WebSocket.CONNECTING
      ) {
        ws.close();
      }
    };
  }, []);

  const loadSRSData = async () => {
    try {
      setLoading(true);
      const [doc, sprintsData] = await Promise.all([
        getSRSDocument(),
        getSprints(),
      ]);
      setSrsDocument(doc);
      setSprints(sprintsData);

      // Debug: Log sprint data
      console.log('Loaded sprints:', sprintsData);
      sprintsData.forEach((sprint: Sprint, idx: number) => {
        console.log(`Sprint ${idx + 1} (${sprint.name}):`, {
          userStoriesCount: sprint.userStories?.length || 0,
          userStories: sprint.userStories,
        });
      });
    } catch (error) {
      console.error('Error loading SRS data:', error);
    } finally {
      setLoading(false);
    }
  };

  // SRS processing is done by Cursor's AI, not through the frontend
  // Users should ask Cursor to process SRS documents and send sprints to dashboard

  const getStatusColor = (status: string) => {
    const statusMap: Record<
      string,
      { bg: string; text: string; border: string }
    > = {
      backlog: {
        bg: isDark ? 'rgba(100, 100, 100, 0.15)' : 'rgba(100, 100, 100, 0.1)',
        text: isDark ? '#aaa' : '#666',
        border: isDark
          ? 'rgba(100, 100, 100, 0.3)'
          : 'rgba(100, 100, 100, 0.2)',
      },
      todo: {
        bg: isDark ? 'rgba(255, 198, 39, 0.15)' : 'rgba(255, 198, 39, 0.1)',
        text: '#FFC627',
        border: isDark ? 'rgba(255, 198, 39, 0.3)' : 'rgba(255, 198, 39, 0.2)',
      },
      'in-progress': {
        bg: isDark ? 'rgba(140, 29, 64, 0.15)' : 'rgba(140, 29, 64, 0.1)',
        text: '#8C1D40',
        border: isDark ? 'rgba(140, 29, 64, 0.3)' : 'rgba(140, 29, 64, 0.2)',
      },
      done: {
        bg: isDark ? 'rgba(34, 197, 94, 0.15)' : 'rgba(34, 197, 94, 0.1)',
        text: '#22C55E',
        border: isDark ? 'rgba(34, 197, 94, 0.3)' : 'rgba(34, 197, 94, 0.2)',
      },
    };
    return statusMap[status] || statusMap.backlog;
  };

  const getPriorityColor = (priority: string) => {
    const priorityMap: Record<string, string> = {
      high: '#8C1D40',
      medium: '#FFC627',
      low: '#888',
    };
    return priorityMap[priority.toLowerCase()] || '#888';
  };

  if (loading) {
    return (
      <div className="text-center py-8">
        <div
          className="animate-spin rounded-full h-8 w-8 border-b-2 mx-auto"
          style={{ borderColor: '#FFC627' }}
        />
        <p className="mt-4" style={{ color: isDark ? '#aaa' : '#666' }}>
          Loading SRS data...
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* SRS Document Card */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h2
            className="text-2xl font-bold"
            style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
          >
            SRS-Based Sprint Planning
          </h2>
        </div>

        <div
          className="card p-6"
          style={{
            borderColor: isDark
              ? 'rgba(140, 29, 64, 0.4)'
              : 'rgba(140, 29, 64, 0.3)',
            backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
          }}
        >
          {!srsDocument ? (
            <div className="text-center py-8">
              <div
                className="p-4 rounded-lg inline-block mb-4"
                style={{
                  backgroundColor: isDark
                    ? 'rgba(140, 29, 64, 0.2)'
                    : 'rgba(140, 29, 64, 0.1)',
                }}
              >
                <svg
                  className="w-12 h-12 mx-auto"
                  fill="none"
                  viewBox="0 0 24 24"
                  stroke="currentColor"
                  style={{ color: '#8C1D40' }}
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                  />
                </svg>
              </div>
              <h3
                className="text-xl font-semibold mb-2"
                style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
              >
                No SRS Document Processed
              </h3>
              <p
                className="text-sm mb-6 max-w-2xl mx-auto"
                style={{ color: isDark ? '#aaa' : '#666' }}
              >
                To generate sprints from an SRS document, ask Cursor to process
                it using the{' '}
                <code
                  className="px-2 py-1 rounded text-xs"
                  style={{
                    backgroundColor: isDark
                      ? 'rgba(140, 29, 64, 0.2)'
                      : 'rgba(140, 29, 64, 0.1)',
                    color: '#8C1D40',
                  }}
                >
                  send_sprints_to_dashboard
                </code>{' '}
                tool. Ask Cursor's AI to read your Google Docs SRS,
                generate sprints, and send them to the dashboard.
              </p>

              <div
                className="max-w-2xl mx-auto p-4 rounded-lg mb-6 text-left"
                style={{
                  backgroundColor: isDark
                    ? 'rgba(255, 198, 39, 0.1)'
                    : 'rgba(255, 198, 39, 0.05)',
                  border: `1px solid ${
                    isDark
                      ? 'rgba(255, 198, 39, 0.2)'
                      : 'rgba(255, 198, 39, 0.3)'
                  }`,
                }}
              >
                <p
                  className="text-sm font-semibold mb-2"
                  style={{ color: '#FFC627' }}
                >
                  How to use:
                </p>
                <ol
                  className="text-sm space-y-2 list-decimal list-inside"
                  style={{ color: isDark ? '#aaa' : '#666' }}
                >
                  <li>
                    Cursor will read the SRS, generate sprints with user stories, and send them to the dashboard
                  </li>
                  <li>Sprints will automatically appear here when ready</li>
                </ol>
              </div>
            </div>
          ) : (
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center gap-3">
                <div
                  className="p-3 rounded-lg"
                  style={{
                    backgroundColor: isDark
                      ? 'rgba(140, 29, 64, 0.2)'
                      : 'rgba(140, 29, 64, 0.1)',
                  }}
                >
                  <svg
                    className="w-6 h-6"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    style={{ color: '#8C1D40' }}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                </div>
                <div>
                  <h3
                    className="text-xl font-bold mb-1"
                    style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                  >
                    {srsDocument.name}
                  </h3>
                  <p
                    className="text-sm"
                    style={{ color: isDark ? '#aaa' : '#666' }}
                  >
                    {srsDocument.totalRequirements} requirements • Last updated:{' '}
                    {new Date(srsDocument.lastUpdated).toLocaleDateString()}
                  </p>
                </div>
              </div>
              <span
                className={`px-3 py-1 text-xs font-medium rounded-full ${
                  srsDocument.status === 'ready'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : srsDocument.status === 'processing'
                    ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
                    : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-200'
                }`}
              >
                {srsDocument.status === 'ready'
                  ? 'Ready'
                  : srsDocument.status === 'processing'
                  ? 'Processing'
                  : 'Connected'}
              </span>
            </div>
          )}
        </div>
      </div>

      {/* Processing Indicator */}
      {sprints.length === 0 && srsDocument && (
        <div
          className="card p-6 text-center"
          style={{
            borderColor: isDark
              ? 'rgba(255, 198, 39, 0.4)'
              : 'rgba(255, 198, 39, 0.3)',
            backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
          }}
        >
          <div className="flex items-center justify-center gap-3">
            <div
              className="animate-spin rounded-full h-5 w-5 border-b-2"
              style={{ borderColor: '#FFC627' }}
            />
            <p style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>
              Processing SRS and generating sprints... This may take a moment.
            </p>
          </div>
          <p
            className="text-xs mt-2"
            style={{ color: isDark ? '#aaa' : '#666' }}
          >
            Sprints will appear automatically when ready.
          </p>
        </div>
      )}

      {/* Sprints Overview */}
      {sprints.length > 0 && (
        <div>
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2
                className="text-2xl font-bold mb-1"
                style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
              >
                Generated Sprints
              </h2>
              <p
                className="text-sm"
                style={{ color: isDark ? '#aaa' : '#666' }}
              >
                Click on a sprint to view its user stories
              </p>
            </div>
            <div className="flex items-center gap-3">
              <div
                className="px-4 py-2 rounded-lg border"
                style={{
                  backgroundColor: isDark
                    ? 'rgba(34, 197, 94, 0.1)'
                    : 'rgba(34, 197, 94, 0.05)',
                  borderColor: isDark
                    ? 'rgba(34, 197, 94, 0.3)'
                    : 'rgba(34, 197, 94, 0.2)',
                }}
              >
                <span
                  className="text-sm font-semibold"
                  style={{ color: '#22C55E' }}
                >
                  {sprints.length} Sprints
                </span>
              </div>
              <div
                className="px-4 py-2 rounded-lg border"
                style={{
                  backgroundColor: isDark
                    ? 'rgba(255, 198, 39, 0.1)'
                    : 'rgba(255, 198, 39, 0.05)',
                  borderColor: isDark
                    ? 'rgba(255, 198, 39, 0.3)'
                    : 'rgba(255, 198, 39, 0.2)',
                }}
              >
                <span
                  className="text-sm font-semibold"
                  style={{ color: '#FFC627' }}
                >
                  {sprints.reduce((sum, s) => sum + s.totalStoryPoints, 0)} SP
                </span>
              </div>
            </div>
          </div>

          {/* Split View: Sprints List | Selected Sprint Details */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            {/* Sprints List - Left Side */}
            <div className="lg:col-span-1 space-y-4">
              {sprints.map(sprint => (
                <div
                  key={sprint.id}
                  className="card p-5 cursor-pointer transition-all duration-300 relative overflow-hidden"
                  style={{
                    borderColor:
                      selectedSprint?.id === sprint.id
                        ? '#8C1D40'
                        : isDark
                        ? 'rgba(140, 29, 64, 0.3)'
                        : 'rgba(140, 29, 64, 0.2)',
                    backgroundColor:
                      selectedSprint?.id === sprint.id
                        ? isDark
                          ? 'rgba(140, 29, 64, 0.25)'
                          : 'rgba(140, 29, 64, 0.15)'
                        : isDark
                        ? '#1a1a1a'
                        : '#ffffff',
                    borderWidth: selectedSprint?.id === sprint.id ? '3px' : '1px',
                    transform:
                      selectedSprint?.id === sprint.id ? 'scale(1.03)' : 'scale(1)',
                    boxShadow:
                      selectedSprint?.id === sprint.id
                        ? isDark
                          ? '0 12px 30px rgba(140, 29, 64, 0.4), 0 0 0 2px rgba(140, 29, 64, 0.2)'
                          : '0 12px 30px rgba(140, 29, 64, 0.3), 0 0 0 2px rgba(140, 29, 64, 0.15)'
                        : '0 2px 8px rgba(0, 0, 0, 0.1)',
                  }}
                  onClick={() =>
                    setSelectedSprint(
                      selectedSprint?.id === sprint.id ? null : sprint
                    )
                }
                >
                  {/* Selection Indicator - Maroon colored */}
                  {selectedSprint?.id === sprint.id && (
                    <>
                      <div
                        className="absolute top-0 left-0 w-2 h-full"
                        style={{ backgroundColor: '#8C1D40' }}
                      />
                      <div
                        className="absolute top-0 right-0 w-16 h-16 opacity-15"
                        style={{
                          background: 'radial-gradient(circle, #8C1D40 0%, transparent 70%)',
                        }}
                      />
                    </>
                  )}
                  
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <h3
                        className="text-base font-bold mb-1 transition-colors"
                        style={{
                          color:
                            selectedSprint?.id === sprint.id
                              ? '#8C1D40'
                              : isDark
                              ? '#f5f5f5'
                              : '#1a1a1a',
                        }}
                      >
                        {sprint.name}
                      </h3>
                      <div className="flex items-center gap-2 mt-2">
                        <span
                          className="px-2 py-1 text-xs font-medium rounded-full"
                          style={{
                            backgroundColor: isDark
                              ? 'rgba(34, 197, 94, 0.15)'
                              : 'rgba(34, 197, 94, 0.1)',
                            color: '#22C55E',
                          }}
                        >
                          {sprint.userStories?.length || 0} stories
                        </span>
                        <span
                          className="px-2 py-1 text-xs font-medium rounded-full"
                          style={{
                            backgroundColor: isDark
                              ? 'rgba(255, 198, 39, 0.15)'
                              : 'rgba(255, 198, 39, 0.1)',
                            color: '#FFC627',
                          }}
                        >
                          {sprint.totalStoryPoints} SP
                        </span>
                      </div>
                    </div>
                  </div>

                  <p
                    className="text-sm mb-3 line-clamp-2"
                    style={{ color: isDark ? '#aaa' : '#666' }}
                  >
                    {sprint.goal}
                  </p>

                  <div className="space-y-2">
                    <div>
                      <div className="flex items-center justify-between text-xs mb-1">
                        <span style={{ color: isDark ? '#aaa' : '#666' }}>
                          Progress
                        </span>
                        <span
                          className="font-semibold"
                          style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                        >
                          {sprint.progress}%
                        </span>
                      </div>
                      <div
                        className="w-full h-1.5 rounded-full overflow-hidden"
                        style={{
                          backgroundColor: isDark ? '#2a2a2a' : '#f5f5f5',
                        }}
                      >
                        <div
                          className="h-full transition-all duration-500"
                          style={{
                            width: `${sprint.progress}%`,
                            backgroundColor:
                              selectedSprint?.id === sprint.id
                                ? '#8C1D40'
                                : '#FFC627',
                            boxShadow:
                              selectedSprint?.id === sprint.id
                                ? isDark
                                  ? '0 0 8px rgba(140, 29, 64, 0.6)'
                                  : '0 0 8px rgba(140, 29, 64, 0.4)'
                                : 'none',
                          }}
                        />
                      </div>
                    </div>

                    <div className="flex items-center justify-between text-xs pt-1">
                      <span style={{ color: isDark ? '#888' : '#999' }}>
                        {new Date(sprint.startDate).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                        })}{' '}
                        -{' '}
                        {new Date(sprint.endDate).toLocaleDateString('en-US', {
                          month: 'short',
                          day: 'numeric',
                        })}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {/* Selected Sprint Details - Right Side */}
            {selectedSprint ? (
              <div className="lg:col-span-2 space-y-4 animate-fadeIn">
                {/* Sprint Header */}
                <div
                  className="card p-6 relative overflow-hidden"
                  style={{
                    borderColor: '#FFC627',
                    backgroundColor: isDark
                      ? 'rgba(255, 198, 39, 0.1)'
                      : 'rgba(255, 198, 39, 0.08)',
                    borderLeftWidth: '5px',
                    borderLeftColor: '#FFC627',
                    borderWidth: '2px',
                    boxShadow: '0 8px 20px rgba(255, 198, 39, 0.2)',
                  }}
                >
                  {/* Decorative background accent */}
                  <div
                    className="absolute top-0 right-0 w-32 h-32 opacity-10"
                    style={{
                      background: 'radial-gradient(circle, #FFC627 0%, transparent 70%)',
                    }}
                  />
                  
                  <div className="flex items-start justify-between mb-4 relative z-10">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-3">
                        <div
                          className="px-3 py-1 rounded-lg"
                          style={{
                            backgroundColor: '#FFC627',
                            color: '#1a1a1a',
                          }}
                        >
                          <span className="text-xs font-bold uppercase tracking-wide">
                            Sprint
                          </span>
                        </div>
                        <h2
                          className="text-3xl font-bold"
                          style={{ color: '#FFC627' }}
                        >
                          {selectedSprint.name}
                        </h2>
                      </div>
                      <p
                        className="text-lg leading-relaxed font-medium"
                        style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                      >
                        {selectedSprint.goal}
                      </p>
                    </div>
                    <button
                      onClick={() => setSelectedSprint(null)}
                      className="ml-4 p-2 rounded-lg hover:bg-opacity-20 transition-colors"
                      style={{
                        backgroundColor: isDark
                          ? 'rgba(140, 29, 64, 0.2)'
                          : 'rgba(140, 29, 64, 0.1)',
                        color: isDark ? '#aaa' : '#666',
                      }}
                      title="Close"
                    >
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
                          d="M6 18L18 6M6 6l12 12"
                        />
                      </svg>
                    </button>
                  </div>

                  {/* Sprint Metrics */}
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t border-opacity-20" style={{ borderColor: isDark ? 'rgba(255, 198, 39, 0.2)' : 'rgba(255, 198, 39, 0.1)' }}>
                    <div>
                      <p
                        className="text-xs mb-1 uppercase tracking-wide"
                        style={{ color: isDark ? '#888' : '#999' }}
                      >
                        Start Date
                      </p>
                      <p
                        className="font-semibold"
                        style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                      >
                        {new Date(selectedSprint.startDate).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p
                        className="text-xs mb-1 uppercase tracking-wide"
                        style={{ color: isDark ? '#888' : '#999' }}
                      >
                        End Date
                      </p>
                      <p
                        className="font-semibold"
                        style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                      >
                        {new Date(selectedSprint.endDate).toLocaleDateString()}
                      </p>
                    </div>
                    <div>
                      <p
                        className="text-xs mb-1 uppercase tracking-wide"
                        style={{ color: isDark ? '#888' : '#999' }}
                      >
                        Story Points
                      </p>
                      <p className="font-semibold" style={{ color: '#FFC627' }}>
                        {selectedSprint.totalStoryPoints} SP
                      </p>
                    </div>
                    <div>
                      <p
                        className="text-xs mb-1 uppercase tracking-wide"
                        style={{ color: isDark ? '#888' : '#999' }}
                      >
                        Progress
                      </p>
                      <p
                        className="font-semibold"
                        style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                      >
                        {selectedSprint.progress}%
                      </p>
                    </div>
                  </div>
                </div>

                {/* User Stories Section */}
                <div>
                  <div className="mb-6">
                    <div className="flex items-center gap-4 mb-3">
                      <div
                        className="w-1.5 h-14 rounded-full"
                        style={{ backgroundColor: '#8C1D40' }}
                      />
                      <div className="flex-1">
                        <h3
                          className="text-2xl font-bold mb-2"
                          style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                        >
                          User Stories
                        </h3>
                        <div
                          className="inline-flex items-center gap-2 px-4 py-2 rounded-lg"
                          style={{
                            backgroundColor: isDark
                              ? 'rgba(140, 29, 64, 0.2)'
                              : 'rgba(140, 29, 64, 0.1)',
                            border: `2px solid ${
                              isDark
                                ? 'rgba(140, 29, 64, 0.4)'
                                : 'rgba(140, 29, 64, 0.3)'
                            }`,
                          }}
                        >
                          <span
                            className="text-sm font-semibold"
                            style={{ color: isDark ? '#aaa' : '#666' }}
                          >
                            Sprint:
                          </span>
                          <span
                            className="text-lg font-bold"
                            style={{ color: '#8C1D40' }}
                          >
                            {selectedSprint.name}
                          </span>
                          <span
                            className="ml-2 px-2.5 py-1 rounded-full text-xs font-bold"
                            style={{
                              backgroundColor: '#8C1D40',
                              color: '#ffffff',
                            }}
                          >
                            {selectedSprint.userStories?.length || 0} Stories
                          </span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {!selectedSprint.userStories ||
                  selectedSprint.userStories.length === 0 ? (
                    <div
                      className="card p-8 text-center"
                      style={{
                        borderColor: isDark
                          ? 'rgba(140, 29, 64, 0.4)'
                          : 'rgba(140, 29, 64, 0.3)',
                        backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
                      }}
                    >
                      <p style={{ color: isDark ? '#aaa' : '#666' }}>
                        No user stories generated for this sprint.
                      </p>
                    </div>
                  ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                      {selectedSprint.userStories.map((story, idx) => {
                        const statusColors = getStatusColor(story.status);
                        return (
                          <div
                            key={story.id}
                            className="card p-5 hover:shadow-lg transition-all duration-300 group"
                            style={{
                              borderColor: isDark
                                ? 'rgba(140, 29, 64, 0.3)'
                                : 'rgba(140, 29, 64, 0.2)',
                              backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
                              borderLeftWidth: '3px',
                              borderLeftColor: getPriorityColor(story.priority),
                            }}
                          >
                            {/* Story Header */}
                            <div className="flex items-start justify-between mb-3">
                              <div className="flex items-start gap-3 flex-1">
                                <div
                                  className="flex-shrink-0 w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold mt-0.5"
                                  style={{
                                    backgroundColor: isDark
                                      ? 'rgba(255, 198, 39, 0.2)'
                                      : 'rgba(255, 198, 39, 0.15)',
                                    color: '#FFC627',
                                  }}
                                >
                                  {idx + 1}
                                </div>
                                <div className="flex-1 min-w-0">
                                  <h4
                                    className="text-base font-bold mb-1"
                                    style={{
                                      color: isDark ? '#f5f5f5' : '#1a1a1a',
                                    }}
                                  >
                                    {story.title}
                                  </h4>
                                  <p
                                    className="text-sm leading-relaxed"
                                    style={{
                                      color: isDark ? '#aaa' : '#666',
                                    }}
                                  >
                                    {story.description}
                                  </p>
                                </div>
                              </div>
                              <span
                                className="px-2.5 py-1 text-xs font-bold rounded-full flex-shrink-0 ml-2"
                                style={{
                                  backgroundColor: isDark
                                    ? 'rgba(255, 198, 39, 0.2)'
                                    : 'rgba(255, 198, 39, 0.15)',
                                  color: '#FFC627',
                                }}
                              >
                                {story.storyPoints} SP
                              </span>
                            </div>

                            {/* Story Metadata */}
                            <div className="flex items-center justify-between flex-wrap gap-2 pt-3 border-t" style={{ borderColor: isDark ? 'rgba(140, 29, 64, 0.2)' : 'rgba(140, 29, 64, 0.1)' }}>
                              <div className="flex items-center gap-2">
                                <span
                                  className="px-2.5 py-1 text-xs font-medium rounded-full border"
                                  style={{
                                    backgroundColor: statusColors.bg,
                                    borderColor: statusColors.border,
                                    color: statusColors.text,
                                  }}
                                >
                                  {story.status.replace('-', ' ')}
                                </span>
                                <span
                                  className="px-2.5 py-1 text-xs font-medium rounded-full"
                                  style={{
                                    backgroundColor: isDark
                                      ? 'rgba(140, 29, 64, 0.2)'
                                      : 'rgba(140, 29, 64, 0.1)',
                                    color: getPriorityColor(story.priority),
                                  }}
                                >
                                  {story.priority}
                                </span>
                              </div>
                              {story.assignee && (
                                <div
                                  className="text-xs"
                                  style={{ color: isDark ? '#888' : '#999' }}
                                >
                                  👤 {story.assignee}
                                </div>
                              )}
                            </div>

                            {/* Acceptance Criteria */}
                            {story.acceptanceCriteria &&
                              story.acceptanceCriteria.length > 0 && (
                                <div className="mt-3 pt-3 border-t" style={{ borderColor: isDark ? 'rgba(140, 29, 64, 0.2)' : 'rgba(140, 29, 64, 0.1)' }}>
                                  <p
                                    className="text-xs font-semibold mb-2 uppercase tracking-wide"
                                    style={{ color: isDark ? '#888' : '#999' }}
                                  >
                                    Acceptance Criteria
                                  </p>
                                  <ul className="space-y-1.5">
                                    {story.acceptanceCriteria.map(
                                      (criteria, criteriaIdx) => (
                                        <li
                                          key={criteriaIdx}
                                          className="flex items-start gap-2 text-xs"
                                          style={{
                                            color: isDark ? '#aaa' : '#666',
                                          }}
                                        >
                                          <span
                                            className="mt-1.5 flex-shrink-0 w-1.5 h-1.5 rounded-full"
                                            style={{
                                              backgroundColor: '#FFC627',
                                            }}
                                          />
                                          <span className="leading-relaxed">
                                            {criteria}
                                          </span>
                                        </li>
                                      )
                                    )}
                                  </ul>
                                </div>
                              )}
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="lg:col-span-2 flex items-center justify-center min-h-[400px]">
                <div
                  className="text-center p-8 rounded-lg"
                  style={{
                    backgroundColor: isDark
                      ? 'rgba(140, 29, 64, 0.1)'
                      : 'rgba(140, 29, 64, 0.05)',
                    border: `2px dashed ${
                      isDark
                        ? 'rgba(140, 29, 64, 0.3)'
                        : 'rgba(140, 29, 64, 0.2)'
                    }`,
                  }}
                >
                  <svg
                    className="w-16 h-16 mx-auto mb-4 opacity-50"
                    fill="none"
                    viewBox="0 0 24 24"
                    stroke="currentColor"
                    style={{ color: isDark ? '#aaa' : '#666' }}
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={1.5}
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
                    />
                  </svg>
                  <p
                    className="text-lg font-medium mb-2"
                    style={{ color: isDark ? '#aaa' : '#666' }}
                  >
                    Select a sprint to view user stories
                  </p>
                  <p
                    className="text-sm"
                    style={{ color: isDark ? '#888' : '#999' }}
                  >
                    Click on any sprint card from the list to see its details
                    and associated user stories
                  </p>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
