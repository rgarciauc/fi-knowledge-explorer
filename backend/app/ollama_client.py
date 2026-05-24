import logging
from time import perf_counter
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from .config import settings


logger = logging.getLogger("super_bank.ollama")
ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


def structured_generate(task: str, prompt: str, response_model: type[ResponseModel]) -> ResponseModel | None:
    """Ask Ollama for validated JSON conforming to a Pydantic JSON schema."""
    if not settings.llm_enabled:
        logger.info("ollama.structured_skipped task=%s reason=disabled", task)
        return None

    started = perf_counter()
    try:
        response = httpx.post(
            settings.llm_url,
            json={
                "model": settings.llm_model,
                "prompt": prompt,
                "stream": False,
                "format": response_model.model_json_schema(),
                "options": {"temperature": 0.0},
            },
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        raw = str(response.json().get("response", "")).strip()
        parsed = response_model.model_validate_json(raw)
        logger.info(
            "ollama.structured_completed task=%s model=%s duration_ms=%d",
            task,
            settings.llm_model,
            round((perf_counter() - started) * 1000),
        )
        return parsed
    except (httpx.HTTPError, ValidationError, ValueError, KeyError):
        logger.exception(
            "ollama.structured_failed task=%s model=%s duration_ms=%d",
            task,
            settings.llm_model,
            round((perf_counter() - started) * 1000),
        )
        return None
