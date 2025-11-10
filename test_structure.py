#!/usr/bin/env python3
"""
Structure validation test for the Chloros Blog MCP Server.
Tests the project structure and basic imports without requiring external dependencies.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_project_structure():
    """Test that all required files and directories exist."""
    logger.info("🧪 Testing project structure...")
    
    required_files = [
        "src/__init__.py",
        "src/main.py",
        "src/config.py",
        "src/models/__init__.py",
        "src/models/content.py",
        "src/models/evaluation.py",
        "src/models/patterns.py",
        "src/services/__init__.py",
        "src/services/pinecone_service.py",
        "src/services/perplexity_service.py",
        "src/services/openai_service.py",
        "src/services/openrouter_service.py",
        "src/services/google_service.py",
        "src/tools/__init__.py",
        "src/tools/research_tools.py",
        "src/tools/generation_tools.py",
        "src/tools/evaluation_tools.py",
        "src/tools/publishing_tools.py",
        "src/tools/workflow_tools.py",
        "src/utils/__init__.py",
        "src/utils/content_validator.py",
        "src/utils/scoring_engine.py",
        "src/utils/retry_handler.py",
        "requirements.txt",
        "pyproject.toml",
        ".gitignore",
        "README.md"
    ]
    
    missing_files = []
    for file_path in required_files:
        if not os.path.exists(file_path):
            missing_files.append(file_path)
    
    if missing_files:
        logger.error(f"❌ Missing files: {missing_files}")
        return False
    
    logger.info("✅ All required files present")
    return True


def test_python_syntax():
    """Test that all Python files have valid syntax."""
    logger.info("🧪 Testing Python syntax...")
    
    python_files = []
    for root, dirs, files in os.walk("src"):
        for file in files:
            if file.endswith(".py"):
                python_files.append(os.path.join(root, file))
    
    syntax_errors = []
    for file_path in python_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, file_path, 'exec')
        except SyntaxError as e:
            syntax_errors.append(f"{file_path}: {e}")
        except Exception as e:
            syntax_errors.append(f"{file_path}: {e}")
    
    if syntax_errors:
        logger.error(f"❌ Syntax errors found:")
        for error in syntax_errors:
            logger.error(f"  {error}")
        return False
    
    logger.info("✅ All Python files have valid syntax")
    return True


def test_import_structure():
    """Test that import statements are correctly structured."""
    logger.info("🧪 Testing import structure...")
    
    # Test that models can be imported without external dependencies
    try:
        sys.path.insert(0, os.path.abspath('.'))
        
        # Test basic model imports
        from src.models.content import ContentStrategy, Article, Section
        from src.models.evaluation import Evaluation, ScoreBreakdown  
        from src.models.patterns import Pattern, AntiPattern, PatternType
        
        logger.info("✅ Model imports successful")
        return True
    except Exception as e:
        logger.error(f"❌ Import structure test failed: {e}")
        return False


def test_configuration_structure():
    """Test configuration file structure."""
    logger.info("🧪 Testing configuration structure...")
    
    try:
        # Check requirements.txt
        with open("requirements.txt", 'r') as f:
            requirements = f.read()
        
        required_packages = [
            "fastmcp", "pydantic", "pydantic-settings", "python-dotenv",
            "httpx", "openai", "pinecone-client", "google-api-python-client",
            "markdown", "beautifulsoup4", "tenacity"
        ]
        
        missing_packages = []
        for package in required_packages:
            if package not in requirements:
                missing_packages.append(package)
        
        if missing_packages:
            logger.error(f"❌ Missing packages in requirements.txt: {missing_packages}")
            return False
        
        # Check pyproject.toml exists and has basic structure
        with open("pyproject.toml", 'r') as f:
            pyproject_content = f.read()
        
        required_sections = ["[build-system]", "[project]", "dependencies"]
        missing_sections = []
        for section in required_sections:
            if section not in pyproject_content:
                missing_sections.append(section)
        
        if missing_sections:
            logger.error(f"❌ Missing sections in pyproject.toml: {missing_sections}")
            return False
        
        logger.info("✅ Configuration structure valid")
        return True
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False


def test_readme_documentation():
    """Test that README contains essential information."""
    logger.info("🧪 Testing README documentation...")
    
    try:
        with open("README.md", 'r') as f:
            readme_content = f.read()
        
        required_sections = [
            "# Chloros Blog MCP Server",
            "## Features",
            "## Quick Start",
            "## Architecture"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in readme_content:
                missing_sections.append(section)
        
        if missing_sections:
            logger.error(f"❌ Missing sections in README.md: {missing_sections}")
            return False
        
        # Check for key information
        key_info = [
            "MCP", "orthopedic", "Greek", "quality scoring", "RAG"
        ]
        
        missing_info = []
        for info in key_info:
            if info.lower() not in readme_content.lower():
                missing_info.append(info)
        
        if missing_info:
            logger.warning(f"⚠️ README might be missing key information: {missing_info}")
        
        logger.info("✅ README documentation structure valid")
        return True
    except Exception as e:
        logger.error(f"❌ README test failed: {e}")
        return False


def test_workflow_completeness():
    """Test that all workflow phases are represented."""
    logger.info("🧪 Testing workflow completeness...")
    
    try:
        # Check that all phase tools exist
        phase_files = [
            "src/tools/research_tools.py",      # Phase 1
            "src/tools/generation_tools.py",    # Phase 2
            "src/tools/evaluation_tools.py",    # Phase 3
            "src/tools/publishing_tools.py",    # Phase 4
            "src/tools/workflow_tools.py"       # Integration
        ]
        
        for file_path in phase_files:
            if not os.path.exists(file_path):
                logger.error(f"❌ Missing workflow file: {file_path}")
                return False
        
        # Check that each file has expected content
        expected_functions = {
            "research_tools.py": ["medical_research_query", "cultural_context_research", "read_blog_patterns"],
            "generation_tools.py": ["generate_complete_article"],
            "evaluation_tools.py": ["evaluate_article_quality", "comprehensive_evaluation"],
            "publishing_tools.py": ["create_google_doc", "publish_article"],
            "workflow_tools.py": ["complete_article_workflow"]
        }
        
        for file_name, functions in expected_functions.items():
            file_path = f"src/tools/{file_name}"
            with open(file_path, 'r') as f:
                content = f.read()
            
            for function in functions:
                if function not in content:
                    logger.error(f"❌ Missing function {function} in {file_name}")
                    return False
        
        logger.info("✅ Workflow completeness validated")
        return True
    except Exception as e:
        logger.error(f"❌ Workflow completeness test failed: {e}")
        return False


def run_structure_tests():
    """Run all structure validation tests."""
    logger.info("🚀 Starting Chloros Blog MCP Server Structure Tests")
    logger.info("=" * 60)
    
    tests = [
        ("Project Structure", test_project_structure),
        ("Python Syntax", test_python_syntax),
        ("Import Structure", test_import_structure),
        ("Configuration Structure", test_configuration_structure),
        ("README Documentation", test_readme_documentation),
        ("Workflow Completeness", test_workflow_completeness)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        logger.info(f"\n🧪 Running: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("📊 STRUCTURE TEST RESULTS")
    logger.info("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
    
    logger.info(f"\n🎯 Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        logger.info("🎉 All structure tests passed!")
        logger.info("\n📋 Project Structure Summary:")
        logger.info("├── 5 service integrations (Pinecone, Perplexity, OpenAI, OpenRouter, Google)")
        logger.info("├── 4 workflow phases (Research, Generation, Evaluation, Publishing)")
        logger.info("├── 3 utility classes (Validator, Scoring Engine, Retry Handler)")
        logger.info("├── 3 data model categories (Content, Evaluation, Patterns)")
        logger.info("└── Complete MCP server with retry logic and quality gates")
        logger.info("\n🚀 Ready for dependency installation and API key configuration!")
    else:
        logger.warning("⚠️ Some structure tests failed. Please review and fix issues.")
    
    return passed == total


if __name__ == "__main__":
    success = run_structure_tests()
    exit(0 if success else 1)
