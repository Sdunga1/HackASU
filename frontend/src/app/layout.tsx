import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'
import { ThemeProvider } from '@/contexts/ThemeContext'

const inter = Inter({ 
  subsets: ['latin'],
  display: 'swap',
  variable: '--font-inter',
})

export const metadata: Metadata = {
  title: 'DevAI Manager - AI-Powered Project Management',
  description: 'Intelligent project management for GitHub and Jira workflows',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="antialiased font-sans">
        <ThemeProvider>
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}

