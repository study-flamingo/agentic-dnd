# Contributing to Agentic D&D

Thanks for your interest in contributing! This project is an experiment in AI agents playing tabletop RPGs together, and we welcome improvements from both humans and agents.

## Ways to Contribute

### Report Issues
- Bug reports for the scripts
- Documentation improvements
- Feature requests
- Gameplay balance concerns

### Submit Code
- Bug fixes
- New features
- Additional game system support
- Improved verification methods

### Improve Documentation
- Clarify existing docs
- Add examples
- Translate to other languages
- Write tutorials

### Playtest
- Run campaigns using the system
- Report what works and what doesn't
- Suggest improvements based on actual play

## Development Setup

1. Clone the repo:
   ```bash
   git clone https://github.com/study-flamingo/agentic-dnd.git
   cd agentic-dnd
   ```

2. Get a random.org API key for testing:
   ```bash
   export RANDOM_ORG_API_KEY="your-test-key"
   ```

3. Test the scripts:
   ```bash
   ./scripts/roll.sh 1 20 "TestCharacter" "Test roll"
   ```

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Test thoroughly
5. Commit with clear messages (`git commit -m 'Add amazing feature'`)
6. Push to your fork (`git push origin feature/amazing-feature`)
7. Open a Pull Request

## Code Style

### Shell Scripts
- Use `#!/bin/bash` shebang
- Include usage comments at the top
- Handle errors gracefully (`set -e` where appropriate)
- Quote variables to handle spaces

### Python Scripts
- Python 3.6+ compatible
- No external dependencies (stdlib only)
- Include docstrings
- Type hints appreciated but not required

### Documentation
- Markdown format
- Clear headings
- Code examples where helpful
- Keep lines under 100 characters

## Commit Messages

Use clear, descriptive commit messages:

```
Good:
- Add support for advantage/disadvantage rolls
- Fix verification script JSON parsing
- Update gameplay-loop docs with initiative rules

Bad:
- Fix stuff
- Updates
- WIP
```

## Testing

Before submitting:
1. Test roll scripts with various dice combinations
2. Test verification with both valid and invalid signatures
3. Ensure documentation examples are accurate

## Questions?

- Open an issue for general questions
- Tag maintainers for urgent matters

## Code of Conduct

Be respectful. This is a collaborative project for fun. Don't be a jerk.

## License

By contributing, you agree that your contributions will be licensed under the GPL v3 license.
