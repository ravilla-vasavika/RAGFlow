"""LLM integration service using OpenAI."""

from abc import ABC, abstractmethod
from openai import OpenAI
import os
from app.utils.logger import setup_logger

logger = setup_logger(__name__)


class LLMBase(ABC):
    """Abstract base class for LLM implementations."""

    @abstractmethod
    def generate_answer(self, context: str, query: str) -> str:
        """Generate an answer based on context and query."""
        pass


class OpenAILLM(LLMBase):
    """OpenAI LLM implementation using gpt-4o-mini."""

    def __init__(
        self,
        api_key: str = None,
        model: str = "gpt-4o-mini",
        stream: bool = False
    ):
        """
        Initialize OpenAI LLM service.

        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY env var)
            model: Model to use for completion
            stream: Whether to stream responses (default: False)
        """
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY not set in environment")

        self.client = OpenAI(api_key=api_key)
        self.model = model
        self.stream = stream

    def generate_answer(self, context: str, query: str) -> str:
        """
        Generate a grounded answer from context using the LLM.

        Args:
            context: Concatenated chunk texts to use as grounding
            query: User's question

        Returns:
            Generated answer string
        """
        if not context.strip():
            logger.warning("Empty context passed to LLM — returning fallback")
            return "I could not find relevant information in the selected documents."

        prompt = self._build_prompt(context, query)

        try:
            logger.info(f"Sending request to {self.model}")
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        # Concise system prompt — detailed grounding is in user prompt
                        "content": "You are a precise assistant that answers questions strictly from provided context."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1,   # Low temperature = grounded, deterministic answers
                max_tokens=1000,
                stream=self.stream
            )

            if self.stream:
                answer = ""
                for chunk in response:
                    if chunk.choices[0].delta.content:
                        answer += chunk.choices[0].delta.content
                return answer
            else:
                return response.choices[0].message.content

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def _build_prompt(self, context: str, query: str) -> str:
        """
        Build a RAG prompt that grounds the model strictly in retrieved context.

        The prompt instructs the model to synthesize across chunks rather than
        look for an exact match, which prevents false 'I don't know' responses.
        """
        return f"""Use the context sections below to answer the question.
Synthesize information across all sections to form a complete, detailed answer.
Do not use any knowledge outside of the provided context.
If the answer truly cannot be found in the context, say "I don't know based on the provided documents."

Context:
{context}

Question: {query}

Answer:"""