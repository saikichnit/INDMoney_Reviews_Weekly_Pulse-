'use client'
import { useState, useEffect } from 'react'
import { useParams, useRouter } from 'next/navigation'

export default function ReportPreview() {
  const { id } = useParams()
  const router = useRouter()
  const [report, setReport] = useState(null)
  const [loading, setLoading] = useState(true)
  const [sending, setSending] = useState(false)
  const [success, setSuccess] = useState(false)
  const [recipientEmail, setRecipientEmail] = useState('')

  useEffect(() => {
    fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/reports/${id}`)
      .then(res => res.json())
      .then(data => {
        if (data && !data.error) {
          setReport(data)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error("Fetch report failed", err)
        setLoading(false)
      })
  }, [id])

  const handleDeliver = async () => {
    if (!recipientEmail) return alert("Please enter a recipient email")
    setSending(true)
    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/send-email/${id}?recipient_email=${encodeURIComponent(recipientEmail)}`, {
        method: 'POST'
      })
      if (res.ok) {
        setSuccess(true)
        setTimeout(() => setSuccess(false), 5000)
      }
    } catch (err) {
      console.error(err)
    } finally {
      setSending(false)
    }
  }

  if (loading) return (
    <div className="flex flex-col gap-8 max-w-7xl mx-auto py-8">
      <div className="h-12 w-1/3 animate-shimmer rounded-lg" />
      <div className="flex gap-8">
        <div className="w-2/3 h-[600px] animate-shimmer rounded-2xl" />
        <div className="w-1/3 h-[400px] animate-shimmer rounded-2xl" />
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
    <div className="max-w-7xl mx-auto py-8 animate-in fade-in duration-700">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <span className="text-sm font-bold text-[#0066CC] uppercase tracking-widest">Weekly Note</span>
            <span className="text-slate-200">/</span>
            <span className="text-sm text-slate-400">{new Date(report.created_at).toLocaleDateString()}</span>
          </div>
          <h1 className="text-3xl font-bold text-slate-900">Pulse Report Intelligence</h1>
        </div>
        <div className="flex items-center gap-3">
          <button onClick={() => router.push('/reports')} className="btn-secondary">
            Back to Archive
          </button>
        </div>
      </div>

      {success && (
        <div className="mb-6 p-4 bg-green-50 border border-green-100 rounded-xl flex items-center gap-3 text-green-700 animate-in zoom-in duration-300">
          <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20"><path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" /></svg>
          <span className="font-medium">Appended to Notes + Email Draft Sent Successfully</span>
        </div>
      )}

      <div className="flex flex-col lg:flex-row gap-8">
        {/* Left Panel - Insights */}
        <div className="lg:w-2/3 space-y-6">
          <div className="card-premium p-8">
            <div className="flex items-center justify-between mb-8 pb-4 border-b border-slate-50">
              <div className="flex items-center gap-6">
                <div>
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Reviews Analyzed</p>
                  <p className="font-bold text-slate-900">{report.review_count || 0}</p>
                </div>
                <div className="w-px h-8 bg-slate-100" />
                <div>
                  <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Source</p>
                  <p className="font-bold text-slate-900">iOS & Android</p>
                </div>
                <div className="w-px h-8 bg-slate-100" />
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-green-500" />
                  <span className="text-[10px] font-bold text-slate-400 uppercase">PII Stripped</span>
                </div>
              </div>
            </div>

            <article className="prose max-w-none">
              <section className="mb-10">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-lg bg-blue-50 text-[#0066CC] flex items-center justify-center text-sm">1</span>
                  Executive Summary
                </h3>
                <div className="p-4 bg-slate-50 rounded-xl border border-slate-100 text-slate-600 leading-relaxed italic">
                  {report.summary || "No summary available for this report."}
                </div>
              </section>

              <section className="mb-10">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-lg bg-blue-50 text-[#0066CC] flex items-center justify-center text-sm">2</span>
                  Top Themes Identified
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {report.themes?.map((theme, i) => (
                    <div key={i} className="p-4 bg-white border border-slate-100 rounded-xl shadow-sm">
                      <div className="flex justify-between items-center mb-2">
                        <span className="font-bold text-slate-900">{theme.name || theme}</span>
                        <span className="text-sm font-bold text-[#0066CC]">{theme.percentage || 0}%</span>
                      </div>
                      <div className="w-full bg-slate-50 h-1.5 rounded-full overflow-hidden">
                        <div className="bg-[#0066CC] h-full transition-all duration-1000" style={{ width: `${theme.percentage || 0}%` }} />
                      </div>
                    </div>
                  )) || <p className="text-slate-400 italic text-sm">No themes categorized.</p>}
                </div>
              </section>

              <section className="mb-10">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-lg bg-blue-50 text-[#0066CC] flex items-center justify-center text-sm">3</span>
                  Golden User Quotes
                </h3>
                <div className="space-y-4">
                  {report.quotes?.map((quote, i) => (
                    <div key={i} className="p-4 border-l-4 border-blue-100 bg-blue-50/20 rounded-r-xl">
                      <p className="text-slate-600 leading-relaxed italic">"{quote}"</p>
                    </div>
                  )) || <p className="text-slate-400 italic text-sm">No specific quotes highlighted.</p>}
                </div>
              </section>

              <section>
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span className="w-8 h-8 rounded-lg bg-blue-50 text-[#0066CC] flex items-center justify-center text-sm">4</span>
                  Actionable Recommendations
                </h3>
                <ul className="space-y-3">
                  {report.action_items?.map((item, i) => (
                    <li key={i} className="flex gap-3 text-slate-600">
                      <span className="text-green-500 mt-1">✓</span>
                      <span>{item}</span>
                    </li>
                  )) || <li className="text-slate-400 italic text-sm">No recommendations generated.</li>}
                </ul>
              </section>
            </article>
          </div>
        </div>

        {/* Right Panel - Actions */}
        <div className="lg:w-1/3">
          <div className="sticky top-24 space-y-6">
            <div className="card-premium p-6 border-blue-100 bg-blue-50/10">
              <h3 className="font-bold text-lg mb-2 text-slate-900">Approve & Deliver</h3>
              <p className="text-xs text-slate-500 mb-6">Distribute this pulse to the engineering and product channels.</p>
              
              <div className="space-y-4">
                <div>
                  <label className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1.5 block">Recipient Email</label>
                  <input 
                    type="email" 
                    value={recipientEmail}
                    onChange={(e) => setRecipientEmail(e.target.value)}
                    className="w-full bg-white border border-slate-200 rounded-lg py-2 px-3 text-xs font-bold text-slate-700 focus:outline-none focus:border-slate-400 transition-all shadow-sm"
                    placeholder="e.g. leadership@indmoney.com"
                  />
                </div>

                <button 
                  onClick={handleDeliver}
                  disabled={sending}
                  className="btn-primary w-full flex items-center justify-center gap-2 py-3"
                >
                  {sending ? 'Delivering...' : '✅ Send an email'}
                </button>
                <div className="flex gap-2">
                  <button className="btn-secondary flex-1 text-[10px]">Copy JSON</button>
                  <button className="btn-secondary flex-1 text-[10px]">Edit Note</button>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-slate-50">
                <h4 className="text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-3">Google Workspace Automation (MCP)</h4>
                <div className="flex flex-col gap-2">
                  <div className="flex items-center justify-between p-3 bg-white border border-slate-100 rounded-lg shadow-sm">
                    <div className="flex items-center gap-2">
                        <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
                        <span className="text-[10px] font-bold text-slate-600 uppercase">Synced to Google Docs</span>
                    </div>
                    <a 
                      href="https://docs.google.com/document/d/18CMQaITOJK02gX2BfQwL1Rkw4QWC6sJDMjim865-bOk" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-[9px] font-bold text-[#0066CC] hover:underline uppercase tracking-widest"
                    >
                      View on Google Docs
                    </a>
                  </div>
                  <button className="w-full py-2 bg-slate-50 border border-slate-100 rounded-lg text-[9px] font-bold text-slate-400 uppercase tracking-widest hover:text-slate-600 transition-colors">
                    Re-Sync Strategic Note
                  </button>
                </div>
              </div>
            </div>

            <div className="card-premium p-6">
              <h3 className="font-bold text-[10px] uppercase tracking-[0.2em] text-slate-400 mb-4">Financial Education</h3>
              <div className="space-y-4">
                {report.fee_scenarios?.map((fee, i) => (
                  <div key={i} className="space-y-1">
                    <p className="text-xs font-bold text-slate-800">{fee.scenario_name}</p>
                    <p className="text-[10px] text-slate-500 line-clamp-2 leading-relaxed">{fee.explanation_bullets?.[0]}</p>
                  </div>
                )) || <p className="text-[10px] text-slate-400 italic">No education scenarios for this period.</p>}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
