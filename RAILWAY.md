# Railway Deployment

## 🚀 Quick Deployment

1. **Create Railway Project**: https://railway.app/ → Deploy from GitHub
2. **Connect Repository**: `ankaravanas/chloros-blog`
3. **Set Environment Variables** in Railway dashboard:
   ```bash
   OPENAI_API_KEY=sk-...
   OPENROUTER_API_KEY=sk-or-v1-...
   PERPLEXITY_API_KEY=pplx-...
   PINECONE_API_KEY=...
   PINECONE_ENVIRONMENT=us-west1-gcp
   GOOGLE_CLIENT_ID=your_client_id
   GOOGLE_CLIENT_SECRET=your_client_secret
   GOOGLE_REFRESH_TOKEN=your_refresh_token
   GOOGLE_SHEETS_ID=1cRGUsLbpaSBJmA8AmpQkSzpziE4A6RlTIfwywDqKFGY
   GOOGLE_PUBLISHED_FOLDER_ID=11XQo6t3NXvOBLNmFrcTixm1Q8K6-2m8W
   ```
4. **Deploy**: Railway auto-deploys from GitHub

## ✅ Expected Logs
```
✅ Starting Chloros Blog MCP Server...
✅ Status: HEALTHY
✅ All tools registered successfully
✅ Server ready for blog automation!
```

Railway handles PORT, HOST, scaling, and monitoring automatically.
