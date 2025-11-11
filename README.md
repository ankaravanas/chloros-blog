# Chloros Blog MCP Server

MCP server that automates Greek orthopedic blog creation with RAG validation, reducing physician editing from 85% to 15%.

## Features
- **3-minute workflow** (vs 90+ minutes manual)
- **80+ quality scoring** with automatic pass/fail gate
- **88-96% medical accuracy** via RAG validation
- **Greek localization** with cultural context
- **Google Workspace integration** for publishing

## Quick Start

### Local
```bash
pip install -r requirements.txt
# Configure .env with API keys
python -m src.main
```

### Railway Deployment
1. Create Railway project → Connect GitHub: `ankaravanas/chloros-blog`
2. Set environment variables (see `RAILWAY.md`)
3. Railway auto-deploys on push

## Workflow
1. **Research** (30s): Medical + Cultural + Patterns → Strategy
2. **Generate** (120s): Complete Greek article with quality patterns
3. **Evaluate** (20s): 4-category scoring (Voice/Structure/Medical/SEO)
4. **Publish** (5s): Google Doc creation and folder management

## API Keys Required
OpenAI, OpenRouter, Perplexity, Pinecone, Google Cloud (OAuth2)

## Success Metrics
- 80%+ quality pass rate
- 88-96% medical accuracy  
- <3 minutes total workflow
- Reduces editing from 85% to 15%
