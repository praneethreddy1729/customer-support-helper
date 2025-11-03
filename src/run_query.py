from openai import OpenAI
from dotenv import load_dotenv
import os
import tiktoken
import json
import time
import argparse
import csv
from datetime import datetime
from pathlib import Path
from validation import validate_response_schema, get_fallback_response, check_token_limits

class CustomerSupportHelper:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("OPENROUTER_API_KEY")
        base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")

        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing. Please ensure it's added to .env file")

        self.client = OpenAI(
            api_key=api_key,
            base_url=base_url
        )

        self.model = "openai/gpt-4o-mini"
        
        # Load system prompt from file
        prompt_path = Path(__file__).parent / 'prompts' / 'main_prompt.txt'
        with open(prompt_path, 'r') as f:
            self.system_prompt = f.read()
        
        # Cost per 1M tokens in USD (gpt-4o-mini pricing)
        self.input_token_cost = 0.15  # $0.15 per 1M input tokens
        self.output_token_cost = 0.60  # $0.60 per 1M output tokens
        
        # Initialize tokenizer for estimation
        self.encoding = tiktoken.encoding_for_model("gpt-4o-mini")

    def moderate_and_sanitize_user_query(self, query):
        """Sanitize user query and check for adversarial inputs using pattern matching"""
        from safety import check_safety
        
        # Basic sanitization
        query = query.strip()
        
        # Check for safety issues (simple pattern-based checks, no API calls)
        is_safe, reason = check_safety(query)
        if not is_safe:
            raise ValueError(f"Query failed safety check: {reason}")
        
        return query

    def count_tokens(self, text):
        """Count tokens in a text string"""
        return len(self.encoding.encode(text))

    def process_query(self, query: str) -> dict:
        """
        Process a user query and return structured JSON response with metrics
        
        Args:
            query: User's question
            
        Returns:
            dict with response and metrics
        """
        start_time = time.time()
        
        try:
            # Sanitize and moderate query
            user_query = self.moderate_and_sanitize_user_query(query)
            
            # Count tokens before API call
            system_tokens = self.count_tokens(self.system_prompt)
            user_tokens = self.count_tokens(user_query)
            
            # Check token limits
            within_limits, limit_msg = check_token_limits(user_tokens, system_tokens)
            if not within_limits:
                raise ValueError(limit_msg)
            
            estimated_prompt_tokens = system_tokens + user_tokens
            
            # Call LLM API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={'type': 'json_object'}
            )
            
            # Extract response content
            content = response.choices[0].message.content
            
            # Parse and validate JSON response
            try:
                parsed_response = json.loads(content)
                
                # Validate response schema
                is_valid, error_msg = validate_response_schema(parsed_response)
                if not is_valid:
                    print(f"Warning: Response validation failed: {error_msg}")
                    parsed_response = get_fallback_response(content, "validation_error")
                    
            except json.JSONDecodeError as e:
                print(f"Warning: JSON parse error: {e}")
                parsed_response = get_fallback_response(content, "parse_error")
            
            # Calculate metrics
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            tokens_prompt = response.usage.prompt_tokens
            tokens_completion = response.usage.completion_tokens
            total_tokens = response.usage.total_tokens
            
            # Calculate cost in USD
            estimated_cost_usd = (
                (tokens_prompt * self.input_token_cost / 1_000_000) +
                (tokens_completion * self.output_token_cost / 1_000_000)
            )
            
            # Prepare metrics
            metrics = {
                "timestamp": datetime.now().isoformat(),
                "tokens_prompt": tokens_prompt,
                "tokens_completion": tokens_completion,
                "total_tokens": total_tokens,
                "latency_ms": round(latency_ms, 2),
                "estimated_cost_usd": round(estimated_cost_usd, 6),
                "model": self.model
            }
            
            # Log metrics
            self.log_metrics(metrics)
            
            return {
                "response": parsed_response,
                "metrics": metrics
            }
            
        except Exception as e:
            # Handle errors gracefully
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            error_response = {
                "answer": f"An error occurred: {str(e)}",
                "confidence": "none",
                "actions": ["contact_human_agent", "retry_later"],
                "error": True
            }
            
            error_metrics = {
                "timestamp": datetime.now().isoformat(),
                "tokens_prompt": 0,
                "tokens_completion": 0,
                "total_tokens": 0,
                "latency_ms": round(latency_ms, 2),
                "estimated_cost_usd": 0.0,
                "model": self.model,
                "error": str(e)
            }
            
            self.log_metrics(error_metrics)
            
            return {
                "response": error_response,
                "metrics": error_metrics
            }

    def log_metrics(self, metrics):
        """Log metrics to CSV file"""
        metrics_dir = Path(__file__).parent / 'metrics'
        metrics_dir.mkdir(exist_ok=True)
        
        csv_file = metrics_dir / 'metrics.csv'
        
        # Check if file exists to determine if we need to write headers
        file_exists = csv_file.exists()
        
        with open(csv_file, 'a', newline='') as f:
            fieldnames = ['timestamp', 'tokens_prompt', 'tokens_completion', 
                         'total_tokens', 'latency_ms', 'estimated_cost_usd', 
                         'model', 'error']
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if not file_exists:
                writer.writeheader()
            
            # Ensure all fields are present
            metrics_copy = metrics.copy()
            if 'error' not in metrics_copy:
                metrics_copy['error'] = ''
            
            writer.writerow(metrics_copy)


def main():
    parser = argparse.ArgumentParser(
        description='Customer Support Helper - Process support queries with AI'
    )
    parser.add_argument(
        '--query',
        type=str,
        required=True,
        help='The customer support query to process'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Optional: path to save JSON output (default: print to console)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize helper
        helper = CustomerSupportHelper()
        
        # Process query
        result = helper.process_query(args.query)
        
        # Format output
        output = json.dumps(result, indent=2)
        
        # Save or print output
        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Response saved to {args.output}")
        else:
            # Just print the JSON response
            print(json.dumps(result['response'], indent=2))
        
    except Exception as e:
        print(f"Error: {str(e)}")
        exit(1)


if __name__ == "__main__":
    main()
