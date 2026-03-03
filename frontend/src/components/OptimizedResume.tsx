'use client'

import { useState } from 'react'
import { OptimizedResume as OptimizedResumeType } from '@/types'

interface OptimizedResumeProps {
  optimized: OptimizedResumeType
}

export default function OptimizedResume({ optimized }: OptimizedResumeProps) {
  const [copiedSection, setCopiedSection] = useState<string | null>(null)

  const copyToClipboard = async (text: string, section: string) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedSection(section)
      setTimeout(() => setCopiedSection(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const copyAllSections = async () => {
    const allText = Object.entries(optimized.sections)
      .map(([key, value]) => value)
      .join('\n\n---\n\n')
    
    try {
      await navigator.clipboard.writeText(allText)
      setCopiedSection('all')
      setTimeout(() => setCopiedSection(null), 2000)
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  const sectionLabels: Record<string, string> = {
    contact: 'Contact Information',
    summary: 'Professional Summary',
    skills: 'Skills Section',
    experience: 'Experience Section',
    education: 'Education Section'
  }

  return (
    <div className="space-y-6">
      {/* Introduction */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h3 className="font-semibold text-blue-900 mb-2">ATS-Optimized Resume Template</h3>
        <p className="text-sm text-blue-700">
          Below are optimized templates for each section of your resume. Copy and customize these 
          with your actual information to improve your ATS score.
        </p>
      </div>

      {/* Template Tips */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-semibold text-gray-900 mb-3">Template Suggestions</h4>
        <ul className="space-y-2">
          {optimized.template_suggestions.map((tip, index) => (
            <li key={index} className="flex items-start gap-2 text-sm text-gray-700">
              <svg className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
              {tip}
            </li>
          ))}
        </ul>
      </div>

      {/* Copy All Button */}
      <button
        onClick={copyAllSections}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition flex items-center justify-center gap-2"
      >
        {copiedSection === 'all' ? (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
            Copied All Sections!
          </>
        ) : (
          <>
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Copy All Sections
          </>
        )}
      </button>

      {/* Individual Sections */}
      <div className="space-y-4">
        {Object.entries(optimized.sections).map(([key, content]) => (
          <div key={key} className="border border-gray-200 rounded-lg overflow-hidden">
            <div className="flex items-center justify-between bg-gray-50 px-4 py-2 border-b">
              <h4 className="font-medium text-gray-900">
                {sectionLabels[key] || key.charAt(0).toUpperCase() + key.slice(1)}
              </h4>
              <button
                onClick={() => copyToClipboard(content, key)}
                className="text-sm text-blue-600 hover:text-blue-800 flex items-center gap-1"
              >
                {copiedSection === key ? (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                    </svg>
                    Copied!
                  </>
                ) : (
                  <>
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    Copy
                  </>
                )}
              </button>
            </div>
            <pre className="p-4 text-sm text-gray-700 whitespace-pre-wrap font-mono bg-white overflow-x-auto">
              {content}
            </pre>
          </div>
        ))}
      </div>
    </div>
  )
}
