'use client'

interface Keyword {
  keyword: string
  is_matched: boolean
  category: string
}

interface KeywordAnalysisProps {
  matched: Keyword[]
  missing: Keyword[]
  suggestions: string[]
}

export default function KeywordAnalysis({ matched, missing, suggestions }: KeywordAnalysisProps) {
  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6">
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        Keyword Analysis
      </h2>

      {/* Matched Keywords */}
      <div className="mb-6">
        <h3 className="flex items-center gap-2 text-sm font-medium text-green-700 mb-3">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
          Matched Keywords ({matched.length})
        </h3>
        <div className="flex flex-wrap gap-2">
          {matched.length > 0 ? (
            matched.map((kw, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-green-100 text-green-700"
              >
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                {kw.keyword}
              </span>
            ))
          ) : (
            <span className="text-gray-500 text-sm">No matched keywords found</span>
          )}
        </div>
      </div>

      {/* Missing Keywords */}
      <div className="mb-6">
        <h3 className="flex items-center gap-2 text-sm font-medium text-red-700 mb-3">
          <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
          Missing Keywords ({missing.length})
        </h3>
        <div className="flex flex-wrap gap-2">
          {missing.length > 0 ? (
            missing.map((kw, idx) => (
              <span
                key={idx}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-red-100 text-red-700"
              >
                <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
                </svg>
                {kw.keyword}
              </span>
            ))
          ) : (
            <span className="text-green-600 text-sm">All keywords matched!</span>
          )}
        </div>
      </div>

      {/* Suggestions */}
      {suggestions.length > 0 && (
        <div className="pt-4 border-t border-gray-200">
          <h3 className="flex items-center gap-2 text-sm font-medium text-primary-700 mb-3">
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Suggestions to Improve
          </h3>
          <ul className="space-y-2">
            {suggestions.map((suggestion, idx) => (
              <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                <svg className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
                {suggestion}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Tips */}
      <div className="mt-6 p-4 bg-blue-50 rounded-lg">
        <h4 className="text-sm font-medium text-blue-800 mb-2">Pro Tips:</h4>
        <ul className="text-sm text-blue-700 space-y-1">
          <li>• Mirror exact keywords from the job description</li>
          <li>• Include both acronyms and full forms (AWS & Amazon Web Services)</li>
          <li>• Quantify experience with years and metrics</li>
          <li>• Use action verbs (developed, implemented, managed)</li>
        </ul>
      </div>
    </div>
  )
}
