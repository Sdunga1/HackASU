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
    const response = await apiClient.get<Issue[]>('/issues')
    return response.data
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

