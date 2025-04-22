import os
import pytest
from src.analyzer.codebase_parser import CodebaseParser, ImportInfo, ExportInfo

@pytest.fixture
def sample_code():
    return """
import os
from typing import List, Dict
from .utils import helper_function

def main_function():
    return helper_function()

__all__ = ['main_function']
"""

def test_parse_imports(sample_code):
    parser = CodebaseParser()
    imports = parser._parse_imports(sample_code)
    
    assert len(imports) == 3
    assert ImportInfo("os", None, None) in imports
    assert ImportInfo("typing", "List", None) in imports
    assert ImportInfo(".utils", "helper_function", None) in imports

def test_parse_exports(sample_code):
    parser = CodebaseParser()
    exports = parser._parse_exports(sample_code)
    
    assert len(exports) == 1
    assert ExportInfo("main_function", None) in exports

def test_parse_file(tmp_path):
    # Create a temporary Python file
    file_path = tmp_path / "test_file.py"
    file_path.write_text("""
def test_function():
    return "test"
    """)
    
    parser = CodebaseParser()
    result = parser.parse_file(str(file_path))
    
    assert result is not None
    assert len(result.exports) == 1
    assert result.exports[0].name == "test_function" 