"""
Content validation utilities for pattern checking and quality assurance.
"""

import logging
import re
from typing import List, Dict, Any
from ..models.patterns import Pattern, AntiPattern, ValidationResult

logger = logging.getLogger(__name__)


class ContentValidator:
    """Validates content against approved patterns and anti-patterns."""
    
    def __init__(self, patterns: List[Pattern], anti_patterns: List[AntiPattern]):
        """
        Initialize validator with patterns.
        
        Args:
            patterns: List of approved patterns
            anti_patterns: List of forbidden patterns
        """
        self.patterns = patterns
        self.anti_patterns = anti_patterns
    
    def validate_content(self, content: str) -> ValidationResult:
        """
        Validate content against all patterns.
        
        Args:
            content: Content to validate
            
        Returns:
            Validation results with scores and recommendations
        """
        try:
            # Check approved patterns
            matched_patterns = self._check_approved_patterns(content)
            
            # Check anti-patterns (violations)
            violated_antipatterns = self._check_anti_patterns(content)
            
            # Calculate validation score
            validation_score = self._calculate_validation_score(
                matched_patterns, violated_antipatterns
            )
            
            # Generate suggested fixes
            suggested_fixes = self._suggest_fixes(violated_antipatterns)
            
            # Determine if content is valid
            is_valid = validation_score >= 70 and len(violated_antipatterns) == 0
            
            # Generate detailed feedback
            detailed_feedback = self._generate_detailed_feedback(
                content, matched_patterns, violated_antipatterns
            )
            
            return ValidationResult(
                is_valid=is_valid,
                matched_patterns=[p.id for p in matched_patterns],
                violated_antipatterns=[p.id for p in violated_antipatterns],
                suggested_fixes=suggested_fixes,
                validation_score=validation_score,
                detailed_feedback=detailed_feedback
            )
            
        except Exception as e:
            logger.error(f"Error validating content: {e}")
            raise
    
    def _check_approved_patterns(self, content: str) -> List[Pattern]:
        """Check which approved patterns are matched in the content."""
        matched_patterns = []
        
        for pattern in self.patterns:
            if self._pattern_matches(content, pattern):
                matched_patterns.append(pattern)
        
        return matched_patterns
    
    def _check_anti_patterns(self, content: str) -> List[AntiPattern]:
        """Check which anti-patterns are violated in the content."""
        violated_patterns = []
        
        for anti_pattern in self.anti_patterns:
            if self._anti_pattern_matches(content, anti_pattern):
                violated_patterns.append(anti_pattern)
        
        return violated_patterns
    
    def _pattern_matches(self, content: str, pattern: Pattern) -> bool:
        """Check if a pattern matches the content."""
        content_lower = content.lower()
        
        # Check examples for pattern matching
        for example in pattern.examples:
            if example.lower() in content_lower:
                return True
        
        # Pattern-specific matching logic
        if pattern.pattern_type.value == "voice":
            return self._check_voice_pattern(content, pattern)
        elif pattern.pattern_type.value == "structure":
            return self._check_structure_pattern(content, pattern)
        elif pattern.pattern_type.value == "medical":
            return self._check_medical_pattern(content, pattern)
        elif pattern.pattern_type.value == "seo":
            return self._check_seo_pattern(content, pattern)
        
        return False
    
    def _anti_pattern_matches(self, content: str, anti_pattern: AntiPattern) -> bool:
        """Check if an anti-pattern is violated in the content."""
        content_lower = content.lower()
        
        # Check examples for anti-pattern violations
        for example in anti_pattern.examples:
            if example.lower() in content_lower:
                return True
        
        # Anti-pattern specific checking
        if anti_pattern.pattern_type.value == "voice":
            return self._check_voice_violation(content, anti_pattern)
        elif anti_pattern.pattern_type.value == "structure":
            return self._check_structure_violation(content, anti_pattern)
        elif anti_pattern.pattern_type.value == "medical":
            return self._check_medical_violation(content, anti_pattern)
        
        return False
    
    def _check_voice_pattern(self, content: str, pattern: Pattern) -> bool:
        """Check voice-related patterns."""
        # Check for third person usage (Γ' ενικό)
        if "third_person" in pattern.name.lower():
            # Look for third person indicators in Greek
            third_person_indicators = [
                "ο δρ", "η θεραπεία", "η επέμβαση", "το πρόβλημα",
                "εφαρμόζει", "χρησιμοποιεί", "συνιστά"
            ]
            return any(indicator in content.lower() for indicator in third_person_indicators)
        
        return False
    
    def _check_voice_violation(self, content: str, anti_pattern: AntiPattern) -> bool:
        """Check for voice violations."""
        # Check for first person usage (Α' ενικό) - forbidden
        if "first_person" in anti_pattern.name.lower():
            first_person_indicators = [
                " εγώ ", " με ", " μου ", " μας ", "πιστεύω", "νομίζω",
                "συνιστώ", "προτείνω", "χρησιμοποιώ"
            ]
            return any(indicator in content.lower() for indicator in first_person_indicators)
        
        return False
    
    def _check_structure_pattern(self, content: str, pattern: Pattern) -> bool:
        """Check structure-related patterns."""
        # Check for logical flow
        if "logical_flow" in pattern.name.lower():
            sections = self._extract_sections(content)
            expected_order = ["ανατομία", "συμπτώματα", "διάγνωση", "θεραπεία"]
            return self._check_section_order(sections, expected_order)
        
        return False
    
    def _check_structure_violation(self, content: str, anti_pattern: AntiPattern) -> bool:
        """Check for structure violations."""
        # Check for emotional stories
        if "emotional" in anti_pattern.name.lower():
            emotional_indicators = [
                "προσωπικές ιστορίες", "ιστορία ασθενούς", "συναισθήματα",
                "φόβος", "ανησυχία", "στενοχώρια"
            ]
            return any(indicator in content.lower() for indicator in emotional_indicators)
        
        return False
    
    def _check_medical_pattern(self, content: str, pattern: Pattern) -> bool:
        """Check medical accuracy patterns."""
        # Check for success rate ranges
        if "success_rate" in pattern.name.lower():
            range_pattern = r'\d{1,2}-\d{1,2}%'
            return bool(re.search(range_pattern, content))
        
        return False
    
    def _check_medical_violation(self, content: str, anti_pattern: AntiPattern) -> bool:
        """Check for medical violations."""
        # Check for absolute claims without ranges
        if "absolute_claims" in anti_pattern.name.lower():
            absolute_patterns = [
                r'\d{1,2}% επιτυχία', r'πάντα επιτυχής', r'ποτέ αποτυγχάνει'
            ]
            return any(re.search(pattern, content.lower()) for pattern in absolute_patterns)
        
        return False
    
    def _check_seo_pattern(self, content: str, pattern: Pattern) -> bool:
        """Check SEO-related patterns."""
        # This would check for proper keyword placement, etc.
        return False
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content."""
        sections = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('##'):
                section_title = line.replace('##', '').strip().lower()
                sections.append(section_title)
        
        return sections
    
    def _check_section_order(self, sections: List[str], expected_order: List[str]) -> bool:
        """Check if sections follow expected order."""
        section_indices = {}
        
        for i, section in enumerate(sections):
            for j, expected in enumerate(expected_order):
                if expected in section:
                    section_indices[expected] = i
                    break
        
        # Check if found sections are in order
        prev_index = -1
        for expected in expected_order:
            if expected in section_indices:
                if section_indices[expected] < prev_index:
                    return False
                prev_index = section_indices[expected]
        
        return True
    
    def _calculate_validation_score(
        self, 
        matched_patterns: List[Pattern], 
        violated_patterns: List[AntiPattern]
    ) -> int:
        """Calculate overall validation score."""
        # Base score from matched patterns
        pattern_score = sum(p.weight * 10 for p in matched_patterns)
        
        # Penalty from violations
        penalty = sum(p.penalty_points for p in violated_patterns)
        
        # Final score (0-100)
        final_score = max(0, min(100, pattern_score - penalty))
        
        return final_score
    
    def _suggest_fixes(self, violated_patterns: List[AntiPattern]) -> List[str]:
        """Generate suggested fixes for violations."""
        fixes = []
        
        for violation in violated_patterns:
            if violation.pattern_type.value == "voice":
                fixes.append("voice_fix_third_person")
            elif violation.pattern_type.value == "structure":
                fixes.append("structure_fix_logical_flow")
            elif violation.pattern_type.value == "medical":
                fixes.append("medical_fix_ranges")
        
        return list(set(fixes))  # Remove duplicates
    
    def _generate_detailed_feedback(
        self,
        content: str,
        matched_patterns: List[Pattern],
        violated_patterns: List[AntiPattern]
    ) -> Dict[str, Any]:
        """Generate detailed feedback for the validation."""
        return {
            "content_length": len(content),
            "sections_found": len(self._extract_sections(content)),
            "matched_pattern_count": len(matched_patterns),
            "violation_count": len(violated_patterns),
            "voice_analysis": self._analyze_voice(content),
            "structure_analysis": self._analyze_structure(content),
            "medical_analysis": self._analyze_medical_content(content)
        }
    
    def _analyze_voice(self, content: str) -> Dict[str, Any]:
        """Analyze voice consistency in content."""
        first_person_count = len(re.findall(r'\b(εγώ|με|μου|μας)\b', content.lower()))
        third_person_count = len(re.findall(r'\b(ο δρ|η θεραπεία|εφαρμόζει)\b', content.lower()))
        
        return {
            "first_person_usage": first_person_count,
            "third_person_usage": third_person_count,
            "voice_consistency": third_person_count > first_person_count
        }
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze structure quality."""
        sections = self._extract_sections(content)
        paragraphs = content.split('\n\n')
        
        return {
            "section_count": len(sections),
            "paragraph_count": len(paragraphs),
            "average_paragraph_length": sum(len(p.split()) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        }
    
    def _analyze_medical_content(self, content: str) -> Dict[str, Any]:
        """Analyze medical content quality."""
        success_rates = re.findall(r'\d{1,2}-\d{1,2}%', content)
        absolute_claims = re.findall(r'\d{1,2}% επιτυχία', content.lower())
        
        return {
            "success_rate_ranges": len(success_rates),
            "absolute_claims": len(absolute_claims),
            "medical_terms": self._count_medical_terms(content)
        }
    
    def _count_medical_terms(self, content: str) -> int:
        """Count medical terms in content."""
        medical_terms = [
            "χόνδρος", "σύνδεσμος", "μηνίσκος", "αρθρίτιδα", "επέμβαση",
            "θεραπεία", "αποκατάσταση", "φυσιοθεραπεία", "χειρουργική"
        ]
        
        count = 0
        content_lower = content.lower()
        for term in medical_terms:
            count += content_lower.count(term)
        
        return count
