'use client'

import { ATSSuggestion, ATSIssue } from '@/types'

interface SuggestionsPanelProps {
  suggestions: ATSSuggestion[]
  issues: ATSIssue[]
}

export default function SuggestionsPanel({ suggestions, issues }: SuggestionsPanelProps) {
  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'critical':
        return 'bg-red-100 text-red-800 border-red-200'
      case 'major':
        return 'bg-orange-100 text-orange-800 border-orange-200'
      case 'minor':
        return 'bg-yellow-100 text-yellow-800 border-yellow-200'
      default:
        return 'bg-gray-100 text-gray-800 border-gray-200'
    }
  }

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'critical':
        return (
          <svg className="w-5 h-5 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        )
      case 'major':
        return (
          <svg className="w-5 h-5 text-orange-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
      default:
        return (
          <svg className="w-5 h-5 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        )
    }
  }

  const criticalCount = suggestions.filter(s => s.priority === 'critical').length
  const majorCount = suggestions.filter(s => s.priority === 'major').length
  const minorCount = suggestions.filter(s => s.priority === 'minor').length

  return (
    <div className="space-y-6">
      {/* Summary */}
      <div className="flex gap-4 mb-6">
        <div className="flex items-center gap-2 px-3 py-1 bg-red-100 rounded-full">
          <span className="w-2 h-2 bg-red-500 rounded-full"></span>
          <span className="text-sm font-medium text-red-800">{criticalCount} Critical</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-orange-100 rounded-full">
          <span className="w-2 h-2 bg-orange-500 rounded-full"></span>
          <span className="text-sm font-medium text-orange-800">{majorCount} Major</span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1 bg-yellow-100 rounded-full">
          <span className="w-2 h-2 bg-yellow-500 rounded-full"></span>
          <span className="text-sm font-medium text-yellow-800">{minorCount} Minor</span>
        </div>
      </div>

      {/* Suggestions List */}
      <div className="space-y-4">
        {suggestions.length === 0 ? (
          <div className="text-center py-8 text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-4 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <p className="font-medium">Great job! No major issues found.</p>
          </div>
        ) : (
          suggestions.map((suggestion, index) => (
            <div
              key={index}
              className={`p-4 rounded-lg border ${getPriorityColor(suggestion.priority)}`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getPriorityIcon(suggestion.priority)}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-semibold uppercase tracking-wide opacity-75">
                      {suggestion.category}
                    </span>
                    <span className={`text-xs px-2 py-0.5 rounded ${
                      suggestion.impact === 'high' ? 'bg-red-200' :
                      suggestion.impact === 'medium' ? 'bg-orange-200' : 'bg-yellow-200'
                    }`}>
                      {suggestion.impact} impact
                    </span>
                  </div>
                  <p className="font-medium mb-1">{suggestion.issue}</p>
                  <p className="text-sm opacity-90">{suggestion.suggestion}</p>
                </div>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
