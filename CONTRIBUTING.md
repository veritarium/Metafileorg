# Contributing to Virtual File Organizer

Thank you for your interest in contributing to the Virtual File Organizer! We welcome contributions from the community.

## How to Contribute

### Reporting Bugs

If you find a bug, please create an issue on GitHub with:

- A clear, descriptive title
- Steps to reproduce the bug
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)
- Any relevant logs or screenshots

### Suggesting Enhancements

We welcome feature requests! Please create an issue with:

- A clear description of the enhancement
- Why it would be useful
- Any implementation ideas you have

### Pull Requests

1. **Fork the repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/YOUR-USERNAME/Metafileorg.git
   cd Metafileorg
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/amazing-feature
   ```

3. **Make your changes**
   - Write clean, readable code
   - Follow PEP 8 style guidelines
   - Add tests for new features
   - Update documentation as needed

4. **Test your changes**
   ```bash
   # Run existing tests
   pytest file_organizer/tests/

   # Test manually with sample data
   python file_organizer/src/main.py --help
   ```

5. **Commit your changes**
   ```bash
   git add .
   git commit -m "Add amazing feature"

   # Use descriptive commit messages:
   # - Start with a verb (Add, Fix, Update, Remove, etc.)
   # - Keep the first line under 50 characters
   # - Add details in the body if needed
   ```

6. **Push to your fork**
   ```bash
   git push origin feature/amazing-feature
   ```

7. **Create a Pull Request**
   - Go to the original repository on GitHub
   - Click "New Pull Request"
   - Select your fork and branch
   - Describe your changes clearly
   - Reference any related issues

## Development Guidelines

### Code Style

- Follow [PEP 8](https://peps.python.org/pep-0008/)
- Use meaningful variable names
- Add docstrings to functions and classes
- Keep functions focused and small
- Use type hints where appropriate

### Testing

- Write tests for new features
- Ensure all tests pass before submitting PR
- Aim for good test coverage
- Test on multiple platforms if possible

### Documentation

- Update README.md if adding new features
- Add docstrings to new functions
- Update IMPLEMENTATION_SUMMARY.md for bug fixes
- Comment complex logic

### Commit Messages

Good commit message format:

```
Add feature to detect project markers

- Scan for .git, package.json, .sln files
- Group files by detected project
- Add tests for project detection
- Update documentation
```

## Areas Where We Need Help

- **Cross-platform testing** - Testing on macOS, Windows, Linux
- **Performance optimization** - Parallel processing for large datasets
- **UI improvements** - Enhance the Flask web interface
- **Documentation** - Improve user guides and tutorials
- **Bug fixes** - See open issues
- **New features** - See roadmap in README.md

## Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism gracefully
- Focus on what is best for the community
- Show empathy towards others

### Unacceptable Behavior

- Harassment of any kind
- Trolling or inflammatory comments
- Personal attacks
- Publishing others' private information
- Other unethical or unprofessional conduct

### Enforcement

Instances of abusive behavior may be reported by opening an issue or contacting the project maintainers. All complaints will be reviewed and investigated.

## Questions?

Feel free to open an issue with the "question" label if you need help or clarification.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

**Thank you for making Virtual File Organizer better!** 🎉
