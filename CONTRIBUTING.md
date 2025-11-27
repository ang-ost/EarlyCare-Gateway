# Contributing to EarlyCare Gateway

Thank you for your interest in contributing to EarlyCare Gateway! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for all contributors.

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in Issues
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - System information (OS, Python version, etc.)
   - Relevant logs or screenshots

### Suggesting Enhancements

1. Check if the enhancement has been suggested
2. Create an issue describing:
   - Use case and motivation
   - Proposed solution
   - Alternative approaches considered

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add/update tests
5. Ensure all tests pass (`pytest`)
6. Update documentation
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Development Setup

```bash
# Clone repository
git clone https://github.com/your-org/earlycare-gateway.git
cd earlycare-gateway

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
flake8 src/
black src/ --check
mypy src/
```

## Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Maximum line length: 100 characters
- Use type hints where appropriate
- Write docstrings for all public functions/classes

## Testing

- Write unit tests for new features
- Maintain or improve code coverage
- Include integration tests for system components
- Test privacy/security features thoroughly

## Documentation

- Update README.md for user-facing changes
- Add docstrings to new functions/classes
- Update configuration documentation
- Include examples for new features

## Commit Messages

Format: `type(scope): description`

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation
- `test`: Tests
- `refactor`: Code refactoring
- `perf`: Performance improvement
- `chore`: Maintenance

Example: `feat(strategy): add ensemble model support`

## Review Process

1. Maintainers review PRs within 3-5 business days
2. Address feedback and requested changes
3. Maintain clean commit history
4. Ensure CI/CD checks pass

## Questions?

Open an issue or contact the maintainers.

Thank you for contributing!
