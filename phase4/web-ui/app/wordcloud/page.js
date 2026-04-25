'use client'
import { useState, useEffect } from 'react'

export default function WordCloudPage() {
  const [keywords, setKeywords] = useState([
    { text: 'app', size: 40, color: 'text-white' },
    { text: 'good', size: 36, color: 'text-[#00E676]' },
    { text: 'nice', size: 24, color: 'text-zinc-400' },
    { text: 'easy', size: 30, color: 'text-[#00E676]' },
    { text: 'best', size: 22, color: 'text-amber-500' },
    { text: 'user', size: 28, color: 'text-zinc-400' },
    { text: 'market', size: 20, color: 'text-zinc-500' },
    { text: 'groww', size: 32, color: 'text-[#0066CC]' },
    { text: 'update', size: 18, color: 'text-red-500' },
    { text: 'trading', size: 26, color: 'text-white' },
    { text: 'money', size: 20, color: 'text-[#00E676]' },
    { text: 'price', size: 16, color: 'text-zinc-500' },
    { text: 'chart', size: 24, color: 'text-white' },
    { text: 'simple', size: 22, color: 'text-zinc-400' },
    { text: 'funds', size: 18, color: 'text-[#0066CC]' },
    { text: 'customer', size: 20, color: 'text-zinc-400' },
  ])

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div>
        <h1 className="text-3xl font-bold mb-2">Word Cloud</h1>
        <p className="text-zinc-500">Most used words, top keywords, and emerging themes.</p>
      </div>

      {/* Hero Word Cloud */}
      <div className="card-premium p-12 min-h-[400px] flex items-center justify-center relative overflow-hidden">
        <div className="absolute inset-0 opacity-10 bg-[radial-gradient(#0066CC_1px,transparent_1px)] [background-size:20px_20px]" />
        <div className="flex flex-wrap items-center justify-center gap-x-12 gap-y-8 max-w-4xl relative z-10">
          {keywords.map((kw, i) => (
            <button 
              key={i} 
              className={`${kw.color} hover:scale-110 transition-transform cursor-pointer font-bold`}
              style={{ fontSize: `${kw.size}px` }}
            >
              {kw.text}
            </button>
          ))}
        </div>
      </div>

      {/* Top Keywords Ranking */}
      <div className="card-premium">
        <div className="p-6 border-b border-zinc-800 flex justify-between items-center">
          <h3 className="text-sm font-bold text-zinc-400 uppercase">Keyword Frequency Ranking</h3>
          <span className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Showing Top 15</span>
        </div>
        <div className="p-6 space-y-6">
          {keywords.slice(0, 10).map((kw, i) => (
            <div key={i} className="flex items-center gap-6">
              <span className="text-xs font-bold text-zinc-500 w-4">{i + 1}</span>
              <span className="text-sm font-bold text-white w-24">{kw.text}</span>
              <div className="flex-1 bg-zinc-900 h-2 rounded-full overflow-hidden">
                <div 
                  className="bg-[#0066CC] h-full transition-all duration-1000"
                  style={{ width: `${(kw.size / 40) * 100}%` }}
                />
              </div>
              <span className="text-xs font-bold text-zinc-500 w-12 text-right">{kw.size * 3} hits</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
