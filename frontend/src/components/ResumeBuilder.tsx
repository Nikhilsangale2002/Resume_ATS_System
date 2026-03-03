'use client'

import { useState, useRef } from 'react'
import { OptimizedResume as OptimizedResumeType, StandaloneATSResult } from '@/types'

interface ResumeBuilderProps {
  result: StandaloneATSResult
  originalFileName: string
  onClose: () => void
}

export default function ResumeBuilder({ result, originalFileName, onClose }: ResumeBuilderProps) {
  const [isGenerating, setIsGenerating] = useState(false)
  const [activeSection, setActiveSection] = useState<string>('all')
  const resumeRef = useRef<HTMLDivElement>(null)

  const optimized = result.optimized_resume

  // Get sections with flexible key handling (supports both V3 and V4 formats)
  const getSectionContent = (keys: string[]): string | undefined => {
    for (const key of keys) {
      const content = optimized?.sections?.[key]
      if (content) return content
    }
    return undefined
  }

  // Get all sections in order for display
  const getAllSections = (): { key: string, title: string, content: string }[] => {
    if (!optimized?.sections) return []
    
    const sections: { key: string, title: string, content: string }[] = []
    const sectionOrder = [
      { keys: ['CONTACT', 'contact'], title: 'Contact' },
      { keys: ['PROFESSIONAL SUMMARY', 'CAREER OBJECTIVE', 'summary', 'objective'], title: 'Professional Summary' },
      { keys: ['PROFESSIONAL EXPERIENCE', 'experience'], title: 'Professional Experience' },
      { keys: ['EDUCATION', 'education'], title: 'Education' },
      { keys: ['SKILLS', 'skills'], title: 'Skills' },
      { keys: ['PROJECTS', 'projects'], title: 'Projects' },
      { keys: ['CERTIFICATIONS', 'certifications'], title: 'Certifications' },
      { keys: ['AWARDS & ACHIEVEMENTS', 'awards'], title: 'Awards & Achievements' },
      { keys: ['PUBLICATIONS', 'publications'], title: 'Publications' },
      { keys: ['LANGUAGES', 'languages'], title: 'Languages' },
      { keys: ['VOLUNTEER EXPERIENCE', 'volunteer'], title: 'Volunteer Experience' },
      { keys: ['INTERESTS', 'interests'], title: 'Interests' },
    ]

    for (const section of sectionOrder) {
      const content = getSectionContent(section.keys)
      if (content) {
        sections.push({ key: section.keys[0], title: section.title, content })
      }
    }

    return sections
  }

  const handleDownloadText = () => {
    const content = generatePlainText()
    const blob = new Blob([content], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ATS_Optimized_${originalFileName.replace(/\.[^/.]+$/, '')}.txt`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handleDownloadHTML = () => {
    const content = generateHTMLContent()
    const blob = new Blob([content], { type: 'text/html' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `ATS_Optimized_${originalFileName.replace(/\.[^/.]+$/, '')}.html`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
  }

  const handlePrint = () => {
    const printContent = resumeRef.current
    if (!printContent) return

    const printWindow = window.open('', '_blank')
    if (!printWindow) return

    printWindow.document.write(`
      <!DOCTYPE html>
      <html>
      <head>
        <title>ATS Optimized Resume</title>
        <style>
          body {
            font-family: 'Arial', sans-serif;
            line-height: 1.6;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px;
            color: #333;
          }
          h1 { font-size: 24px; margin-bottom: 5px; color: #1a1a1a; }
          h2 { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; border-bottom: 2px solid #333; padding-bottom: 5px; margin-top: 20px; margin-bottom: 10px; }
          .contact { font-size: 12px; color: #666; margin-bottom: 20px; text-align: center; }
          .section { margin-bottom: 15px; }
          .section-content { font-size: 12px; white-space: pre-wrap; }
          ul { margin: 5px 0; padding-left: 20px; }
          li { margin-bottom: 3px; font-size: 12px; }
          @media print {
            body { padding: 20px; }
          }
        </style>
      </head>
      <body>
        ${generatePrintHTML()}
      </body>
      </html>
    `)
    printWindow.document.close()
    printWindow.print()
  }

  const generatePlainText = () => {
    // Use full_resume if available (V4 format)
    if (optimized?.full_resume) {
      return optimized.full_resume
    }

    // Fallback to building from sections
    let content = ''
    const sections = getAllSections()
    
    for (const section of sections) {
      if (section.title === 'Contact') {
        content += section.content + '\n\n'
      } else {
        content += section.title.toUpperCase() + '\n'
        content += '═'.repeat(50) + '\n'
        content += section.content + '\n\n'
      }
    }
    
    return content
  }

  const generateHTMLContent = () => {
    return `
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <title>ATS Optimized Resume</title>
  <style>
    body {
      font-family: 'Arial', sans-serif;
      line-height: 1.6;
      max-width: 800px;
      margin: 0 auto;
      padding: 40px;
      color: #333;
    }
    h1 { font-size: 24px; margin-bottom: 5px; color: #1a1a1a; text-align: center; }
    h2 { 
      font-size: 14px; 
      text-transform: uppercase; 
      letter-spacing: 1px; 
      border-bottom: 2px solid #333; 
      padding-bottom: 5px; 
      margin-top: 25px; 
      margin-bottom: 15px; 
    }
    .contact { font-size: 13px; color: #555; margin-bottom: 25px; text-align: center; }
    .section-content { font-size: 13px; white-space: pre-wrap; line-height: 1.5; }
  </style>
</head>
<body>
  ${generatePrintHTML()}
</body>
</html>`
  }

  const generatePrintHTML = () => {
    let html = ''
    const sections = getAllSections()
    
    for (const section of sections) {
      if (section.title === 'Contact') {
        html += `<div class="contact">${section.content.replace(/\n/g, '<br>')}</div>`
      } else {
        html += `<h2>${section.title}</h2>`
        html += `<div class="section-content">${section.content.replace(/\n/g, '<br>')}</div>`
      }
    }
    
    return html
  }

  const copyToClipboard = async () => {
    const content = generatePlainText()
    try {
      await navigator.clipboard.writeText(content)
      alert('Resume copied to clipboard!')
    } catch (err) {
      console.error('Failed to copy:', err)
    }
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="bg-gradient-to-r from-blue-600 to-indigo-600 text-white px-6 py-4 flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold">ATS-Optimized Resume</h2>
            <p className="text-blue-100 text-sm">Your resume with all improvements applied</p>
          </div>
          <button
            onClick={onClose}
            className="text-white hover:bg-white/20 rounded-full p-2 transition"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        {/* Action Buttons */}
        <div className="bg-gray-50 border-b px-6 py-3 flex flex-wrap gap-3">
          <button
            onClick={handlePrint}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 17h2a2 2 0 002-2v-4a2 2 0 00-2-2H5a2 2 0 00-2 2v4a2 2 0 002 2h2m2 4h6a2 2 0 002-2v-4a2 2 0 00-2-2H9a2 2 0 00-2 2v4a2 2 0 002 2zm8-12V5a2 2 0 00-2-2H9a2 2 0 00-2 2v4h10z" />
            </svg>
            Print / Save as PDF
          </button>
          <button
            onClick={handleDownloadHTML}
            className="flex items-center gap-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
            </svg>
            Download HTML
          </button>
          <button
            onClick={handleDownloadText}
            className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Download TXT
          </button>
          <button
            onClick={copyToClipboard}
            className="flex items-center gap-2 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-100 transition text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
            </svg>
            Copy All
          </button>
        </div>

        {/* Improvements Applied */}
        <div className="bg-green-50 border-b border-green-200 px-6 py-3">
          <h3 className="text-sm font-semibold text-green-800 mb-2">Improvements Applied:</h3>
          <div className="flex flex-wrap gap-2">
            {optimized.improvements.map((improvement, index) => (
              <span key={index} className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded text-xs">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                {improvement}
              </span>
            ))}
          </div>
        </div>

        {/* Original Data Summary */}
        {optimized?.original_data && (
          <div className="bg-gray-50 border-b px-6 py-3">
            <h3 className="text-sm font-semibold text-gray-700 mb-2">Extracted Data:</h3>
            <div className="flex flex-wrap gap-3 text-xs text-gray-600">
              {optimized.original_data.name && (
                <span className="bg-white px-2 py-1 rounded border">👤 {optimized.original_data.name}</span>
              )}
              {(optimized.original_data.experience_count ?? 0) > 0 && (
                <span className="bg-white px-2 py-1 rounded border">💼 {optimized.original_data.experience_count} jobs</span>
              )}
              {(optimized.original_data.education_count ?? 0) > 0 && (
                <span className="bg-white px-2 py-1 rounded border">🎓 {optimized.original_data.education_count} education</span>
              )}
              {(optimized.original_data.skills_count ?? 0) > 0 && (
                <span className="bg-white px-2 py-1 rounded border">🛠 {optimized.original_data.skills_count} skills</span>
              )}
              {(optimized.original_data.projects_count ?? 0) > 0 && (
                <span className="bg-white px-2 py-1 rounded border">📁 {optimized.original_data.projects_count} projects</span>
              )}
              {(optimized.original_data.certifications_count ?? 0) > 0 && (
                <span className="bg-white px-2 py-1 rounded border">📜 {optimized.original_data.certifications_count} certifications</span>
              )}
            </div>
          </div>
        )}

        {/* Resume Preview */}
        <div className="flex-1 overflow-y-auto p-6" ref={resumeRef}>
          <div className="max-w-2xl mx-auto bg-white border border-gray-200 shadow-lg rounded-lg p-8">
            {/* Render all sections dynamically */}
            {getAllSections().map((section, index) => (
              <div key={section.key} className={section.title === 'Contact' ? 'text-center mb-6 pb-4 border-b-2 border-gray-800' : 'mb-6'}>
                {section.title !== 'Contact' && (
                  <h2 className="text-sm font-bold uppercase tracking-wider text-gray-800 border-b-2 border-gray-800 pb-1 mb-3">
                    {section.title}
                  </h2>
                )}
                <pre className="whitespace-pre-wrap font-sans text-sm text-gray-700 leading-relaxed">
                  {section.content}
                </pre>
              </div>
            ))}
          </div>
        </div>

        {/* Template Suggestions */}
        {optimized.template_suggestions && optimized.template_suggestions.length > 0 && (
          <div className="bg-yellow-50 border-t border-yellow-200 px-6 py-3">
            <h3 className="text-xs font-semibold text-yellow-800 mb-1">ATS Tips:</h3>
            <p className="text-xs text-yellow-700">
              {optimized.template_suggestions.slice(0, 3).join(' • ')}
            </p>
          </div>
        )}

        {/* Footer Tips */}
        <div className="bg-blue-50 border-t px-6 py-3">
          <p className="text-xs text-blue-700">
            <strong>Tip:</strong> Use "Print / Save as PDF" to create a PDF file. In the print dialog, select "Save as PDF" as your printer option.
          </p>
        </div>
      </div>
    </div>
  )
}
