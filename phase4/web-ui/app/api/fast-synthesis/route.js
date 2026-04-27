import { NextResponse } from 'next/server';
import { Groq } from 'groq-sdk';

export async function POST(request) {
  const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });
  const { searchParams } = new URL(request.url);
  const days = parseInt(searchParams.get('days') || '30');
  const maxReviews = parseInt(searchParams.get('max_reviews') || '1000');
  
  const githubRepo = process.env.GITHUB_REPO || "saikichnit/INDMoney_Reviews_Weekly_Pulse-";
  const githubToken = process.env.GITHUB_TOKEN;

  try {
    // 1. Fetch Review Lake from GitHub (Warm Cache)
    // We use the raw URL with a timestamp to bypass 5min caching
    const lakeUrl = `https://raw.githubusercontent.com/${githubRepo}/main/data/latest_pulse.json?t=${Date.now()}`;
    const lakeRes = await fetch(lakeUrl, { cache: 'no-store' });
    
    if (!lakeRes.ok) {
        return NextResponse.json({ error: "Review Lake Not Found", message: "Background sync hasn't created the lake yet." }, { status: 404 });
    }
    
    const lakeData = await lakeRes.json();
    const allReviews = lakeData.reviews || [];

    // 2. Filter Reviews by User Parameters
    const cutoffDate = new Date();
    cutoffDate.setDate(cutoffDate.getDate() - days);
    
    const filteredReviews = allReviews
      .filter(r => {
          const rDate = r.review_date || r.date;
          if (!rDate) return true; // Default to passing if date is missing
          return new Date(rDate) > cutoffDate;
      })
      .slice(0, maxReviews);

    if (filteredReviews.length === 0) {
        return NextResponse.json({ error: "No Signals", message: "No reviews found for the selected time window." }, { status: 404 });
    }

    // 3. Fast Synthesis (Discovery + Classification)
    // We combine prompts to minimize round-trips
    const context = filteredReviews.slice(0, 300).map(r => `- ${r.review_text}`).join('\n');
    
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

    // Call Groq with Retry Logic
    let response;
    let retries = 3;
    let delay = 2000;

    for (let i = 0; i < retries; i++) {
        try {
            response = await groq.chat.completions.create({
                messages: [{ role: "user", content: prompt }],
                model: "llama-3.3-70b-versatile",
                response_format: { type: "json_object" }
            });
            break; // Success
        } catch (err) {
            if ((err.status === 429 || err.message.includes("rate_limit")) && i < retries - 1) {
                console.log(`Rate limit hit, retrying in ${delay}ms...`);
                await new Promise(resolve => setTimeout(resolve, delay));
                delay *= 2;
                continue;
            }
            throw err;
        }
    }

    const synthesis = JSON.parse(response.choices[0].message.content);

    // 4. Persistence Dispatch (Async)
    // We trigger the GitHub Action in the background to save this report permanently
    const repo = process.env.GITHUB_REPO || "saikichnit/INDMoney_Reviews_Weekly_Pulse-";
    const githubToken = process.env.GITHUB_TOKEN;
    
    if (githubToken) {
      await fetch(`https://api.github.com/repos/${repo}/actions/workflows/scheduler.yml/dispatches`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${githubToken}`,
          "Accept": "application/vnd.github.v3+json",
        },
    return NextResponse.json({
        id: Date.now(), // Temporary ID for instant UI redirect
        ...synthesis,
        review_count: filteredReviews.length,
        created_at: new Date().toISOString(),
        is_fast_path: true
    });

  } catch (err) {
    console.error("Fast Synthesis Failed:", err);
    return NextResponse.json({ 
        error: "Synthesis Error", 
        message: err.message || "Unknown error during AI synthesis",
        details: err.stack
    }, { status: 500 });
  }
}
