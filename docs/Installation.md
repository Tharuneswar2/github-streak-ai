# Installation

## Prerequisites

- **Python 3.12+** — [Download](https://www.python.org/downloads/)
- **Git** — [Download](https://git-scm.com/downloads)
- **NVIDIA NIM API Key** — [Get one free](https://build.nvidia.com/)

## Quick Install

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/github-streak-ai.git
cd github-streak-ai
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate    # Linux/macOS
# .venv\Scripts\activate     # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Or install as a package (editable mode):

```bash
pip install -e .
```

### 4. Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and set your NVIDIA API key:

```
NVIDIA_API_KEY=your-key-here
MODEL=nvidia/nemotron-3-ultra-550b-a55b
```

### 5. Verify Installation

```bash
python cli.py help
```

## Development Install

For running tests and linting:

```bash
pip install -e ".[dev]"
```

Run the test suite:

```bash
pytest tests/ -v
```

## Docker (Optional)

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "cli.py", "help"]
```

```bash
docker build -t github-streak-ai .
docker run --env-file .env github-streak-ai
```

## Troubleshooting

- If `pip install` fails, try upgrading pip: `pip install --upgrade pip`
- On Linux, you may need `python3` instead of `python`
- For Git-related errors, ensure Git is installed and the repo is initialized (`git init`)
- See [Troubleshooting.md](Troubleshooting.md) for more details
