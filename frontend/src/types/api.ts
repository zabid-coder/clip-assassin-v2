export interface ApiResponse {
  success: boolean
  message: string
}

export interface StatusResponse extends ApiResponse {}

export interface StatsResponse {
  success: boolean
  name: string
  fps: string
  clips: number
  timecode: string
}

export interface ContextResponse {
  success: boolean
  project: string
  timelines: string[]
  current_timeline: string
}

export interface TemplatesResponse {
  success: boolean
  templates: string[]
}

export interface ProjectStatsResponse {
  success: boolean
  project_name: string
  timeline_count: number
  total_duration_seconds: number
  total_clips_used: number
  total_pool_clips: number
}

export interface BadWordsScanResponse {
  success: boolean
  message: string
  timeline_name: string
  total_markers: number
  total_marked_seconds: number
  summary: Record<string, { count: number; total_seconds: number }>
}

export interface AppContext {
  project: string
  timelines: string[]
  current_timeline: string
}

export interface LogEntry {
  id: string
  msg: string
  type: 'info' | 'success' | 'error'
  time: string
}

export interface Toast {
  id: number
  msg: string
  type: 'success' | 'error' | 'info'
}

export interface AppStatus {
  connected: boolean
  message: string
}

export interface AppStats {
  name: string
  fps: string
  clips: number
  timecode: string
}
