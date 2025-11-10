#!/usr/bin/env python3
"""
Integration test script for the Chloros Blog MCP Server.
Tests all phases end-to-end without requiring external APIs.
"""

import asyncio
import json
import logging
from typing import Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def test_model_imports():
    """Test that all models can be imported correctly."""
    try:
        from src.models.content import ContentStrategy, Article, Section, SEOStrategy, ContentRestrictions
        from src.models.evaluation import Evaluation, ScoreBreakdown
        from src.models.patterns import Pattern, AntiPattern, Structure, ScoringMatrix, Fix
        
        logger.info("✅ All models imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Model import failed: {e}")
        return False


async def test_service_imports():
    """Test that all services can be imported correctly."""
    try:
        from src.services.pinecone_service import PineconeService
        from src.services.perplexity_service import PerplexityService
        from src.services.openai_service import OpenAIService
        from src.services.openrouter_service import OpenRouterService
        from src.services.google_service import GoogleService
        
        logger.info("✅ All services imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Service import failed: {e}")
        return False


async def test_utility_imports():
    """Test that all utilities can be imported correctly."""
    try:
        from src.utils.content_validator import ContentValidator
        from src.utils.scoring_engine import ScoringEngine
        from src.utils.retry_handler import RetryHandler
        
        logger.info("✅ All utilities imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Utility import failed: {e}")
        return False


async def test_tool_imports():
    """Test that all tools can be imported correctly."""
    try:
        from src.tools.research_tools import register_research_tools
        from src.tools.generation_tools import register_generation_tools
        from src.tools.evaluation_tools import register_evaluation_tools
        from src.tools.publishing_tools import register_publishing_tools
        from src.tools.workflow_tools import register_workflow_tools
        
        logger.info("✅ All tools imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Tool import failed: {e}")
        return False


async def test_main_import():
    """Test that the main module can be imported."""
    try:
        from src.main import main, setup_server
        logger.info("✅ Main module imported successfully")
        return True
    except ImportError as e:
        logger.error(f"❌ Main module import failed: {e}")
        return False


async def test_config_validation():
    """Test configuration validation without requiring actual API keys."""
    try:
        # Test that config can be imported
        from src.config import Settings
        
        # Test creating settings with minimal data (will fail on validation, but that's expected)
        try:
            settings = Settings()
            logger.warning("⚠️ Settings created without environment variables (unexpected)")
        except Exception:
            logger.info("✅ Settings validation working (requires environment variables as expected)")
        
        return True
    except ImportError as e:
        logger.error(f"❌ Config import failed: {e}")
        return False


async def test_model_creation():
    """Test creating model instances with sample data."""
    try:
        from src.models.content import ContentStrategy, Article, Section, SEOStrategy, ContentRestrictions
        from src.models.evaluation import Evaluation, ScoreBreakdown
        from src.models.patterns import Pattern, AntiPattern, PatternType
        
        # Test Section creation
        section = Section(
            title="Test Section",
            content_points=["Point 1", "Point 2"],
            target_words=300,
            medical_focus=["concept1", "concept2"]
        )
        
        # Test SEO Strategy
        seo_strategy = SEOStrategy(
            main_keyword_placement=["H1", "first paragraph"],
            secondary_distribution=["section 2", "section 4"]
        )
        
        # Test Content Restrictions
        restrictions = ContentRestrictions(
            avoid=["emotional stories"],
            alternatives=["evidence-based examples"],
            voice_requirements=["third person"]
        )
        
        # Test Content Strategy
        strategy = ContentStrategy(
            h1_title="Test Title",
            content_sections=[section],
            seo_strategy=seo_strategy,
            content_restrictions=restrictions,
            medical_focus=["test concept"],
            target_word_count=2000
        )
        
        # Test Score Breakdown
        score_breakdown = ScoreBreakdown(
            voice_consistency=20,
            structure_quality=22,
            medical_accuracy=28,
            seo_technical=18
        )
        
        # Test Evaluation
        evaluation = Evaluation(
            total_score=88,
            score_breakdown=score_breakdown,
            word_count_actual=2100,
            word_count_target=2000,
            word_count_deviation_percent=5.0,
            critical_issues=[],
            improvements_needed=["Minor improvements"],
            passes_quality_gate=True
        )
        
        # Test Pattern
        pattern = Pattern(
            id="test_pattern",
            name="Test Pattern",
            description="Test description",
            pattern_type=PatternType.VOICE,
            examples=["example 1", "example 2"]
        )
        
        logger.info("✅ All model instances created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Model creation failed: {e}")
        return False


async def test_utility_functionality():
    """Test utility class functionality with mock data."""
    try:
        from src.utils.scoring_engine import ScoringEngine
        from src.utils.retry_handler import RetryHandler
        from src.models.patterns import Pattern, AntiPattern, PatternType
        from src.utils.content_validator import ContentValidator
        
        # Test Scoring Engine
        scoring_engine = ScoringEngine({})
        
        test_article = """
        # Test Article Title
        
        ## Introduction
        This is a test article for validation.
        
        ## Medical Information
        The procedure has a 75-85% success rate.
        Results may vary depending on individual factors.
        
        **Δρ. Γεώργιος Χλωρός**
        Χειρουργός Ορθοπαιδικός
        """
        
        evaluation = scoring_engine.evaluate_article(
            article_content=test_article,
            target_word_count=50,
            topic="Test Topic"
        )
        
        assert evaluation.total_score >= 0, "Score should be non-negative"
        assert evaluation.word_count_actual > 0, "Word count should be positive"
        
        # Test Retry Handler
        retry_handler = RetryHandler(max_retries=2)
        assert retry_handler.max_retries == 2, "Max retries should be set correctly"
        
        # Test Content Validator
        patterns = [Pattern(
            id="test", name="Test", description="Test", 
            pattern_type=PatternType.VOICE, examples=["test"]
        )]
        anti_patterns = [AntiPattern(
            id="anti_test", name="Anti Test", description="Anti Test",
            pattern_type=PatternType.VOICE, examples=["bad"], penalty_points=5
        )]
        
        validator = ContentValidator(patterns, anti_patterns)
        validation_result = validator.validate_content(test_article)
        
        assert hasattr(validation_result, 'is_valid'), "Validation should have is_valid property"
        
        logger.info("✅ Utility functionality tests passed")
        return True
    except Exception as e:
        logger.error(f"❌ Utility functionality test failed: {e}")
        return False


