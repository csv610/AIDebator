"""Base participant class for debate platform."""

import logging
from abc import ABC, abstractmethod

from litellm import completion

logger = logging.getLogger(__name__)


class Participant(ABC):
    """Base class for all debate participants."""

    def __init__(self, name: str, model: str):
        """
        Initialize participant.

        Args:
            name: Participant's display name
            model: LLM model identifier (e.g., 'gpt-4', 'claude-3-opus-20240229')
        """
        self.name = name
        self.model = model

    @abstractmethod
    def get_role(self) -> str:
        """Return participant's role."""
        pass

    def generate_response(self, prompt: str, max_tokens: int = 1000, response_format: type = None, temperature: float = 0.7) -> str:
        """
        Generate response using litellm.

        Args:
            prompt: The prompt to send to the model
            max_tokens: Maximum tokens in response
            response_format: Optional Pydantic model class for structured output
            temperature: Sampling temperature (0.0 to 1.0)

        Returns:
            Generated response text (JSON string if response_format is provided)

        Raises:
            Exception: If API call fails
        """
        try:
            logger.debug(f"Generating response for {self.name} using {self.model}")
            
            kwargs = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature
            }
            
            if response_format:
                try:
                    kwargs["response_format"] = response_format
                    response = completion(**kwargs)
                except Exception as e:
                    if "UnsupportedParamsError" in str(e) or "response_format" in str(e):
                        logger.warning(f"Model {self.model} does not support response_format. Falling back to text response.")
                    else:
                        raise e
            else:
                response = completion(**kwargs)
            return response.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating response for {self.name}: {str(e)}")
            raise

    @staticmethod
    def count_words(text: str) -> int:
        """Count words in text."""
        return len(text.split())
