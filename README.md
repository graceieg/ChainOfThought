# Chain of Thought – A Debugger for Human Reasoning

An AI-powered tool that helps you analyze and improve your reasoning processes using machine learning to provide intelligent, context-aware feedback on your thought processes.

## Features

- Parse natural language reasoning chains into structured steps
- Detect logical fallacies and reasoning issues:
  - Circular reasoning
  - Hasty generalizations
  - Emotional reasoning
  - Unsupported assumptions
  - And more...
- Provide context-aware suggestions for improvement
- Support for various reasoning contexts (relationships, career, decisions, etc.)
- Real-time feedback on reasoning quality
- Comprehensive test suite with 100% test coverage

## Installation

### Using pip

```bash
pip install git+https://github.com/yourusername/chain-of-thought.git
```

### From Source

1. Clone this repository:
   ```bash
   git clone https://github.com/yourusername/chain-of-thought.git
   cd chain-of-thought
   ```

2. Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. Download the required NLTK data:
   ```bash
   python -c "import nltk; nltk.download('punkt')"
   python -c "import nltk; nltk.download('wordnet')"
   ```

4. (Optional) Install development dependencies:
   ```bash
   pip install -r requirements-dev.txt
   ```

## Usage

Run the tool:
```bash
python main.py
```

Enter your reasoning steps one per line, then press Enter twice to finish. For example:
```
1. I want to find a new job
2. I'm not happy with my current salary
3. I've been in the same role for 3 years
4. I should start looking for new opportunities
```

The tool will analyze your reasoning and provide feedback on potential issues and suggestions for improvement, including:

- Adding supporting evidence
- Clarifying ambiguous statements
- Identifying and resolving contradictions
- Detecting logical fallacies
- Providing more specific language
- Suggesting alternative perspectives

### Example Output

```
Issues Found:
- Potential assumption: Step 4 makes an assumption about job satisfaction
- Emotional reasoning: Step 2 uses emotional language that might cloud judgment

Suggestions:
- Consider gathering more data about job market conditions
- Evaluate specific skills and experience to highlight
- Research companies that align with your career goals
```

## Development

### Project Structure

```
.
├── main.py                 # Command-line interface
├── tests/                  # Test suite
│   └── test_reasoning.py   # All test cases
└── reasoner/               # Core logic
    ├── __init__.py         # Package definition
    ├── models.py           # Data models for reasoning chains
    ├── parser.py           # Parses natural language input
    ├── analyzer.py         # Detects logical issues
    ├── suggestions.py      # Generates improvement suggestions
    └── ml_suggestions.py   # ML-based suggestion engine
```

### Running Tests

Run all tests with detailed output:
```bash
python -m unittest tests/test_reasoning.py -v
```

Or with the custom test runner for better visualization:
```bash
python -c "from tests.test_reasoning import run_tests; run_tests()"
```

### Test Coverage

To generate a test coverage report:
```bash
pip install coverage
coverage run -m unittest discover
coverage report -m
```

### Type Checking

The project uses type hints. To check types:
```bash
pip install mypy
mypy .
```

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
