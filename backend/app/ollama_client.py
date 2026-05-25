import logging
from time import perf_counter
from typing import Any, TypeVar

import httpx
from pydantic import BaseModel, ValidationError

from .config import settings


logger = logging.getLogger("super_bank.ollama")
ResponseModel = TypeVar("ResponseModel", bound=BaseModel)


def _ms(nanoseconds: int | float | None) -> int | None:
    return round(nanoseconds / 1_000_000) if nanoseconds is not None else None


def _ollama_base_url() -> str:
    return settings.llm_url.rsplit("/api/", 1)[0]


def _safe_body(response: httpx.Response) -> str:
    try:
        return response.text[:800]
    except Exception:
        return "<response body unavailable>"


def get_ollama_status() -> dict[str, Any]:
    """Expose non-secret runtime diagnostics for local troubleshooting."""
    if not settings.llm_enabled:
        return {"enabled": False, "available": False, "model": settings.llm_model, "reason": "disabled"}
    tags_url = f"{_ollama_base_url()}/api/tags"
    try:
        with httpx.Client(timeout=10.0, trust_env=False) as client:
            response = client.get(tags_url)
        if not response.is_success:
            logger.error("ollama.status_http_error status=%d body=%r url=%s", response.status_code, _safe_body(response), tags_url)
            return {"enabled": True, "available": False, "model": settings.llm_model, "status_code": response.status_code}
        model_names = [item.get("name", "") for item in response.json().get("models", [])]
        configured_available = any(
            name == settings.llm_model or name.startswith(f"{settings.llm_model}:")
            for name in model_names
        )
        return {
            "enabled": True,
            "available": True,
            "model": settings.llm_model,
            "configured_model_available": configured_available,
            "installed_models": model_names,
        }
    except httpx.RequestError as exc:
        logger.exception("ollama.status_connect_failed url=%s error=%s", tags_url, exc)
        return {"enabled": True, "available": False, "model": settings.llm_model, "error": type(exc).__name__}


def structured_generate(task: str, prompt: str, response_model: type[ResponseModel]) -> ResponseModel | None:
    """Ask Ollama for validated JSON conforming to a Pydantic JSON schema."""
    if not settings.llm_enabled:
        logger.info("ollama.structured_skipped task=%s reason=disabled", task)
        return None

    started = perf_counter()
    try:
        with httpx.Client(timeout=settings.llm_timeout_seconds, trust_env=False) as client:
            response = client.post(
                settings.llm_url,
                json={
                    "model": settings.llm_model,
                    "prompt": prompt,
                    "stream": False,
                    "format": response_model.model_json_schema(),
                    "keep_alive": settings.ollama_keep_alive,
                    "options": {"temperature": 0.0},
                },
            )
        if not response.is_success:
            logger.error(
                "ollama.structured_http_error task=%s model=%s status=%d body=%r wall_ms=%d",
                task, settings.llm_model, response.status_code, _safe_body(response),
                round((perf_counter() - started) * 1000),
            )
            return None
        payload = response.json()
        raw = str(payload.get("response", "")).strip()
        parsed = response_model.model_validate_json(raw)
        logger.info(
            "ollama.structured_completed task=%s model=%s wall_ms=%d load_ms=%s eval_ms=%s",
            task, settings.llm_model, round((perf_counter() - started) * 1000),
            _ms(payload.get("load_duration")), _ms(payload.get("eval_duration")),
        )
        return parsed
    except ValidationError as exc:
        logger.error("ollama.structured_invalid_json task=%s model=%s error=%s", task, settings.llm_model, exc)
        return None
    except (httpx.RequestError, ValueError, KeyError):
        logger.exception(
            "ollama.structured_failed task=%s model=%s url=%s wall_ms=%d",
            task, settings.llm_model, settings.llm_url, round((perf_counter() - started) * 1000),
        )
        return None
