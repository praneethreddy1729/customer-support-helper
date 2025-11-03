# Sample Run - Customer Support Helper

This file demonstrates a recorded run of the application with actual JSON output and metrics.

## Command Executed

```bash
python3 src/run_query.py --query="How do I track my order?"
```

## JSON Output

```json
{
  "answer": "To track your order, please visit our website and log into your account. Navigate to the 'Orders' section, where you can find the tracking information for your recent purchases. Alternatively, you can use the tracking link sent to your email after your order was shipped.",
  "confidence": "high",
  "actions": [
    "send_response",
    "provide_documentation"
  ],
  "category": "order_tracking"
}
```

## Metrics (from metrics.csv)

| Metric | Value |
|--------|-------|
| Timestamp | 2025-11-03T11:50:36.230757 |
| Tokens (Prompt) | 828 |
| Tokens (Completion) | 83 |
| Total Tokens | 911 |
| Latency | 2,507.23 ms (~2.5 seconds) |
| Estimated Cost | $0.000174 USD |
| Model | openai/gpt-4o-mini |
| Status | Success (no errors) |

## Verification

The system successfully:
- ✓ Accepted the user query
- ✓ Passed safety validation checks
- ✓ Called OpenRouter API with gpt-4o-mini model
- ✓ Returned valid JSON with required fields: answer, confidence, actions, category
- ✓ Logged complete metrics to `src/metrics/metrics.csv`
- ✓ Completed in 2.5 seconds with cost of $0.000174

This demonstrates the complete workflow from query input to JSON output with full metrics tracking.
