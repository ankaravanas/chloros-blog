"""
Google service for Sheets, Docs, and Drive integration.
Handles reading pattern data, creating documents, and managing files.
"""

import logging
from typing import Dict, Any, Optional
from typing import List  # Separate import for Railway compatibility
import json
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import markdown
from bs4 import BeautifulSoup

from ..config import settings
from ..models.patterns import Pattern, AntiPattern, Structure, ScoringMatrix, Fix, PatternType

logger = logging.getLogger(__name__)


class GoogleService:
    """Service for interacting with Google APIs (Sheets, Docs, Drive)."""
    
    def __init__(self):
        """Initialize Google service with OAuth credentials."""
        self.credentials = self._get_credentials()
        self.sheets_service = build('sheets', 'v4', credentials=self.credentials)
        self.docs_service = build('docs', 'v1', credentials=self.credentials)
        self.drive_service = build('drive', 'v3', credentials=self.credentials)
        
        self.sheets_id = settings.google_sheets_id
        self.published_folder_id = settings.google_published_folder_id
    
    def _get_credentials(self) -> Credentials:
        """Get OAuth2 credentials for Google APIs."""
        try:
            # Create credentials from refresh token
            credentials = Credentials(
                token=None,
                refresh_token=settings.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret
            )
            
            # Refresh the token
            credentials.refresh(Request())
            
            logger.info("Google credentials initialized successfully")
            return credentials
            
        except Exception as e:
            logger.error(f"Failed to initialize Google credentials: {e}")
            raise
    
    async def read_blog_patterns(self) -> Dict[str, Any]:
        """
        Read all pattern data from Google Sheets.
        
        Returns:
            Dictionary containing all pattern data
        """
        try:
            # Define the sheet ranges to read
            ranges = [
                'APPROVED_PATTERNS!A:F',
                'FORBIDDEN_PATTERNS!A:G', 
                'APPROVED_STRUCTURE!A:H',
                'SCORING_MATRIX!A:D',
                'SPECIFIC_FIXES!A:F'
            ]
            
            # Batch read all ranges
            result = self.sheets_service.spreadsheets().values().batchGet(
                spreadsheetId=self.sheets_id,
                ranges=ranges
            ).execute()
            
            value_ranges = result.get('valueRanges', [])
            
            # Parse each sheet
            patterns_data = {
                'approved_patterns': self._parse_approved_patterns(value_ranges[0].get('values', [])),
                'forbidden_patterns': self._parse_forbidden_patterns(value_ranges[1].get('values', [])),
                'approved_structure': self._parse_approved_structure(value_ranges[2].get('values', [])),
                'scoring_matrix': self._parse_scoring_matrix(value_ranges[3].get('values', [])),
                'specific_fixes': self._parse_specific_fixes(value_ranges[4].get('values', []))
            }
            
            logger.info("Successfully read all blog patterns from Google Sheets")
            return patterns_data
            
        except HttpError as e:
            logger.error(f"HTTP error reading Google Sheets: {e}")
            raise
        except Exception as e:
            logger.error(f"Error reading blog patterns: {e}")
            raise
    
    def _parse_approved_patterns(self, values: List[List[str]]) -> List[Pattern]:
        """Parse approved patterns from sheet data."""
        patterns = []
        if not values or len(values) < 2:
            return patterns
        
        headers = values[0]
        for row in values[1:]:
            if len(row) >= 6:
                pattern = Pattern(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    pattern_type=PatternType(row[3].lower()),
                    examples=row[4].split(';') if row[4] else [],
                    weight=int(row[5]) if row[5].isdigit() else 1
                )
                patterns.append(pattern)
        
        return patterns
    
    def _parse_forbidden_patterns(self, values: List[List[str]]) -> List[AntiPattern]:
        """Parse forbidden patterns from sheet data."""
        patterns = []
        if not values or len(values) < 2:
            return patterns
        
        for row in values[1:]:
            if len(row) >= 7:
                pattern = AntiPattern(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    pattern_type=PatternType(row[3].lower()),
                    examples=row[4].split(';') if row[4] else [],
                    penalty_points=int(row[5]) if row[5].isdigit() else 0,
                    auto_fail=row[6].lower() == 'true' if len(row) > 6 else False
                )
                patterns.append(pattern)
        
        return patterns
    
    def _parse_approved_structure(self, values: List[List[str]]) -> List[Structure]:
        """Parse approved structure from sheet data."""
        structures = []
        if not values or len(values) < 2:
            return structures
        
        for row in values[1:]:
            if len(row) >= 8:
                structure = Structure(
                    id=row[0],
                    name=row[1],
                    description=row[2],
                    required_sections=row[3].split(';') if row[3] else [],
                    optional_sections=row[4].split(';') if row[4] else [],
                    section_order=row[5].split(';') if row[5] else [],
                    min_sections=int(row[6]) if row[6].isdigit() else 3,
                    max_sections=int(row[7]) if row[7].isdigit() else 8
                )
                structures.append(structure)
        
        return structures
    
    def _parse_scoring_matrix(self, values: List[List[str]]) -> ScoringMatrix:
        """Parse scoring matrix from sheet data."""
        # This is a simplified version - in reality you'd parse detailed criteria
        return ScoringMatrix(
            voice_consistency=[],
            structure_quality=[],
            medical_accuracy=[],
            seo_technical=[]
        )
    
    def _parse_specific_fixes(self, values: List[List[str]]) -> List[Fix]:
        """Parse specific fixes from sheet data."""
        fixes = []
        if not values or len(values) < 2:
            return fixes
        
        for row in values[1:]:
            if len(row) >= 6:
                fix = Fix(
                    id=row[0],
                    issue_description=row[1],
                    fix_description=row[2],
                    pattern_type=PatternType(row[3].lower()),
                    priority=int(row[5]) if row[5].isdigit() else 1
                )
                fixes.append(fix)
        
        return fixes
    
    async def create_google_doc(self, article_markdown: str, title: str, status: str) -> Dict[str, str]:
        """
        Create a Google Doc from markdown content.
        
        Args:
            article_markdown: Article content in Markdown format
            title: Document title
            status: "PASS" or "FAIL" status
            
        Returns:
            Dictionary with doc_id and doc_url
        """
        try:
            # Convert markdown to HTML
            html_content = markdown.markdown(article_markdown)
            
            # Clean up HTML for Google Docs
            soup = BeautifulSoup(html_content, 'html.parser')
            clean_html = str(soup)
            
            # Create document title based on status
            doc_title = f"{title} - Blog Post {'✅' if status == 'PASS' else '⚠️ REVIEW'}"
            
            # Create blank document
            document = {
                'title': doc_title
            }
            
            doc = self.docs_service.documents().create(body=document).execute()
            doc_id = doc.get('documentId')
            
            # Insert content into document
            # Note: Google Docs API requires specific formatting - this is simplified
            requests = [
                {
                    'insertText': {
                        'location': {'index': 1},
                        'text': self._convert_markdown_to_text(article_markdown)
                    }
                }
            ]
            
            self.docs_service.documents().batchUpdate(
                documentId=doc_id,
                body={'requests': requests}
            ).execute()
            
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            logger.info(f"Created Google Doc: {doc_title}")
            return {
                'doc_id': doc_id,
                'doc_url': doc_url
            }
            
        except Exception as e:
            logger.error(f"Error creating Google Doc: {e}")
            raise
    
    def _convert_markdown_to_text(self, markdown_content: str) -> str:
        """Convert markdown to plain text for Google Docs."""
        # Simple conversion - remove markdown syntax
        import re
        
        # Remove headers
        text = re.sub(r'^#+\s*', '', markdown_content, flags=re.MULTILINE)
        
        # Remove bold/italic
        text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
        text = re.sub(r'\*(.*?)\*', r'\1', text)
        
        # Remove links
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        
        return text
    
    async def publish_article(
        self,
        doc_id: str,
        article_content: str,
        status: str,
        evaluation: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Publish article by moving to appropriate folder and logging.
        
        Args:
            doc_id: Google Doc ID
            article_content: Article content
            status: "PASS" or "FAIL"
            evaluation: Evaluation results
            
        Returns:
            Publication results
        """
        try:
            timestamp = datetime.now().isoformat()
            doc_url = f"https://docs.google.com/document/d/{doc_id}/edit"
            
            if status == "PASS":
                # Move to PUBLISHED folder
                self.drive_service.files().update(
                    fileId=doc_id,
                    addParents=self.published_folder_id,
                    fields='id, parents'
                ).execute()
                
                # Log to PUBLISHED sheet
                self._log_to_sheet('PUBLISHED', {
                    'doc_url': doc_url,
                    'quality_score': evaluation.get('total_score', 0),
                    'word_count': evaluation.get('word_count_actual', 0),
                    'timestamp': timestamp
                })
                
                result_status = "PUBLISHED"
                
            else:
                # Log to NEEDS_REVIEW sheet
                self._log_to_sheet('NEEDS_REVIEW', {
                    'doc_url': doc_url,
                    'quality_score': evaluation.get('total_score', 0),
                    'critical_issues': '; '.join(evaluation.get('critical_issues', [])),
                    'improvements_needed': '; '.join(evaluation.get('improvements_needed', [])),
                    'timestamp': timestamp
                })
                
                result_status = "NEEDS_REVIEW"
            
            logger.info(f"Article published with status: {result_status}")
            
            return {
                'google_doc_url': doc_url,
                'status': result_status,
                'quality_score': evaluation.get('total_score', 0),
                'completed_at': timestamp
            }
            
        except Exception as e:
            logger.error(f"Error publishing article: {e}")
            raise
    
    def _log_to_sheet(self, sheet_name: str, data: Dict[str, Any]):
        """Log data to a specific sheet."""
        try:
            # Prepare row data
            if sheet_name == 'PUBLISHED':
                row_data = [
                    data['doc_url'],
                    str(data['quality_score']),
                    str(data['word_count']),
                    data['timestamp']
                ]
            else:  # NEEDS_REVIEW
                row_data = [
                    data['doc_url'],
                    str(data['quality_score']),
                    data['critical_issues'],
                    data['improvements_needed'],
                    data['timestamp']
                ]
            
            # Append to sheet
            self.sheets_service.spreadsheets().values().append(
                spreadsheetId=self.sheets_id,
                range=f'{sheet_name}!A:Z',
                valueInputOption='RAW',
                body={'values': [row_data]}
            ).execute()
            
            logger.debug(f"Logged data to {sheet_name} sheet")
            
        except Exception as e:
            logger.error(f"Error logging to sheet {sheet_name}: {e}")
            # Don't raise - logging failure shouldn't stop the process
