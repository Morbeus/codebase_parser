import os
import ast
import importlib
import sys
from typing import Dict, List, Set, Tuple, Optional, Union
from dataclasses import dataclass
import networkx as nx
import matplotlib.pyplot as plt

@dataclass(frozen=True)
class ImportInfo:
    module: str
    name: Optional[str]
    alias: Optional[str]

@dataclass(frozen=True)
class ExportInfo:
    name: str
    alias: Optional[str]

@dataclass
class ParseResult:
    imports: List[ImportInfo]
    exports: List[ExportInfo]

class CodebaseParser:
    def __init__(self, root_dir: Optional[str] = None):
        self.root_dir = root_dir
        self.graph = nx.DiGraph()
        self.imports: Dict[str, List[ImportInfo]] = {}
        self.exports: Dict[str, List[ExportInfo]] = {}
        self.visited_files: Set[str] = set()
        self.import_stack: List[str] = []  # For detecting circular imports
        self.dynamic_imports: Dict[str, Set[str]] = {}  # file -> {dynamic_import_strings}

    def parse_file(self, file_path: str) -> Optional[ParseResult]:
        """Parse a single Python file and extract imports and exports."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = self._parse_imports(content)
            exports = self._parse_exports(content)
            
            return ParseResult(imports=imports, exports=exports)
        except Exception as e:
            print(f"Error parsing {file_path}: {str(e)}")
            return None

    def _parse_imports(self, content: str) -> List[ImportInfo]:
        imports = []
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for name in node.names:
                    imports.append(ImportInfo(
                        module=name.name,
                        name=None,
                        alias=name.asname
                    ))
            elif isinstance(node, ast.ImportFrom):
                module = node.module if node.module else ''
                for name in node.names:
                    imports.append(ImportInfo(
                        module=module,
                        name=name.name,
                        alias=name.asname
                    ))
        
        return imports

    def _parse_exports(self, content: str) -> List[ExportInfo]:
        exports = []
        tree = ast.parse(content)
        
        # Check for __all__ definition
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == '__all__':
                        if isinstance(node.value, ast.List):
                            for item in node.value.elts:
                                if isinstance(item, ast.Str):
                                    exports.append(ExportInfo(
                                        name=item.s,
                                        alias=None
                                    ))
        
        # Add function and class definitions
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                exports.append(ExportInfo(
                    name=node.name,
                    alias=None
                ))
        
        return exports

    def _process_import_node(self, node: ast.AST, file_path: str) -> None:
        """Process different types of import statements."""
        if isinstance(node, ast.Import):
            for name in node.names:
                import_info = ImportInfo(
                    module=name.name,
                    name=None,
                    alias=name.asname
                )
                self.imports[file_path].append(import_info)
                
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ''
            level = getattr(node, 'level', 0)
            is_relative = level > 0
            
            for name in node.names:
                import_info = ImportInfo(
                    module=module,
                    name=name.name,
                    alias=name.asname
                )
                self.imports[file_path].append(import_info)

    def _process_export_node(self, node: ast.AST, file_path: str) -> None:
        """Process different types of exportable nodes."""
        if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
            export_info = ExportInfo(
                name=node.name,
                alias=None
            )
            self.exports[file_path].append(export_info)
            
        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    export_info = ExportInfo(
                        name=target.id,
                        alias=None
                    )
                    self.exports[file_path].append(export_info)

    def _process_dynamic_imports(self, node: ast.AST, file_path: str, content: str) -> None:
        """Detect and process dynamic imports."""
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in ('__import__', 'importlib.import_module'):
                # Extract the import string from the arguments
                if node.args and isinstance(node.args[0], ast.Str):
                    self.dynamic_imports[file_path].add(node.args[0].s)
                    
        # Look for common dynamic import patterns
        dynamic_patterns = [
            'importlib.import_module',
            '__import__',
            'exec("import")',
            'eval("import")'
        ]
        
        for pattern in dynamic_patterns:
            if pattern in content:
                self.dynamic_imports[file_path].add(pattern)

    def _resolve_import_path(self, source_file: str, import_info: ImportInfo) -> Optional[str]:
        """Resolve an import to an actual file path, handling various cases."""
        if import_info.is_dynamic:
            return None
            
        module = import_info.module
        
        if import_info.is_relative:
            base_dir = os.path.dirname(source_file)
            module = module.lstrip('.')
            potential_path = os.path.join(base_dir, module.replace('.', '/'))
        else:
            potential_path = module.replace('.', '/')
        
        # Check for .py extension
        if not potential_path.endswith('.py'):
            potential_path += '.py'
        
        # Check if the file exists
        full_path = os.path.join(self.root_dir, potential_path)
        if os.path.exists(full_path):
            return potential_path
        
        # Check for __init__.py in package directories
        package_path = os.path.join(self.root_dir, module.replace('.', '/'), '__init__.py')
        if os.path.exists(package_path):
            return os.path.join(module.replace('.', '/'), '__init__.py')
        
        # Check Python path
        try:
            spec = importlib.util.find_spec(module)
            if spec and spec.origin:
                return os.path.relpath(spec.origin, self.root_dir)
        except (ImportError, ValueError):
            pass
        
        return None

    def build_dependency_graph(self) -> None:
        """Build the dependency graph with enhanced edge information."""
        # Add nodes for all files
        for file_path in self.imports:
            self.graph.add_node(file_path)
        
        # Add edges for dependencies with detailed information
        for file_path, imports in self.imports.items():
            for import_info in imports:
                imported_file = self._resolve_import_path(file_path, import_info)
                if imported_file:
                    edge_data = {
                        'symbol': import_info.name,
                        'alias': import_info.alias,
                        'is_relative': False,
                        'is_dynamic': False
                    }
                    self.graph.add_edge(file_path, imported_file, **edge_data)
        
        # Handle circular dependencies
        self._handle_circular_dependencies()

    def _handle_circular_dependencies(self) -> None:
        """Detect and handle circular dependencies."""
        cycles = list(nx.simple_cycles(self.graph))
        if cycles:
            print("\nWarning: Circular dependencies detected:")
            for cycle in cycles:
                print(f"Cycle: {' -> '.join(cycle)}")
            
            # Add metadata to the graph about circular dependencies
            self.graph.graph['circular_dependencies'] = cycles

    def analyze_codebase(self) -> None:
        """Analyze the entire codebase with enhanced error handling."""
        try:
            for root, _, files in os.walk(self.root_dir):
                for file in files:
                    if file.endswith('.py'):
                        file_path = os.path.join(root, file)
                        self.parse_file(file_path)
            
            self.build_dependency_graph()
            
        except Exception as e:
            print(f"Error analyzing codebase: {str(e)}")
            raise

    def get_detailed_analysis(self) -> Dict:
        """Get a detailed analysis of the codebase."""
        return {
            'dependencies': {
                file: [
                    {
                        'target': target,
                        'symbol': self.graph[file][target].get('symbol'),
                        'alias': self.graph[file][target].get('alias'),
                        'is_relative': self.graph[file][target].get('is_relative', False),
                        'is_dynamic': self.graph[file][target].get('is_dynamic', False)
                    }
                    for target in self.graph.successors(file)
                ]
                for file in self.graph.nodes()
            },
            'exports': {
                file: [
                    {
                        'name': export.name,
                        'alias': export.alias
                    }
                    for export in exports
                ]
                for file, exports in self.exports.items()
            },
            'dynamic_imports': {
                file: list(imports)  # Convert set to list
                for file, imports in self.dynamic_imports.items()
            },
            'circular_dependencies': [
                list(cycle)  # Convert set to list
                for cycle in self.graph.graph.get('circular_dependencies', [])
            ]
        }

    def visualize_graph(self, output_path: str = 'data/dependency_graph.png') -> None:
        """Generate a clean visualization of the file dependency graph."""
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(self.graph, k=1, iterations=50)  # Adjust layout parameters
        
        # Draw nodes with simple labels
        nx.draw_networkx_nodes(
            self.graph, 
            pos, 
            node_color='lightblue',
            node_size=1500,
            alpha=0.8
        )
        
        # Draw edges with arrows
        nx.draw_networkx_edges(
            self.graph, 
            pos, 
            edge_color='gray',
            arrows=True,
            arrowsize=15,
            width=1.5
        )
        
        # Add simple file names as labels
        labels = {node: os.path.basename(node) for node in self.graph.nodes()}
        nx.draw_networkx_labels(
            self.graph, 
            pos, 
            labels,
            font_size=10,
            font_weight='bold'
        )
        
        # Save the graph
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close() 