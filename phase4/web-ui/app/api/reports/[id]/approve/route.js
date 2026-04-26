import { NextResponse } from 'next/server';
import { exec } from 'child_process';
import path from 'path';

export async function POST(request, { params }) {
  const { id } = params;
  const body = await request.json();
  const { text, email, mode } = body;

  const projectRoot = process.cwd().includes('web-ui') 
    ? path.join(process.cwd(), '..', '..') 
    : process.cwd();
  
  const bridgePath = path.join(projectRoot, 'phase4', 'approve_bridge.py');
  
  // Escape arguments for shell
  const escapedText = text.replace(/"/g, '\\"');
  const command = `python3 "${bridgePath}" --id ${id} --text "${escapedText}" --email "${email}" --mode ${mode || 'both'}`;

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
