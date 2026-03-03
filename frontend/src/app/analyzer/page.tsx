'use client'

import { useState, useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import ScoreCard from '@/components/ScoreCard'
import ScoreBreakdown from '@/components/ScoreBreakdown'
import SuggestionsPanel from '@/components/SuggestionsPanel'
import OptimizedResume from '@/components/OptimizedResume'
import SkillsDetected from '@/components/SkillsDetected'
import ResumeBuilder from '@/components/ResumeBuilder'
import { StandaloneATSResult } from '@/types'
import { useAuth } from '@/context/AuthContext'

export default function Home() {
  const { isAuthenticated, isLoading: authLoading } = useAuth()
  const [file, setFile] = useState<File | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<StandaloneATSResult | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [activeTab, setActiveTab] = useState<'analysis' | 'suggestions' | 'optimized'>('analysis')
  const [showResumeBuilder, setShowResumeBuilder] = useState(false)

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0])
      setError(null)
      setResult(null)
    }
  }, [])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024 // 10MB
  })

  // Show loading state while checking auth
  if (authLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    )
  }

  // Auth redirect is handled by AuthContext, but show nothing while redirecting
  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    )
  }

  const handleAnalyze = async () => {
    if (!file) {
      setError('Please upload a resume')
      return
    }

    setIsLoading(true)
    setError(null)

    try {
      const formData = new FormData()
      formData.append('file', file)

      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'}/api/v1/resume/analyze-direct`, {
        method: 'POST',
        body: formData,
      })

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to analyze resume')
      }

      const data: StandaloneATSResult = await res.json()
      setResult(data)
      setActiveTab('analysis')

    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred')
    } finally {
      setIsLoading(false)
    }
  }

  const getGradeColor = (grade: string) => {
    if (grade.startsWith('A')) return 'text-green-600'
    if (grade.startsWith('B')) return 'text-blue-600'
    if (grade.startsWith('C')) return 'text-yellow-600'
    return 'text-red-600'
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50">
      <div className="max-w-7xl mx-auto px-4 py-8 sm:px-6 lg:px-8">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            ATS Resume Analyzer
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload your resume and get instant ATS compatibility analysis.
            No job description needed - we analyze against industry best practices.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Input Section */}
          <div className="space-y-6">
            {/* File Upload */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">
                Upload Your Resume
              </h2>
              
              <div
                {...getRootProps()}
                className={`border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition
                  ${isDragActive ? 'border-blue-500 bg-blue-50' : 'border-gray-300 hover:border-blue-400'}
                  ${file ? 'bg-green-50 border-green-300' : ''}`}
              >
                <input {...getInputProps()} />
                
                {file ? (
                  <div className="flex items-center justify-center gap-3">
                    <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div>
                      <p className="font-medium text-gray-900">{file.name}</p>
                      <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(1)} KB</p>
                    </div>
                    <button
                      onClick={(e) => { e.stopPropagation(); setFile(null); setResult(null); }}
                      className="text-red-500 hover:text-red-700"
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  </div>
                ) : (
                  <div>
                    <svg className="w-12 h-12 text-gray-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="text-gray-600 mb-2">
                      {isDragActive ? 'Drop your resume here' : 'Drag & drop your resume here'}
                    </p>
                    <p className="text-sm text-gray-500">or click to browse (PDF, DOCX - Max 10MB)</p>
                  </div>
                )}
              </div>

              {/* Analyze Button */}
              <button
                onClick={handleAnalyze}
                disabled={isLoading || !file}
                className={`w-full mt-6 py-4 rounded-lg font-semibold text-lg transition flex items-center justify-center gap-2
                  ${isLoading || !file
                    ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                    : 'bg-blue-600 text-white hover:bg-blue-700'
                  }`}
              >
                {isLoading ? (
                  <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    Analyzing Resume...
                  </>
                ) : (
                  <>
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                    </svg>
                    Analyze Resume
                  </>
                )}
              </button>

              {error && (
                <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4 text-red-700">
                  {error}
                </div>
              )}
            </div>

            {/* How it works */}
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">How It Works</h3>
              <div className="space-y-4">
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">1</div>
                  <div>
                    <p className="font-medium text-gray-900">Upload Resume</p>
                    <p className="text-sm text-gray-600">PDF or DOCX format</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">2</div>
                  <div>
                    <p className="font-medium text-gray-900">AI Analysis</p>
                    <p className="text-sm text-gray-600">We check 8 key ATS factors</p>
                  </div>
                </div>
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 font-semibold text-sm">3</div>
                  <div>
                    <p className="font-medium text-gray-900">Get Results</p>
                    <p className="text-sm text-gray-600">Score, suggestions & optimized resume</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Results Section */}
          <div className="space-y-6">
            {result ? (
              <>
                {/* Score and Grade */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div>
                      <h2 className="text-2xl font-bold text-gray-900">ATS Score</h2>
                      <p className="text-gray-600">{result.summary}</p>
                    </div>
                    <div className="text-center">
                      <div className={`text-5xl font-bold ${getGradeColor(result.grade)}`}>
                        {result.grade}
                      </div>
                      <div className="text-gray-500 text-sm">Grade</div>
                    </div>
                  </div>
                  <ScoreCard score={result.total_score} />
                  
                  {/* Create ATS Friendly Resume Button */}
                  <button
                    onClick={() => setShowResumeBuilder(true)}
                    className="w-full mt-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 text-white rounded-xl font-semibold text-lg hover:from-green-700 hover:to-emerald-700 transition shadow-lg hover:shadow-xl flex items-center justify-center gap-3"
                  >
                    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    Create ATS-Friendly Resume
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                    </svg>
                  </button>
                  <p className="text-center text-sm text-gray-500 mt-2">
                    Generate an optimized version with all suggestions applied
                  </p>
                </div>

                {/* Tab Navigation */}
                <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
                  <div className="flex border-b">
                    <button
                      onClick={() => setActiveTab('analysis')}
                      className={`flex-1 py-3 px-4 text-sm font-medium transition
                        ${activeTab === 'analysis' 
                          ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' 
                          : 'text-gray-600 hover:bg-gray-50'}`}
                    >
                      Analysis
                    </button>
                    <button
                      onClick={() => setActiveTab('suggestions')}
                      className={`flex-1 py-3 px-4 text-sm font-medium transition relative
                        ${activeTab === 'suggestions' 
                          ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' 
                          : 'text-gray-600 hover:bg-gray-50'}`}
                    >
                      Suggestions
                      {result.suggestions.filter(s => s.priority === 'critical').length > 0 && (
                        <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></span>
                      )}
                    </button>
                    <button
                      onClick={() => setActiveTab('optimized')}
                      className={`flex-1 py-3 px-4 text-sm font-medium transition
                        ${activeTab === 'optimized' 
                          ? 'bg-blue-50 text-blue-600 border-b-2 border-blue-600' 
                          : 'text-gray-600 hover:bg-gray-50'}`}
                    >
                      Optimized Resume
                    </button>
                  </div>

                  <div className="p-6">
                    {activeTab === 'analysis' && (
                      <div className="space-y-6">
                        <ScoreBreakdown details={result.score_details} />
                        <SkillsDetected skills={result.detected_skills} />
                      </div>
                    )}
                    
                    {activeTab === 'suggestions' && (
                      <SuggestionsPanel suggestions={result.suggestions} issues={result.issues} />
                    )}
                    
                    {activeTab === 'optimized' && (
                      <OptimizedResume optimized={result.optimized_resume} />
                    )}
                  </div>
                </div>
              </>
            ) : (
              <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-12 text-center">
                <svg className="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Your Results Will Appear Here
                </h3>
                <p className="text-gray-500">
                  Upload your resume to see your ATS compatibility score and improvement suggestions
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <footer className="mt-16 text-center text-gray-500 text-sm">
          <p>ATS Resume Analyzer - Check your resume compatibility with Applicant Tracking Systems</p>
        </footer>
      </div>

      {/* Resume Builder Modal */}
      {showResumeBuilder && result && file && (
        <ResumeBuilder
          result={result}
          originalFileName={file.name}
          onClose={() => setShowResumeBuilder(false)}
        />
      )}
    </div>
  )
}
