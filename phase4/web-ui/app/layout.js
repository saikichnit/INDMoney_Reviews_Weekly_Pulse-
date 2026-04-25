import './globals.css'
import Link from 'next/link'

export const metadata = {
  title: 'INDMoney Pulse | Review Intelligence',
  description: 'Automated weekly pulse for product and engineering teams.',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
      </head>
      <body className="antialiased">
        <nav className="glass-panel px-6 py-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2 group mr-4">
                <div className="w-8 h-8 bg-[#0066CC] rounded-lg flex items-center justify-center text-white font-bold text-xl group-hover:scale-105 transition-transform">
                  I
                </div>
                <span className="font-bold text-xl tracking-tight text-slate-900 dark:text-white">Pulse</span>
              </Link>
              <div className="hidden lg:flex items-center gap-1">
                <Link href="/reviews" className="px-3 py-2 text-xs font-medium text-slate-600 hover:text-[#0066CC] transition-colors">INDMoney Insights</Link>
                <Link href="/analytics" className="px-3 py-2 text-xs font-medium text-slate-600 hover:text-[#0066CC] transition-colors">Categories</Link>
                <Link href="/reports" className="px-3 py-2 text-xs font-medium text-slate-600 hover:text-[#0066CC] transition-colors flex items-center gap-1.5">
                  INDPlus
                  <span className="text-[8px] px-1 bg-[#0066CC]/10 text-[#0066CC] rounded font-bold border border-[#0066CC]/20">MCP</span>
                </Link>
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 text-xs font-bold rounded-full border border-green-200 dark:border-green-800 uppercase tracking-widest">
                Production
              </div>
              <button className="w-8 h-8 rounded-full bg-slate-100 dark:bg-zinc-800 flex items-center justify-center">
                <span className="sr-only">Profile</span>
                <div className="w-6 h-6 rounded-full bg-[#0066CC]/20 text-[#0066CC] text-[10px] font-bold flex items-center justify-center">
                  SK
                </div>
              </button>
            </div>
          </div>
        </nav>
        <main className="max-w-7xl mx-auto p-6 min-h-[calc(100vh-76px)]">
          {children}
        </main>
      </body>
    </html>
  )
}
