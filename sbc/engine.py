from sbc.models import *


def is_variable(term: str) -> bool:
    return term[0].isupper()


def unify(pattern: Triple, fact: Triple, bindings: dict) -> dict | None:
    result = dict(bindings)
    for p, f in zip(
        (pattern.subject, pattern.predicate, pattern.obj),
        (fact.subject, fact.predicate, fact.obj),
    ):
        p = result.get(p, p)
        if is_variable(p):
            result[p] = f
        elif p != f:
            return None
    return result


def query(kb: KnowledgeBase, pattern: Triple) -> list[tuple[dict, float]]:
    results = []
    seen = []
    for fact in kb.facts:
        b = unify(pattern, fact, {})
        if b is not None and b not in seen:
            seen.append(b)
            results.append((b, fact.degree))
    return results


def forward_chain(kb: KnowledgeBase) -> set[Triple]:
    new_facts = set()
    changed = True
    while changed:
        changed = False
        for rule in kb.rules:
            for bindings, degree in match_body(kb, rule.body, {}, rule.constraints):
                head = apply_bindings(rule.head, bindings)
                derived_degree = degree * rule.degree
                derived_triple = Triple(
                    head.subject, head.predicate, head.obj, derived_degree
                )

                existing = None
                for f in kb.facts:
                    if (
                        f.subject == derived_triple.subject
                        and f.predicate == derived_triple.predicate
                        and f.obj == derived_triple.obj
                    ):
                        existing = f
                        break

                if existing is None or existing.degree < derived_degree:
                    if existing:
                        kb.facts.discard(existing)
                    kb.facts.add(derived_triple)
                    new_facts.add(derived_triple)
                    changed = True
    return new_facts


def apply_bindings(triple: Triple, bindings: dict) -> Triple:
    return Triple(
        bindings.get(triple.subject, triple.subject),
        bindings.get(triple.predicate, triple.predicate),
        bindings.get(triple.obj, triple.obj),
        triple.degree,
    )


def match_body(
    kb, body: list[Triple], bindings: dict, constraints: list = [], degree: float = 1.0
):
    if not body:
        for constraint in constraints:
            if len(constraint) == 2:
                # legacy != constraint
                left, right = constraint
                if bindings.get(left, left) == bindings.get(right, right):
                    return
            elif len(constraint) == 3:
                left, op, right = constraint
                left_val = bindings.get(left, left)
                # numeric restriction: Variable op digit
                if isinstance(right, int):
                    try:
                        left_num = float(left_val)
                    except (ValueError, TypeError):
                        return
                    if op == "<" and not (left_num < right):
                        return
                    if op == "<=" and not (left_num <= right):
                        return
                    if op == "=" and not (left_num == right):
                        return
                    if op == ">=" and not (left_num >= right):
                        return
                    if op == ">" and not (left_num > right):
                        return
                # != between two variables
                else:
                    if bindings.get(left, left) == bindings.get(right, right):
                        return
        yield bindings, degree
        return
    for b, d in query(kb, apply_bindings(body[0], bindings)):
        merged = {**bindings, **b}
        yield from match_body(kb, body[1:], merged, constraints, min(degree, d))


def backward_chain(
    kb: KnowledgeBase, goal: Triple, bindings: dict | None = None
) -> list[tuple[dict, float]]:
    if bindings is None:
        bindings = {}
    results = []
    for b, d in query(kb, apply_bindings(goal, bindings)):
        results.append(({**bindings, **b}, d))
    for rule in kb.rules:
        head = apply_bindings(rule.head, {f"_{k}": v for k, v in bindings.items()})
        b = unify(head, apply_bindings(goal, bindings), {})
        if b is not None:
            for body_bindings, body_degree in match_body_backward(
                kb, rule.body, b, 1.0
            ):
                results.append((body_bindings, body_degree * rule.degree))
    return results


def match_body_backward(kb, body, bindings, degree: float = 1.0):
    if not body:
        yield bindings, degree
        return
    goal = apply_bindings(body[0], bindings)
    for b, d in backward_chain(kb, goal, bindings):
        yield from match_body_backward(kb, body[1:], {**bindings, **b}, min(degree, d))
