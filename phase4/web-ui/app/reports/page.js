'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function ReportsAndAutomation() {
  const router = useRouter()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [selectedMonths, setSelectedMonths] = useState(10)
  const [isPolling, setIsPolling] = useState(false)
  const [pollCount, setPollCount] = useState(0)
  const [startTime, setStartTime] = useState(null)
  const [recipientEmail, setRecipientEmail] = useState('stakeholders@indmoney.com')
  const [sending, setSending] = useState(false)

  const handleApprove = async (reportId, mode) => {
    setSending(true)
    try {
      const res = await fetch(`/api/reports/${reportId}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: recipientEmail, mode })
      })
      if (res.ok) alert("Email sent successfully!")
      else alert("Failed to send email")
    } catch (err) {
      console.error(err)
    } finally {
      setSending(false)
    }
  }

  useEffect(() => {
    fetchReports()
  }, [])

  const [runId, setRunId] = useState(null)
  const [runStatus, setRunStatus] = useState('queued')

  useEffect(() => {
    let interval;
    if (isPolling) {
      interval = setInterval(() => {
        setPollCount(prev => prev + 1)
        if (runId) {
          checkRunStatus()
        } else {
          fetchReports(true)
        }
      }, 3000)
    }
    return () => clearInterval(interval)
  }, [isPolling, runId])

  const checkRunStatus = async () => {
    try {
      // Use the Next.js API as a proxy to check GitHub Action status (avoids CORS/Token leaks)
      const res = await fetch(`/api/check-run?run_id=${runId}`)
      const data = await res.json()
      setRunStatus(data.status) // 'queued', 'in_progress', 'completed'
      
      if (data.status === 'completed') {
        fetchReports(true)
      }
    } catch (err) {
      console.error(err)
      // Fallback to report polling if status check fails
      fetchReports(true)
    }
  }

  useEffect(() => {
    if (isPolling && reports.length > 0 && startTime) {
      const latest = reports[0]
      const createdAt = new Date(latest.created_at).getTime()
      // If the report was created after we clicked "Generate", it's the new one!
      if (createdAt > startTime) {
        setIsPolling(false)
        router.push(`/report/${latest.id}`)
      }
    }
  }, [reports, isPolling, startTime])

  const fetchReports = async (bypassCache = false) => {
    if (!isPolling && !bypassCache) setLoading(true)
    try {
      // Use the GitHub Contents API for polling instead of the RAW URL to avoid 5-minute caching
      const GITHUB_API_URL = "https://api.github.com/repos/saikichnit/INDMoney_Reviews_Weekly_Pulse-/contents/data/reports_archive.json";
      const res = await fetch(GITHUB_API_URL, { 
        headers: { 
          'Accept': 'application/vnd.github.v3.raw',
          'Cache-Control': 'no-cache'
        }
      });
      const data = await res.json();
      if (Array.isArray(data)) {
        setReports(data);
      }
    } catch (err) {
      console.error(err)
    } finally {
      if (!isPolling) setLoading(false)
    }
  }

  const handleGenerate = async () => {
    // 1. OPTIMISTIC REDIRECT: To achieve the 5-10 second goal, we instantly open the latest report
    // while the cloud worker refreshes the signals in the background.
    if (reports.length > 0) {
      router.push(`/report/${reports[0].id}?status=updating`)
    }

    setGenerating(true)
    const days = selectedMonths * 30
    const clickTime = Date.now()
    setStartTime(clickTime)

    try {
      const res = await fetch(`/api/generate-report?days=${days}`, { method: 'POST' })
      const data = await res.json()
      
      if (data.report_id) {
        router.push(`/report/${data.report_id}`)
      } else if (data.status === "started") {
        if (data.run_id) setRunId(data.run_id)
        setIsPolling(true)
        setPollCount(0)
      } else {
        alert("Generation failed: " + (data.error || "Unknown error"))
      }
    } catch (err) {
      console.error(err)
    } finally {
      setGenerating(false)
    }
  }

  const getRangeLabel = (m) => {
    return `TARGET: ${m}-MONTH DEEP DIVE`
  }

  const getAnalysisWindow = () => {
    const now = new Date()
    const start = new Date()
    start.setMonth(now.getMonth() - selectedMonths)
    const months = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
    const format = (d) => `${months[d.getMonth()]} ${d.getDate()}, ${d.getFullYear()}`
    return `${format(start).toUpperCase()} – ${format(now).toUpperCase()}`
  }

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans">
      {/* Top Navigation Bar */}
      <nav className="flex items-center justify-between px-8 py-4 border-b border-gray-100">
        <div className="flex items-center space-x-12">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-[#0066CC] rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">I</span>
            </div>
            <span className="text-xl font-bold text-gray-400">Pulse</span>
          </div>
          <div className="hidden md:flex items-center space-x-8 text-sm font-medium text-gray-500">
            <Link href="/" className="hover:text-[#0066CC] transition-colors">INDMoney Insights</Link>
            <Link href="/categories" className="hover:text-[#0066CC] transition-colors">Categories</Link>
            <div className="flex items-center space-x-1">
              <Link href="/reports" className="text-slate-900 font-semibold underline decoration-2 underline-offset-8">INDPlus</Link>
              <span className="text-[10px] bg-blue-50 text-[#0066CC] px-1.5 py-0.5 rounded font-bold uppercase tracking-tighter border border-blue-100">MCP</span>
            </div>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          <span className="bg-[#E7F7F1] text-[#22C55E] text-[10px] font-bold px-3 py-1 rounded-full uppercase tracking-widest border border-[#D1F2E5]">Production</span>
          <div className="w-10 h-10 bg-slate-800 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-sm">SK</div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-8 py-16">
        {/* Intelligence Console Section */}
        <div className="flex flex-col lg:flex-row justify-between items-start gap-20 mb-24">
          <div className="max-w-2xl">
            <div className="flex items-center space-x-3 mb-4">
              <span className="text-[10px] font-bold text-[#0066CC] uppercase tracking-widest">INDPLUS INTELLIGENCE</span>
              <span className="text-gray-300 text-xs">|</span>
              <span className="text-[10px] font-bold text-gray-300 uppercase tracking-widest">MODEL CONTEXT PROTOCOL</span>
            </div>
            <h1 className="text-4xl font-bold text-slate-900 mb-6 tracking-tight">Strategic Intelligence Console</h1>
            <p className="text-lg text-slate-500 leading-relaxed max-w-xl">
              Select your strategic window from 1 to 12 months. The AI will synthesize thousands of signals into a one-page executive note, automatically syncing to Google Workspace and drafting leadership reports.
            </p>
          </div>

          <div className="w-full lg:w-96 bg-white space-y-10 pt-4">
            <div className="space-y-6">
              <div className="flex justify-between items-end">
                <div className="flex flex-col">
                  <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">TIME WINDOW</span>
                  <span className="text-[10px] font-bold text-[#0066CC] uppercase tracking-widest">{getAnalysisWindow()}</span>
                </div>
                <div className="text-3xl font-bold text-[#0066CC]">{selectedMonths} Months</div>
              </div>
              <div className="relative">
                <input 
                  type="range" 
                  min="1" 
                  max="12" 
                  value={selectedMonths}
                  onChange={(e) => setSelectedMonths(parseInt(e.target.value))}
                  className="w-full h-1 bg-gray-100 rounded-lg appearance-none cursor-pointer accent-[#0066CC]"
                />
                <div className="flex justify-between mt-4 text-[9px] font-bold text-gray-300 uppercase tracking-widest">
                  <span>1 MONTH</span>
                  <span>6 MONTHS</span>
                  <span>12 MONTHS</span>
                </div>
              </div>
            </div>

            <div className="space-y-4">
              <div className="bg-[#F4F9FF] py-2 text-center rounded-md border border-[#E1EEFF]">
                <span className="text-[10px] font-bold text-[#0066CC] tracking-widest uppercase">{getRangeLabel(selectedMonths)}</span>
              </div>
              <button 
                onClick={handleGenerate}
                disabled={generating || isPolling}
                className={`w-full py-5 rounded-xl font-bold text-lg flex items-center justify-center space-x-3 transition-all ${
                  generating || isPolling 
                  ? 'bg-gray-100 text-gray-400 cursor-not-allowed shadow-none' 
                  : 'bg-[#0066CC] hover:bg-[#0052A3] text-white shadow-xl shadow-blue-200 active:scale-95'
                }`}
              >
                <span>{generating || isPolling ? 'Processing...' : '✨ Generate INDPlus Note'}</span>
              </button>
            </div>
          </div>
        </div>

        {/* Progress Overlay (Clean & White Theme) */}
        {isPolling && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/90 backdrop-blur-sm">
            <div className="max-w-md w-full text-center">
              <div className="mb-10 inline-block relative">
                <div className="w-24 h-24 border-4 border-gray-50 border-t-[#0066CC] rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-[#0066CC] font-bold text-xl">MCP</span>
                </div>
              </div>
              <h2 className="text-3xl font-bold text-slate-900 mb-3 tracking-tight">Synthesizing Strategic Pulse</h2>
              <p className="text-slate-400 mb-12">Analysis running in secure cloud container...</p>
              
              <div className="space-y-5 text-left max-w-xs mx-auto">
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-1.5 h-1.5 rounded-full ${runStatus !== 'queued' ? 'bg-[#0066CC]' : 'bg-gray-200'}`}></div>
                    <span className={`text-sm font-bold uppercase tracking-widest ${runStatus !== 'queued' ? 'text-slate-800' : 'text-gray-300'}`}>Cloud Environment</span>
                  </div>
                  <span className="text-[10px] font-black text-[#0066CC] tracking-tighter">
                    {runStatus === 'queued' ? 'QUEUING...' : 'READY'}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-1.5 h-1.5 rounded-full ${runStatus === 'in_progress' || runStatus === 'completed' ? 'bg-[#0066CC]' : 'bg-gray-200'}`}></div>
                    <span className={`text-sm font-bold uppercase tracking-widest ${runStatus === 'in_progress' || runStatus === 'completed' ? 'text-slate-800' : 'text-gray-300'}`}>AI Synthesis</span>
                  </div>
                  <span className="text-[10px] font-black text-[#0066CC] tracking-tighter">
                    {runStatus === 'in_progress' ? 'PROCESSING...' : (runStatus === 'completed' ? 'DONE' : 'PENDING')}
                  </span>
                </div>
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-4">
                    <div className={`w-1.5 h-1.5 rounded-full ${runStatus === 'completed' ? 'bg-[#0066CC]' : 'bg-gray-200'}`}></div>
                    <span className={`text-sm font-bold uppercase tracking-widest ${runStatus === 'completed' ? 'text-slate-800' : 'text-gray-300'}`}>Finalizing Report</span>
                  </div>
                  <span className="text-[10px] font-black text-[#0066CC] tracking-tighter">
                    {runStatus === 'completed' ? 'SYNCING...' : 'PENDING'}
                  </span>
                </div>
              </div>
              <div className="mt-16 text-gray-300 text-[10px] font-bold uppercase tracking-widest">
                ELAPSED TIME: {pollCount * 5} SECONDS
              </div>
            </div>
          </div>
        )}

        {/* Archive Section */}
        <div>
          <div className="flex items-center justify-between mb-8 border-b border-gray-100 pb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-1">INDPlus Archive</h2>
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">HISTORICAL DECISIONS & SIGNAL RECORDS</p>
            </div>
            <div className="flex items-center space-x-2">
              <div className="w-2 h-2 bg-[#22C55E] rounded-full"></div>
              <span className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Synced to MCP</span>
            </div>
          </div>

          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden min-h-[400px] flex flex-col">
            <div className="grid grid-cols-4 px-10 py-5 bg-gray-50/50 border-b border-gray-100 text-[10px] font-bold text-gray-400 uppercase tracking-[0.2em]">
              <span>GENERATION DATE</span>
              <span>SIGNALS</span>
              <span>STRATEGIC THEMES</span>
              <span className="text-right">ACTIONS</span>
            </div>
            
            <div className="flex-1 divide-y divide-gray-50">
              {loading && !isPolling ? (
                <div className="h-full flex items-center justify-center py-40">
                  <div className="w-10 h-10 border-2 border-gray-100 border-t-[#0066CC] rounded-full animate-spin"></div>
                </div>
              ) : reports.length > 0 ? (
                reports.map((report) => (
                  <div key={report.id} className="grid grid-cols-4 px-10 py-8 items-center hover:bg-gray-50/30 transition-colors group">
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-slate-900 uppercase">
                        {new Date(report.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </span>
                      <span className="text-[10px] font-bold text-gray-400 uppercase mt-1">
                        {new Date(report.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </span>
                    </div>
                    <div>
                      <span className="bg-[#F4F9FF] text-[#0066CC] text-[11px] font-black px-3 py-1.5 rounded-lg border border-[#E1EEFF]">
                        {report.review_count} SIGNALS
                      </span>
                    </div>
                    <div className="flex flex-col space-y-3">
                      <div className="flex flex-wrap gap-2">
                        {(typeof report.themes === 'string' ? JSON.parse(report.themes) : report.themes).slice(0, 2).map((t, i) => (
                          <span key={i} className="text-[10px] font-bold text-slate-500 uppercase px-2 py-1 bg-gray-100 rounded border border-gray-200">
                            {typeof t === 'string' ? t : t.name}
                          </span>
                        ))}
                      </div>
                      {/* Email Field for Latest Report */}
                      {report.id === reports[0].id && (
                        <div className="flex items-center space-x-2">
                          <input 
                            type="email" 
                            className="text-[10px] bg-white border border-gray-200 rounded px-2 py-1 w-40 focus:border-blue-300 outline-none"
                            placeholder="recipient@indmoney.com"
                            onClick={(e) => e.stopPropagation()}
                            value={recipientEmail}
                            onChange={(e) => setRecipientEmail(e.target.value)}
                          />
                          <button 
                            onClick={(e) => { e.stopPropagation(); handleApprove(report.id, 'email'); }}
                            className="bg-emerald-500 text-white text-[9px] font-black px-2 py-1 rounded hover:bg-emerald-600 transition-colors"
                          >
                            SEND
                          </button>
                        </div>
                      )}
                    </div>
                    <div className="text-right">
                      <Link href={`/report/${report.id}`} className="text-[10px] font-black text-[#0066CC] uppercase tracking-widest hover:underline flex items-center justify-end space-x-1">
                        <span>VIEW INSIGHTS</span>
                        <span className="text-sm">→</span>
                      </Link>
                    </div>
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center py-32 text-gray-300">
                  <p className="text-sm font-medium italic">No reports in the intelligence archive.</p>
                </div>
              )}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
