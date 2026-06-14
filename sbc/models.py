from dataclasses import dataclass, field


@dataclass(frozen=True, eq=False)
class Triple:
    subject: str
    predicate: str
    obj: str
    degree: float = 1.0

    def __eq__(self, other):
        if not isinstance(other, Triple):
            return NotImplemented
        return (
            self.subject == other.subject
            and self.predicate == other.predicate
            and self.obj == other.obj
        )

    def __hash__(self):
        return hash((self.subject, self.predicate, self.obj))

    def __str__(self):
        if self.degree != 1.0:
            return f"{self.subject} {self.predicate} {self.obj} {self.degree}"
        else:
            return f"{self.subject} {self.predicate} {self.obj}"


@dataclass
class Rule:
    head: Triple
    body: list[Triple]
    constraints: list[tuple[str, str]] = field(default_factory=list)
    degree: float = 1.0


@dataclass
class KnowledgeBase:
    facts: set[Triple] = field(default_factory=set)
    rules: list[Rule] = field(default_factory=list)
