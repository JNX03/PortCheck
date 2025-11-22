"""
Basic tests for Thai Portfolio Analyzer
Run with: pytest test_basic.py
"""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))


def test_imports():
    """Test that all required modules can be imported"""
    try:
        from models.schemas import AnalysisResult, LanguageIssue, FieldMatch
        from services.pdf_processor import PDFProcessor
        from services.typhoon_analyzer import TyphoonAnalyzer
        print("✅ All imports successful")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False


def test_pdf_processor_init():
    """Test PDF processor initialization"""
    try:
        from services.pdf_processor import PDFProcessor
        processor = PDFProcessor()
        assert processor.min_text_threshold == 100
        print("✅ PDF processor initialized successfully")
        return True
    except Exception as e:
        print(f"❌ PDF processor init error: {e}")
        return False


def test_schemas():
    """Test that schemas work correctly"""
    try:
        from models.schemas import LanguageIssue, FieldMatch, AnalysisResult

        # Test LanguageIssue
        issue = LanguageIssue(
            text="เจ๋ง",
            start_pos=0,
            end_pos=4,
            issue_type="informal_word",
            severity="high",
            suggestion="ยอดเยี่ยม",
            explanation="เป็นภาษาพูด"
        )
        assert issue.text == "เจ๋ง"

        # Test FieldMatch
        field_match = FieldMatch(
            target_field="doctor",
            matches=True,
            confidence=0.85,
            detected_fields=["แพทย์"],
            evidence=["Test evidence"],
            recommendations=["Test recommendation"]
        )
        assert field_match.confidence == 0.85

        # Test AnalysisResult
        result = AnalysisResult(
            success=True,
            text_length=100,
            overall_formality_score=0.75,
            formality_level="formal",
            field_match=field_match,
            summary="Test summary",
            language_issues=[issue]
        )
        assert result.text_length == 100

        print("✅ All schemas work correctly")
        return True
    except Exception as e:
        print(f"❌ Schema test error: {e}")
        return False


def test_environment():
    """Test environment configuration"""
    print("\n=== Environment Check ===")
    print(f"Python version: {sys.version}")
    print(f"Current directory: {os.getcwd()}")

    # Check for .env file
    env_file = Path(".env")
    if env_file.exists():
        print("✅ .env file exists")
    else:
        print("⚠️  .env file not found (copy from .env.example)")

    # Check required directories
    required_dirs = ["models", "services", "templates", "uploads"]
    for dir_name in required_dirs:
        if Path(dir_name).is_dir():
            print(f"✅ {dir_name}/ directory exists")
        else:
            print(f"❌ {dir_name}/ directory missing")

    return True


def test_dependencies():
    """Test that key dependencies are installed"""
    print("\n=== Dependency Check ===")

    dependencies = {
        "fastapi": "FastAPI",
        "uvicorn": "Uvicorn",
        "PyPDF2": "PyPDF2",
        "pdf2image": "pdf2image",
        "pytesseract": "pytesseract",
        "openai": "OpenAI",
        "pydantic": "Pydantic"
    }

    all_ok = True
    for module, name in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} not installed")
            all_ok = False

    return all_ok


def main():
    """Run all tests"""
    print("=" * 50)
    print("Thai Portfolio Analyzer - Basic Tests")
    print("=" * 50)

    tests = [
        ("Environment", test_environment),
        ("Dependencies", test_dependencies),
        ("Imports", test_imports),
        ("PDF Processor", test_pdf_processor_init),
        ("Schemas", test_schemas),
    ]

    results = []
    for test_name, test_func in tests:
        print(f"\n--- Testing: {test_name} ---")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with error: {e}")
            results.append((test_name, False))

    print("\n" + "=" * 50)
    print("Test Summary")
    print("=" * 50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
