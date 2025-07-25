import { NextRequest, NextResponse } from 'next/server';
import { generateChatCompletion, generateChatCompletionStream, ChatMessage } from '@/lib/openai-wrapper';

export async function POST(req: NextRequest) {
  try {
    const { messages, stream = false } = await req.json();

    if (!messages || !Array.isArray(messages)) {
      return NextResponse.json({ error: 'Messages array is required' }, { status: 400 });
    }

    // Validate message format
    const validMessages: ChatMessage[] = messages.map(msg => ({
      role: msg.role,
      content: msg.content
    }));

    // Handle streaming response
    if (stream) {
      const openaiStream = await generateChatCompletionStream(validMessages);
      
      // Create a ReadableStream for Server-Sent Events
      const encoder = new TextEncoder();
      const readable = new ReadableStream({
        async start(controller) {
          try {
            let fullContent = '';
            let model = '';
            let id = '';
            
            for await (const chunk of openaiStream) {
              const delta = chunk.choices[0]?.delta;
              if (delta?.content) {
                fullContent += delta.content;
                
                // Send the delta content as SSE
                const sseData = `data: ${JSON.stringify({
                  type: 'content',
                  content: delta.content,
                  fullContent: fullContent
                })}\n\n`;
                controller.enqueue(encoder.encode(sseData));
              }
              
              // Store metadata from the first chunk
              if (chunk.model && !model) {
                model = chunk.model;
              }
              if (chunk.id && !id) {
                id = chunk.id;
              }
            }
            
            // Send completion event
            const completionData = `data: ${JSON.stringify({
              type: 'done',
              fullContent: fullContent,
              model: model,
              id: id
            })}\n\n`;
            controller.enqueue(encoder.encode(completionData));
            
            controller.close();
          } catch (error) {
            console.error('Streaming error:', error);
            const errorData = `data: ${JSON.stringify({
              type: 'error',
              error: 'Streaming failed'
            })}\n\n`;
            controller.enqueue(encoder.encode(errorData));
            controller.close();
          }
        },
      });

      return new NextResponse(readable, {
        headers: {
          'Content-Type': 'text/event-stream',
          'Cache-Control': 'no-cache',
          'Connection': 'keep-alive',
        },
      });
    }

    // Handle regular (non-streaming) response
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