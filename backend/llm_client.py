from dotenv import load_dotenv
import os
import logging
from groq import AsyncGroq, APITimeoutError, APIConnectionError, InternalServerError, RateLimitError
from tenacity import retry, wait_exponential, stop_after_attempt, retry_if_exception_type

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Retry only on specific retryable errors, not Auth/Validation errors
RETRYABLE_ERRORS = (APITimeoutError, APIConnectionError, InternalServerError, RateLimitError)

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=10),
    stop=stop_after_attempt(2),
    retry=retry_if_exception_type(RETRYABLE_ERRORS),
    reraise=True
)
async def call_llm(prompt: str, system_prompt: str = "You are a helpful assistant.", json_mode: bool = False) -> str:
    """
    Calls the Groq LLM asynchronously.
    Retries up to 2 times with exponential backoff on retryable network/server errors.
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing.")
        
    client_args = {"api_key": api_key}
    
    # Injectable failure mode to demonstrate retries and fallback
    if os.environ.get("FORCE_LLM_TIMEOUT") == "1":
        logger.info("FORCE_LLM_TIMEOUT is set. Injecting bad base_url to force connection error.")
        client_args["base_url"] = "http://192.0.2.1:8000" # Reserved IP, will timeout
        client_args["timeout"] = 2.0 # Fast timeout
        
    client = AsyncGroq(**client_args)
    
    response_format = {"type": "json_object"} if json_mode else {"type": "text"}
    
    try:
        logger.info("Attempting LLM call...")
        completion = await client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            model="llama-3.3-70b-versatile",
            response_format=response_format,
            temperature=0.0
        )
        return completion.choices[0].message.content or ""
    except RETRYABLE_ERRORS as e:
        logger.warning(f"LLM call encountered retryable error: {type(e).__name__} - {str(e)}")
        raise
    except Exception as e:
        logger.error(f"LLM call encountered fatal error: {type(e).__name__} - {str(e)}")
        raise
