import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { AuthProvider } from '@/context/AuthContext'
import Navbar from '@/components/Navbar'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'ATS Resume Scorer | Get Your Resume ATS Score',
  description: 'Free ATS Resume Scoring System - Check your resume compatibility with Applicant Tracking Systems',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <div className="min-h-screen">
            {/* Navigation */}
            <Navbar />
            
            {/* Main Content */}
            <main>
              {children}
            </main>
          </div>
        </AuthProvider>
      </body>
    </html>
  )
}
