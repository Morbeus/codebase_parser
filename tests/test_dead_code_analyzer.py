import pytest
from src.analyzer.dead_code_analyzer import DeadCodeAnalyzer

@pytest.fixture
def sample_code():
    return """
def used_function():
    return "used"

def unused_function():
    return "unused"

def main():
    print(used_function())
"""

def test_analyze_file(sample_code):
    analyzer = DeadCodeAnalyzer()
    analyzer.analyze_file("test_file.py", sample_code)
    
    dead_code = analyzer.get_dead_code()
    assert "test_file.py" in dead_code
    assert "unused_function" in dead_code["test_file.py"]
    assert "used_function" not in dead_code["test_file.py"]
    assert "main" not in dead_code["test_file.py"]

def test_get_used_symbols(sample_code):
    analyzer = DeadCodeAnalyzer()
    analyzer.analyze_file("test_file.py", sample_code)
    
    used_symbols = analyzer.get_used_symbols()
    assert "used_function" in used_symbols
    assert "main" in used_symbols
    assert "unused_function" not in used_symbols

def test_is_symbol_used(sample_code):
    analyzer = DeadCodeAnalyzer()
    analyzer.analyze_file("test_file.py", sample_code)
    
    assert analyzer.is_symbol_used("used_function")
    assert analyzer.is_symbol_used("main")
    assert not analyzer.is_symbol_used("unused_function") 