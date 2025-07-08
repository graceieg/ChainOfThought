# Contributing to Chain of Thought Debugger

We welcome contributions to improve the Chain of Thought Debugger! Here's how you can help:

## How to Contribute

1. **Fork the repository** and create your feature branch (`git checkout -b feature/AmazingFeature`)
2. **Commit your changes** (`git commit -m 'Add some AmazingFeature'`)
3. **Push to the branch** (`git push origin feature/AmazingFeature`)
4. Open a **Pull Request**

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/chain-of-thought.git
   cd chain-of-thought
   ```

2. Set up a virtual environment (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install development dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Install pre-commit hooks (optional but recommended):
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Running Tests

Run the test suite:
```bash
python -m unittest discover -s tests
```

## Code Style

We use:
- Black for code formatting
- Flake8 for linting
- Mypy for type checking

## Reporting Issues

Please use the [GitHub issue tracker](https://github.com/yourusername/chain-of-thought/issues) to report any bugs or suggest new features.
