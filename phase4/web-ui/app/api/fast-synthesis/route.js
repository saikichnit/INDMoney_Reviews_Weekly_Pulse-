import { NextResponse } from 'next/server';
import { Groq } from 'groq-sdk';

export async function POST(request) {
  const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
  const geminiKey = process.env.GEMINI_API_KEY;
  
  const { searchParams } = new URL(request.url);
  const days = parseInt(searchParams.get('days') || '30');
  const maxReviews = parseInt(searchParams.get('max_reviews') || '1000');
  
  const githubRepo = process.env.GITHUB_REPO || "saikichnit/INDMoney_Reviews_Weekly_Pulse-";
  const githubToken = process.env.GITHUB_TOKEN;

  try {
    // 1. Fetch Review Lake from GitHub
    const lakeUrl = `https://raw.githubusercontent.com/${githubRepo}/main/data/latest_pulse.json?t=${Date.now()}`;
    const lakeRes = await fetch(lakeUrl, { cache: 'no-store' });
    
    if (!lakeRes.ok) {
        return NextResponse.json({ error: "Review Lake Not Found", message: "Background sync hasn't created the lake yet." }, { status: 404 });
    }
    
    const lakeData = await lakeRes.json();
    const allReviews = lakeData.reviews || [];

    // 2. Filter Reviews
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const filteredReviews = allReviews
      .filter(r => {
          const rDate = r.review_date || r.date;
          if (!rDate) return true;
          return new Date(rDate) > cutoffDate;
      })
      .slice(0, maxReviews);

    if (filteredReviews.length === 0) {
        return NextResponse.json({ error: "No Signals", message: "No reviews found for the selected window." }, { status: 404 });
    }

    // 3. Synthesis Preparation
    const context = filteredReviews.slice(0, 50).map(r => `- ${r.review_text}`).join('\n');
    const prompt = `
    Analyze these INDMoney app reviews and generate a Strategic Intelligence Report.
    REVIEWS:
    ${context}

    Return a JSON object with:
    1. "summary": A 3-sentence executive summary.
    2. "themes": Array of 3-5 themes {name, percentage}.
    3. "quotes": Array of 3 impactful user quotes.
    4. "action_items": Array of 3-5 actionable product tasks.
    5. "sentiment_distribution": {positive, negative, neutral} percentages.
    `;

    let synthesis = null;

    // A. Try Groq (Primary)
    try {
        const response = await groq.chat.completions.create({
            messages: [{ role: "user", content: prompt }],
            model: "llama-3.3-70b-versatile",
            response_format: { type: "json_object" }
        });
        synthesis = JSON.parse(response.choices[0].message.content);
    } catch (err) {
        console.error("Groq Failed, trying Gemini Fallback:", err.message);
        
        // B. Try Gemini (Fallback with Discovery)
        if (geminiKey) {
            try {
                // First try Flash
                let modelName = "gemini-1.5-flash";
                let geminiUrl = `https://generativelanguage.googleapis.com/v1beta/models/${modelName}:generateContent?key=${geminiKey}`;
                let geminiRes = await fetch(geminiUrl, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        contents: [{ parts: [{ text: prompt + "\nIMPORTANT: Return ONLY raw JSON." }] }]
                    })
                });

                if (!geminiRes.ok) {
                    const errStatus = geminiRes.status;
                    if (errStatus === 404) {
                        // AUTO-DISCOVERY: If 404, ask the API what models we ARE allowed to use
                        const listUrl = `https://generativelanguage.googleapis.com/v1beta/models?key=${geminiKey}`;
                        const listRes = await fetch(listUrl);
                        const listData = await listRes.json();
                        const availableModels = listData.models?.map(m => m.name) || [];
                        throw new Error(`Model ${modelName} not found. Available models for your key: ${availableModels.join(', ')}`);
                    }
                    const errText = await geminiRes.text();
                    throw new Error(`Gemini Error (${errStatus}): ${errText}`);
                }

                const geminiData = await geminiRes.json();
                let text = geminiData.candidates[0].content.parts[0].text;
                
                // Cleanup markdown
                if (text.includes("```json")) text = text.split("```json")[1].split("```")[0].trim();
                else if (text.includes("```")) text = text.split("```")[1].split("```")[0].trim();
                
                synthesis = JSON.parse(text);
            } catch (geminiErr) {
                console.error("Gemini Discovery Failed:", geminiErr);
                throw new Error(`Both Groq and Gemini failed. ${geminiErr.message}`);
            }
        } else {
            throw err;
        }
    }

    // 4. Persistence Dispatch (Async)
    if (githubToken) {
      fetch(`https://api.github.com/repos/${githubRepo}/actions/workflows/scheduler.yml/dispatches`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${githubToken}`,
          "Accept": "application/vnd.github.v3+json",
        },
        body: JSON.stringify({ ref: "main" }),
      }).catch(e => console.error("Persistence sync failed:", e));
    }

    return NextResponse.json({
        id: Date.now(),
        ...synthesis,
        review_count: filteredReviews.length,
        created_at: new Date().toISOString(),
        is_fast_path: true
    });

  } catch (err) {
    console.error("Synthesis Failed:", err);
    return NextResponse.json({ 
        error: "Synthesis Error", 
        message: err.message || "AI synthesis failed on all providers."
    }, { status: 500 });
  }
}
