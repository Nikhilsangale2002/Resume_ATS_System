'use client'

interface ScoreCardProps {
  score: number
}

export default function ScoreCard({ score }: ScoreCardProps) {
  const getScoreColor = (score: number) => {
    if (score >= 80) return { stroke: '#22c55e', bg: 'bg-green-50', text: 'text-green-600', label: 'Excellent' }
    if (score >= 60) return { stroke: '#f59e0b', bg: 'bg-yellow-50', text: 'text-yellow-600', label: 'Good' }
    if (score >= 40) return { stroke: '#f97316', bg: 'bg-orange-50', text: 'text-orange-600', label: 'Fair' }
    return { stroke: '#ef4444', bg: 'bg-red-50', text: 'text-red-600', label: 'Needs Work' }
  }

  const colorConfig = getScoreColor(score)
  const circumference = 2 * Math.PI * 45
  const dashOffset = circumference - (score / 100) * circumference

  return (
    <div className={`${colorConfig.bg} rounded-xl shadow-sm border border-gray-200 p-8 text-center`}>
      <h2 className="text-lg font-semibold text-gray-900 mb-6">
        ATS Score
      </h2>
      
      <div className="relative w-40 h-40 mx-auto">
        <svg className="w-full h-full transform -rotate-90">
          {/* Background circle */}
          <circle
            cx="80"
            cy="80"
            r="45"
            stroke="#e5e7eb"
            strokeWidth="10"
            fill="none"
          />
          {/* Score circle */}
          <circle
            cx="80"
            cy="80"
            r="45"
            stroke={colorConfig.stroke}
            strokeWidth="10"
            fill="none"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            className="score-circle"
          />
        </svg>
        
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={`text-4xl font-bold ${colorConfig.text}`}>
            {Math.round(score)}
          </span>
          <span className="text-gray-500 text-sm">out of 100</span>
        </div>
      </div>

      <div className={`mt-6 inline-flex items-center gap-2 px-4 py-2 rounded-full ${colorConfig.bg}`}>
        <span className={`font-semibold ${colorConfig.text}`}>
          {colorConfig.label}
        </span>
      </div>

      <p className="text-gray-600 mt-4 text-sm">
        {score >= 80 && "Your resume is highly optimized for ATS systems!"}
        {score >= 60 && score < 80 && "Good match! A few improvements can boost your score."}
        {score >= 40 && score < 60 && "There's room for improvement. Follow the suggestions below."}
        {score < 40 && "Significant improvements needed. Focus on matching job requirements."}
      </p>
    </div>
  )
}
