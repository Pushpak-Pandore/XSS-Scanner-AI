# AI-Enhanced XSS Scanner - API Configuration Guide

## Overview
This guide explains how to configure API keys for the AI-Enhanced XSS Scanner Platform. The application currently uses the Emergent LLM Universal Key but can be easily switched to use your own API keys for different providers.

## Current Configuration

### Default Setup (Emergent LLM Universal Key)
The application is currently configured to use the Emergent LLM Universal Key which provides access to:
- OpenAI GPT-4o (for vulnerability analysis)
- Anthropic Claude 3.7 Sonnet (for security reports and remediation)
- Google Gemini (backup option)

**Current Key Location:** `/app/backend/.env`
```
EMERGENT_LLM_KEY=sk-emergent-556F249747fEbDfFd2
```

## Switching to Custom API Keys

### 1. OpenAI Configuration
To use your own OpenAI API key:

1. **Get your API key** from https://platform.openai.com/api-keys
2. **Update the backend code** in `/app/backend/server.py`:

```python
# Replace the get_gpt4_chat function
async def get_gpt4_chat(session_id: str, system_message: str = "You are an expert cybersecurity analyst specializing in XSS vulnerability analysis."):
    # Use your OpenAI API key
    openai_key = os.environ.get('OPENAI_API_KEY', 'your-openai-api-key-here')
    chat = LlmChat(
        api_key=openai_key,
        session_id=session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    return chat
```

3. **Add to environment variables** in `/app/backend/.env`:
```
OPENAI_API_KEY=sk-your-openai-key-here
```

### 2. Anthropic (Claude) Configuration
To use your own Anthropic API key:

1. **Get your API key** from https://console.anthropic.com/
2. **Update the backend code** in `/app/backend/server.py`:

```python
# Replace the get_claude_chat function
async def get_claude_chat(session_id: str, system_message: str = "You are a security report specialist."):
    # Use your Anthropic API key
    anthropic_key = os.environ.get('ANTHROPIC_API_KEY', 'your-anthropic-key-here')
    chat = LlmChat(
        api_key=anthropic_key,
        session_id=session_id,
        system_message=system_message
    ).with_model("anthropic", "claude-3-7-sonnet-20250219")
    return chat
```

3. **Add to environment variables** in `/app/backend/.env`:
```
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
```

### 3. Mixed Configuration
You can also use different keys for different providers:

```python
# In server.py, update both functions
OPENAI_KEY = os.environ.get('OPENAI_API_KEY')
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY')
EMERGENT_KEY = os.environ.get('EMERGENT_LLM_KEY')

async def get_gpt4_chat(session_id: str, system_message: str = "..."):
    # Use OpenAI key if available, otherwise fallback to Emergent
    api_key = OPENAI_KEY if OPENAI_KEY else EMERGENT_KEY
    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message=system_message
    ).with_model("openai", "gpt-4o")
    return chat

async def get_claude_chat(session_id: str, system_message: str = "..."):
    # Use Anthropic key if available, otherwise fallback to Emergent
    api_key = ANTHROPIC_KEY if ANTHROPIC_KEY else EMERGENT_KEY
    chat = LlmChat(
        api_key=api_key,
        session_id=session_id,
        system_message=system_message
    ).with_model("anthropic", "claude-3-7-sonnet-20250219")
    return chat
```

## Available Models

### OpenAI Models
- `gpt-4o` (recommended for analysis)
- `gpt-4`
- `gpt-4o-mini` (faster, cheaper)
- `gpt-5` (if available)

### Anthropic Models
- `claude-3-7-sonnet-20250219` (recommended for reports)
- `claude-3-5-sonnet-20241022`
- `claude-4-sonnet-20250514`

### Google Models
- `gemini-2.0-flash`
- `gemini-1.5-pro`
- `gemini-2.5-pro`

## Environment Variables Reference

### Complete .env File Example
```bash
# Database
MONGO_URL="mongodb://localhost:27017"
DB_NAME="xss_scanner_db"
CORS_ORIGINS="*"

# AI Keys (choose one approach)
# Option 1: Universal Key (current setup)
EMERGENT_LLM_KEY=sk-emergent-556F249747fEbDfFd2

# Option 2: Individual Keys
# OPENAI_API_KEY=sk-your-openai-key
# ANTHROPIC_API_KEY=sk-ant-your-anthropic-key
# GOOGLE_API_KEY=your-google-api-key

# Optional: Webhook endpoints for CI/CD integration
# WEBHOOK_SECRET=your-webhook-secret
# SLACK_WEBHOOK_URL=your-slack-webhook
```

## Restart Instructions

After making any configuration changes:

1. **Restart the backend server:**
```bash
sudo supervisorctl restart backend
```

2. **Verify the changes:**
```bash
tail -f /var/log/supervisor/backend.out.log
```

3. **Test the AI integration** by creating a new scan through the web interface.

## Cost Considerations

### Emergent LLM Universal Key
- Pre-funded credits
- Shared across all AI providers
- Convenient for development and testing
- Can be topped up as needed

### Your Own API Keys
- Direct billing from providers
- More control over usage limits
- Potentially better rates for high volume
- Separate billing for each provider

## Security Best Practices

1. **Never commit API keys to version control**
2. **Use environment variables only**
3. **Rotate keys regularly**
4. **Monitor usage and set billing alerts**
5. **Use least privilege access where possible**

## Troubleshooting

### Common Issues

1. **"API key not found" errors:**
   - Check that the key is properly set in `/app/backend/.env`
   - Restart the backend service
   - Verify the key format is correct

2. **"Rate limit exceeded" errors:**
   - Check your API usage limits
   - Consider upgrading your API plan
   - Implement request queuing if needed

3. **Model not available errors:**
   - Verify the model name is spelled correctly
   - Check if you have access to the specific model
   - Try a different model as fallback

### Debug Mode
To enable detailed logging, add to your `.env`:
```bash
LOG_LEVEL=DEBUG
```

## Support

For questions about:
- **Emergent LLM Key**: Contact Emergent support
- **OpenAI API**: Check OpenAI documentation
- **Anthropic API**: Contact Anthropic support
- **Application Issues**: Check the application logs

## Future Enhancements

Planned features for API configuration:
- Web-based key management interface
- Automatic failover between providers
- Cost optimization algorithms
- Usage analytics dashboard