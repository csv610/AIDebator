"""Organizer participant for debate platform."""

import logging

from .base import Participant

logger = logging.getLogger(__name__)


class Organizer(Participant):
    """Provides neutral overview of debate topic."""

    def get_role(self) -> str:
        """Return role."""
        return "organizer"

    def generate_overview(self, topic: str) -> str:
        """
        Generate neutral overview of the topic (200-300 words).

        Args:
            topic: The debate topic

        Returns:
            Neutral overview text
        """
        prompt = f"""You are a neutral debate organizer. Provide a comprehensive but neutral overview of the following topic in 200-300 words.

Topic: {topic}

Your overview should:
1. Explain the key aspects of the topic
2. Identify main arguments that could be made on both sides
3. Define any important terms or concepts
4. Present historical or current context if relevant
5. Remain completely neutral and unbiased

Overview:"""

        logger.info(f"{self.name} generating overview for topic: {topic[:50]}...")
        response = self.generate_response(prompt, max_tokens=500)
        return response
