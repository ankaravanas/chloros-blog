"""
Content-related data models for article generation and strategy.
"""

from typing import Optional, Dict, Any
from typing import List  # Separate import for Railway compatibility
from pydantic import BaseModel, Field


class Section(BaseModel):
    """Represents a section of the article."""
    title: str = Field(..., description="Section title (H2 or H3)")
    content_points: List[str] = Field(..., description="Key points to cover in this section")
    target_words: Optional[int] = Field(None, description="Target word count for this section")
    medical_focus: Optional[List[str]] = Field(None, description="Medical concepts to emphasize")


class SEOStrategy(BaseModel):
    """SEO keyword placement and distribution strategy."""
    main_keyword_placement: List[str] = Field(..., description="Where to place the main keyword")
    secondary_distribution: List[str] = Field(..., description="How to distribute secondary keywords")
    target_density: Optional[float] = Field(None, description="Target keyword density percentage")


class ContentRestrictions(BaseModel):
    """Content restrictions and alternatives."""
    avoid: List[str] = Field(..., description="Terms and patterns to avoid")
    alternatives: List[str] = Field(..., description="Alternative phrasings to use instead")
    voice_requirements: List[str] = Field(..., description="Voice and tone requirements")


class ContentStrategy(BaseModel):
    """Complete content strategy for article generation."""
    h1_title: str = Field(..., description="Main H1 title with primary keyword")
    content_sections: List[Section] = Field(..., description="Planned article sections")
    seo_strategy: SEOStrategy = Field(..., description="SEO keyword strategy")
    content_restrictions: ContentRestrictions = Field(..., description="Content restrictions")
    medical_focus: List[str] = Field(..., description="Primary medical concepts to emphasize")
    target_word_count: int = Field(..., description="Target word count for the complete article")
    cultural_context: Optional[str] = Field(None, description="Greek cultural context to incorporate")


class Article(BaseModel):
    """Generated article with metadata."""
    article_markdown: str = Field(..., description="Complete article in Markdown format")
    word_count: int = Field(..., description="Actual word count of the generated article")
    sections_generated: List[str] = Field(..., description="List of section titles that were generated")
    h1_title: str = Field(..., description="The H1 title used")
    generation_metadata: Optional[Dict[str, Any]] = Field(None, description="Additional generation metadata")
    
    def calculate_word_count(self) -> int:
        """Calculate word count from markdown content."""
        # Remove markdown syntax and count words
        import re
        text = re.sub(r'[#*_`\[\]()]', '', self.article_markdown)
        words = text.split()
        self.word_count = len(words)
        return self.word_count
