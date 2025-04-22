import os
import sys
from typing import Dict, List, Set
from analyzer.codebase_parser import CodebaseParser, ImportInfo, ExportInfo
from analyzer.llm_context import LLMContextBuilder
from analyzer.dead_code_analyzer import DeadCodeAnalyzer

def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <codebase_directory>")
        sys.exit(1)

    codebase_dir = sys.argv[1]
    if not os.path.isdir(codebase_dir):
        print(f"Error: {codebase_dir} is not a valid directory")
        sys.exit(1)

    # Get the project root directory (one level up from src)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(project_root, 'data')
    os.makedirs(data_dir, exist_ok=True)

    # Initialize components
    parser = CodebaseParser(root_dir=codebase_dir)
    context_builder = LLMContextBuilder(codebase_dir)
    dead_code_analyzer = DeadCodeAnalyzer()

    # Parse the codebase and build dependency graph
    dependency_graph: Dict[str, Set[str]] = {}
    for root, _, files in os.walk(codebase_dir):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, codebase_dir)
                
                # Parse file
                result = parser.parse_file(file_path)
                if result:
                    # Add to context builder
                    context_builder.add_code_context(
                        file_path=rel_path,
                        content=open(file_path, 'r').read(),
                        imports=result.imports,
                        exports=result.exports,
                        used_symbols=set()  # Will be updated by dead code analyzer
                    )
                    
                    # Analyze for dead code
                    dead_code_analyzer.analyze_file(rel_path, open(file_path, 'r').read())
                    
                    # Build dependency graph
                    dependency_graph[rel_path] = set()
                    for imp in result.imports:
                        if imp.module:
                            dep_path = imp.module.replace('.', '/') + '.py'
                            if os.path.exists(os.path.join(codebase_dir, dep_path)):
                                dependency_graph[rel_path].add(dep_path)

    # Update used symbols in context
    for file_path in context_builder.code_contexts:
        context_builder.code_contexts[file_path]['used_symbols'] = list(
            dead_code_analyzer.get_used_symbols()
        )

    # Set dependency graph and prepare context
    context_builder.set_dependency_graph(dependency_graph)
    context = context_builder.prepare_context()

    # Save context to data directory
    context_builder.save_context(os.path.join(data_dir, 'llm_context.json'))

    # Generate and save prompt
    prompt = context_builder.get_llm_prompt()
    with open(os.path.join(data_dir, 'llm_prompt.txt'), 'w') as f:
        f.write(prompt)

    print("Analysis complete. Results saved in data/ directory.")

if __name__ == "__main__":
    main() 