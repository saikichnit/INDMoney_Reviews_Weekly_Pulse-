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

  if (process.env.VERCEL || githubToken) {
    try {
      const res = await fetch(`https://api.github.com/repos/${githubRepo}/actions/workflows/scheduler.yml/dispatches`, {
        method: 'POST',
        headers: {
          'Authorization': `token ${githubToken}`,
          'Accept': 'application/vnd.github.v3+json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ref: 'main',
          inputs: {
            max_reviews: maxReviews,
            weeks: (parseInt(days)/7).toString()
          }
        })
      });

      if (res.ok) {
        return NextResponse.json({ 
          status: "started", 
          message: "GitHub Action triggered. Intelligence Pulse will update in ~2 minutes.",
          remote: true 
        });
      }
    } catch (e) {
      console.error("GitHub Action trigger failed", e);
    }
  }

  // Fallback to local execution (for local development)
  const bridgePath = path.join(projectRoot, 'phase4', 'generate_bridge.py');
  const command = `python3 "${bridgePath}" --days ${days} --max_reviews ${maxReviews}`;

  return new Promise((resolve) => {
    exec(command, { cwd: projectRoot }, (error, stdout, stderr) => {
      if (error) {
        console.error(`Error: ${error.message}`);
        resolve(NextResponse.json({ error: error.message, details: stderr }, { status: 500 }));
        return;
      }
      
      try {
        const result = JSON.parse(stdout);
        resolve(NextResponse.json(result));
      } catch (e) {
        resolve(NextResponse.json({ error: "Failed to parse Python output", output: stdout, stderr }, { status: 500 }));
      }
    });
  });
}
