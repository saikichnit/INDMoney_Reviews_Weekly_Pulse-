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
