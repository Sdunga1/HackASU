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
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2
                className="text-2xl font-bold"
                style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
              >
                Generated Sprints
              </h2>
              <p
                className="text-sm mt-1"
                style={{ color: isDark ? '#aaa' : '#666' }}
              >
                Generated from SRS document via MCP
              </p>
            </div>
            <span
              className="text-sm px-3 py-1 rounded-full"
              style={{
                backgroundColor: isDark
                  ? 'rgba(34, 197, 94, 0.15)'
                  : 'rgba(34, 197, 94, 0.1)',
                color: '#22C55E',
                border: `1px solid ${
                  isDark ? 'rgba(34, 197, 94, 0.3)' : 'rgba(34, 197, 94, 0.2)'
                }`,
              }}
            >
              {sprints.length} sprints •{' '}
              {sprints.reduce((sum, s) => sum + s.totalStoryPoints, 0)} total
              story points
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
            {sprints.map(sprint => (
              <div
                key={sprint.id}
                className="card p-5 cursor-pointer hover:shadow-xl transition-all duration-200"
                style={{
                  borderColor:
                    selectedSprint?.id === sprint.id
                      ? '#FFC627'
                      : isDark
                      ? 'rgba(140, 29, 64, 0.4)'
                      : 'rgba(140, 29, 64, 0.3)',
                  backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
                  borderWidth: selectedSprint?.id === sprint.id ? '2px' : '1px',
                }}
                onClick={() =>
                  setSelectedSprint(
                    selectedSprint?.id === sprint.id ? null : sprint
                  )
                }
              >
                <div className="flex items-start justify-between mb-3">
                  <h3
                    className="text-lg font-semibold flex-1"
                    style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                  >
                    {sprint.name}
                  </h3>
                </div>

                <p
                  className="text-sm mb-4 line-clamp-2"
                  style={{ color: isDark ? '#aaa' : '#666' }}
                >
                  {sprint.goal}
                </p>

                <div className="space-y-3">
                  <div>
                    <div className="flex items-center justify-between text-sm mb-1">
                      <span style={{ color: isDark ? '#aaa' : '#666' }}>
                        Progress
                      </span>
                      <span style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}>
                        {sprint.completedStoryPoints}/{sprint.totalStoryPoints}{' '}
                        SP
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
                          backgroundColor: '#FFC627',
                        }}
                      />
                    </div>
                  </div>

                  <div className="flex items-center justify-between text-sm">
                    <span style={{ color: isDark ? '#aaa' : '#666' }}>
                      {sprint.userStories.length} user stories
                    </span>
                    <span style={{ color: isDark ? '#aaa' : '#666' }}>
                      {new Date(sprint.startDate).toLocaleDateString()} -{' '}
                      {new Date(sprint.endDate).toLocaleDateString()}
                    </span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Selected Sprint Details */}
      {selectedSprint && (
        <div className="mt-6">
          <div className="flex items-center justify-between mb-4">
            <h2
              className="text-2xl font-bold"
              style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
            >
              {selectedSprint.name}
            </h2>
            <button
              onClick={() => setSelectedSprint(null)}
              className="text-sm font-medium transition-colors"
              style={{ color: isDark ? '#aaa' : '#666' }}
            >
              Close
            </button>
          </div>

          <div
            className="card p-6 mb-4"
            style={{
              borderColor: isDark
                ? 'rgba(140, 29, 64, 0.4)'
                : 'rgba(140, 29, 64, 0.3)',
              backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
            }}
          >
            <p
              className="text-base mb-4"
              style={{ color: isDark ? '#aaa' : '#666' }}
            >
              {selectedSprint.goal}
            </p>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p
                  className="text-sm mb-1"
                  style={{ color: isDark ? '#aaa' : '#666' }}
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
                  className="text-sm mb-1"
                  style={{ color: isDark ? '#aaa' : '#666' }}
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
                  className="text-sm mb-1"
                  style={{ color: isDark ? '#aaa' : '#666' }}
                >
                  Total Story Points
                </p>
                <p className="font-semibold" style={{ color: '#FFC627' }}>
                  {selectedSprint.totalStoryPoints}
                </p>
              </div>
              <div>
                <p
                  className="text-sm mb-1"
                  style={{ color: isDark ? '#aaa' : '#666' }}
                >
                  User Stories
                </p>
                <p
                  className="font-semibold"
                  style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                >
                  {selectedSprint.userStories.length}
                </p>
              </div>
            </div>
          </div>

          {/* User Stories Grid */}
          <div>
            <h3
              className="text-xl font-bold mb-4"
              style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
            >
              User Stories
            </h3>
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
                  No user stories generated for this sprint. This may indicate
                  an issue with the SRS processing.
                </p>
                <p
                  className="text-xs mt-2"
                  style={{ color: isDark ? '#888' : '#999' }}
                >
                  Check backend logs for details.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {selectedSprint.userStories.map(story => {
                  const statusColors = getStatusColor(story.status);
                  return (
                    <div
                      key={story.id}
                      className="card p-5 hover:shadow-xl transition-shadow duration-200"
                      style={{
                        borderColor: isDark
                          ? 'rgba(140, 29, 64, 0.4)'
                          : 'rgba(140, 29, 64, 0.3)',
                        backgroundColor: isDark ? '#1a1a1a' : '#ffffff',
                      }}
                    >
                      <div className="flex items-start justify-between mb-3">
                        <h4
                          className="text-base font-semibold flex-1"
                          style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                        >
                          {story.title}
                        </h4>
                        <span
                          className="px-2 py-1 text-xs font-bold rounded-full ml-2"
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

                      <p
                        className="text-sm mb-3 line-clamp-2"
                        style={{ color: isDark ? '#aaa' : '#666' }}
                      >
                        {story.description}
                      </p>

                      <div className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span
                            className={`px-2 py-1 text-xs font-medium rounded-full border ${statusColors.border}`}
                            style={{
                              backgroundColor: statusColors.bg,
                              color: statusColors.text,
                            }}
                          >
                            {story.status.replace('-', ' ')}
                          </span>
                          <span
                            className="text-xs font-medium"
                            style={{ color: getPriorityColor(story.priority) }}
                          >
                            {story.priority} priority
                          </span>
                        </div>

                        {story.assignee && (
                          <div className="flex items-center text-sm">
                            <span style={{ color: isDark ? '#aaa' : '#666' }}>
                              Assigned to:
                            </span>
                            <span
                              className="ml-2 font-medium"
                              style={{ color: isDark ? '#f5f5f5' : '#1a1a1a' }}
                            >
                              {story.assignee}
                            </span>
                          </div>
                        )}

                        <div
                          className="pt-2"
                          style={{
                            borderTop: '1px solid rgba(140, 29, 64, 0.2)',
                          }}
                        >
                          <p
                            className="text-xs font-medium mb-1"
                            style={{ color: isDark ? '#aaa' : '#666' }}
                          >
                            Acceptance Criteria:
                          </p>
                          <ul
                            className="list-disc list-inside text-xs space-y-1"
                            style={{ color: isDark ? '#aaa' : '#666' }}
                          >
                            {story.acceptanceCriteria
                              .slice(0, 2)
                              .map((criteria, idx) => (
                                <li key={idx} className="line-clamp-1">
                                  {criteria}
                                </li>
                              ))}
                            {story.acceptanceCriteria.length > 2 && (
                              <li className="text-[#FFC627]">
                                +{story.acceptanceCriteria.length - 2} more
                              </li>
                            )}
                          </ul>
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
