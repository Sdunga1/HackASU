'use client'

import { useTheme } from '@/contexts/ThemeContext'

export default function Header() {
  const { theme, toggleTheme } = useTheme()
  const isDark = theme === 'dark'

  return (
    <header style={{ 
      background: isDark 
        ? 'linear-gradient(135deg, #8C1D40 0%, #6B1530 50%, #8C1D40 100%)'
        : 'linear-gradient(135deg, #8C1D40 0%, #a02350 50%, #8C1D40 100%)',
      borderBottom: '2px solid rgba(255, 198, 39, 0.3)',
      boxShadow: isDark ? '0 4px 20px rgba(140, 29, 64, 0.4)' : '0 4px 20px rgba(140, 29, 64, 0.2)',
      transition: 'all 0.3s ease'
    }}>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="w-12 h-12 rounded-xl flex items-center justify-center shadow-lg transform hover:scale-105 transition-transform duration-200" style={{
              background: 'linear-gradient(135deg, #FFC627 0%, #FFD757 100%)',
              boxShadow: '0 4px 15px rgba(255, 198, 39, 0.5)'
            }}>
              <span className="text-3xl">🔱</span>
            </div>
            <div>
              <h1 className="text-2xl font-bold tracking-tight" style={{
                background: 'linear-gradient(135deg, #FFC627 0%, #FFD757 100%)',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                backgroundClip: 'text'
              }}>
                DevAI Manager
              </h1>
              <p className="text-sm font-medium tracking-wide" style={{ color: 'rgba(255, 198, 39, 0.8)' }}>
                AI-Powered Project Intelligence
              </p>
            </div>
          </div>
          
          <button
            onClick={toggleTheme}
            className="p-2 rounded-lg transition-all duration-200 hover:scale-110"
            style={{
              backgroundColor: 'rgba(255, 198, 39, 0.15)',
              border: '1px solid rgba(255, 198, 39, 0.3)'
            }}
            aria-label="Toggle theme"
          >
            {isDark ? (
              <svg className="w-6 h-6" style={{ color: '#FFC627' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364 6.364l-.707-.707M6.343 6.343l-.707-.707m12.728 0l-.707.707M6.343 17.657l-.707.707M16 12a4 4 0 11-8 0 4 4 0 018 0z" />
              </svg>
            ) : (
              <svg className="w-6 h-6" style={{ color: '#8C1D40' }} fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
              </svg>
            )}
          </button>
        </div>
      </div>
    </header>
  )
}

