'use client'

import { Radar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, ResponsiveContainer, Tooltip } from 'recharts'
import { StandaloneScoreDetails } from '@/types'

interface ScoreBreakdownProps {
  details: StandaloneScoreDetails
}

export default function ScoreBreakdown({ details }: ScoreBreakdownProps) {
  const chartData = [
    { subject: 'Formatting', score: details.formatting, label: 'Formatting' },
    { subject: 'Contact', score: details.contact_info, label: 'Contact Info' },
    { subject: 'Skills', score: details.skills_section, label: 'Skills Section' },
    { subject: 'Experience', score: details.experience_section, label: 'Experience' },
    { subject: 'Education', score: details.education_section, label: 'Education' },
    { subject: 'Keywords', score: details.keywords_density, label: 'Keywords' },
    { subject: 'Readability', score: details.readability, label: 'Readability' },
    { subject: 'Length', score: details.length_optimization, label: 'Length' },
  ]

  const getBarColor = (score: number) => {
    if (score >= 80) return 'bg-green-500'
    if (score >= 60) return 'bg-yellow-500'
    if (score >= 40) return 'bg-orange-500'
    return 'bg-red-500'
  }

  const getStatusIcon = (score: number) => {
    if (score >= 80) return '✓'
    if (score >= 60) return '!'
    return '✗'
  }

  const getStatusColor = (score: number) => {
    if (score >= 80) return 'text-green-500'
    if (score >= 60) return 'text-yellow-500'
    return 'text-red-500'
  }

  return (
    <div>
      <h3 className="font-semibold text-gray-900 mb-4">Score Breakdown</h3>

      {/* Radar Chart */}
      <div className="h-64 mb-6">
        <ResponsiveContainer width="100%" height="100%">
          <RadarChart data={chartData}>
            <PolarGrid stroke="#e5e7eb" />
            <PolarAngleAxis 
              dataKey="subject" 
              tick={{ fill: '#6b7280', fontSize: 10 }}
              tickLine={false}
            />
            <PolarRadiusAxis 
              angle={90} 
              domain={[0, 100]} 
              tick={{ fill: '#9ca3af', fontSize: 10 }}
              tickCount={5}
            />
            <Radar
              name="Score"
              dataKey="score"
              stroke="#3b82f6"
              fill="#3b82f6"
              fillOpacity={0.3}
              strokeWidth={2}
            />
            <Tooltip 
              formatter={(value: number) => [`${value.toFixed(0)}%`, 'Score']}
              contentStyle={{ 
                backgroundColor: 'white', 
                border: '1px solid #e5e7eb',
                borderRadius: '8px',
                fontSize: '12px'
              }}
            />
          </RadarChart>
        </ResponsiveContainer>
      </div>

      {/* Detailed Bars */}
      <div className="space-y-3">
        {chartData.map((item) => (
          <div key={item.subject}>
            <div className="flex justify-between text-sm mb-1">
              <span className="text-gray-700 flex items-center gap-2">
                <span className={`font-bold ${getStatusColor(item.score)}`}>
                  {getStatusIcon(item.score)}
                </span>
                {item.label}
              </span>
              <span className={`font-medium ${getStatusColor(item.score)}`}>
                {item.score.toFixed(0)}%
              </span>
            </div>
            <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
              <div
                className={`h-full ${getBarColor(item.score)} transition-all duration-500`}
                style={{ width: `${item.score}%` }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
