import pytest
from src.analyzer.context_chunker import ContextChunker

@pytest.fixture
def sample_context():
    return {
        "files": {
            "main.py": {
                "content": "def main():\n    print('Hello')\n",
                "imports": [],
                "exports": ["main"],
                "used_symbols": ["print"],
                "dependent_files": []
            },
            "utils.py": {
                "content": "def helper():\n    return 'Helper'\n",
                "imports": [],
                "exports": ["helper"],
                "used_symbols": [],
                "dependent_files": []
            }
        },
        "dependency_graph": {
            "main.py": [],
            "utils.py": []
        }
    }

def test_estimate_tokens():
    chunker = ContextChunker()
    text = "Hello world"
    assert chunker.estimate_tokens(text) > 0

def test_chunk_context(sample_context):
    chunker = ContextChunker(max_tokens=100)
    chunks = chunker.chunk_context(sample_context)
    
    assert len(chunks) > 0
    assert all(isinstance(chunk, dict) for chunk in chunks)
    assert all("files" in chunk for chunk in chunks)
    assert all("dependency_graph" in chunk for chunk in chunks)

def test_sort_files_by_importance(sample_context):
    chunker = ContextChunker()
    sorted_files = chunker._sort_files_by_importance(sample_context["files"])
    
    assert len(sorted_files) == 2
    assert "main.py" in sorted_files
    assert "utils.py" in sorted_files

def test_get_chunk_prompts(sample_context):
    chunker = ContextChunker()
    chunks = chunker.chunk_context(sample_context)
    prompts = chunker.get_chunk_prompts(chunks)
    
    assert len(prompts) == len(chunks)
    assert all(isinstance(prompt, str) for prompt in prompts)
    assert all("Analyze the following code context" in prompt for prompt in prompts) 