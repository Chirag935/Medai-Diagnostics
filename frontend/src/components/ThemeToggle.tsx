'use client'

import { useTheme } from '@/context/ThemeContext'
import { Sun, Moon, Monitor } from 'lucide-react'

export default function ThemeToggle() {
  const { theme, setTheme, actualTheme, toggleTheme } = useTheme()

  return (
    <div className="flex items-center gap-2">
      <button
        onClick={toggleTheme}
        className="relative p-2 rounded-lg bg-white/10 dark:bg-gray-800/50 hover:bg-white/20 dark:hover:bg-gray-700/50 transition-all duration-300 group"
        aria-label={`Switch to ${actualTheme === 'dark' ? 'light' : 'dark'} mode`}
      >
        <div className="relative w-5 h-5">
          <Sun 
            className={`absolute inset-0 w-5 h-5 text-yellow-500 transition-all duration-300 ${
              actualTheme === 'light' ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 rotate-90 scale-0'
            }`}
          />
          <Moon 
            className={`absolute inset-0 w-5 h-5 text-blue-400 transition-all duration-300 ${
              actualTheme === 'dark' ? 'opacity-100 rotate-0 scale-100' : 'opacity-0 -rotate-90 scale-0'
            }`}
          />
        </div>
        <span className="sr-only">Toggle theme</span>
      </button>

      <div className="flex items-center bg-white/10 dark:bg-gray-800/50 rounded-lg p-1">
        <button
          onClick={() => setTheme('light')}
          className={`p-1.5 rounded-md transition-all duration-200 ${
            theme === 'light' 
              ? 'bg-yellow-500/20 text-yellow-600 dark:text-yellow-400' 
              : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
          }`}
          title="Light mode"
        >
          <Sun className="w-4 h-4" />
        </button>
        <button
          onClick={() => setTheme('dark')}
          className={`p-1.5 rounded-md transition-all duration-200 ${
            theme === 'dark' 
              ? 'bg-blue-500/20 text-blue-600 dark:text-blue-400' 
              : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
          }`}
          title="Dark mode"
        >
          <Moon className="w-4 h-4" />
        </button>
        <button
          onClick={() => setTheme('system')}
          className={`p-1.5 rounded-md transition-all duration-200 ${
            theme === 'system' 
              ? 'bg-purple-500/20 text-purple-600 dark:text-purple-400' 
              : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
          }`}
          title="System preference"
        >
          <Monitor className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
