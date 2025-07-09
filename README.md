# Chain of Thought – A Debugger for Human Reasoning

An AI-powered tool that helps you analyze and improve your reasoning processes using machine learning to provide intelligent, context-aware feedback on your thought processes.

## Features

- **Advanced Natural Language Processing**: Parse and analyze natural language reasoning chains with high accuracy
- **Comprehensive Issue Detection**:
  - Circular reasoning and logical fallacies
  - Hasty generalizations and unsupported claims
  - Emotional and subjective language
  - Unsupported assumptions and missing evidence
  - Abrupt topic changes and flow issues
- **Intelligent Suggestions**:
  - Context-aware improvements for clarity and precision
  - Specific guidance on strengthening arguments
  - Identification of emotional or biased language
  - Recommendations for better transitions and flow
- **Local Processing**: All analysis happens on your device - no data is sent to external servers
- **Extensible Architecture**: Easy to add new detection rules and suggestion types
- **Comprehensive Test Suite**: Thoroughly tested with 100% test coverage

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

### Basic Usage

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

### Example Analysis

The tool will analyze your reasoning and provide structured feedback:

```
Analysis Results:

Step 1: I want to find a new job
  ✓ Clear statement of intent

Step 2: I'm not happy with my current salary
  ! Emotional language detected
  → Consider if this strong language is necessary
  → Balance emotional statements with factual evidence

Step 3: I've been in the same role for 3 years
  ✓ Provides useful context

Step 4: I should start looking for new opportunities
  ! Consider adding more specific criteria for your job search
  → What specific opportunities are you looking for?
  → Have you considered internal growth opportunities?

Flow Analysis:
  ✓ Smooth progression of ideas
  → Consider connecting salary concerns to job search more explicitly
```

### Key Features in Action

- **Emotional Language Detection**: Identifies when emotions might be clouding judgment
- **Evidence Evaluation**: Highlights claims that could use more support
- **Flow Analysis**: Checks for logical progression between steps
- **Specific Suggestions**: Provides actionable recommendations for improvement
- **Context-Aware**: Adapts feedback based on the reasoning context

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
├── main.py                     # Command-line interface
├── tests/                      # Comprehensive test suite
│   └── test_reasoning.py       # All test cases
├── .github/                    # GitHub workflows
│   └── workflows/              # CI/CD pipelines
│       ├── test.yml            # Test runner
│       └── lint.yml            # Code quality checks
└── reasoner/                   # Core logic
    ├── __init__.py             # Package definition
    ├── models.py               # Data models for reasoning chains
    ├── parser.py               # Parses natural language input
    ├── analyzer.py             # Detects logical issues
    ├── suggestions.py          # Rule-based improvement suggestions
    └── ml_suggestions.py       # Advanced ML-based analysis
```

### Key Components

- **Parser**: Converts natural language input into structured reasoning steps
- **Analyzer**: Identifies logical issues and potential improvements
- **Suggestion Engine**: Provides specific, actionable recommendations
- **ML Integration**: Uses machine learning for advanced analysis
- **Test Suite**: Ensures reliability and accuracy

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
