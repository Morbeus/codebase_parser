# Codebase Analyzer

A Python tool for analyzing codebases, identifying dependencies, and generating comprehensive reports using LLM-powered analysis.

## Features

- Codebase parsing and dependency graph generation
- Dead code analysis
- LLM-powered code analysis
- Visualization of dependencies
- JSON-based reporting

## Project Structure

```
codebase_analyzer/
├── src/
│   ├── analyzer/
│   │   ├── __init__.py
│   │   ├── codebase_parser.py
│   │   ├── llm_context.py
│   │   ├── dead_code_analyzer.py
│   │   └── codebase_agent.py
│   ├── utils/
│   │   └── __init__.py
│   └── main.py
├── tests/
├── docs/
├── pyproject.toml
└── README.md
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd codebase_analyzer
```

2. Install dependencies using Poetry:
```bash
poetry install
```

## Usage

1. Prepare the environment:
```bash
cp .env.example .env
# Edit .env to add your OpenAI API key
```

2. Run the analyzer:
```bash
poetry run python src/main.py <path_to_codebase>
```

This will:
- Parse the codebase
- Generate a dependency graph
- Analyze dead code
- Create an LLM-powered analysis
- Save results to JSON files

## Output Files

- `llm_context.json`: Contains the prepared context for LLM analysis
- `llm_analysis.json`: Contains the LLM's analysis of the codebase
- `dependency_graph.png`: Visualization of the codebase dependencies
- `raw_response.txt`: Debug file containing the raw LLM response

## Development

### Running Tests
```bash
poetry run pytest tests/
```

### Adding New Features
1. Create a new module in `src/analyzer/`
2. Add tests in `tests/`
3. Update documentation in `docs/`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request
