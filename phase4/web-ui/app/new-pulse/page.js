'use client'
import { useState } from 'react'
import { useRouter } from 'next/navigation'

export default function NewPulsePage() {
  const router = useRouter()
  const [step, setStep] = useState(0)
  const [loading, setLoading] = useState(false)
  const [reviewsCount, setReviewsCount] = useState(300)

  const steps = [
    { label: 'Collect', desc: 'Fetching reviews' },
    { label: 'Clean', desc: 'PII Removal' },
    { label: 'Analyze', desc: 'Signal Discovery' },
    { label: 'Generate', desc: 'Finalizing Note' }
  ]

  const handleStart = async () => {
    setLoading(true)
    setStep(0)
    
    // Simulating progress
    for (let i = 0; i < steps.length; i++) {
      setStep(i)
      await new Promise(r => setTimeout(r, 2000))
    }

    try {
      const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'}/api/generate-report?max_reviews=${reviewsCount}`, { method: 'POST' })
      const data = await res.json()
      router.push(`/report/${data.report_id}`)
    } catch (err) {
      console.error(err)
      setLoading(false)
    }
  }

  return (
    <div className="max-w-2xl mx-auto py-20">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold mb-4">Start New Intelligence Pulse</h1>
        <p className="text-zinc-500">Trigger the 6-layer AI pipeline to synthesize recent feedback.</p>
      </div>

      {!loading ? (
        <div className="card-premium p-8 space-y-8">
          <div>
            <label className="text-xs font-bold text-zinc-500 uppercase mb-4 block">Select Review Volume</label>
            <div className="grid grid-cols-3 gap-4">
              {[100, 300, 500].map(c => (
                <button 
                  key={c}
                  onClick={() => setReviewsCount(c)}
                  className={`p-4 rounded-xl border-2 transition-all ${reviewsCount === c ? 'border-[#0066CC] bg-[#0066CC]/10 text-white' : 'border-zinc-800 text-zinc-500'}`}
                >
                  <span className="text-lg font-bold">{c}</span>
                  <p className="text-[10px] uppercase">Reviews</p>
                </button>
              ))}
            </div>
          </div>
          
          <button 
            onClick={handleStart}
            className="btn-primary w-full py-4 text-lg"
          >
            Launch Pulse Pipeline
          </button>
        </div>
      ) : (
        <div className="card-premium p-12">
          <div className="flex justify-between mb-8">
            {steps.map((s, i) => (
              <div key={i} className="flex flex-col items-center gap-2 flex-1">
                <div className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-xs transition-all ${i === step ? 'bg-[#0066CC] text-white scale-110 shadow-lg shadow-blue-500/20' : i < step ? 'bg-[#00E676] text-white' : 'bg-zinc-800 text-zinc-500'}`}>
                  {i < step ? '✓' : i + 1}
                </div>
                <span className={`text-[10px] font-bold uppercase ${i === step ? 'text-white' : 'text-zinc-600'}`}>{s.label}</span>
              </div>
            ))}
          </div>
          <div className="text-center">
            <h2 className="text-xl font-bold mb-2 animate-pulse">{steps[step].desc}...</h2>
            <p className="text-sm text-zinc-500">Synthesizing intelligence for INDMoney leadership.</p>
          </div>
        </div>
      )}
    </div>
  )
}
