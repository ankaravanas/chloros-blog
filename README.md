# Chloros Blog MCP Server

MCP server for automated Greek orthopedic blog creation. Transforms 90+ minute manual process into 3-minute automated workflow with 88-96% medical accuracy.

## How It Works

Connect this MCP server to Claude Desktop to automate medical blog creation through 7 sequential tools:

### Sequential Workflow Tools
1. **`cultural_context_research`** - Research Greek patient attitudes and cultural context
2. **`read_blog_patterns`** - Load approved writing patterns from Google Sheets  
3. **`search_pinecone_medical`** - Query medical database for research facts
4. **`create_content_strategy`** - Generate content strategy based on research
5. **`generate_blog_post`** - Create complete Greek medical article
6. **`evaluate_article`** - Score quality with 4-category system (Voice/Structure/Medical/SEO)
7. **`export_to_google_doc`** - Export to Google Drive folder

### Complete Workflow Tool
- **`create_blog_article`** - Runs all 7 steps automatically for full automation

## MCP Connection

### Railway (Production)
```
URL: https://chloros-blog-blog-generator.up.railway.app/
MCP Endpoint: Use the Railway URL in Claude Desktop MCP settings
```

### Local Development
```bash
pip install -r requirements.txt
# Configure .env with API keys  
python -m src.main
```

## Usage Examples

**Sequential Workflow (Manual Control)**:
1. `cultural_context_research("ACL reconstruction")`
2. `read_blog_patterns()`
3. `search_pinecone_medical("ACL reconstruction", "knee surgery recovery")`
4. `create_content_strategy(topic, keywords, 2000, medical_facts, cultural_context, patterns)`
5. `generate_blog_post(topic, 2000, medical_facts, cultural_context, strategy)`
6. `evaluate_article(article_content, 2000)`
7. `export_to_google_doc(article_markdown, title, quality_score)`

**Full Automation**:
`create_blog_article("ACL reconstruction", "knee surgery recovery", 2000)`

## Quality System
- **Pass threshold**: 80+ points
- **Scoring**: Voice consistency, structure, medical accuracy, SEO
- **Output**: Google Doc with ✅ (pass) or ⚠️ (review) status

## API Requirements
OpenAI, OpenRouter, Perplexity, Pinecone, Google Cloud OAuth2
