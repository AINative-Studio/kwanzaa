# Contributing to Kwanzaa

Thank you for your interest in contributing to Kwanzaa! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Contribution Guidelines](#contribution-guidelines)
- [Data Provenance Requirements](#data-provenance-requirements)
- [Licensing Expectations](#licensing-expectations)
- [Code Standards](#code-standards)
- [Submitting Contributions](#submitting-contributions)

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md). Please read it before contributing.

## Getting Started

1. Fork the repository on GitHub
2. Clone your fork locally
3. Create a new branch for your contribution
4. Make your changes
5. Test your changes thoroughly
6. Submit a pull request

## Contribution Guidelines

### Types of Contributions

We welcome various types of contributions:

- **Bug Reports**: Submit detailed bug reports with steps to reproduce
- **Feature Requests**: Propose new features with clear use cases
- **Code Contributions**: Submit bug fixes, new features, or improvements
- **Documentation**: Improve or expand documentation
- **Data Contributions**: Provide culturally authentic datasets
- **Evaluation Scripts**: Add or improve evaluation methodologies

### Branch Naming Convention

Use descriptive branch names:
- `feature/description` for new features
- `bugfix/description` for bug fixes
- `docs/description` for documentation updates
- `data/description` for data-related contributions

### Commit Messages

Write clear, descriptive commit messages:
- Use the imperative mood ("Add feature" not "Added feature")
- Keep the first line under 72 characters
- Provide detailed context in the body if needed
- Reference related issues with #issue-number

## Data Provenance Requirements

Data contributions are critical to Kwanzaa's mission. All data must meet strict provenance standards:

### Required Documentation

For all data contributions, you must provide:

1. **Source Information**
   - Original source of the data
   - Collection methodology
   - Date of collection
   - Geographic/cultural context

2. **Cultural Authenticity**
   - Verification that data represents authentic cultural knowledge
   - Identification of cultural community represented
   - Documentation of community consultation (if applicable)
   - Attribution to cultural sources

3. **Licensing and Permissions**
   - Clear licensing terms for the data
   - Permissions for use and distribution
   - Any restrictions on use or modification
   - Attribution requirements

4. **Quality Assurance**
   - Data validation methodology
   - Quality checks performed
   - Known limitations or biases
   - Recommended use cases

### Data Format Standards

- Use standard formats (JSON, CSV, Parquet) as appropriate
- Include comprehensive metadata files
- Document schema and field definitions
- Provide sample data when possible

### Cultural Sensitivity

- Respect cultural knowledge and intellectual property
- Obtain appropriate permissions for culturally sensitive information
- Acknowledge indigenous data sovereignty principles
- Avoid appropriation or misrepresentation

## Licensing Expectations

### Code Contributions

All code contributions must be compatible with the project's GPL v3 license:

- By submitting code, you agree to license it under GPL v3
- Ensure you have the right to contribute the code
- Do not include code from incompatible licenses
- Document any third-party dependencies and their licenses

### Data Contributions

Data contributions should use licenses that:
- Allow for open use and modification
- Preserve attribution requirements
- Respect cultural intellectual property
- Are compatible with GPL v3 for integrated works

Recommended licenses for data:
- Creative Commons Attribution 4.0 (CC BY 4.0)
- Creative Commons Attribution-ShareAlike 4.0 (CC BY-SA 4.0)
- Open Data Commons Attribution License (ODC-By)

### Documentation

Documentation contributions are licensed under:
- Creative Commons Attribution 4.0 (CC BY 4.0)

## Code Standards

### General Principles

- Write clean, readable, maintainable code
- Follow language-specific style guides
- Use meaningful variable and function names
- Comment complex logic
- Keep functions focused and single-purpose

### Python Code Standards

- Follow PEP 8 style guide
- Use type hints for function signatures
- Document functions with docstrings (Google or NumPy style)
- Maintain test coverage above 80%
- Use virtual environments for dependencies

### Testing Requirements

- Write unit tests for all new functionality
- Ensure existing tests pass
- Add integration tests where appropriate
- Include edge cases in test coverage
- Document test scenarios

### Documentation Standards

- Update documentation for all changes
- Include docstrings for public APIs
- Provide usage examples
- Document configuration options
- Keep README.md up to date

## Submitting Contributions

### Pull Request Process

1. **Before Submitting**
   - Ensure all tests pass
   - Update documentation
   - Add necessary data provenance information
   - Review your own code for quality

2. **Pull Request Content**
   - Clear title describing the change
   - Detailed description of what and why
   - Reference related issues
   - List any breaking changes
   - Include screenshots for UI changes

3. **Review Process**
   - Address reviewer feedback promptly
   - Make requested changes
   - Keep discussions professional and constructive
   - Be patient during review

4. **After Merge**
   - Delete your feature branch
   - Update your fork
   - Celebrate your contribution!

### Review Criteria

Pull requests will be evaluated on:

- Code quality and style compliance
- Test coverage and passing tests
- Documentation completeness
- Data provenance (for data contributions)
- Cultural sensitivity and accuracy
- Performance impact
- Security considerations

## Questions or Issues?

If you have questions or run into issues:

- Check existing documentation
- Search closed issues for similar questions
- Open a new issue with a clear description
- Join community discussions

## Recognition

Contributors will be recognized in:
- CONTRIBUTORS.md file
- Project documentation
- Release notes for significant contributions

Thank you for contributing to making AI more culturally inclusive and authentic!
