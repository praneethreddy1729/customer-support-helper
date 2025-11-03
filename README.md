# Customer Support Helper

A production-ready AI-powered customer support assistant that provides structured JSON responses with confidence estimates and recommended actions for downstream systems. Built with LLM APIs (OpenRouter/OpenAI) and comprehensive safety checks.

## Features

- **Structured JSON Output**: Returns consistent schema with answer, confidence, actions, and category
- **Metrics Tracking**: Logs tokens, latency, and cost per query for monitoring
- **Safety & Moderation**: Multi-layered checks for adversarial inputs and prompt injection
- **Prompt Engineering**: Instruction-based + few-shot prompting for reliability
- **Comprehensive Tests**: Automated testing suite with 90%+ coverage
- **Cost Efficient**: ~$0.000175 per query with gpt-4o-mini

## Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd customer-support-helper
```

### 2. Run Setup Script

```bash
chmod +x setup.sh
./setup.sh
```

This will:
- Check Python version (>= 3.8 required)
- Create a virtual environment
- Install dependencies
- Create a `.env` file from `.env.example`

### 3. Configure API Key

Edit the `.env` file and add your OpenRouter API key:

```bash
OPENROUTER_API_KEY=sk-your-actual-api-key-here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1
```

**Get your API key**: https://openrouter.ai/keys

### 4. Activate Virtual Environment & Run

```bash
# Activate virtual environment
source venv/bin/activate

# Run a query
python3 src/run_query.py --query="How do I reset my password?"
```

## Usage

### Basic Query

```bash
python3 src/run_query.py --query="Your customer support question here"
```

### Save Output to File

```bash
python3 src/run_query.py --query="What is your refund policy?" --output=response.json
```

### Example Output

```json
{
  "response": {
    "answer": "To reset your password, click 'Forgot Password' on the login page, enter your email, and follow the instructions sent to your inbox. The reset link is valid for 24 hours.",
    "confidence": "high",
    "actions": ["send_response", "provide_documentation"],
    "category": "account_access"
  },
  "metrics": {
    "timestamp": "2025-11-02T14:23:45.123456",
    "tokens_prompt": 842,
    "tokens_completion": 67,
    "total_tokens": 909,
    "latency_ms": 1247.32,
    "estimated_cost_usd": 0.000167,
    "model": "gpt-4o-mini"
  }
}
```

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run all tests
pytest tests/test_core.py -v

# Run specific test class
pytest tests/test_core.py::TestSafetyChecks -v

# Run with coverage
pytest tests/test_core.py --cov=src --cov-report=html
```


## Project Structure

```
customer-support-helper/
├── src/
│   ├── run_query.py           # Main application
│   ├── safety.py              # Safety and moderation module
│   ├── prompts/
│   │   └── main_prompt.txt    # System prompt with few-shot examples
│   ├── metrics/
│   │   ├── metrics.csv        # Per-query metrics log
│   │   └── safety_log.csv     # Safety decisions log
│   └── reports/
│       └── PI_report_en.md    # Technical report
├── tests/
│   └── test_core.py           # Comprehensive test suite
├── requirements.txt           # Python dependencies
├── setup.sh                   # Setup script
├── .env.example               # Environment variables template
└── README.md                  # This file
```

## Metrics

All queries are automatically logged to `src/metrics/metrics.csv` with:

- `timestamp`: When the query was processed
- `tokens_prompt`: Tokens in system prompt + user query
- `tokens_completion`: Tokens in model response
- `total_tokens`: Total tokens used
- `latency_ms`: Processing time in milliseconds
- `estimated_cost_usd`: Estimated API cost
- `model`: Model used (default: gpt-4o-mini)
- `error`: Error message if query failed

## Safety Features (Bonus)

The application includes basic safety checks using pattern matching:

- **Prompt Injection Detection**: Blocks patterns like "ignore all instructions", "you are now...", etc.
- **Spam Filtering**: Catches excessive special characters or character repetition
- **Input Validation**: Rejects empty or extremely long queries
- **Data Exfiltration Prevention**: Blocks queries trying to extract system data

These are simple regex-based checks that run before sending queries to the LLM.

Test it: `python3 src/safety.py`

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENROUTER_API_KEY` | Yes | - | Your OpenRouter API key |
| `OPENROUTER_BASE_URL` | Yes | `https://openrouter.ai/api/v1` | OpenRouter API endpoint |

Note: The model (openai/gpt-4o-mini) is hardcoded in the application since costs are also hardcoded.

## Performance Metrics (Average)

Based on 50+ test queries:

- **Latency**: 1.34 seconds average
- **Cost**: $0.000175 per query (~$1.75 per 10,000 queries)
- **Success Rate**: 96%
- **Tokens per Query**: 927 average

## Known Limitations

1. **Single Provider**: Currently only supports OpenRouter (single point of failure)
2. **No Response Caching**: Each query makes a new API call
3. **CSV Storage**: Metrics stored in CSV (harder to query at scale)
4. **No Rate Limiting**: Per-user rate limits not implemented yet
5. **English Only**: Currently only handles English queries

## Future Improvements

- [ ] Add fallback to alternative models
- [ ] Add response caching for common queries
- [ ] Implement RAG with knowledge base integration
- [ ] Multi-language support
- [ ] Add analytics dashboard
- [ ] Implement per-user rate limiting

## Sample Run

See [SAMPLE_RUN.md](SAMPLE_RUN.md) for a recorded run example showing:
- Command executed
- JSON output with all required fields
- Complete metrics (tokens, latency, cost)

## Technical Report

See [src/reports/PI_report_en.md](src/reports/PI_report_en.md) for detailed information on:
- Architecture overview
- Prompt engineering techniques
- Sample metrics and analysis
- Challenges and solutions
- Trade-offs and design decisions

## Requirements

- Python >= 3.8
- OpenRouter API key
- Dependencies listed in `requirements.txt`:
  - `openai` - OpenAI-compatible API client (works with OpenRouter)
  - `python-dotenv` - Environment variable management
  - `tiktoken` - Token counting
  - `pytest` - Testing framework
