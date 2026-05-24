from app.db import _json_safe
from app.service import _definition_concept


def test_dataset_definition_is_a_fast_path() -> None:
    assert _definition_concept("what is a dataset?") == "dataset"
    assert _definition_concept("Define a data pipeline") == "data pipeline"


def test_non_definition_is_not_routed_to_fast_path() -> None:
    assert _definition_concept("Which datasets are used by Payment Processing?") is None


def test_json_safe_recursively_preserves_plain_values() -> None:
    assert _json_safe({"nested": [1, "x"]}) == {"nested": [1, "x"]}
