
export async function POST(request: Request) {
  try {
    const { messages } = await request.json()

    const response = await fetch('https://apps.abacus.ai/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.ABACUSAI_API_KEY}`
      },
      body: JSON.stringify({
        model: 'gpt-4.1-mini',
        messages: [
          {
            role: 'system',
            content: `You are an AI sales assistant for a comprehensive sales-enablement platform. You help sales teams analyze customer interactions, provide insights, and suggest next best actions.

Your capabilities include:
- Analyzing sales call transcripts and emails
- Providing insights on customer sentiment and pain points
- Suggesting follow-up strategies and next steps
- Identifying opportunities and potential concerns
- Offering coaching tips for sales reps
- Analyzing deal progression and pipeline health
- Providing CRM recommendations and updates

Always provide actionable, specific, and professional advice. Be concise but thorough. When discussing deals or customers, reference realistic sales scenarios. Focus on practical recommendations that can drive sales success.

Current platform metrics:
- 127 total contacts in pipeline
- $847K monthly revenue 
- 73% win rate
- 23 active deals
- 156 AI insights generated this month`
          },
          ...messages
        ],
        stream: true,
        max_tokens: 3000,
        temperature: 0.7,
      }),
    })

    if (!response.ok) {
      throw new Error(`API call failed: ${response.status}`)
    }

    const encoder = new TextEncoder()
    const decoder = new TextDecoder()

    const readable = new ReadableStream({
      async start(controller) {
        try {
          const reader = response.body?.getReader()
          if (!reader) {
            throw new Error('No response body')
          }

          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value)
            const lines = chunk.split('\n')

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                const data = line.slice(6)
                if (data === '[DONE]') {
                  controller.enqueue(encoder.encode('data: [DONE]\n\n'))
                  controller.close()
                  return
                }
                
                try {
                  const parsed = JSON.parse(data)
                  const content = parsed.choices?.[0]?.delta?.content || ''
                  if (content) {
                    controller.enqueue(encoder.encode(`data: ${JSON.stringify({content})}\n\n`))
                  }
                } catch (e) {
                  // Skip invalid JSON
                }
              }
            }
          }
        } catch (error) {
          console.error('Streaming error:', error)
          controller.error(error)
        }
      }
    })

    return new Response(readable, {
      headers: {
        'Content-Type': 'text/plain; charset=utf-8',
        'Cache-Control': 'no-cache',
      },
    })

  } catch (error) {
    console.error('Chat API error:', error)
    return new Response(JSON.stringify({ error: 'Failed to process request' }), {
      status: 500,
      headers: {
        'Content-Type': 'application/json',
      },
    })
  }
}
