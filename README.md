# Chain of Thought

An AI-powered tool that helps you analyze and improve your reasoning processes using machine learning to provide intelligent, context-aware feedback on your thought processes.

## About

Chain of Thought is designed to help individuals and teams improve their reasoning and decision-making processes. This project was created to address the common challenges people face when trying to structure their thoughts and arguments effectively. By providing real-time, intelligent feedback on reasoning patterns, it helps users identify logical fallacies, emotional biases, and areas where their arguments could be strengthened.

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

### Prerequisites

- Python 3.7+
- pip (Python package manager)
- Git (for installation from source)
- NLTK data (automatically downloaded during setup)

### Installation Steps

#### Using pip

```bash
pip install git+https://github.com/yourusername/chain-of-thought.git
```

#### From Source

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

### Running the Application

To start the Chain of Thought analyzer, run:

```bash
python main.py
```

### Basic Workflow

1. Enter your reasoning steps one per line
2. Press Enter twice when you're done entering your thoughts
3. The tool will analyze your reasoning and provide feedback

### Example Input

```
1. I want to find a new job
2. I'm not happy with my current salary
3. I've been in the same role for 3 years
4. I should start looking for new opportunities
```

### Example Output

The tool provides structured feedback on your reasoning:

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

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.


## Acknowledgements

- [NLTK](https://www.nltk.org/) - For natural language processing capabilities
- [spaCy](https://spacy.io/) - For advanced NLP features
- [TextBlob](https://textblob.readthedocs.io/) - For sentiment analysis
