import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const apiClient = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Issue {
  id: string
  title: string
  status: string
  assignee?: string
  priority: string
  createdAt: string
}

export interface ProjectStats {
  totalIssues: number
  openIssues: number
  closedIssues: number
  inProgress: number
}

export const fetchIssues = async (): Promise<Issue[]> => {
  try {
    // Try to fetch from dashboard endpoint first (MCP-synced data)
    const response = await apiClient.get('/dashboard/issues')
    
    if (response.data.issues && response.data.issues.length > 0) {
      return response.data.issues
    }
    
    // Fallback to regular issues endpoint if no dashboard data
    const fallbackResponse = await apiClient.get<Issue[]>('/issues')
    return fallbackResponse.data
  } catch (error) {
    console.error('Error fetching issues:', error)
    throw error
  }
}

export const fetchProjectStats = async (): Promise<ProjectStats> => {
  try {
    const response = await apiClient.get<ProjectStats>('/stats')
    return response.data
  } catch (error) {
    console.error('Error fetching stats:', error)
    throw error
  }
}

export const assignIssue = async (issueId: string, assignee: string): Promise<void> => {
  try {
    await apiClient.post(`/issues/${issueId}/assign`, { assignee })
  } catch (error) {
    console.error('Error assigning issue:', error)
    throw error
  }
}

export const getAIRecommendation = async (issueId: string): Promise<{ assignee: string; reasoning: string }> => {
  try {
    const response = await apiClient.get(`/ai/recommend-assignment/${issueId}`)
    return response.data
  } catch (error) {
    console.error('Error getting AI recommendation:', error)
    throw error
  }
}

// SRS and Sprint Management APIs
export interface UserStory {
  id: string
  title: string
  description: string
  storyPoints: number
  priority: string
  status: string
  assignee?: string
  acceptanceCriteria: string[]
}

export interface Sprint {
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

export interface SRSDocument {
  id: string
  name: string
  url?: string
  lastUpdated: string
  totalRequirements: number
  status: string
}

// SRS processing is done by Cursor's AI, not through the API
// Use send_sprints_to_dashboard MCP tool from Cursor instead

export const getSRSDocument = async (): Promise<SRSDocument | null> => {
  try {
    const response = await apiClient.get('/srs/document')
    if (response.data.status === 'not_found') {
      return null
    }
    return response.data.document
  } catch (error) {
    console.error('Error fetching SRS document:', error)
    return null
  }
}

export const getSprints = async (): Promise<Sprint[]> => {
  try {
    const response = await apiClient.get('/srs/sprints')
    return response.data.sprints || []
  } catch (error) {
    console.error('Error fetching sprints:', error)
    return []
  }
}

export const getSprint = async (sprintId: string): Promise<Sprint> => {
  try {
    const response = await apiClient.get(`/srs/sprints/${sprintId}`)
    return response.data.sprint
  } catch (error) {
    console.error('Error fetching sprint:', error)
    throw error
  }
}

export const updateUserStoryStatus = async (sprintId: string, storyId: string, status: string): Promise<Sprint> => {
  try {
    const response = await apiClient.post(`/srs/sprints/${sprintId}/user-stories/${storyId}/update`, {
      status
    })
    return response.data.sprint
  } catch (error) {
    console.error('Error updating user story status:', error)
    throw error
  }
}

