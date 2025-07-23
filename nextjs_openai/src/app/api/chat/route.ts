import { NextRequest, NextResponse } from 'next/server';
import { generateChatCompletion, ChatMessage } from '@/lib/openai-wrapper';

export async function POST(req: NextRequest) {
  try {
    const { messages } = await req.json();

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json({ error: 'Messages array is required' }, { status: 400 });
    }

    // Validate message format
    const validMessages: ChatMessage[] = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    const result = await generateChatCompletion(validMessages);

    return NextResponse.json({ 
      message: result.message,
      usage: result.usage,
      model: result.model,
      id: result.id
    });

  } catch (error) {
    console.error('Chat API error:', error);
    return NextResponse.json(
      { error: 'Failed to get response from OpenAI' },
      { status: 500 }
    );
  }
} 