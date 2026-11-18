from abc import ABC, abstractmethod
from typing import Type, Any
from pydantic import BaseModel, ValidationError
import logging

logger = logging.getLogger(__name__)

class AgentExecutionError(Exception):
    """Raised when an AI agent encounters a validation or execution failure."""
    pass

class BaseAgent(ABC):
    """
    Abstract base class for all SecureMind AI specialized agents.
    Enforces deterministic validation schemas on both inputs and outputs.
    """
    agent_id: str
    agent_name: str
    input_schema: Type[BaseModel]
    output_schema: Type[BaseModel]

    def __init__(self, llm_client=None):
        self.llm_client = llm_client

    def validate_input(self, raw_data: dict) -> BaseModel:
        try:
            return self.input_schema(**raw_data)
        except ValidationError as e:
            logger.error(f"[{self.agent_id}] Input schema validation failed: {e}")
            raise AgentExecutionError(f"Input validation error in {self.agent_name}: {e}")

    def validate_output(self, raw_output: dict) -> BaseModel:
        try:
            return self.output_schema(**raw_output)
        except ValidationError as e:
            logger.error(f"[{self.agent_id}] Output schema validation failed: {e}")
            raise AgentExecutionError(f"Output validation error in {self.agent_name}: {e}")

    @abstractmethod
    def run(self, validated_input: BaseModel) -> BaseModel:
        """Core execution logic of the specialized agent."""
        pass

    def execute(self, payload: dict) -> dict:
        """
        Public execution entrypoint with pre- and post-validation hooks.
        """
        validated_input = self.validate_input(payload)
        validated_output = self.run(validated_input)
        if isinstance(validated_output, dict):
            validated_output = self.validate_output(validated_output)
        return validated_output.model_dump()
