"""
JSON Schema Validation for Customer Support Helper responses.
"""

import re
from typing import Tuple

# Token limits for safety and cost control
MAX_USER_QUERY_TOKENS = 1500  # Max tokens in user query
MAX_TOTAL_PROMPT_TOKENS = 2500  # Max total tokens (system + user)


def validate_response_schema(response: dict) -> Tuple[bool, str]:
    """
    Validate that response matches expected schema.
    
    Required fields:
    - answer: non-empty string
    - confidence: one of [high, medium, low, none]
    - actions: non-empty list of snake_case strings
    - category: snake_case string
    
    Args:
        response: Dictionary to validate
        
    Returns:
        (is_valid, error_message) tuple
    """
    if not isinstance(response, dict):
        return False, "Response must be a dictionary"
    
    # Check required fields
    required_fields = ["answer", "confidence", "actions", "category"]
    for field in required_fields:
        if field not in response:
            return False, f"Missing required field: {field}"
    
    # Validate answer
    if not isinstance(response["answer"], str):
        return False, "answer must be a string"
    if len(response["answer"].strip()) == 0:
        return False, "answer cannot be empty"
    
    # Validate confidence
    valid_confidence = ["high", "medium", "low", "none"]
    if response["confidence"] not in valid_confidence:
        return False, f"confidence must be one of {valid_confidence}, got: {response['confidence']}"
    
    # Validate actions
    if not isinstance(response["actions"], list):
        return False, "actions must be a list"
    if len(response["actions"]) == 0:
        return False, "actions cannot be empty"
    
    for action in response["actions"]:
        if not isinstance(action, str):
            return False, f"actions must contain strings, got: {type(action)}"
        if len(action) == 0:
            return False, "action cannot be empty string"
        # Actions should use snake_case
        if not re.match(r'^[a-z]+(_[a-z]+)*$', action):
            return False, f"action should be snake_case: {action}"
    
    # Validate category
    if not isinstance(response["category"], str):
        return False, "category must be a string"
    if len(response["category"].strip()) == 0:
        return False, "category cannot be empty"
    
    return True, "Valid"


def check_token_limits(user_tokens: int, system_tokens: int) -> Tuple[bool, str]:
    """
    Check if token counts are within acceptable limits.
    
    Args:
        user_tokens: Number of tokens in user query
        system_tokens: Number of tokens in system prompt
        
    Returns:
        (is_valid, error_message) tuple
    """
    if user_tokens > MAX_USER_QUERY_TOKENS:
        return False, f"Query too long: {user_tokens} tokens (max: {MAX_USER_QUERY_TOKENS})"
    
    total_tokens = user_tokens + system_tokens
    if total_tokens > MAX_TOTAL_PROMPT_TOKENS:
        return False, f"Total prompt too long: {total_tokens} tokens (max: {MAX_TOTAL_PROMPT_TOKENS})"
    
    return True, "Within limits"


def get_fallback_response(content: str, reason: str = "parse_error") -> dict:
    """
    Create a fallback response when validation fails.
    
    Args:
        content: The original content from LLM
        reason: Why we're using fallback (parse_error, validation_error)
        
    Returns:
        Valid response dictionary
    """
    return {
        "answer": content if content else "I apologize, but I'm having trouble processing your request. Please contact our support team directly.",
        "confidence": "low",
        "actions": ["escalate_to_human", "review_response"],
        "category": "general_inquiry"
    }

