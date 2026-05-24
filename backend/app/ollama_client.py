import logging
from time import perf_counter
from typing import TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from .config import settings


logger = logging.getLogger("super_bank.ollama")
ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


def _ms(nanoseconds: int | float | None) -> int | None:
    return round(nanoseconds / 1_000_000) if nanoseconds is not None else None


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
                "keep_alive": settings.ollama_keep_alive,
                "options": {"temperature": 0.0},
            },
            timeout=settings.llm_timeout_seconds,
        )
        response.raise_for_status()
        payload = response.json()
        raw = str(payload.get("response", "")).strip()
        parsed = response_model.model_validate_json(raw)
        logger.info(
            "ollama.structured_completed task=%s model=%s wall_ms=%d load_ms=%s eval_ms=%s",
            task,
            settings.llm_model,
            round((perf_counter() - started) * 1000),
            _ms(payload.get("load_duration")),
            _ms(payload.get("eval_duration")),
        )
        return parsed
    except (httpx.HTTPError, ValidationError, ValueError, KeyError):
        logger.exception(
            "ollama.structured_failed task=%s model=%s wall_ms=%d",
            task,
            settings.llm_model,
            round((perf_counter() - started) * 1000),
        )
        return None
