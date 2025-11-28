# Contributing to Rider-Pi MCP

Thank you for your interest in contributing to Rider-Pi MCP! This document provides guidelines and instructions for contributing.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue with:

- Clear description of the bug
- Steps to reproduce
- Expected vs. actual behavior
- Environment details (Python version, OS, etc.)
- Error messages or logs (if applicable)

### Suggesting Features

Feature suggestions are welcome! Please create an issue with:

- Clear description of the feature
- Use case and motivation
- Proposed implementation (if you have ideas)
- Examples of how it would be used

### Code Contributions

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow the code style
   - Add tests for new features
   - Update documentation

4. **Test your changes**
   ```bash
   pytest tests/
   ```

5. **Commit your changes**
   ```bash
   git commit -m "Add: Description of your changes"
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

7. **Create a Pull Request**
   - Provide clear description
   - Reference related issues
   - Include test results

## Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write docstrings for all functions
- Keep functions focused and small
- Add comments for complex logic

## Testing

- Write tests for all new features
- Ensure all tests pass
- Aim for good test coverage
- Test edge cases and error conditions

## Documentation

- Update README.md if needed
- Add docstrings to new functions
- Update examples if behavior changes
- Keep roadmap updated

## Security

- Never commit SSH keys or credentials
- Validate all user inputs
- Follow security best practices
- Report security issues privately

## Questions?

Feel free to open an issue or start a discussion if you have questions!

---

Thank you for contributing! 🎉

