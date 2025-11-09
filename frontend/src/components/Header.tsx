'use client'

export default function Header() {
  return (
    <header className="bg-gray-800 border-b border-gray-700">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-xl">D</span>
            </div>
            <div>
              <h1 className="text-xl font-bold text-gray-100">DevAI Manager</h1>
              <p className="text-sm text-gray-400">AI-Powered Project Management</p>
            </div>
          </div>
          <nav className="flex items-center space-x-4">
            <button className="text-gray-400 hover:text-gray-200 px-3 py-2 rounded-md text-sm font-medium">
              Settings
            </button>
          </nav>
        </div>
      </div>
    </header>
  )
}

