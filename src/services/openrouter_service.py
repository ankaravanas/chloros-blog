"""
OpenRouter service for content generation and evaluation.
Handles article generation and quality evaluation using advanced models.
"""

import logging
import httpx
from typing import Dict, Any, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

from ..config import settings
from ..models.content import ContentStrategy, Article
from ..models.evaluation import Evaluation

logger = logging.getLogger(__name__)


class OpenRouterService:
    """Service for interacting with OpenRouter API."""
    
    def __init__(self):
        """Initialize OpenRouter service."""
        self.base_url = "https://openrouter.ai/api/v1"
        self.model = settings.openrouter_model
        self.headers = {
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://chloros.gr",
            "X-Title": "Chloros Blog MCP Server"
        }
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def generate_complete_article(
        self,
        strategy: ContentStrategy,
        medical_facts: str,
        cultural_context: str,
        patterns: Dict[str, Any],
        retry_count: int = 0,
        previous_evaluation: Optional[Evaluation] = None
    ) -> Article:
        """
        Generate a complete article using the content strategy.
        
        Args:
            strategy: Content strategy with sections and requirements
            medical_facts: Medical research from Pinecone
            cultural_context: Cultural context from Perplexity
            patterns: Approved patterns and restrictions from Google Sheets
            retry_count: Current retry attempt number
            previous_evaluation: Previous evaluation if this is a retry
            
        Returns:
            Complete generated article
        """
        try:
            system_prompt = self._get_generation_system_prompt(patterns)
            user_prompt = self._build_generation_user_prompt(
                strategy, medical_facts, cultural_context, retry_count, previous_evaluation
            )
            
            async with httpx.AsyncClient(timeout=300.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.4,
                        "max_tokens": 30000,
                        "stream": False
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                
                # Create Article object
                article = Article(
                    article_markdown=content,
                    word_count=0,  # Will be calculated
                    sections_generated=self._extract_sections(content),
                    h1_title=strategy.h1_title,
                    generation_metadata={
                        "model": self.model,
                        "retry_count": retry_count,
                        "strategy_sections": len(strategy.content_sections)
                    }
                )
                
                # Calculate word count
                article.calculate_word_count()
                
                logger.info(f"Generated article with {article.word_count} words")
                return article
                
        except httpx.TimeoutException:
            logger.error("Timeout during article generation")
            raise
        except Exception as e:
            logger.error(f"Error generating article: {e}")
            raise
    
    def _get_generation_system_prompt(self, patterns: Dict[str, Any]) -> str:
        """Get the comprehensive system prompt for article generation."""
        return f"""
        Είσαι ειδικός συγγραφέας ιατρικών άρθρων για ορθοπαιδικό χειρουργό στην Ελλάδα.
        Ο στόχος σου είναι να δημιουργήσεις άρθρα υψηλής ποιότητας που:
        
        ΦΩΝΗ & ΣΤΥΛ (25 πόντοι):
        ✅ Χρησιμοποιούν ΜΟΝΟ Γ' ενικό πρόσωπο ("Ο Δρ. Χλωρός εφαρμόζει", "Η θεραπεία περιλαμβάνει")
        ✅ Αναφέρουν τα διαπιστευτήρια ΜΙΑ ΦΟΡΑ στην εισαγωγή ("VCU Medical Center USA, Leeds Hospital UK")
        ✅ Διατηρούν επαγγελματικό, εκπαιδευτικό τόνο χωρίς συναισθηματικές ιστορίες
        ✅ Αποφεύγουν διδακτικό ύφος και προωθητικές φράσεις
        
        ΔΟΜΗ & ΟΡΓΑΝΩΣΗ (25 πόντοι):
        ✅ Ακολουθούν λογική ροή: Ανατομία → Συμπτώματα → Διάγνωση → Θεραπεία → Αποκατάσταση
        ✅ Παράγραφοι 2-3 προτάσεων για εύκολη ανάγνωση
        ✅ Καθαρές μεταβάσεις μεταξύ ενοτήτων
        ✅ Χωρίς επαναλήψεις ή περιττό περιεχόμενο
        
        ΙΑΤΡΙΚΗ ΑΚΡΙΒΕΙΑ (30 πόντοι):
        ✅ Ποσοστά επιτυχίας ως ΠΕΡΙΟΧΕΣ ("75-85%" όχι "80%")
        ✅ Αναφορές στη μεταβλητότητα αποτελεσμάτων
        ✅ Ελληνικοί όροι + απλές εξηγήσεις ("χόνδρος (το προστατευτικό στρώμα)")
        ✅ Καμία αντίφαση με τα ιατρικά δεδομένα
        
        SEO & ΤΕΧΝΙΚΑ (20 πόντοι):
        ✅ Κύρια λέξη-κλειδί στον H1 και πρώτη παράγραφο
        ✅ Δευτερεύουσες λέξεις-κλειδιά κατανεμημένες φυσικά
        ✅ Σωστή μορφοποίηση Markdown (# H1, ## H2, ### H3, **έμφαση**, λίστες)
        ✅ Ακρίβεια αριθμού λέξεων
        
        ΑΠΑΓΟΡΕΥΜΕΝΑ ΜΟΤΙΒΑ:
        ❌ Α' ενικό πρόσωπο (-10 πόντοι)
        ❌ Συναισθηματικές ιστορίες ασθενών (-8 πόντοι)
        ❌ Ενότητα "Προσωπικές Ιστορίες" (-8 πόντοι)
        ❌ Έλλειψη αναφορών μεταβλητότητας (-8 πόντοι)
        ❌ Αριθμός λέξεων <85% του στόχου (ΑΥΤΟΜΑΤΗ ΑΠΟΤΥΧΙΑ)
        
        ΥΠΟΓΡΑΦΗ (υποχρεωτική στο τέλος):
        
        ---
        
        **Δρ. Γεώργιος Χλωρός**  
        Χειρουργός Ορθοπαιδικός  
        Χειρουργική Ισχίου-Γόνατος-Ποδιού  
        Αναγεννητικές-Ορθοβιολογικές Θεραπείες
        
        Δημιούργησε ΠΛΗΡΕΣ άρθρο σε μία απάντηση, όχι τμήματα.
        """
    
    def _build_generation_user_prompt(
        self,
        strategy: ContentStrategy,
        medical_facts: str,
        cultural_context: str,
        retry_count: int,
        previous_evaluation: Optional[Evaluation]
    ) -> str:
        """Build the user prompt for article generation."""
        base_prompt = f"""
        Δημιούργησε πλήρες άρθρο blog βάσει της παρακάτω στρατηγικής:
        
        ΣΤΡΑΤΗΓΙΚΗ ΠΕΡΙΕΧΟΜΕΝΟΥ:
        Τίτλος H1: {strategy.h1_title}
        Στόχος λέξεων: {strategy.target_word_count}
        
        ΕΝΟΤΗΤΕΣ:
        """
        
        # Add sections
        for i, section in enumerate(strategy.content_sections, 1):
            base_prompt += f"""
        {i}. {section.title} (~{section.target_words} λέξεις)
           Σημεία: {', '.join(section.content_points)}
           Ιατρική εστίαση: {', '.join(section.medical_focus or [])}
        """
        
        # Add medical facts
        base_prompt += f"""
        
        ΙΑΤΡΙΚΑ ΔΕΔΟΜΕΝΑ (χρησιμοποίησε για ακρίβεια):
        {medical_facts[:2000]}
        
        ΠΟΛΙΤΙΣΜΙΚΟ ΠΛΑΙΣΙΟ:
        {cultural_context[:800]}
        
        SEO ΣΤΡΑΤΗΓΙΚΗ:
        - Κύρια λέξη-κλειδί: {', '.join(strategy.seo_strategy.main_keyword_placement)}
        - Δευτερεύουσες: {', '.join(strategy.seo_strategy.secondary_distribution)}
        
        ΠΕΡΙΟΡΙΣΤΙΚΕΣ ΟΔΗΓΙΕΣ:
        - Αποφεύγεις: {', '.join(strategy.content_restrictions.avoid)}
        - Εναλλακτικές: {', '.join(strategy.content_restrictions.alternatives)}
        - Φωνή: {', '.join(strategy.content_restrictions.voice_requirements)}
        """
        
        # Add retry feedback if applicable
        if retry_count > 0 and previous_evaluation:
            base_prompt += f"""
        
        ΠΡΟΣΟΧΗ - ΑΥΤΗ ΕΙΝΑΙ ΠΡΟΣΠΑΘΕΙΑ #{retry_count + 1}:
        Προηγούμενο σκορ: {previous_evaluation.total_score}/100
        Κρίσιμα προβλήματα: {', '.join(previous_evaluation.critical_issues)}
        Βελτιώσεις που χρειάζονται: {', '.join(previous_evaluation.improvements_needed)}
        
        ΔΙΟΡΘΩΣΕ ΤΑ ΠΑΡΑΠΑΝΩ ΠΡΟΒΛΗΜΑΤΑ!
        """
        
        base_prompt += """
        
        ΟΔΗΓΙΕΣ ΠΑΡΑΓΩΓΗΣ:
        1. Γράψε το ΠΛΗΡΕΣ άρθρο σε μία απάντηση
        2. Χρησιμοποίησε σωστή μορφοποίηση Markdown
        3. Διασφάλισε ότι ο αριθμός λέξεων είναι εντός ±15% του στόχου
        4. Κάθε παράγραφος 2-3 προτάσεις
        5. Συμπεριέλαβε την υπογραφή στο τέλος
        6. Γ' ενικό πρόσωπο σε όλο το άρθρο
        
        ΑΡΧΙΣΕ ΤΟ ΑΡΘΡΟ ΤΩΡΑ:
        """
        
        return base_prompt
    
    def _extract_sections(self, content: str) -> List[str]:
        """Extract section titles from the generated content."""
        sections = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('##') and not line.startswith('###'):
                # Extract H2 headers
                section_title = line.replace('##', '').strip()
                sections.append(section_title)
        
        return sections
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def evaluate_article_quality(
        self,
        complete_article: str,
        topic: str,
        word_count_target: int,
        patterns: Dict[str, Any],
        scoring_matrix: Dict[str, Any]
    ) -> Evaluation:
        """
        Evaluate article quality using the scoring matrix.
        
        Args:
            complete_article: The complete article to evaluate
            topic: Article topic
            word_count_target: Target word count
            patterns: Pattern validation data
            scoring_matrix: Scoring criteria
            
        Returns:
            Comprehensive evaluation results
        """
        try:
            system_prompt = self._get_evaluation_system_prompt(scoring_matrix)
            user_prompt = self._build_evaluation_user_prompt(
                complete_article, topic, word_count_target
            )
            
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers=self.headers,
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt}
                        ],
                        "temperature": 0.1,  # Very deterministic for evaluation
                        "max_tokens": 3000,
                        "response_format": {"type": "json_object"}
                    }
                )
                response.raise_for_status()
                
                result = response.json()
                evaluation_data = eval(result["choices"][0]["message"]["content"])
                
                # Parse into Evaluation object
                evaluation = self._parse_evaluation_response(evaluation_data, word_count_target)
                
                logger.info(f"Evaluated article: {evaluation.total_score}/100")
                return evaluation
                
        except Exception as e:
            logger.error(f"Error evaluating article quality: {e}")
            raise
    
    def _get_evaluation_system_prompt(self, scoring_matrix: Dict[str, Any]) -> str:
        """Get the system prompt for article evaluation."""
        return f"""
        Είσαι αξιολογητής ποιότητας για ιατρικά άρθρα ορθοπαιδικής στα ελληνικά.
        Αξιολογείς άρθρα βάσει αυστηρών κριτηρίων με σκάλα 0-100 πόντων.
        
        ΚΡΙΤΗΡΙΑ ΑΞΙΟΛΟΓΗΣΗΣ:
        
        1. ΣΥΝΕΠΕΙΑ ΦΩΝΗΣ (25 πόντοι):
        - Γ' ενικό σε όλο το άρθρο: 10 πόντοι
        - Επαγγελματικός τόνος: 8 πόντοι  
        - Διαπιστευτήρια αναφέρονται φυσικά μία φορά: 4 πόντοι
        - Καμία συναισθηματική ιστορία: 3 πόντοι
        
        2. ΠΟΙΟΤΗΤΑ ΔΟΜΗΣ (25 πόντοι):
        - Λογική ροή (Ανατομία→Συμπτώματα→Θεραπεία): 10 πόντοι
        - Χωρίς επαναλήψεις: 8 πόντοι
        - Παράγραφοι 2-3 προτάσεων: 4 πόντοι
        - Καθαρές μεταβάσεις ενοτήτων: 3 πόντοι
        
        3. ΙΑΤΡΙΚΗ ΑΚΡΙΒΕΙΑ (30 πόντοι):
        - Ποσοστά επιτυχίας ως περιοχές (75-85%): 10 πόντοι
        - Αναφορές μεταβλητότητας: 8 πόντοι
        - Καμία αντίφαση: 8 πόντοι
        - Ελληνικοί όροι + απλές εξηγήσεις: 4 πόντοι
        
        4. SEO & ΤΕΧΝΙΚΑ (20 πόντοι):
        - Κύρια λέξη-κλειδί σε H1 και πρώτη παράγραφο: 6 πόντοι
        - Δευτερεύουσες λέξεις κατανεμημένες φυσικά: 4 πόντοι
        - Σωστή μορφοποίηση Markdown: 4 πόντοι
        - Ακρίβεια αριθμού λέξεων: 6 πόντοι
        
        ΚΡΙΣΙΜΕΣ ΠΑΡΑΒΙΑΣΕΙΣ:
        - Α' ενικό: -10 πόντοι
        - Συναισθηματικές ιστορίες: -8 πόντοι
        - Έλλειψη αναφορών μεταβλητότητας: -8 πόντοι
        - Αριθμός λέξεων <85% στόχου: ΑΥΤΟΜΑΤΗ ΑΠΟΤΥΧΙΑ
        
        Απάντησε με JSON που περιλαμβάνει όλες τις βαθμολογίες και λεπτομερή ανάλυση.
        """
    
    def _build_evaluation_user_prompt(self, article: str, topic: str, target_words: int) -> str:
        """Build the user prompt for evaluation."""
        return f"""
        Αξιολόγησε το παρακάτω άρθρο για το θέμα "{topic}":
        
        ΣΤΟΧΟΣ ΛΕΞΕΩΝ: {target_words}
        
        ΑΡΘΡΟ:
        {article}
        
        Δώσε JSON απάντηση με την εξής δομή:
        {{
            "voice_consistency": <πόντοι 0-25>,
            "structure_quality": <πόντοι 0-25>,
            "medical_accuracy": <πόντοι 0-30>,
            "seo_technical": <πόντοι 0-20>,
            "total_score": <συνολικοί πόντοι>,
            "word_count_actual": <πραγματικός αριθμός λέξεων>,
            "critical_issues": [<λίστα κρίσιμων προβλημάτων>],
            "improvements_needed": [<λίστα βελτιώσεων>],
            "detailed_analysis": {{
                "voice_issues": [<προβλήματα φωνής>],
                "structure_issues": [<προβλήματα δομής>],
                "medical_issues": [<ιατρικά προβλήματα>],
                "seo_issues": [<SEO προβλήματα>]
            }}
        }}
        
        Να είσαι αυστηρός στην αξιολόγηση - μόνο άρθρα υψηλής ποιότητας πρέπει να περνούν.
        """
    
    def _parse_evaluation_response(self, data: Dict[str, Any], target_words: int) -> Evaluation:
        """Parse evaluation response into Evaluation object."""
        from ..models.evaluation import ScoreBreakdown
        
        # Calculate word count and deviation
        actual_words = data.get("word_count_actual", 0)
        deviation = ((actual_words - target_words) / target_words) * 100 if target_words > 0 else 0
        
        # Create score breakdown
        score_breakdown = ScoreBreakdown(
            voice_consistency=data.get("voice_consistency", 0),
            structure_quality=data.get("structure_quality", 0),
            medical_accuracy=data.get("medical_accuracy", 0),
            seo_technical=data.get("seo_technical", 0)
        )
        
        # Create evaluation
        evaluation = Evaluation(
            total_score=data.get("total_score", score_breakdown.calculate_total()),
            score_breakdown=score_breakdown,
            word_count_actual=actual_words,
            word_count_target=target_words,
            word_count_deviation_percent=deviation,
            critical_issues=data.get("critical_issues", []),
            improvements_needed=data.get("improvements_needed", []),
            passes_quality_gate=False  # Will be calculated
        )
        
        # Determine pass status
        evaluation.determine_pass_status()
        
        return evaluation
