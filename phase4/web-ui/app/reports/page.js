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

  useEffect(() => {
    fetchReports()
  }, [])

  const fetchReports = async () => {
    setLoading(true)
    try {
      // Primary: Use Raw GitHub URL for high reliability on Vercel
      const ARCHIVE_URL = "https://raw.githubusercontent.com/saikichnit/INDMoney_Reviews_Weekly_Pulse-/main/data/reports_archive.json";
      const res = await fetch(ARCHIVE_URL, { cache: 'no-store' });
      const data = await res.json();
      if (Array.isArray(data)) {
        setReports(data);
      } else {
        throw new Error("Invalid archive data");
      }
    } catch (err) {
      console.error("GitHub Archive failed, trying local fallback", err)
      try {
        const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/reports`)
        const data = await res.json()
        setReports(data)
      } catch (e) {}
    } finally {
      setLoading(false)
    }
  }

  const handleGenerate = async () => {
    setGenerating(true)
    const days = selectedMonths * 30
    try {
      // Use the internal Next.js API bridge instead of the separate 8001 server
      const res = await fetch(`/api/generate-report?days=${days}`, { method: 'POST' })
      const data = await res.json()
      
      if (data.report_id) {
        router.push(`/report/${data.report_id}`)
      } else if (data.status === "started") {
        alert(data.message || "Generation started in the cloud. Please refresh in 2 minutes.")
      } else {
        alert("Generation failed: " + (data.error || "Unknown error"))
      }
    } catch (err) {
      console.error(err)
      alert("Network error occurred during generation")
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

  const getAnalysisWindow = () => {
    const now = new Date()
    const start = new Date()
    start.setMonth(now.getMonth() - selectedMonths)
    return `${start.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })} – ${now.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}`
  }

  return (
    <div className="max-w-7xl mx-auto py-12 space-y-12 animate-in fade-in duration-700">
      
      {/* 1. Pulse Generation Console */}
      <div className="card-premium p-10 bg-slate-50/50 border-blue-100">
        <div className="flex flex-col md:flex-row justify-between items-center gap-12">
          <div className="max-w-xl">
             <div className="flex items-center gap-2 mb-3">
                <span className="text-[10px] font-bold text-[#0066CC] uppercase tracking-widest bg-blue-50 px-2 py-1 rounded">INDPlus Intelligence</span>
                <span className="text-[10px] font-bold text-slate-300 uppercase tracking-widest">Model Context Protocol</span>
             </div>
             <h2 className="text-2xl font-bold text-slate-900 mb-2">Strategic Intelligence Console</h2>
             <p className="text-sm text-slate-500 leading-relaxed">
               Select your strategic window from 1 to 12 months. The AI will synthesize thousands of signals into a one-page executive note, automatically syncing to Google Workspace and drafting leadership reports.
             </p>
          </div>
          
          <div className="w-full md:w-80 flex flex-col gap-8">
             <div className="space-y-4">
                <div className="flex justify-between items-end mb-2">
                   <div className="flex flex-col">
                      <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Time Window</span>
                      <span className="text-[9px] font-bold text-[#0066CC] uppercase tracking-widest mt-1">
                        {getAnalysisWindow()}
                      </span>
                   </div>
                   <span className="text-xl font-bold text-[#0066CC]">{selectedMonths} Months</span>
                </div>
                <input 
                  type="range" 
                  min="1" 
                  max="12" 
                  value={selectedMonths}
                  onChange={(e) => setSelectedMonths(parseInt(e.target.value))}
                  className="w-full h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-[#0066CC]"
                />
                <div className="flex justify-between text-[8px] font-bold text-slate-300 uppercase tracking-widest">
                   <span>1 Month</span>
                   <span>6 Months</span>
                   <span>12 Months</span>
                </div>
             </div>

             <div className="space-y-3">
               <div className="text-center">
                  <p className="text-[10px] font-bold text-[#0066CC] uppercase tracking-widest bg-blue-50/50 py-1 rounded border border-blue-100/50">
                    Target: {getRangeLabel(selectedMonths)}
                  </p>
               </div>
               <button 
                 onClick={handleGenerate}
                 disabled={generating}
                 className={`btn-primary w-full py-4 flex items-center justify-center gap-2 shadow-lg shadow-blue-100 ${generating ? 'opacity-70 cursor-not-allowed' : ''}`}
               >
                 {generating ? (
                   <>
                     <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                     Analyzing {selectedMonths * 30} Days...
                   </>
                 ) : (
                   '✨ Generate INDPlus Note'
                 )}
               </button>
             </div>
          </div>
        </div>
      </div>

      {/* 2. Intelligence Archive */}
      <div>
        <div className="flex items-center justify-between mb-8 px-1">
          <div>
            <h2 className="text-xl font-bold text-slate-900">INDPlus Archive</h2>
            <p className="text-xs text-slate-400 mt-1 uppercase tracking-widest font-bold">Historical Decisions & Signal Records</p>
          </div>
          <div className="flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest">
             <div className="w-2 h-2 rounded-full bg-emerald-500" />
             Synced to MCP
          </div>
        </div>

        <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50/50 border-b border-slate-100">
                <th className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Generation Date</th>
                <th className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Signals</th>
                <th className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-widest">Strategic Themes</th>
                <th className="px-8 py-5 text-[10px] font-bold text-slate-400 uppercase tracking-widest text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {loading ? (
                [1,2,3].map(i => (
                  <tr key={i} className="animate-pulse">
                    <td colSpan="4" className="px-8 py-6 h-20 bg-slate-50/20" />
                  </tr>
                ))
              ) : reports.length > 0 ? reports.map((report) => (
                <tr key={report.id} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-8 py-6">
                    <div className="flex flex-col">
                      <span className="text-sm font-bold text-slate-900">
                        {new Date(report.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                      </span>
                      <span className="text-[10px] text-slate-400 uppercase font-bold">{new Date(report.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
                    </div>
                  </td>
                  <td className="px-8 py-6">
                    <span className="px-3 py-1 bg-blue-50 text-[#0066CC] text-[10px] font-bold rounded-lg border border-blue-100/50">
                      {report.review_count} Analyzed
                    </span>
                  </td>
                  <td className="px-8 py-6">
                    <div className="flex flex-wrap gap-2 max-w-md">
                      {JSON.parse(report.themes).slice(0, 3).map((theme, i) => (
                        <span key={i} className="px-2.5 py-1 bg-white text-slate-600 text-[10px] font-bold rounded border border-slate-200 shadow-sm">
                          {theme.name || theme}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td className="px-8 py-6 text-right">
                    <Link href={`/report/${report.id}`} className="inline-flex items-center gap-2 text-[10px] font-bold text-[#0066CC] uppercase tracking-widest hover:underline">
                      View Insights
                      <span>→</span>
                    </Link>
                  </td>
                </tr>
              )) : (
                <tr>
                  <td colSpan="4" className="py-20 text-center italic text-slate-400 text-sm">No reports in the intelligence archive.</td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

function StatItem({ label, count, color, total }) {
  const percent = total > 0 ? Math.round((count / total) * 100) : 0
  return (
    <div className="flex justify-between items-center">
      <div>
        <p className="text-[9px] font-bold text-slate-400 uppercase tracking-wider">{label}</p>
        <p className={`text-sm font-bold ${color}`}>{count}</p>
      </div>
      <p className="text-[10px] font-bold text-slate-300">{percent}%</p>
    </div>
  )
}
