// API Response Types

export interface User {
  id: number
  name: string
  email: string
  created_at: string
}

export interface Resume {
  id: number
  user_id: number
  file_name: string
  file_path: string | null
  format_ok: boolean
  created_at: string
}

export interface JobDescription {
  id: number
  user_id: number
  title: string
  description: string
  created_at: string
}

export interface ScoreDetails {
  technical: number
  experience: number
  education: number
  certifications: number
  soft_skills: number
  semantic: number
  format: number
}

// Standalone ATS Analysis Types
export interface StandaloneScoreDetails {
  formatting: number
  contact_info: number
  skills_section: number
  experience_section: number
  education_section: number
  keywords_density: number
  readability: number
  length_optimization: number
}

export interface ATSIssue {
  category: string
  severity: 'critical' | 'major' | 'minor'
  issue: string
  suggestion: string
  impact_score: number
}

export interface ATSSuggestion {
  priority: 'critical' | 'major' | 'minor'
  category: string
  issue: string
  suggestion: string
  impact: 'high' | 'medium' | 'low'
}

export interface DetectedSkills {
  technical: string[]
  soft: string[]
  tools: string[]
}

export interface OriginalData {
  name?: string
  email?: string
  phone?: string
  location?: string
  linkedin?: string
  github?: string
  experience_count?: number
  education_count?: number
  skills_count?: number
  projects_count?: number
  certifications_count?: number
  awards_count?: number
  languages_count?: number
}

export interface OptimizedResume {
  sections: {
    [key: string]: string
  }
  full_resume?: string
  improvements: string[]
  template_suggestions: string[]
  original_data?: OriginalData
  section_order?: string[]
}

export interface StandaloneATSResult {
  total_score: number
  grade: string
  summary: string
  score_details: StandaloneScoreDetails
  issues: ATSIssue[]
  suggestions: ATSSuggestion[]
  detected_skills: DetectedSkills
  optimized_resume: OptimizedResume
}

export interface Keyword {
  keyword: string
  is_matched: boolean
  category: string
}

export interface ATSScore {
  id: number
  resume_id: number
  job_id: number
  total_score: number
  score_details: ScoreDetails
  created_at: string
  matched_keywords: Keyword[]
  missing_keywords: Keyword[]
  suggestions: string[]
}

export interface AuthToken {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface ApiError {
  detail: string
}
