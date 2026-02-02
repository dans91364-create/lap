# Contributing to LAP

Thank you for your interest in contributing to LAP!

## Development Setup

1. Fork the repository
2. Clone your fork:
```bash
git clone https://github.com/YOUR_USERNAME/lap.git
cd lap
```

3. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

5. Copy environment variables:
```bash
cp .env.example .env
```

## Running Tests

```bash
pytest tests/ -v
```

## Code Style

We use:
- **black** for code formatting
- **flake8** for linting

Format your code before committing:
```bash
black src/ tests/
flake8 src/ tests/
```

## Pull Request Process

1. Create a new branch for your feature:
```bash
git checkout -b feature/your-feature-name
```

2. Make your changes
3. Add tests for new functionality
4. Run tests to ensure everything works
5. Commit your changes:
```bash
git commit -m "Add your feature description"
```

6. Push to your fork:
```bash
git push origin feature/your-feature-name
```

7. Create a Pull Request

## Guidelines

- Write clear commit messages
- Add tests for new features
- Update documentation as needed
- Follow Python best practices
- Keep pull requests focused and small

## Questions?

Open an issue for questions or discussions!
