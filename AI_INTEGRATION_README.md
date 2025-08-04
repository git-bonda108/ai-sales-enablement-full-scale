# AI Integration for Sales MCP Platform

## Overview

This AI integration provides intelligent chat responses, transcript processing, and email generation using OpenAI's GPT-3.5-turbo model. The system includes graceful fallback modes and context-aware responses based on your CRM data.

## Features

### ✅ Real OpenAI Integration
- **GPT-3.5-turbo** for intelligent chat responses
- **Context-aware** email generation
- **Intelligent transcript processing** with entity extraction
- **Fallback mode** when API is unavailable
- **Cost tracking** and usage monitoring

### ✅ Smart Chat Queries
- "What deals need attention?" → AI analyzes your actual pipeline data
- "Create account called Microsoft" → AI understands and creates records
- "Draft follow-up for TechCorp" → AI writes contextual emails

### ✅ Intelligent Transcript Processing
- Upload transcript → AI extracts entities (not regex!)
- Auto-creates deals for high-score opportunities
- Suggests specific next actions
- Identifies budget and timeline information

### ✅ AI Email Generation
- Context-aware professional emails
- Specific to each prospect and situation
- Progressive autonomy levels

## Architecture Benefits

- **Graceful Degradation**: Works with/without OpenAI API
- **Cost Efficient**: ~$0.10/day for 100 queries
- **OpenAI Compatible**: Standard /chat endpoint
- **Context Aware**: Uses your CRM data for responses

## Quick Start

### 1. Environment Setup

```bash
# Set your API key
export OPENAI_API_KEY="sk-your-key-here"

# Or create .env file
echo "OPENAI_API_KEY=sk-your-key-here" > .env
```

### 2. Install Dependencies

```bash
# Using uv (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

### 3. Run Setup Script

```bash
./setup_ai_integration.sh
```

### 4. Start the API Server

```bash
# Using uv
uv run python api_gateway.py

# Or using pip
python api_gateway.py
```

## API Endpoints

### Health Check
```bash
curl http://localhost:8000/health
```

### AI Status
```bash
curl http://localhost:8000/ai/status
```

### Intelligent Chat
```bash
curl -X POST http://localhost:8000/ai/chat \
  -H "Content-Type: application/json" \
  -d '{
    "model": "sales-ai-v1",
    "messages": [
      {"role": "user", "content": "Analyze my top 3 deals"}
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

### Smart Transcript Processing
```bash
curl -X POST http://localhost:8000/ai/process-transcript \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Budget is $500K, need by Q3",
    "source": "upload"
  }'
```

### AI Email Generation
```bash
curl -X POST http://localhost:8000/ai/generate-email \
  -H "Content-Type: application/json" \
  -d '{
    "prospect_name": "John Smith",
    "email_type": "follow_up",
    "context": {
      "company": "TechCorp",
      "discussion": "AI platform implementation"
    }
  }'
```

### Deal Analysis
```bash
curl -X POST http://localhost:8000/ai/analyze-deals \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Analyze my top 3 deals"
  }'
```

## Testing

### Run All Tests
```bash
# Using uv
uv run python test_ai_integration.py

# Or using pip
python test_ai_integration.py
```

### Test Individual Components

```python
from ai_integration import ai_integration
import asyncio

# Test chat completion
async def test_chat():
    messages = [{"role": "user", "content": "What deals need attention?"}]
    response = await ai_integration.chat_completion(messages)
    print(f"Response: {response.content}")

# Test transcript processing
async def test_transcript():
    transcript = "Prospect mentioned budget of $500K and timeline of Q3"
    result = await ai_integration.process_transcript(transcript)
    print(f"Analysis: {result['analysis']}")

# Run tests
asyncio.run(test_chat())
asyncio.run(test_transcript())
```

## Configuration

### Environment Variables

```bash
# Required
OPENAI_API_KEY=sk-your-openai-key-here

# Optional
ANTHROPIC_API_KEY=sk-your-anthropic-key-here
APP_ENV=development
LOG_LEVEL=INFO
```

### AI Integration Settings

```python
# In ai_integration.py
class AIIntegration:
    def __init__(self):
        self.model = "gpt-3.5-turbo"  # Change model here
        self.max_tokens = 1000         # Adjust token limit
        self.temperature = 0.7         # Adjust creativity (0.0-1.0)
```

## Cost Estimation

The system provides cost estimates for each API call:

- **GPT-3.5-turbo**: ~$0.0015 per 1K tokens
- **Typical chat response**: ~$0.002-0.005
- **Transcript processing**: ~$0.01-0.03
- **Email generation**: ~$0.005-0.015

## Fallback Mode

When OpenAI API is unavailable, the system provides intelligent fallback responses:

- **Keyword-based responses** for common queries
- **Context-aware suggestions** based on CRM data
- **Graceful error handling** with helpful messages

## Integration with Existing Systems

### CRM Context Updates

```python
# Update AI with current CRM data
ai_integration.update_crm_context({
    "deals": [
        {"name": "TechCorp", "stage": "Proposal", "amount": 50000},
        {"name": "StartupXYZ", "stage": "Qualification", "amount": 25000}
    ],
    "accounts": [
        {"name": "Acme Corp", "industry": "Technology"}
    ]
})
```

### Custom Prompts

```python
# Add custom system prompts
def custom_prompt(context_type):
    if context_type == "sales_analysis":
        return "You are a sales expert analyzing pipeline data..."
    return "You are an AI sales assistant..."
```

## Troubleshooting

### Common Issues

1. **API Key Not Found**
   ```bash
   export OPENAI_API_KEY="your-key-here"
   ```

2. **Connection Errors**
   - Check internet connection
   - Verify API key is valid
   - Check OpenAI service status

3. **Fallback Mode Active**
   - Normal when API is unavailable
   - Check API key and network
   - Review error logs

### Debug Mode

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Check AI status
status = ai_integration.get_status()
print(f"AI Status: {status}")
```

## Security Considerations

- **API Keys**: Store securely, never commit to version control
- **Rate Limiting**: Implement if needed for production
- **Data Privacy**: Review OpenAI data usage policies
- **Access Control**: Implement proper authentication

## Production Deployment

### Environment Setup
```bash
# Production environment variables
export OPENAI_API_KEY="sk-prod-key"
export APP_ENV=production
export LOG_LEVEL=WARNING
```

### Monitoring
- Monitor API usage and costs
- Track response times and quality
- Set up alerts for API failures

### Scaling
- Implement caching for repeated queries
- Use connection pooling for API calls
- Consider multiple API keys for load balancing

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review error logs
3. Test with the provided test scripts
4. Verify API key and network connectivity

## License

This AI integration is part of the Sales MCP Platform and follows the same licensing terms. 