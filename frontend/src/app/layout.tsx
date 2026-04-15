import './globals.css'
import { Inter } from 'next/font/google'
import { ThemeProvider } from '@/context/ThemeContext'
import { ToastProvider } from '@/context/ToastContext'
import { SessionProvider } from '@/context/SessionContext'

const inter = Inter({ subsets: ['latin'] })

export const metadata = {
  title: 'MedAI Diagnostics - Medical AI Disease Detection Platform',
  description: 'Advanced AI-powered disease detection and prediction platform for medical diagnostics',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body className={inter.className}>
        <ThemeProvider>
          <ToastProvider>
            <SessionProvider>
              {children}
            </SessionProvider>
          </ToastProvider>
        </ThemeProvider>
      </body>
    </html>
  )
}
