from app.config import settings
from app.ollama_request_options import ollama_keep_alive_value


def test_plain_negative_number_is_normalized_to_integer(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ollama_keep_alive", "-1")
    assert ollama_keep_alive_value() == -1
    assert isinstance(ollama_keep_alive_value(), int)


def test_duration_value_stays_text(monkeypatch) -> None:
    monkeypatch.setattr(settings, "ollama_keep_alive", "-1m")
    assert ollama_keep_alive_value() == "-1m"
