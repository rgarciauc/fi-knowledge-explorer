import re
from difflib import SequenceMatcher

from .config import settings
from .intent_models import EntityCandidate


STOPWORDS = {
    "a", "an", "and", "are", "all", "about", "after", "be", "by", "can",
    "does", "down", "everything", "for", "from", "give", "goes", "if", "in",
    "is", "it", "me", "of", "on", "or", "please", "related", "show", "system",
    "the", "to", "what", "when", "which", "who", "with", "would",
}


def normalize(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def meaningful_tokens(value: str) -> list[str]:
    return [
        token for token in normalize(value).split()
        if len(token) >= 3 and token not in STOPWORDS
    ]


def _ratio(left: str, right: str) -> float:
    return SequenceMatcher(None, left, right).ratio() if left and right else 0.0


def _candidate_score(search_text: str, row: dict) -> float:
    name = normalize(str(row.get("name", "")))
    node_id = normalize(str(row.get("node_id", "")))
    description = normalize(str(row.get("description", "")))
    search = normalize(search_text)

    if not name:
        return 0.0
    if name in search or node_id in search:
        return 1.0

    search_tokens = meaningful_tokens(search)
    candidate_tokens = meaningful_tokens(f"{name} {node_id}")
    token_score = max(
        (_ratio(left, right) for left in search_tokens for right in candidate_tokens),
        default=0.0,
    )
    phrase_score = max(_ratio(search, name), _ratio(search, node_id))
    description_score = max(
        (_ratio(token, word) for token in search_tokens for word in meaningful_tokens(description)),
        default=0.0,
    )
    return min(1.0, max(token_score, phrase_score, description_score * 0.84))


def find_entity_candidates(
    question: str,
    catalog: list[dict],
    *,
    labels: set[str] | None = None,
    term: str | None = None,
    limit: int = 5,
) -> list[EntityCandidate]:
    search_text = f"{term or ''} {question}".strip()
    matches: list[EntityCandidate] = []
    for row in catalog:
        label = str(row.get("label", ""))
        if labels and label not in labels:
            continue
        score = _candidate_score(search_text, row)
        if score < settings.entity_match_threshold:
            continue
        matches.append(
            EntityCandidate(
                label=label,
                node_id=str(row.get("node_id", "")),
                name=str(row.get("name", "")),
                score=round(score, 3),
                description=str(row.get("description", "") or ""),
            )
        )
    matches.sort(key=lambda item: item.score, reverse=True)
    return matches[:limit]


def best_candidate_for_intent(intent: str, candidates: list[EntityCandidate]) -> EntityCandidate | None:
    label_by_intent = {
        "system_impact": {"System"},
        "process_pipeline": {"BusinessProcess"},
        "next_step": {"ProcessStep"},
        "employee_search": {"Employee"},
        "ownership_search": {"System", "BusinessProcess"},
    }
    labels = label_by_intent.get(intent)
    for candidate in candidates:
        if labels is None or candidate.label in labels:
            return candidate
    return None
