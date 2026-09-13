
import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'AI Sales-Enablement Platform',
  description: 'Intelligent sales insights powered by AI - Transform your sales process with advanced analytics, automated insights, and seamless CRM integration.',
  keywords: ['AI', 'Sales', 'CRM', 'Analytics', 'Automation', 'Insights'],
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-100">
          {children}
        </div>
      </body>
    </html>
  )
}
