"""
Scoring engine for quality evaluation of generated articles.
Implements the 4-category scoring system with critical violation detection.
"""

import logging
import re
from typing import Dict, Any
from typing import List  # Separate import for Railway compatibility
from ..models.evaluation import Evaluation, ScoreBreakdown

logger = logging.getLogger(__name__)


class ScoringEngine:
    """Engine for scoring article quality across multiple dimensions."""
    
    def __init__(self, scoring_matrix: Dict[str, Any]):
        """
        Initialize scoring engine with scoring criteria.
        
        Args:
            scoring_matrix: Scoring criteria and weights
        """
        self.scoring_matrix = scoring_matrix
        self.pass_threshold = 80
        self.word_count_fail_threshold = -15.0  # -15%
    
    def evaluate_article(
        self,
        article_content: str,
        target_word_count: int,
        topic: str,
        retry_count: int = 0
    ) -> Evaluation:
        """
        Comprehensive evaluation of article quality.
        
        Args:
            article_content: Complete article content
            target_word_count: Target word count
            topic: Article topic
            retry_count: Current retry attempt
            
        Returns:
            Complete evaluation with scores and recommendations
        """
        try:
            # Calculate actual word count
            actual_word_count = self._count_words(article_content)
            word_count_deviation = self._calculate_word_count_deviation(
                actual_word_count, target_word_count
            )
            
            # Evaluate each category
            voice_score = self._evaluate_voice_consistency(article_content)
            structure_score = self._evaluate_structure_quality(article_content)
            medical_score = self._evaluate_medical_accuracy(article_content)
            seo_score = self._evaluate_seo_technical(article_content, target_word_count)
            
            # Create score breakdown
            score_breakdown = ScoreBreakdown(
                voice_consistency=voice_score,
                structure_quality=structure_score,
                medical_accuracy=medical_score,
                seo_technical=seo_score
            )
            
            total_score = score_breakdown.calculate_total()
            
            # Detect critical issues
            critical_issues = self._detect_critical_issues(
                article_content, word_count_deviation
            )
            
            # Apply critical penalties
            total_score = self._apply_critical_penalties(total_score, critical_issues)
            
            # Generate improvement recommendations
            improvements_needed = self._generate_improvements(
                article_content, score_breakdown, critical_issues
            )
            
            # Create evaluation object
            evaluation = Evaluation(
                total_score=total_score,
                score_breakdown=score_breakdown,
                word_count_actual=actual_word_count,
                word_count_target=target_word_count,
                word_count_deviation_percent=word_count_deviation,
                critical_issues=critical_issues,
                improvements_needed=improvements_needed,
                passes_quality_gate=False,  # Will be calculated
                retry_count=retry_count
            )
            
            # Determine pass status
            evaluation.determine_pass_status(
                self.pass_threshold, self.word_count_fail_threshold
            )
            
            logger.info(f"Article evaluation completed: {total_score}/100")
            return evaluation
            
        except Exception as e:
            logger.error(f"Error evaluating article: {e}")
            raise
    
    def _count_words(self, content: str) -> int:
        """Count words in content, excluding markdown syntax."""
        # Remove markdown syntax
        text = re.sub(r'[#*_`\[\]()]', '', content)
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Split and count
        words = text.strip().split()
        return len(words)
    
    def _calculate_word_count_deviation(self, actual: int, target: int) -> float:
        """Calculate word count deviation percentage."""
        if target == 0:
            return 0.0
        return ((actual - target) / target) * 100
    
    def _evaluate_voice_consistency(self, content: str) -> int:
        """Evaluate voice consistency (0-25 points)."""
        score = 25  # Start with full points
        content_lower = content.lower()
        
        # Check for third person usage (Γ' ενικό) - 10 points
        third_person_indicators = [
            "ο δρ", "η θεραπεία", "η επέμβαση", "το πρόβλημα",
            "εφαρμόζει", "χρησιμοποιεί", "συνιστά", "περιλαμβάνει"
        ]
        third_person_count = sum(content_lower.count(indicator) for indicator in third_person_indicators)
        
        if third_person_count < 3:
            score -= 5  # Insufficient third person usage
        
        # Check for first person violations (Α' ενικό) - CRITICAL
        first_person_violations = [
            " εγώ ", " με ", " μου ", " μας ", "πιστεύω", "νομίζω",
            "συνιστώ", "προτείνω", "χρησιμοποιώ"
        ]
        first_person_count = sum(content_lower.count(violation) for violation in first_person_violations)
        
        if first_person_count > 0:
            score = max(0, score - 10)  # Major penalty for first person
        
        # Check for professional tone - 8 points
        professional_indicators = [
            "ιατρικός", "κλινικός", "θεραπευτικός", "χειρουργικός",
            "επιστημονικός", "αποτελεσματικός"
        ]
        professional_count = sum(content_lower.count(indicator) for indicator in professional_indicators)
        
        if professional_count < 2:
            score = max(0, score - 4)  # Insufficient professional tone
        
        # Check for credentials mentioned naturally once - 4 points
        credentials_mentions = content_lower.count("vcu medical center") + content_lower.count("leeds hospital")
        
        if credentials_mentions == 0:
            score = max(0, score - 4)  # No credentials mentioned
        elif credentials_mentions > 2:
            score = max(0, score - 2)  # Over-mentioned credentials
        
        # Check for absence of emotional stories - 3 points
        emotional_indicators = [
            "προσωπικές ιστορίες", "ιστορία ασθενούς", "συναισθήματα",
            "φόβος", "ανησυχία", "στενοχώρια"
        ]
        emotional_count = sum(content_lower.count(indicator) for indicator in emotional_indicators)
        
        if emotional_count > 0:
            score = max(0, score - 3)  # Penalty for emotional content
        
        return max(0, min(25, score))
    
    def _evaluate_structure_quality(self, content: str) -> int:
        """Evaluate structure quality (0-25 points)."""
        score = 25  # Start with full points
        
        # Extract sections
        sections = self._extract_sections(content)
        
        # Check for logical flow - 10 points
        expected_flow = ["ανατομία", "συμπτώματα", "διάγνωση", "θεραπεία", "αποκατάσταση"]
        flow_score = self._check_logical_flow(sections, expected_flow)
        score = max(0, score - (10 - flow_score))
        
        # Check for repetitions - 8 points
        repetition_penalty = self._check_repetitions(content)
        score = max(0, score - repetition_penalty)
        
        # Check paragraph length (2-3 sentences) - 4 points
        paragraph_penalty = self._check_paragraph_length(content)
        score = max(0, score - paragraph_penalty)
        
        # Check section transitions - 3 points
        transition_penalty = self._check_section_transitions(content)
        score = max(0, score - transition_penalty)
        
        return max(0, min(25, score))
    
    def _evaluate_medical_accuracy(self, content: str) -> int:
        """Evaluate medical accuracy (0-30 points)."""
        score = 30  # Start with full points
        content_lower = content.lower()
        
        # Check for success rate ranges (75-85%) - 10 points
        range_patterns = re.findall(r'\d{1,2}-\d{1,2}%', content)
        if len(range_patterns) < 1:
            score = max(0, score - 5)  # No ranges found
        
        # Check for absolute claims (should be avoided) - penalty
        absolute_patterns = re.findall(r'\d{1,2}% επιτυχία', content_lower)
        if len(absolute_patterns) > 0:
            score = max(0, score - 3)  # Penalty for absolute claims
        
        # Check for variability disclaimers - 8 points
        variability_indicators = [
            "μεταβλητότητα", "εξαρτάται", "διαφέρει", "ποικίλλει",
            "ατομικές διαφορές", "περίπτωση"
        ]
        variability_count = sum(content_lower.count(indicator) for indicator in variability_indicators)
        
        if variability_count < 2:
            score = max(0, score - 4)  # Insufficient variability mentions
        
        # Check for contradictions - 8 points
        contradiction_penalty = self._check_medical_contradictions(content)
        score = max(0, score - contradiction_penalty)
        
        # Check for Greek terms + plain explanations - 4 points
        explanation_penalty = self._check_medical_explanations(content)
        score = max(0, score - explanation_penalty)
        
        return max(0, min(30, score))
    
    def _evaluate_seo_technical(self, content: str, target_word_count: int) -> int:
        """Evaluate SEO and technical aspects (0-20 points)."""
        score = 20  # Start with full points
        
        # Check main keyword in H1 and first paragraph - 6 points
        h1_keyword_penalty = self._check_h1_keyword(content)
        first_para_keyword_penalty = self._check_first_paragraph_keyword(content)
        score = max(0, score - h1_keyword_penalty - first_para_keyword_penalty)
        
        # Check secondary keyword distribution - 4 points
        keyword_distribution_penalty = self._check_keyword_distribution(content)
        score = max(0, score - keyword_distribution_penalty)
        
        # Check markdown formatting - 4 points
        markdown_penalty = self._check_markdown_formatting(content)
        score = max(0, score - markdown_penalty)
        
        # Check word count accuracy - 6 points
        actual_words = self._count_words(content)
        word_count_penalty = self._calculate_word_count_penalty(actual_words, target_word_count)
        score = max(0, score - word_count_penalty)
        
        return max(0, min(20, score))
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section headers from content."""
        sections = []
        lines = content.split('\n')
        
        for line in lines:
            if line.startswith('##') and not line.startswith('###'):
                section_title = line.replace('##', '').strip().lower()
                sections.append(section_title)
        
        return sections
    
    def _check_logical_flow(self, sections: List[str], expected_flow: List[str]) -> int:
        """Check logical flow of sections (0-10 points)."""
        score = 10
        section_indices = {}
        
        # Find indices of expected sections
        for i, section in enumerate(sections):
            for j, expected in enumerate(expected_flow):
                if expected in section:
                    section_indices[expected] = i
                    break
        
        # Check order
        prev_index = -1
        for expected in expected_flow:
            if expected in section_indices:
                if section_indices[expected] < prev_index:
                    score -= 2  # Out of order penalty
                prev_index = section_indices[expected]
        
        return max(0, score)
    
    def _check_repetitions(self, content: str) -> int:
        """Check for repetitive content (0-8 penalty points)."""
        sentences = content.split('.')
        unique_sentences = set(sentence.strip().lower() for sentence in sentences if sentence.strip())
        
        repetition_ratio = 1 - (len(unique_sentences) / len(sentences)) if sentences else 0
        
        if repetition_ratio > 0.1:  # More than 10% repetition
            return min(8, int(repetition_ratio * 40))  # Scale penalty
        
        return 0
    
    def _check_paragraph_length(self, content: str) -> int:
        """Check paragraph length (2-3 sentences ideal) (0-4 penalty points)."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        penalty = 0
        
        for paragraph in paragraphs:
            sentences = paragraph.split('.')
            sentence_count = len([s for s in sentences if s.strip()])
            
            if sentence_count > 5:  # Too long
                penalty += 1
            elif sentence_count < 2:  # Too short
                penalty += 1
        
        return min(4, penalty)
    
    def _check_section_transitions(self, content: str) -> int:
        """Check quality of section transitions (0-3 penalty points)."""
        # Simple check for abrupt transitions
        sections = content.split('##')[1:]  # Skip content before first section
        penalty = 0
        
        for section in sections:
            if not section.strip().startswith('\n'):
                penalty += 1  # Abrupt transition
        
        return min(3, penalty)
    
    def _check_medical_contradictions(self, content: str) -> int:
        """Check for medical contradictions (0-8 penalty points)."""
        content_lower = content.lower()
        contradictions = [
            ("αυξάνει", "μειώνει"), ("υψηλός", "χαμηλός"), 
            ("αποτελεσματικός", "αναποτελεσματικός"),
            ("ασφαλής", "επικίνδυνος"), ("συνιστάται", "δεν συνιστάται")
        ]
        
        penalty = 0
        for positive, negative in contradictions:
            if positive in content_lower and negative in content_lower:
                penalty += 2
        
        return min(8, penalty)
    
    def _check_medical_explanations(self, content: str) -> int:
        """Check for proper medical term explanations (0-4 penalty points)."""
        # Look for medical terms with explanations in parentheses
        medical_terms = ["χόνδρος", "σύνδεσμος", "μηνίσκος", "αρθρίτιδα"]
        explained_terms = 0
        
        for term in medical_terms:
            if term in content.lower():
                # Look for explanation pattern: term (explanation)
                pattern = f"{term}.*?\\([^)]+\\)"
                if re.search(pattern, content.lower()):
                    explained_terms += 1
        
        total_medical_terms = sum(1 for term in medical_terms if term in content.lower())
        
        if total_medical_terms > 0:
            explanation_ratio = explained_terms / total_medical_terms
            if explanation_ratio < 0.5:  # Less than 50% explained
                return min(4, int((0.5 - explanation_ratio) * 8))
        
        return 0
    
    def _check_h1_keyword(self, content: str) -> int:
        """Check if main keyword is in H1 (0-3 penalty points)."""
        lines = content.split('\n')
        h1_line = next((line for line in lines if line.startswith('#') and not line.startswith('##')), '')
        
        # This is simplified - in reality, you'd check against the actual main keyword
        if not h1_line or len(h1_line.strip()) < 10:
            return 3
        
        return 0
    
    def _check_first_paragraph_keyword(self, content: str) -> int:
        """Check if main keyword is in first paragraph (0-3 penalty points)."""
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        if not paragraphs or len(paragraphs[0]) < 50:
            return 3
        
        # This is simplified - would check for actual keyword presence
        return 0
    
    def _check_keyword_distribution(self, content: str) -> int:
        """Check keyword distribution throughout content (0-4 penalty points)."""
        # Simplified check for even distribution
        sections = content.split('##')[1:]  # Skip intro
        
        if len(sections) < 3:
            return 2  # Too few sections for good distribution
        
        return 0
    
    def _check_markdown_formatting(self, content: str) -> int:
        """Check markdown formatting quality (0-4 penalty points)."""
        penalty = 0
        
        # Check for proper headers
        if not re.search(r'^#[^#]', content, re.MULTILINE):
            penalty += 1  # No H1
        
        if not re.search(r'^##[^#]', content, re.MULTILINE):
            penalty += 1  # No H2s
        
        # Check for bold text
        if not re.search(r'\*\*[^*]+\*\*', content):
            penalty += 1  # No bold text
        
        # Check for lists
        if not re.search(r'^[-*+]\s', content, re.MULTILINE):
            penalty += 1  # No lists
        
        return penalty
    
    def _calculate_word_count_penalty(self, actual: int, target: int) -> int:
        """Calculate word count penalty (0-6 points)."""
        if target == 0:
            return 0
        
        deviation = abs(actual - target) / target
        
        if deviation <= 0.05:  # Within 5%
            return 0
        elif deviation <= 0.10:  # Within 10%
            return 1
        elif deviation <= 0.15:  # Within 15%
            return 2
        elif deviation <= 0.20:  # Within 20%
            return 4
        else:  # More than 20% off
            return 6
    
    def _detect_critical_issues(self, content: str, word_count_deviation: float) -> List[str]:
        """Detect critical issues that warrant penalties or automatic failure."""
        issues = []
        content_lower = content.lower()
        
        # First person usage (Α' ενικό) - CRITICAL
        first_person_violations = [
            " εγώ ", " με ", " μου ", " μας ", "πιστεύω", "νομίζω",
            "συνιστώ", "προτείνω", "χρησιμοποιώ"
        ]
        if any(violation in content_lower for violation in first_person_violations):
            issues.append("Α' ενικό usage detected (forbidden voice)")
        
        # Emotional stories - CRITICAL
        emotional_indicators = [
            "προσωπικές ιστορίες", "ιστορία ασθενούς", "συναισθήματα"
        ]
        if any(indicator in content_lower for indicator in emotional_indicators):
            issues.append("Emotional stories detected (forbidden pattern)")
        
        # Missing variability disclaimers - CRITICAL
        variability_indicators = [
            "μεταβλητότητα", "εξαρτάται", "διαφέρει", "ποικίλλει"
        ]
        if not any(indicator in content_lower for indicator in variability_indicators):
            issues.append("Missing variability disclaimers")
        
        # Word count below -15% - AUTOMATIC FAIL
        if word_count_deviation < -15.0:
            issues.append(f"Word count critically low ({word_count_deviation:.1f}% below target)")
        
        return issues
    
    def _apply_critical_penalties(self, score: int, critical_issues: List[str]) -> int:
        """Apply penalties for critical issues."""
        for issue in critical_issues:
            if "Α' ενικό" in issue:
                score -= 10
            elif "Emotional stories" in issue:
                score -= 8
            elif "variability disclaimers" in issue:
                score -= 8
        
        return max(0, score)
    
    def _generate_improvements(
        self,
        content: str,
        score_breakdown: ScoreBreakdown,
        critical_issues: List[str]
    ) -> List[str]:
        """Generate specific improvement recommendations."""
        improvements = []
        
        # Voice improvements
        if score_breakdown.voice_consistency < 20:
            improvements.append("Ensure consistent use of Γ' ενικό (third person) throughout")
            improvements.append("Remove any first person references (εγώ, μου, etc.)")
        
        # Structure improvements
        if score_breakdown.structure_quality < 20:
            improvements.append("Improve logical flow: Ανατομία → Συμπτώματα → Θεραπεία")
            improvements.append("Keep paragraphs to 2-3 sentences for better readability")
        
        # Medical improvements
        if score_breakdown.medical_accuracy < 24:
            improvements.append("Use success rate ranges (75-85%) instead of exact percentages")
            improvements.append("Add more variability disclaimers and individual differences")
        
        # SEO improvements
        if score_breakdown.seo_technical < 16:
            improvements.append("Ensure main keyword appears in H1 and first paragraph")
            improvements.append("Improve markdown formatting with proper headers and bold text")
        
        # Critical issue improvements
        for issue in critical_issues:
            if "Word count" in issue:
                improvements.append("Significantly expand content to meet minimum word count requirements")
        
        return improvements
