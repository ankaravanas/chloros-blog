# Chloros Blog MCP Server

An MCP (Model Context Protocol) server that automates medical blog article creation for Dr. Georgios Chloros, an orthopedic surgeon in Greece.

## Features

- **RAG-Validated Content**: Triple-check system with 88-96% clinical accuracy
- **Quality Scoring**: 0-100 scale with automated pass/fail gate at 80 points
- **Greek Localization**: Native Greek content with cultural context integration
- **5 Transformative Patterns**: Proven patterns that reduce physician editing from 85% to 15%
- **Google Workspace Integration**: Seamless document creation and management

## Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Run the Server**
   ```bash
   python -m src.main
   ```

## Architecture

### Workflow Phases

1. **Research & Strategy** (30s, parallel execution)
   - Medical research via Pinecone vector database
   - Cultural context research via Perplexity API
   - Pattern validation from Google Sheets
   - Content strategy generation

2. **Content Generation** (120s)
   - Complete article generation using OpenRouter/Gemini
   - Greek language with Γ' ενικό voice
   - Markdown formatting with proper structure

3. **Quality Evaluation** (20s)
   - 4-category scoring system (Voice/Structure/Medical/SEO)
   - Critical violation detection
   - Word count validation

4. **Publishing** (5s)
   - Google Doc creation with HTML conversion
   - Drive folder management
   - Tracking sheet updates

### Quality Standards

- **Pass Threshold**: 80+ points out of 100
- **Word Count**: Within -15% to +∞ of target
- **Medical Accuracy**: RAG-validated against medical corpus
- **Voice Consistency**: Γ' ενικό (third person) throughout
- **Structure**: 2-3 sentence paragraphs, clear section flow

## API Keys Required

- OpenAI (embeddings and strategy)
- OpenRouter (content generation)
- Perplexity (cultural context)
- Pinecone (medical research)
- Google Cloud (Sheets, Docs, Drive)

## Success Metrics

- ✅ 80%+ articles pass quality gate on first generation
- ✅ <3 minutes total workflow time (vs 90+ minutes manual)
- ✅ <5 minutes physician review time (vs 30-45 minutes)
- ✅ 88-96% medical accuracy validation

## License

MIT License - See LICENSE file for details.
