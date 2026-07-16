# Configuration

## Environment Variables

All configuration is managed through environment variables loaded from a `.env` file.

### Required

| Variable | Description | Example |
|----------|-------------|---------|
| `NVIDIA_API_KEY` | Your NVIDIA NIM API key | `nvapi-xxxx...` |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `MODEL` | `nvidia/nemotron-3-ultra-550b-a55b` | NVIDIA model identifier |
| `NVIDIA_BASE_URL` | `https://integrate.api.nvidia.com/v1` | API base URL |
| `PROJECT_ROOT` | Current directory | Root directory of the project |
| `TIMEZONE` | `UTC` | Timezone for log dates |
| `MAX_TOKENS` | `2048` | Maximum tokens for AI responses (64–8192) |
| `AI_TEMPERATURE` | `0.7` | AI creativity (0.0–2.0, lower = more deterministic) |

## Setup Steps

### 1. Copy the Template

```bash
cp .env.example .env
```

### 2. Get an NVIDIA API Key

1. Visit [build.nvidia.com](https://build.nvidia.com/)
2. Sign up or log in
3. Navigate to API Keys
4. Create a new key
5. Copy it to your `.env` file

### 3. Choose a Model

The default model is `nvidia/nemotron-3-ultra-550b-a55b`. Available models can be found on the [NVIDIA NIM catalog](https://build.nvidia.com/explore/discover).

Other compatible models:
- `meta/llama-3.1-405b-instruct`
- `meta/llama-3.1-70b-instruct`
- `mistralai/mixtral-8x22b-instruct-v0.1`

### 4. Configure Temperature

| Temperature | Behavior | Best For |
|-------------|----------|----------|
| `0.0–0.3` | Deterministic, focused | Summaries, documentation |
| `0.4–0.7` | Balanced | Daily summaries (default) |
| `0.8–1.5` | Creative, varied | Brainstorming, creative writing |
| `1.5–2.0` | Very creative | Experimental |

## Security Notes

- **Never commit `.env`** — it's in `.gitignore`
- **Never hardcode API keys** in source files
- For CI/CD, use GitHub Secrets: `Settings → Secrets → Actions → NVIDIA_API_KEY`
- The application will function without an API key, but AI features will be disabled
