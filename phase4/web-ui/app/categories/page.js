'use client'
import { useState } from 'react'

export default function CategoriesPage() {
  const [categories, setCategories] = useState([
    { name: 'Bugs', desc: 'Technical errors and crashes reported by users.', count: 42, color: 'bg-red-500' },
    { name: 'UX Issues', desc: 'Difficulty in navigating or understanding the UI.', count: 128, color: 'bg-[#0066CC]' },
    { name: 'Performance', desc: 'App lag, slow loading, and battery drain.', count: 56, color: 'bg-amber-500' },
    { name: 'Payments', desc: 'Issues related to transactions and withdrawals.', count: 24, color: 'bg-[#00E676]' },
    { name: 'Security', desc: 'Login issues and 2FA related feedback.', count: 18, color: 'bg-indigo-500' },
    { name: 'Features', desc: 'Feature requests and general praise.', count: 151, color: 'bg-pink-500' },
  ])

  return (
    <div className="space-y-8 animate-in fade-in duration-700">
      <div>
        <h1 className="text-3xl font-bold mb-2">Categories</h1>
        <p className="text-zinc-500">AI-based classification of reviews into product buckets.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {categories.map((cat, i) => (
          <div key={i} className="card-premium p-6 hover:translate-y-[-4px] transition-all">
            <div className="flex justify-between items-start mb-6">
              <div className={`w-12 h-12 rounded-xl ${cat.color} bg-opacity-20 flex items-center justify-center text-xl`}>
                <div className={`w-3 h-3 rounded-full ${cat.color}`} />
              </div>
              <div className="text-right">
                <p className="text-2xl font-bold text-white">{cat.count}</p>
                <p className="text-[10px] font-bold text-zinc-500 uppercase tracking-widest">Reviews</p>
              </div>
            </div>
            <h3 className="text-lg font-bold text-white mb-2">{cat.name}</h3>
            <p className="text-sm text-zinc-400 mb-6 leading-relaxed">{cat.desc}</p>
            <div className="w-full bg-zinc-900 h-1 rounded-full overflow-hidden">
              <div 
                className={`h-full ${cat.color}`} 
                style={{ width: `${(cat.count / 151) * 100}%` }} 
              />
            </div>
          </div>
        ))}
      </div>

      <div className="card-premium p-8 bg-zinc-900/50 border-dashed border-2 border-zinc-800 text-center">
        <p className="text-zinc-500 mb-4">Want to create a custom category?</p>
        <button className="btn-secondary text-xs">Define New Bucket</button>
      </div>
    </div>
  )
}
