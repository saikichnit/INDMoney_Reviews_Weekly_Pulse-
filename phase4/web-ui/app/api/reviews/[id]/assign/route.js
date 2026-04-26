import { NextResponse } from 'next/server';

export async function POST(request, { params }) {
  const { id } = params;
  try {
    const body = await request.json();
    const pmName = body.assigned_to;
    
    // In a real cloud environment, we'd securely hit Jira's API here.
    // For this milestone, we simulate the production Jira Bridge response 
    // to prove the UI and flow work perfectly on Vercel without exposing real keys.
    const mockJiraId = `IND-${Math.floor(1000 + Math.random() * 9000)}`;
    
    return NextResponse.json({ 
      success: true, 
      jira_id: mockJiraId, 
      assigned_to: pmName 
    });
  } catch (error) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
