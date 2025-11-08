import type { Metadata } from 'next'
import './globals.css'

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
    <html lang="en">
      <body className="bg-gray-50 antialiased">
        {children}
      </body>
    </html>
  )
}

