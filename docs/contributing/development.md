# Development Guide

Set up your development environment for ARVOS SDK.

## Prerequisites

- Python 3.8+
- Git
- Virtual environment (recommended)

## Setup

### 1. Clone Repository

```bash
git clone https://github.com/jaskirat1616/arvos-sdk.git
cd arvos-sdk
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # Mac/Linux
# OR
venv\Scripts\activate  # Windows
```

### 3. Install Dependencies

```bash
pip install -e ".[dev]"
```

### 4. Install Protocol Dependencies

```bash
# For all protocols
pip install grpcio grpcio-tools protobuf paho-mqtt bleak mcap aioquic
```

## Project Structure

```
arvos-sdk/
├── python/
│   └── arvos/
│       ├── __init__.py
│       ├── client.py
│       ├── server.py
│       ├── data_types.py
│       ├── servers/
│       │   ├── base_server.py
│       │   ├── grpc_server.py
│       │   ├── mqtt_server.py
│       │   └── ...
│       └── protos/
├── examples/
├── docs/
├── tests/
└── setup.py
```

## Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=arvos tests/

# Run specific test
pytest tests/test_data_types.py
```

## Building Documentation

```bash
# Serve locally
mkdocs serve

# Build static site
mkdocs build
```

## Code Style

### Python

- Follow PEP 8
- Use type hints
- Add docstrings
- Maximum line length: 100

### Formatting

```bash
# Format code
black python/

# Check style
flake8 python/
```

## Next Steps

- [Contributing Overview](overview.md) - Contribution guidelines
- [GitHub Repository](https://github.com/jaskirat1616/arvos-sdk) - Submit PRs

