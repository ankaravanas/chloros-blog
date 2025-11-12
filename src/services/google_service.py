"""
Simplified Google service for Sheets and Docs.
"""

import logging
from typing import Dict, Any, Optional
from typing import List
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import markdown

from ..config import settings

logger = logging.getLogger(__name__)


class GoogleService:
    """Simplified Google service for MCP server."""
    
    def __init__(self):
        """Initialize Google service."""
        self.credentials = self._get_credentials()
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.docs_service = build('docs', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
    
    def _get_credentials(self) -> Credentials:
        """Get OAuth2 credentials."""
        try:
            credentials = Credentials(
                token=None,
                refresh_token=settings.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret
            )
            credentials.refresh(Request())
            return credentials
        except Exception as e:
            logger.error(f"Google credentials error: {e}")
            raise
    
    async def read_blog_patterns(self) -> Dict[str, Any]:
        """Read pattern data from Google Sheets."""
        try:
            # Read basic pattern data
            ranges = ['APPROVED_PATTERNS!A:F', 'FORBIDDEN_PATTERNS!A:G']
            
            result = self.sheets_service.spreadsheets().values().batchGet(
                spreadsheetId=settings.google_sheets_id,
                ranges=ranges
            ).execute()
            
            return {
                'approved_patterns': result.get('valueRanges', [{}])[0].get('values', []),
                'forbidden_patterns': result.get('valueRanges', [{}])[1].get('values', []) if len(result.get('valueRanges', [])) > 1 else []
            }
            
        except Exception as e:
            logger.error(f"Error reading patterns: {e}")
            return {'approved_patterns': [], 'forbidden_patterns': []}
    
    async def create_google_doc(self, article_markdown: str, title: str, status: str) -> Dict[str, str]:
        """Create Google Doc from markdown."""
        try:
            # Create document
            doc_title = f"{title} - Blog Post {'✅' if status == 'PASS' else '⚠️ REVIEW'}"
            
            document = {'title': doc_title}
            doc = self.docs_service.documents().create(body=document).execute()
            doc_id = doc.get('documentId')
            
            # Insert content (simplified)
            text_content = self._markdown_to_text(article_markdown)
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': text_content
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            logger.info(f"Created Google Doc: {doc_title}")
            return {'doc_id': doc_id, 'doc_url': doc_url}
            
        except Exception as e:
            logger.error(f"Error creating Google Doc: {e}")
            raise
    
    def _markdown_to_text(self, markdown_content: str) -> str:
        """Convert markdown to plain text."""
        import re
        text = re.sub(r'^#+\s*', '', markdown_content, flags=re.MULTILINE)
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        return text