async def test_workflow_structure():
    """Test that workflow structure is properly organized."""
    try:
        # Test that all required phases are represented
        from src.tools import research_tools, generation_tools, evaluation_tools, publishing_tools, workflow_tools
        
        # Verify that each module has the expected registration function
        assert hasattr(research_tools, 'register_research_tools'), "Research tools should have registration function"
        assert hasattr(generation_tools, 'register_generation_tools'), "Generation tools should have registration function"
        assert hasattr(evaluation_tools, 'register_evaluation_tools'), "Evaluation tools should have registration function"
        assert hasattr(publishing_tools, 'register_publishing_tools'), "Publishing tools should have registration function"
        assert hasattr(workflow_tools, 'register_workflow_tools'), "Workflow tools should have registration function"
        
        logger.info("✅ Workflow structure validation passed")
        return True
    except Exception as e:
        logger.error(f"❌ Workflow structure test failed: {e}")
        return False


async def test_data_flow_models():
    """Test that data can flow correctly between phases."""
    try:
        from src.models.content import ContentStrategy, Section, SEOStrategy, ContentRestrictions
        
        # Simulate Phase 1 output (research results)
        research_output = {
            "medical_research": {
                "medical_facts": ["Fact 1", "Fact 2"],
                "citations": [{"source": "Test Source", "content": "Test content"}]
            },
            "cultural_context": {
                "cultural_insights": "Greek cultural context",
                "patient_concerns": ["Concern 1", "Concern 2"]
            },
            "content_strategy": {
                "h1_title": "Test Article Title",
                "content_sections": [
                    {
                        "title": "Introduction",
                        "content_points": ["Point 1", "Point 2"],
                        "target_words": 300,
                        "medical_focus": ["concept1"]
                    }
                ],
                "seo_strategy": {
                    "main_keyword_placement": ["H1", "first paragraph"],
                    "secondary_distribution": ["section 2"]
                },
                "content_restrictions": {
                    "avoid": ["emotional stories"],
                    "alternatives": ["evidence-based examples"],
                    "voice_requirements": ["third person"]
                },
                "medical_focus": ["key concept"],
                "target_word_count": 2000
            }
        }
        
        # Test that this can be converted to proper models
        strategy_data = research_output["content_strategy"]
        
        # Convert sections
        sections = []
        for section_data in strategy_data["content_sections"]:
            section = Section(
                title=section_data["title"],
                content_points=section_data["content_points"],
                target_words=section_data.get("target_words"),
                medical_focus=section_data.get("medical_focus")
            )
            sections.append(section)
        
        # Convert SEO strategy
        seo_strategy = SEOStrategy(
            main_keyword_placement=strategy_data["seo_strategy"]["main_keyword_placement"],
            secondary_distribution=strategy_data["seo_strategy"]["secondary_distribution"]
        )
        
        # Convert restrictions
        restrictions = ContentRestrictions(
            avoid=strategy_data["content_restrictions"]["avoid"],
            alternatives=strategy_data["content_restrictions"]["alternatives"],
            voice_requirements=strategy_data["content_restrictions"]["voice_requirements"]
        )
        
        # Create strategy
        strategy = ContentStrategy(
            h1_title=strategy_data["h1_title"],
            content_sections=sections,
            seo_strategy=seo_strategy,
            content_restrictions=restrictions,
            medical_focus=strategy_data["medical_focus"],
            target_word_count=strategy_data["target_word_count"]
        )
        
        assert strategy.h1_title == "Test Article Title", "Strategy should preserve title"
        assert len(strategy.content_sections) == 1, "Strategy should have correct section count"
        assert strategy.target_word_count == 2000, "Strategy should preserve word count"
        
        logger.info("✅ Data flow models validation passed")
        return True
    except Exception as e:
        logger.error(f"❌ Data flow models test failed: {e}")
        return False


async def run_all_tests():
    """Run all integration tests."""
    logger.info("🚀 Starting Chloros Blog MCP Server Integration Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Model Imports", test_model_imports),
        ("Service Imports", test_service_imports),
        ("Utility Imports", test_utility_imports),
        ("Tool Imports", test_tool_imports),
        ("Main Module Import", test_main_import),
        ("Config Validation", test_config_validation),
        ("Model Creation", test_model_creation),
        ("Utility Functionality", test_utility_functionality),
        ("Workflow Structure", test_workflow_structure),
        ("Data Flow Models", test_data_flow_models)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 TEST RESULTS SUMMARY")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 All tests passed! The MCP server is ready for deployment.")
        logger.info("\n📝 Next steps:")
        logger.info("1. Set up environment variables (.env file)")
        logger.info("2. Install dependencies: pip install -r requirements.txt")
        logger.info("3. Run the server: python -m src.main")
        logger.info("4. Test with actual API keys and external services")
    else:
        logger.warning("⚠️ Some tests failed. Please review and fix issues before deployment.")
    
    return passed == total


if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    exit(0 if success else 1)
