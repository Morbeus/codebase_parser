import os
import json
from typing import Dict, List, Set, Optional
from dataclasses import dataclass
from .codebase_parser import ImportInfo, ExportInfo

@dataclass
class CodeContext:
    file_path: str
    content: str
    imports: List[ImportInfo]
    exports: List[ExportInfo]
    used_symbols: List[str]
    dependent_files: List[str]

class LLMContextBuilder:
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.code_contexts: Dict[str, Dict] = {}
        self.dependency_graph: Dict[str, List[str]] = {}

    def add_code_context(self, file_path: str, content: str, 
                        imports: List[ImportInfo], exports: List[ExportInfo],
                        used_symbols: List[str]) -> None:
        """Add context for a single file."""
        self.code_contexts[file_path] = {
            'content': content,
            'imports': [{'module': imp.module, 'name': imp.name, 'alias': imp.alias} 
                       for imp in imports],
            'exports': [{'name': exp.name, 'alias': exp.alias} for exp in exports],
            'used_symbols': used_symbols,
            'dependent_files': []
        }

    def set_dependency_graph(self, graph: Dict[str, Set[str]]) -> None:
        """Set the dependency graph for the codebase."""
        self.dependency_graph = {k: list(v) for k, v in graph.items()}
        
        # Update dependent_files in code contexts
        for file_path, deps in graph.items():
            if file_path in self.code_contexts:
                self.code_contexts[file_path]['dependent_files'] = list(deps)

    def prepare_context(self) -> Dict:
        """Prepare the complete context for the LLM."""
        return {
            'files': self.code_contexts,
            'dependency_graph': self.dependency_graph
        }

    def save_context(self, output_path: str) -> None:
        """Save the context to a JSON file."""
        context = self.prepare_context()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w') as f:
            json.dump(context, f, indent=2)

    def get_llm_prompt(self) -> str:
        """Generate a prompt for the LLM."""
        return """You are a code analysis expert. Analyze the following codebase and provide a detailed analysis in JSON format. The analysis should include:

1. File purposes and relationships
2. Dependencies between files
3. Used and unused code
4. Potential issues or improvements

Format your response as a JSON array of objects, where each object represents a file analysis with the following structure:
[
  {{
    "file_path": "path/to/file.py",
    "purpose": "Brief description of the file's purpose",
    "dependencies": {{
      "imports": ["list of imported modules"],
      "exports": ["list of exported symbols"],
      "dependent_files": ["list of files that depend on this file"]
    }},
    "code_analysis": {{
      "used_symbols": ["list of symbols that are actually used"],
      "unused_symbols": ["list of symbols that are defined but not used"],
      "potential_issues": ["list of potential issues or improvements"]
    }}
  }}
]

Ensure your analysis is thorough and accurate. Pay special attention to:
- Circular dependencies
- Unused imports or functions
- Potential security issues
- Code organization and maintainability
- Performance considerations""" 