from math import isfinite

DEFAULT_WEIGHTS = {
    'compliance': .25,
    'risk': .20,
    'financial': .15,
    'time': .15,
    'strategy': .15,
    'stakeholder': .10,
}


def _score(value):
    """Return a bounded score, or None when the input is absent/invalid."""
    if value is None or isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if not isfinite(number):
        return None
    return max(0.0, min(100.0, number))


def normalize_weights(weights=None):
    candidate = weights or DEFAULT_WEIGHTS
    if not isinstance(candidate, dict) or not candidate:
        raise ValueError('Scoring weights must be a non-empty object')
    cleaned = {}
    for criterion, weight in candidate.items():
        if criterion not in DEFAULT_WEIGHTS:
            raise ValueError(f'Unknown scoring criterion: {criterion}')
        try:
            number = float(weight)
        except (TypeError, ValueError) as exc:
            raise ValueError(f'Invalid weight for {criterion}') from exc
        if not isfinite(number) or number < 0:
            raise ValueError(f'Weight for {criterion} must be finite and non-negative')
        cleaned[criterion] = number
    total = sum(cleaned.values())
    if total <= 0:
        raise ValueError('At least one scoring weight must be greater than zero')
    return {criterion: round(weight / total, 6) for criterion, weight in cleaned.items()}


def score_options(options, weights=None):
    normalized = normalize_weights(weights)
    output = []
    for option in options:
        criteria = option.get('criterion_scores') if isinstance(option, dict) else None
        criteria = criteria if isinstance(criteria, dict) else {}
        parsed = {criterion: _score(criteria.get(criterion)) for criterion in normalized}
        missing = [criterion for criterion, value in parsed.items() if value is None]
        item = dict(option)
        item['score_weights'] = normalized
        item['score_completeness'] = round((len(parsed) - len(missing)) / len(parsed), 4)
        item['missing_criteria'] = missing
        item['score_valid'] = not missing
        item['weighted_score'] = (
            round(sum(parsed[criterion] * weight for criterion, weight in normalized.items()), 2)
            if not missing else None
        )
        output.append(item)
    return sorted(
        output,
        key=lambda item: (item['score_valid'], item['weighted_score'] if item['weighted_score'] is not None else -1),
        reverse=True,
    )


def compose_confidence(evidence, scored_options):
    facts = evidence.get('facts') or []
    unknowns = evidence.get('missing_information') or []
    sources = evidence.get('sources') or []
    evidence_total = len(facts) + len(unknowns)
    evidence_completeness = len(facts) / evidence_total if evidence_total else 0.0
    source_support = min(1.0, len(sources) / 3.0)
    score_coverage = (
        sum(float(option.get('score_completeness', 0)) for option in scored_options) / len(scored_options)
        if scored_options else 0.0
    )
    valid_scores = sorted(
        [float(option['weighted_score']) for option in scored_options if option.get('score_valid')],
        reverse=True,
    )
    separation = min(1.0, (valid_scores[0] - valid_scores[1]) / 20.0) if len(valid_scores) > 1 else 0.0
    confidence = (
        .35 * evidence_completeness
        + .15 * source_support
        + .35 * score_coverage
        + .15 * separation
    )
    if not sources:
        confidence = min(confidence, .65)
    value = round(max(0.0, min(1.0, confidence)), 2)
    return value, {
        'method': 'deterministic-v1',
        'evidence_completeness': round(evidence_completeness, 4),
        'source_support': round(source_support, 4),
        'score_coverage': round(score_coverage, 4),
        'option_separation': round(separation, 4),
        'uncalibrated_model_confidence_excluded': True,
    }
