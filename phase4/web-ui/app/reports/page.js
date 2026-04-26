'use client'
import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'

export default function ReportsAndAutomation() {
  const router = useRouter()
  const [reports, setReports] = useState([])
  const [loading, setLoading] = useState(true)
  const [generating, setGenerating] = useState(false)
  const [selectedMonths, setSelectedMonths] = useState(3)
  const [isPolling, setIsPolling] = useState(false)
  const [pollCount, setPollCount] = useState(0)

  useEffect(() => {
    fetchReports()
  }, [])

  useEffect(() => {
    let interval;
    if (isPolling) {
      interval = setInterval(() => {
        setPollCount(prev => prev + 1)
        fetchReports()
      }, 5000)
    }
    return () => clearInterval(interval)
  }, [isPolling])

  useEffect(() => {
    // If we were polling and a new report appeared, stop polling
    if (isPolling && reports.length > 0) {
      // Check if the latest report is new (less than 3 mins old)
      const latest = reports[0]
      const createdAt = new Date(latest.created_at)
      if ((new Date() - createdAt) < 180000) {
        setIsPolling(false)
        router.push(`/report/${latest.id}`)
      }
    }
  }, [reports])

  const fetchReports = async () => {
    // Keep loading state only for initial fetch
    if (!isPolling) setLoading(true)
    try {
      const ARCHIVE_URL = "https://raw.githubusercontent.com/saikichnit/INDMoney_Reviews_Weekly_Pulse-/main/data/reports_archive.json";
      const res = await fetch(ARCHIVE_URL, { cache: 'no-store' });
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
    setGenerating(true)
    const days = selectedMonths * 30
    try {
      const res = await fetch(`/api/generate-report?days=${days}`, { method: 'POST' })
      const data = await res.json()
      
      if (data.report_id) {
        router.push(`/report/${data.report_id}`)
      } else if (data.status === "started") {
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
    if (m === 1) return 'Monthly Pulse'
    if (m === 3) return 'Quarterly Strategy'
    if (m === 6) return 'Semi-Annual Outlook'
    if (m === 12) return 'Annual Executive Review'
    return `${m}-Month Deep Dive`
  }

  return (
    <div className="min-h-screen bg-[#0F1115] text-white font-sans p-8">
      {/* Premium Progress Overlay */}
      {isPolling && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md">
          <div className="bg-[#1A1D23] border border-white/10 p-8 rounded-2xl max-w-md w-full shadow-2xl">
            <div className="flex flex-col items-center text-center">
              <div className="relative mb-6">
                <div className="w-20 h-20 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin"></div>
                <div className="absolute inset-0 flex items-center justify-center">
                  <span className="text-emerald-500 font-bold">LLM</span>
                </div>
              </div>
              <h2 className="text-2xl font-bold mb-2">Synthesizing Strategic Pulse</h2>
              <p className="text-gray-400 mb-8">Analysis running in secure cloud container...</p>
              
              <div className="w-full space-y-4">
                {[
                  { label: "📡 Signal Ingestion", active: pollCount >= 0 },
                  { label: "🧠 Deep Theme Extraction", active: pollCount >= 2 },
                  { label: "🎓 Strategic Synthesis", active: pollCount >= 5 },
                  { label: "📄 Finalizing Report", active: pollCount >= 8 }
                ].map((step, i) => (
                  <div key={i} className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${step.active ? 'bg-emerald-500 shadow-[0_0_8px_rgba(16,185,129,0.6)]' : 'bg-gray-700'}`}></div>
                    <span className={step.active ? 'text-white' : 'text-gray-600'}>{step.label}</span>
                    {step.active && pollCount >= i*3 && pollCount < (i+1)*3 && (
                      <span className="text-[10px] text-emerald-500 animate-pulse ml-auto">PROCESSING...</span>
                    )}
                    {step.active && pollCount >= (i+1)*3 && (
                      <span className="text-[10px] text-emerald-500 ml-auto">DONE</span>
                    )}
                  </div>
                ))}
              </div>
              
              <div className="mt-8 text-xs text-gray-500">
                Polling Cloud Status: {pollCount * 5}s elapsed
              </div>
            </div>
          </div>
        </div>
      )}

      <div className="max-w-6xl mx-auto">
        <header className="mb-12 flex justify-between items-end">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight mb-2 bg-gradient-to-r from-white to-gray-500 bg-clip-text text-transparent">
              INDPlus Archive
            </h1>
            <p className="text-gray-400 text-lg">Historical Decisions & Signal Records</p>
          </div>
          
          <div className="bg-[#1A1D23] p-4 rounded-xl border border-white/10 flex items-center space-x-6">
            <div className="flex flex-col">
              <span className="text-[10px] text-gray-500 uppercase font-bold tracking-widest mb-1">Rolling Window</span>
              <select 
                value={selectedMonths} 
                onChange={(e) => setSelectedMonths(parseInt(e.target.value))}
                className="bg-transparent border-none text-white focus:ring-0 cursor-pointer font-medium"
              >
                <option value={1}>Last 30 Days</option>
                <option value={3}>Last 90 Days</option>
                <option value={6}>Last 6 Months</option>
                <option value={12}>Last 1 Year</option>
              </select>
            </div>
            <button 
              onClick={handleGenerate}
              disabled={generating || isPolling}
              className={`px-6 py-3 rounded-lg font-bold transition-all flex items-center space-x-2 ${
                generating || isPolling
                ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
                : 'bg-emerald-600 hover:bg-emerald-500 text-white shadow-lg shadow-emerald-900/20 active:scale-95'
              }`}
            >
              <span>✨ {generating ? 'Initializing...' : 'Generate INDPlus Note'}</span>
            </button>
          </div>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="md:col-span-2 space-y-4">
            {loading && !isPolling ? (
              <div className="py-20 flex flex-col items-center justify-center border border-white/5 rounded-2xl bg-white/[0.02]">
                <div className="w-12 h-12 border-4 border-emerald-500/20 border-t-emerald-500 rounded-full animate-spin mb-4"></div>
                <p className="text-gray-500">Syncing Intelligence Vault...</p>
              </div>
            ) : reports.length > 0 ? (
              reports.map((report) => (
                <div key={report.id} className="group bg-[#1A1D23] border border-white/5 p-6 rounded-2xl hover:border-white/20 transition-all cursor-pointer relative overflow-hidden" onClick={() => router.push(`/report/${report.id}`)}>
                  <div className="absolute top-0 right-0 p-4 opacity-0 group-hover:opacity-100 transition-opacity">
                    <span className="text-[10px] bg-emerald-500/10 text-emerald-500 px-2 py-1 rounded-full border border-emerald-500/20">VIEW INSIGHTS</span>
                  </div>
                  <div className="flex justify-between items-start mb-4">
                    <div>
                      <h3 className="text-xl font-bold mb-1">Weekly Pulse #{report.id}</h3>
                      <p className="text-gray-500 text-sm">
                        Generated {new Date(report.created_at).toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </p>
                    </div>
                    <div className="text-right">
                      <div className="text-2xl font-black text-white">{report.review_count}</div>
                      <div className="text-[10px] text-gray-500 uppercase tracking-widest">Signals</div>
                    </div>
                  </div>
                  <div className="text-gray-400 text-sm line-clamp-2 italic border-l-2 border-emerald-500/30 pl-4 py-1">
                    "{report.summary || 'No summary available for this report.'}"
                  </div>
                </div>
              ))
            ) : (
              <div className="py-20 flex flex-col items-center justify-center border border-dashed border-white/10 rounded-2xl">
                <p className="text-gray-500">No reports in the intelligence archive.</p>
                <button onClick={handleGenerate} className="mt-4 text-emerald-500 hover:underline">Trigger first report</button>
              </div>
            )}
          </div>

          <div className="space-y-6">
            <div className="bg-[#1A1D23] border border-white/5 p-8 rounded-2xl">
              <h2 className="text-xl font-bold mb-4 flex items-center">
                <span className="w-8 h-8 bg-emerald-500/10 text-emerald-500 rounded-lg flex items-center justify-center mr-3 text-sm">🎓</span>
                Proactive Intelligence
              </h2>
              <p className="text-gray-400 text-sm leading-relaxed mb-6">
                Our AI actively monitors App Store & Play Store signals to proactively detect fee-related friction before it impacts NPS.
              </p>
              <div className="space-y-4">
                <div className="p-4 bg-white/[0.02] rounded-xl border border-white/5">
                  <div className="text-xs text-gray-500 uppercase mb-1">Status</div>
                  <div className="flex items-center text-emerald-500 font-bold">
                    <div className="w-2 h-2 bg-emerald-500 rounded-full animate-pulse mr-2"></div>
                    Synced to GitHub
                  </div>
                </div>
                <div className="p-4 bg-white/[0.02] rounded-xl border border-white/5">
                  <div className="text-xs text-gray-500 uppercase mb-1">Last Sync</div>
                  <div className="text-white font-medium">{reports.length > 0 ? new Date(reports[0].created_at).toLocaleTimeString() : 'N/A'}</div>
                </div>
              </div>
            </div>
            
            <div className="bg-gradient-to-br from-emerald-600 to-emerald-900 p-8 rounded-2xl shadow-xl shadow-emerald-900/20">
              <h3 className="text-xl font-bold mb-2">Live Support</h3>
              <p className="text-white/80 text-sm mb-6">Need a custom deep-dive report for the board? Trigger a 12-month pulse.</p>
              <button 
                onClick={() => { setSelectedMonths(12); handleGenerate(); }}
                className="w-full py-3 bg-white text-emerald-900 rounded-xl font-bold hover:bg-gray-100 transition-colors"
              >
                Board Synthesis (1Y)
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
