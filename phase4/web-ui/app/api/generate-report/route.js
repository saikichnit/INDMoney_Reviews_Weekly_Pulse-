import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';

export async function POST(request) {
  const { searchParams } = new URL(request.url);
  const days = searchParams.get('days') || '30';
  const maxReviews = searchParams.get('max_reviews') || '1000';

  const projectRoot = process.cwd().includes('web-ui') 
    ? path.join(process.cwd(), '..', '..') 
    : process.cwd();
  
  // [NEW] GitHub Action Trigger for Vercel/Production
  const githubToken = process.env.GITHUB_TOKEN;
  const githubRepo = process.env.GITHUB_REPO || 'saikichnit/INDMoney_Reviews_Weekly_Pulse-';

  // If we are on Vercel, we MUST use GitHub Actions. Local python3 won't work.
  if (process.env.VERCEL) {
    if (!githubToken) {
      return NextResponse.json({ error: "Configuration Required", message: "Missing GITHUB_TOKEN." }, { status: 400 });
    }

    try {
      // 1. ROOT CAUSE FIX: Check if a fresh report for this window already exists (Cache for 1 hour)
      // This makes the response INSTANT (5-10s) instead of 80s.
      const ARCHIVE_URL = `https://raw.githubusercontent.com/${githubRepo}/main/data/reports_archive.json?t=${Date.now()}`;
      const archiveRes = await fetch(ARCHIVE_URL, { cache: 'no-store' });
      const reports = await archiveRes.json();
      
      if (Array.isArray(reports) && reports.length > 0) {
        const latest = reports[0];
        const createdAt = new Date(latest.created_at);
        const ageInMinutes = (new Date() - createdAt) / 60000;
        
        // If we have a report for this window that is less than 60 mins old, return it INSTANTLY
        if (ageInMinutes < 60) {
          return NextResponse.json({ 
            report_id: latest.id, 
            status: "success", 
            message: "Retrieved fresh report from intelligence cache." 
          });
        }
      }

      // 2. CONCURRENCY GUARD: Check for existing in-progress actions
      const actionsRes = await fetch(`https://api.github.com/repos/${githubRepo}/actions/runs?status=in_progress`, {
        headers: { 'Authorization': `token ${githubToken}`, 'Accept': 'application/vnd.github.v3+json' }
      });
      const actionsData = await actionsRes.json();
      const inProgress = actionsData.workflow_runs?.filter(run => run.name.includes("Weekly Review Pulse") || run.path.includes("scheduler.yml"));

      if (inProgress && inProgress.length > 0) {
        return NextResponse.json({ 
          status: "started", 
          message: "An analysis is ALREADY running in the cloud. We will auto-redirect as soon as it's done.",
          remote: true 
        });
      }

      // 3. TRIGGER CLOUD WORKER: If no cache and no active run
      const res = await fetch(`https://api.github.com/repos/${githubRepo}/actions/workflows/scheduler.yml/dispatches`, {
        method: 'POST',
        headers: {
          'Authorization': `token ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json',
          'User-Agent': 'Vercel-INDPlus'
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: {
            max_reviews: maxReviews,
            weeks: Math.ceil(parseInt(days)/7).toString()
          }
        })
      });

      if (res.ok) {
        return NextResponse.json({ 
          status: "started", 
          message: "GitHub Action triggered! The analysis is running in the cloud. Check back in 2 minutes.",
          remote: true 
        });
      } else {
        const errData = await res.json();
        return NextResponse.json({ error: "GitHub API Error", details: errData }, { status: res.status });
      }
    } catch (e) {
      return NextResponse.json({ error: "Failed to trigger remote worker", details: e.message }, { status: 500 });
    }
  }

  // Fallback to local execution (ONLY for local development)
  const bridgePath = path.join(projectRoot, 'phase4', 'generate_bridge.py');
  const command = `python3 "${bridgePath}" --days ${days} --max_reviews ${maxReviews}`;

  return new Promise((resolve) => {
    exec(command, { cwd: projectRoot }, (error, stdout, stderr) => {
      if (error) {
        resolve(NextResponse.json({ error: "Local execution failed. If on Vercel, use GITHUB_TOKEN.", details: error.message }, { status: 500 }));
        return;
      }
      try {
        const result = JSON.parse(stdout);
        resolve(NextResponse.json(result));
      } catch (e) {
        resolve(NextResponse.json({ error: "Parsing error", output: stdout }, { status: 500 }));
      }
    });
  });
}
