'use client'
import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'
import Link from 'next/link'

export default function ReportPreview() {
  const { id } = useParams()
  const router = useRouter()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [approving, setApproving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [recipientEmail, setRecipientEmail] = useState('stakeholders@indmoney.com')
  const [editedSummary, setEditedSummary] = useState('')

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/reports/${id}`)
      .then(res => res.json())
      .then(data => {
        if (data && !data.error) {
          setReport(data)
          setEditedSummary(data.summary || '')
        }
        setLoading(false)
      })
      .catch(err => {
        console.error("Fetch report failed", err)
        setLoading(false)
      })
  }, [id])

  const handleApprove = async (mode = 'both') => {
    setApproving(true)
    try {
      const res = await fetch(`/api/reports/${id}/approve`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text: editedSummary,
          email: recipientEmail,
          mode
        })
      })
      
      const result = await res.json()
      if (res.ok) {
        setSuccess(true)
        setTimeout(() => setSuccess(false), 5000)
      } else {
        alert("Action failed: " + (result.error || "Unknown error"))
      }
    } catch (err) {
      console.error(err)
      alert("Network error occurred")
    } finally {
      setApproving(false)
    }
  }

  if (loading) return (
    <div className="flex flex-col gap-8 max-w-7xl mx-auto py-8">
      <div className="h-12 w-1/3 animate-pulse bg-slate-100 rounded-lg" />
      <div className="flex flex-col lg:flex-row gap-8">
        <div className="lg:w-2/3 h-[600px] animate-pulse bg-slate-100 rounded-2xl" />
        <div className="lg:w-1/3 h-[400px] animate-pulse bg-slate-100 rounded-2xl" />
      </div>
    </div>
  )

  if (!report) return (
    <div className="max-w-7xl mx-auto py-20 text-center space-y-4">
      <h2 className="text-2xl font-bold text-slate-800">Intelligence Report Not Found</h2>
      <p className="text-slate-500">The requested report (ID: {id}) could not be retrieved from the intelligence archive.</p>
      <button onClick={() => router.push('/reports')} className="btn-primary">Back to Reports</button>
    </div>
  )

  return (
    <div className="max-w-7xl mx-auto py-8 space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-700">
      
      {/* 1. Header with Breadcrumbs */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <div className="w-10 h-10 bg-blue-50 text-[#0066CC] rounded-xl flex items-center justify-center shadow-sm">
             <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
             </svg>
          </div>
          <div>
            <h1 className="text-xl font-bold text-slate-900 flex items-center gap-3">
              Weekly Pulse Note Preview
              <span className="text-[10px] font-bold px-2 py-0.5 bg-blue-100 text-[#0066CC] rounded-full uppercase tracking-widest">
                {report.review_count} Reviews Analyzed
              </span>
            </h1>
            <p className="text-[10px] font-bold text-slate-400 uppercase tracking-[0.1em] mt-0.5">Verified Analysis Summary (Editable)</p>
          </div>
        </div>
        <Link href="/reports" className="text-[10px] font-bold text-slate-400 hover:text-slate-900 uppercase tracking-widest transition-colors flex items-center gap-2">
           ✕ Close Preview
        </Link>
      </div>

      <div className="flex flex-col lg:flex-row gap-8">
        
        {/* LEFT CONTENT: THE REPORT */}
        <div className="lg:w-2/3 space-y-8">
          
          {/* Main Editable Card */}
          <div className="card-premium p-1 bg-yellow-50/30 border-yellow-100 overflow-hidden shadow-xl shadow-yellow-900/5">
             <div className="p-8 space-y-6">
                <textarea 
                  className="w-full min-h-[400px] bg-transparent text-slate-700 font-mono text-sm leading-relaxed focus:outline-none resize-none"
                  value={editedSummary}
                  onChange={(e) => setEditedSummary(e.target.value)}
                  placeholder="Drafting executive summary..."
                />
                <div className="pt-4 border-t border-yellow-100 flex items-center gap-2 text-[10px] font-bold text-slate-400 uppercase tracking-widest italic">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  This note will be used for both Google Docs and the Email Draft.
                </div>
             </div>
          </div>

          {/* Categorized Themes & Sections */}
          <div className="space-y-6">
             <div className="flex items-center gap-3 px-1">
                <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0066CC] flex items-center justify-center shadow-sm">
                   <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 7h.01M7 11h.01M7 15h.01M13 7h.01M13 11h.01M13 15h.01M17 7h.01M17 11h.01M17 15h.01" />
                   </svg>
                </div>
                <h3 className="text-lg font-bold text-slate-900">Categorized Themes</h3>
             </div>

             <div className="grid grid-cols-1 gap-4">
                {report.themes?.map((theme, i) => (
                  <div key={i} className="card-premium p-6 hover:translate-x-1 transition-transform cursor-default">
                    <div className="flex items-center justify-between mb-2">
                       <div className="flex items-center gap-3">
                          <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center font-bold text-xs shadow-sm">
                             {theme.name?.[0] || 'T'}
                          </div>
                          <span className="font-bold text-slate-900">{theme.name || theme}</span>
                       </div>
                       <span className="text-xs font-bold text-[#0066CC] bg-blue-50 px-2 py-0.5 rounded-md">{theme.percentage || 0}% Impact</span>
                    </div>
                    <p className="text-xs text-slate-500 leading-relaxed pl-11">
                       High frequency signal detected across multiple platforms. Critical theme for strategic roadmap.
                    </p>
                  </div>
                ))}
             </div>
          </div>

          {/* 🎓 Proactive Financial Education */}
          {report.fee_scenarios?.length > 0 && (
            <div className="space-y-6">
               <div className="flex items-center gap-3 px-1">
                  <div className="w-8 h-8 rounded-lg bg-blue-50 text-[#0066CC] flex items-center justify-center shadow-sm">
                     <span className="text-sm">🎓</span>
                  </div>
                  <h3 className="text-lg font-bold text-slate-900">Proactive Financial Education</h3>
               </div>

               <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.fee_scenarios.map((fee, i) => (
                    <div key={i} className="p-6 bg-blue-50/30 border border-blue-100 rounded-2xl space-y-3">
                       <h4 className="font-bold text-slate-900 text-sm">{fee.scenario_name}</h4>
                       <ul className="space-y-2">
                          {fee.explanation_bullets?.slice(0, 2).map((bullet, j) => (
                            <li key={j} className="text-xs text-slate-600 flex gap-2">
                               <span className="text-blue-400 mt-1">•</span>
                               {bullet}
                            </li>
                          ))}
                       </ul>
                       {fee.source_links?.[0] && (
                         <a href={fee.source_links[0]} target="_blank" className="text-[10px] font-bold text-[#0066CC] uppercase tracking-widest hover:underline block pt-2">
                            Read Official Source
                         </a>
                       )}
                    </div>
                  ))}
               </div>
            </div>
          )}

          {/* Golden User Quotes */}
          <div className="space-y-6">
             <div className="flex items-center gap-3 px-1">
                <div className="w-8 h-8 rounded-lg bg-slate-50 text-slate-600 flex items-center justify-center shadow-sm">
                   <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
                   </svg>
                </div>
                <h3 className="text-lg font-bold text-slate-900">Golden User Quotes</h3>
             </div>

             <div className="space-y-4">
                {report.quotes?.map((quote, i) => (
                  <div key={i} className="p-6 bg-white border border-slate-100 rounded-2xl shadow-sm border-l-4 border-l-[#0066CC]">
                    <p className="text-sm italic text-slate-600 leading-relaxed">"{quote}"</p>
                  </div>
                ))}
             </div>
          </div>

          {/* Action Ideas */}
          <div className="space-y-6">
             <div className="flex items-center gap-3 px-1">
                <div className="w-8 h-8 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center shadow-sm">
                   <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                     <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                   </svg>
                </div>
                <h3 className="text-lg font-bold text-slate-900">Action Ideas</h3>
             </div>

             <div className="space-y-3">
                {report.action_items?.map((item, i) => (
                  <div key={i} className="flex items-center gap-4 p-5 bg-white border border-slate-100 rounded-2xl shadow-sm hover:shadow-md transition-shadow group">
                    <div className="w-8 h-8 rounded-full bg-slate-50 text-slate-400 font-bold text-[10px] flex items-center justify-center border border-slate-100 group-hover:bg-blue-50 group-hover:text-[#0066CC] transition-colors">
                      {i + 1}
                    </div>
                    <p className="text-sm font-medium text-slate-700 leading-relaxed flex-1">{item}</p>
                  </div>
                ))}
             </div>
          </div>

          <div className="flex justify-between items-center text-[10px] font-bold text-slate-300 uppercase tracking-widest pt-8 border-t border-slate-100">
             <span>Generated {new Date(report.created_at).toLocaleString()}</span>
             <div className="flex items-center gap-2">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
                No PII included
             </div>
          </div>
        </div>

        {/* RIGHT SIDEBAR: APPROVAL PANEL */}
        <div className="lg:w-1/3">
           <div className="sticky top-12 space-y-6">
              
              <div className="card-premium p-8 border-slate-200/60 bg-white shadow-2xl shadow-slate-200/50">
                 <div className="flex items-center gap-3 mb-8">
                    <div className="w-10 h-10 bg-emerald-50 text-emerald-600 rounded-xl flex items-center justify-center shadow-sm">
                       <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                         <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                       </svg>
                    </div>
                    <div>
                       <h3 className="font-bold text-lg text-slate-900">Approve & Deliver</h3>
                       <p className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Stakeholder Distribution</p>
                    </div>
                 </div>

                 <div className="space-y-4 mb-8">
                    {/* Action 1: Google Docs */}
                    <button 
                      onClick={() => handleApprove('docs')}
                      disabled={approving}
                      className="w-full text-left p-5 rounded-2xl border border-slate-100 bg-white hover:border-blue-100 hover:bg-blue-50/30 transition-all group relative overflow-hidden"
                    >
                       <div className="flex items-center gap-4 relative z-10">
                          <div className="w-10 h-10 bg-blue-100/50 text-[#0066CC] rounded-xl flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                             <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                             </svg>
                          </div>
                          <div className="flex-1">
                             <p className="text-sm font-bold text-slate-800">Send to Notes</p>
                             <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-1">Push to internal documentation</p>
                          </div>
                          <svg className="w-4 h-4 text-slate-300 group-hover:text-[#0066CC] transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                             <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                          </svg>
                       </div>
                    </button>

                    {/* Action 2: Email */}
                    <div className="w-full text-left p-5 rounded-2xl border border-slate-100 bg-white hover:border-blue-100 hover:bg-blue-50/30 transition-all group">
                       <div className="flex items-center gap-4 mb-4">
                          <div className="w-10 h-10 bg-indigo-100/50 text-indigo-600 rounded-xl flex items-center justify-center shadow-sm group-hover:scale-110 transition-transform">
                             <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                             </svg>
                          </div>
                          <div className="flex-1">
                             <p className="text-sm font-bold text-slate-800">Create Email Draft</p>
                             <p className="text-[9px] font-bold text-slate-400 uppercase tracking-widest mt-1">Format for stakeholder inbox</p>
                          </div>
                          <button 
                            onClick={() => handleApprove('email')}
                            disabled={approving}
                            className="w-4 h-4 text-slate-300 group-hover:text-indigo-600 transition-colors"
                          >
                             <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M9 5l7 7-7 7" />
                             </svg>
                          </button>
                       </div>
                       <input 
                         type="email" 
                         className="w-full bg-slate-50 border border-slate-100 rounded-xl py-2 px-3 text-[10px] font-bold text-slate-600 focus:outline-none focus:border-indigo-200 transition-all"
                         value={recipientEmail}
                         onChange={(e) => setRecipientEmail(e.target.value)}
                         placeholder="recipient@indmoney.com"
                       />
                    </div>
                 </div>

                 <div className="space-y-4">
                    <div className="relative">
                       <div className="absolute inset-0 flex items-center">
                          <div className="w-full border-t border-slate-100"></div>
                       </div>
                       <div className="relative flex justify-center text-[8px] font-bold uppercase tracking-widest text-slate-300">
                          <span className="bg-white px-2">Or Complete</span>
                       </div>
                    </div>

                    <button 
                      onClick={() => handleApprove('both')}
                      disabled={approving}
                      className={`w-full py-5 bg-emerald-500 hover:bg-emerald-600 text-white rounded-2xl font-bold flex items-center justify-center gap-3 shadow-lg shadow-emerald-100 transition-all ${approving ? 'opacity-70 scale-95' : 'hover:scale-[1.02] active:scale-95'}`}
                    >
                       {approving ? (
                         <>
                            <span className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                            Processing...
                         </>
                       ) : (
                         <>
                            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                               <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                            </svg>
                            Do Both & Finish
                         </>
                       )}
                    </button>
                 </div>

                 <div className="mt-8 p-4 bg-slate-50 rounded-2xl border border-slate-100 flex gap-3">
                    <svg className="w-4 h-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                       <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                    </svg>
                    <p className="text-[10px] font-medium text-slate-500 leading-relaxed">
                       Upon completion, the system will mark the weekly analysis as reviewed and freeze the data snapshot for this week.
                    </p>
                 </div>
              </div>

              {/* Success Badge */}
              {success && (
                <div className="p-4 bg-emerald-50 border border-emerald-100 rounded-2xl flex items-center gap-3 text-emerald-700 animate-in zoom-in duration-300">
                  <div className="w-6 h-6 rounded-full bg-emerald-100 flex items-center justify-center">
                    <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
                  </div>
                  <span className="text-[10px] font-bold uppercase tracking-widest">Pulse Delivered Successfully</span>
                </div>
              )}

           </div>
        </div>
      </div>
    </div>
  )
}
