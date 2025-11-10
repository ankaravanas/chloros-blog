# Railway Environment Variables Setup

## Required Environment Variables for Railway Deployment

When you deploy to Railway, you need to set these environment variables in the Railway dashboard:

### 🔑 **API Keys (Required)**

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# OpenRouter  
OPENROUTER_API_KEY=sk-or-v1-...

# Perplexity
PERPLEXITY_API_KEY=pplx-...

# Pinecone
PINECONE_API_KEY=...
PINECONE_ENVIRONMENT=us-west1-gcp
PINECONE_INDEX_NAME=medical

# Google OAuth2
GOOGLE_CLIENT_ID=your_google_client_id_here
GOOGLE_CLIENT_SECRET=your_google_client_secret_here
GOOGLE_REFRESH_TOKEN=your_refresh_token_from_oauth_playground

# Google Resources
GOOGLE_SHEETS_ID=1cRGUsLbpaSBJmA8AmpQkSzpziE4A6RlTIfwywDqKFGY
GOOGLE_PUBLISHED_FOLDER_ID=11XQo6t3NXvOBLNmFrcTixm1Q8K6-2m8W
```

### ⚙️ **Railway Configuration (Optional - Railway sets these automatically)**

```bash
# Railway sets these automatically, but you can override:
PORT=3000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Model Configuration (optional overrides)
OPENROUTER_MODEL=anthropic/claude-3-haiku
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_DIMENSIONS=512

# Quality Configuration (optional overrides)  
QUALITY_PASS_THRESHOLD=80
WORD_COUNT_FAIL_THRESHOLD=-15
MAX_RETRIES=3
```

## 🚀 **Railway Deployment Steps**

### 1. **Connect GitHub Repository**
- Railway project → Settings → Connect GitHub
- Select repository: `ankaravanas/chloros-blog`
- Auto-deploy on push: ✅ Enabled

### 2. **Set Environment Variables**
- Railway dashboard → Variables tab
- Add all the API keys listed above
- **Important**: Don't include quotes around the values

### 3. **Deploy**
- Railway will automatically detect Python project
- Uses `requirements.txt` for dependencies
- Runs `python -m src.main` as startup command
- Serves on Railway's provided PORT (automatically configured)

### 4. **Verify Deployment**
- Check Railway logs for successful startup
- Look for: "All tools registered successfully"
- MCP server will be accessible via Railway's provided URL

## 🔧 **Railway-Specific Features**

- **Auto-scaling**: Railway handles traffic scaling
- **Health checks**: Built into Railway platform
- **Log aggregation**: Available in Railway dashboard
- **Environment management**: Secure variable storage
- **GitHub integration**: Auto-deploy on push to main branch

## 📊 **Expected Railway Logs**

Successful deployment will show:
```
INFO - Starting Chloros Blog MCP Server...
INFO - Connected to Pinecone index: medical
INFO - Phase 1 research tools registered successfully
INFO - Phase 2 generation tools registered successfully  
INFO - Phase 3 evaluation tools registered successfully
INFO - Phase 4 publishing tools registered successfully
INFO - Workflow tools with retry logic registered successfully
INFO - All tools registered successfully
INFO - Server starting on 0.0.0.0:3000
INFO - Environment: Railway
```

## ⚠️ **Important Notes**

- **Port**: Railway automatically assigns PORT environment variable
- **Host**: Must be `0.0.0.0` for Railway (not `localhost`)
- **Environment Variables**: Set in Railway dashboard, not in code
- **Dependencies**: Railway automatically installs from `requirements.txt`
- **Logs**: Available in Railway dashboard for monitoring
