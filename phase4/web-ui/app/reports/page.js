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
  const [runId, setRunId] = useState(null)
  const [runStatus, setRunStatus] = useState('queued')

  useEffect(() => {
    fetchArchive()
  }, [])

  useEffect(() => {
    let interval;
    if (isPolling) {
      interval = setInterval(() => {
        setPollCount(prev => prev + 1)
        if (runId) {
          checkActionStatus()
        } else {
          checkLatestReport()
        }
      }, 3000)
    }
    return () => clearInterval(interval)
  }, [isPolling, runId])

  const fetchArchive = async () => {
    setLoading(true)
    try {
      const res = await fetch('/api/fetch-archive')
      const data = await res.json()
      if (Array.isArray(data)) setReports(data)
    } catch (err) { console.error(err) }
    setLoading(false)
  }

  const checkActionStatus = async () => {
    try {
      const res = await fetch(`/api/check-run?run_id=${runId}`)
      const data = await res.json()
      setRunStatus(data.status)
      if (data.status === 'completed') {
        // ACTION COMPLETED -> Wait 2 seconds for GitHub Sync and then hard redirect
        setTimeout(checkLatestReport, 2000)
      }
    } catch (e) { checkLatestReport() }
  }

  const checkLatestReport = async () => {
    try {
      const res = await fetch('/api/latest-report')
      const data = await res.json()
      if (data.id) {
        // CODE LEVEL FIX: If the Action is done, just GO to the latest report. 
        // No more timestamp math.
        window.location.href = `/report/${data.id}`
      }
    } catch (e) {}
  }

  const handleGenerate = async () => {
    setGenerating(true)
    // 5-SECOND EXPERIENCE: If we have an existing report, show it immediately
    if (reports.length > 0) {
      router.push(`/report/${reports[0].id}?status=updating`)
    }

    try {
      const days = selectedMonths * 30
      const res = await fetch(`/api/generate-report?days=${days}`, { method: 'POST' })
      const data = await res.json()
      
      if (data.report_id) {
        window.location.href = `/report/${data.report_id}`
      } else if (data.status === "started") {
        setRunId(data.run_id)
        setIsPolling(true)
        setPollCount(0)
      }
    } catch (err) { console.error(err) }
    setGenerating(false)
  }

  return (
    <div className="min-h-screen bg-white text-slate-900 font-sans">
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
                <div className="flex flex-col text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                  <span className="mb-1">TIME WINDOW</span>
                  <span className="text-[#0066CC]">LAST {selectedMonths} MONTHS ANALYSIS</span>
                </div>
                <div className="text-3xl font-bold text-[#0066CC]">{selectedMonths} Months</div>
              </div>
              <input 
                type="range" min="1" max="12" value={selectedMonths}
                onChange={(e) => setSelectedMonths(parseInt(e.target.value))}
                className="w-full h-1 bg-gray-100 rounded-lg appearance-none cursor-pointer accent-[#0066CC]"
              />
            </div>
            <button 
              onClick={handleGenerate}
              disabled={generating || isPolling}
              className={`w-full py-5 rounded-xl font-bold text-lg flex items-center justify-center space-x-3 transition-all ${
                generating || isPolling ? 'bg-gray-100 text-gray-400 cursor-not-allowed' : 'bg-[#0066CC] hover:bg-[#0052A3] text-white shadow-xl shadow-blue-200'
              }`}
            >
              <span>{generating || isPolling ? 'Processing...' : '✨ Generate INDPlus Note'}</span>
            </button>
          </div>
        </div>

        {isPolling && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-white/90 backdrop-blur-sm">
            <div className="max-w-md w-full text-center">
              <div className="mb-10 inline-block relative animate-bounce">
                <div className="w-24 h-24 border-4 border-gray-50 border-t-[#0066CC] rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-[#0066CC] font-bold text-xl">MCP</span>
                </div>
              </div>
              <h2 className="text-3xl font-bold text-slate-900 mb-3">Synthesizing Strategic Pulse</h2>
              <div className="space-y-5 text-left max-w-xs mx-auto mt-12">
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold uppercase tracking-widest text-slate-800">Cloud Environment</span>
                  <span className="text-[10px] font-black text-[#0066CC] uppercase">{runStatus === 'queued' ? 'QUEUING' : 'READY'}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold uppercase tracking-widest text-slate-800">AI Synthesis</span>
                  <span className="text-[10px] font-black text-[#0066CC] uppercase">{runStatus === 'in_progress' ? 'PROCESSING' : (runStatus === 'completed' ? 'DONE' : 'PENDING')}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-sm font-bold uppercase tracking-widest text-slate-800">Finalizing Report</span>
                  <span className="text-[10px] font-black text-[#0066CC] uppercase">{runStatus === 'completed' ? 'REDIRECTING...' : 'PENDING'}</span>
                </div>
              </div>
              <div className="mt-16 text-gray-300 text-[10px] font-bold uppercase tracking-widest">
                ELAPSED TIME: {pollCount * 3} SECONDS
              </div>
            </div>
          </div>
        )}

        <div>
          <div className="flex items-center justify-between mb-8 border-b border-gray-100 pb-6">
            <div>
              <h2 className="text-2xl font-bold text-slate-900 mb-1">INDPlus Archive</h2>
              <p className="text-[10px] font-bold text-gray-400 uppercase tracking-widest">HISTORICAL DECISIONS & SIGNAL RECORDS</p>
            </div>
          </div>
          <div className="bg-white rounded-2xl border border-gray-100 shadow-sm overflow-hidden min-h-[400px]">
            <div className="grid grid-cols-4 px-10 py-5 bg-gray-50/50 border-b border-gray-100 text-[10px] font-bold text-gray-400 uppercase tracking-widest">
              <span>GENERATION DATE</span>
              <span>SIGNALS</span>
              <span>STRATEGIC THEMES</span>
              <span className="text-right">ACTIONS</span>
            </div>
            <div className="divide-y divide-gray-50">
              {loading ? (
                <div className="py-40 flex items-center justify-center"><div className="w-10 h-10 border-2 border-t-[#0066CC] rounded-full animate-spin"></div></div>
              ) : reports.map((report) => (
                <div key={report.id} className="grid grid-cols-4 px-10 py-8 items-center hover:bg-gray-50/30">
                  <div className="text-sm font-bold text-slate-900 uppercase">{new Date(report.created_at).toLocaleDateString()}</div>
                  <div><span className="bg-[#F4F9FF] text-[#0066CC] text-[11px] font-black px-3 py-1.5 rounded-lg">{report.review_count} SIGNALS</span></div>
                  <div className="flex gap-2">
                    {(typeof report.themes === 'string' ? JSON.parse(report.themes) : report.themes).slice(0, 2).map((t, i) => (
                      <span key={i} className="text-[10px] font-bold text-slate-500 uppercase px-2 py-1 bg-gray-100 rounded">{typeof t === 'string' ? t : t.name}</span>
                    ))}
                  </div>
                  <div className="text-right">
                    <Link href={`/report/${report.id}`} className="text-[10px] font-black text-[#0066CC] uppercase tracking-widest hover:underline">VIEW INSIGHTS →</Link>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}
