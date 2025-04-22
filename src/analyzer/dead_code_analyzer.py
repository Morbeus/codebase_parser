import ast
from typing import Set, Dict, List, Optional
import os

class DeadCodeAnalyzer:
    def __init__(self):
        self.used_symbols: Set[str] = set()
        self.defined_symbols: Dict[str, Set[str]] = {}
        self.entry_points: Set[str] = {'main', '__init__', 'setup', 'run'}

    def analyze_file(self, file_path: str, content: str) -> None:
        """Analyze a file for dead code."""
        try:
            tree = ast.parse(content)
            self.defined_symbols[file_path] = set()
            self._process_node(tree, file_path)
        except Exception as e:
            print(f"Error analyzing {file_path}: {str(e)}")

    def _process_node(self, node: ast.AST, file_path: str) -> None:
        """Process an AST node to track symbol usage and definitions."""
        if isinstance(node, ast.FunctionDef):
            self.defined_symbols[file_path].add(node.name)
            if node.name in self.entry_points:
                self.used_symbols.add(node.name)
            self._process_node(node.body, file_path)
            
        elif isinstance(node, ast.ClassDef):
            self.defined_symbols[file_path].add(node.name)
            self._process_node(node.body, file_path)
            
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    self.defined_symbols[file_path].add(target.id)
            
        elif isinstance(node, ast.Name):
            if isinstance(node.ctx, ast.Load):
                self.used_symbols.add(node.id)
            
        elif isinstance(node, (ast.Import, ast.ImportFrom)):
            for name in node.names:
                if name.asname:
                    self.used_symbols.add(name.asname)
                else:
                    self.used_symbols.add(name.name.split('.')[0])
            
        # Recursively process child nodes
        for child in ast.iter_child_nodes(node):
            self._process_node(child, file_path)

    def get_dead_code(self) -> Dict[str, List[str]]:
        """Get a dictionary of dead code per file."""
        dead_code = {}
        for file_path, symbols in self.defined_symbols.items():
            dead_symbols = [s for s in symbols if s not in self.used_symbols]
            if dead_symbols:
                dead_code[file_path] = dead_symbols
        return dead_code

    def get_used_symbols(self) -> Set[str]:
        """Get all used symbols."""
        return self.used_symbols

    def is_symbol_used(self, symbol: str) -> bool:
        """Check if a symbol is used anywhere in the codebase."""
        return symbol in self.used_symbols 