"""
Simple test script to verify API functionality.
"""
import sys
import os

# Add the current directory to the path so we can import the API
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_api_import():
    """Test that we can import the API without errors."""
    try:
        from api.app import app
        print("✓ API imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing API: {e}")
        return False

def test_models_import():
    """Test that we can import the models without errors."""
    try:
        from models import Repository, Paper, SearchResult
        print("✓ Models imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing models: {e}")
        return False

def test_connectors_import():
    """Test that we can import the connectors without errors."""
    try:
        from connectors.github import GitHubConnector
        from connectors.arxiv import ArxivConnector
        from connectors.semantic_scholar import SemanticScholarConnector
        from connectors.web_search import WebSearchConnector
        print("✓ Connectors imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing connectors: {e}")
        return False

def test_aggregator_import():
    """Test that we can import the aggregator without errors."""
    try:
        from aggregator import ResultAggregator
        print("✓ Aggregator imported successfully")
        return True
    except Exception as e:
        print(f"✗ Error importing aggregator: {e}")
        return False

if __name__ == "__main__":
    print("Testing API components...")
    tests = [
        test_api_import,
        test_models_import,
        test_connectors_import,
        test_aggregator_import
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    if all(results):
        print("\n✓ All tests passed! The API is ready to use.")
    else:
        print("\n✗ Some tests failed. Please check the errors above.")