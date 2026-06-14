from pathlib import Path
from sbc.models import Triple, Rule, KnowledgeBase


def parse_triple(tokens: list[str]) -> Triple:
    if len(tokens) < 3:
        raise ValueError(f"Invalid triple: {' '.join(tokens)}")
    if len(tokens) == 3:
        return Triple(tokens[0], tokens[1], tokens[2])
    if len(tokens) == 4:
        try:
            degree = float(tokens[3])
            return Triple(tokens[0], tokens[1], tokens[2], degree)
        except ValueError:
            raise ValueError(f"Invalid degree in triple: {' '.join(tokens)}")
    raise ValueError(f"Invalid triple: {' '.join(tokens)}")


def parse_kb(path: Path) -> KnowledgeBase:
    kb = KnowledgeBase()
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if "<-" in line:
            rule_degree = 1.0
            constraints = []
            clean_line = line.rstrip(".")

            if clean_line.endswith("]"):
                bracket_start = clean_line.rfind("[")
                if bracket_start != -1:
                    ext_str = clean_line[bracket_start + 1 : -1].strip()
                    rule_degree, constraints = parse_extension(ext_str)
                    clean_line = clean_line[:bracket_start].strip().rstrip(".")

            head_str, body_str = clean_line.split("<-", 1)
            try:
                head = parse_triple(head_str.strip().split())
            except ValueError:
                continue

            body = []
            for t in body_str.split(","):
                t = t.strip()
                if "!=" in t:
                    left, right = t.split("!=")
                    constraints.append((left.strip(), "!=", right.strip()))
                else:
                    try:
                        body.append(parse_triple(t.split()))
                    except ValueError:
                        continue

            kb.rules.append(
                Rule(head=head, body=body, constraints=constraints, degree=rule_degree)
            )

        elif line.endswith(".") or line.endswith("]"):
            fact_degree = 1.0
            clean = line

            if clean.endswith("]"):
                bracket_start = clean.rfind("[")
                if bracket_start != -1:
                    ext_str = clean[bracket_start + 1 : -1].strip()
                    fact_degree, _ = parse_extension(ext_str)
                    clean = clean[:bracket_start].strip()

            if clean.endswith("."):
                clean = clean[:-1].strip()
                try:
                    t = parse_triple(clean.split())
                    kb.facts.add(Triple(t.subject, t.predicate, t.obj, fact_degree))
                except ValueError:
                    continue

    return kb


def parse_extension(ext_str: str) -> tuple[float, list]:
    """Parse [difusa; precedencia; restriccion ...] — extract degree and numeric constraints."""
    degree = 1.0
    constraints = []
    parts = [p.strip() for p in ext_str.split(";")]
    for part in parts:
        # difusa: 0.XX or 1
        try:
            val = float(part)
            if 0.0 <= val <= 1.0:
                degree = val
            continue
        except ValueError:
            pass
        # precedencia: 3-digit integer — skip
        if part.isdigit() and len(part) == 3:
            continue
        # restriccion: Variable operador digits (e.g. X > 5)
        for op in ["<=", ">=", "<​", ">", "="]:
            if op in part:
                left, right = part.split(op, 1)
                left, right = left.strip(), right.strip()
                if left and right.lstrip("-").isdigit():
                    constraints.append((left, op, int(right)))
                break
    return degree, constraints
