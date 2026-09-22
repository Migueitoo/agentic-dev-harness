from dataclasses import dataclass


@dataclass
class ContextItem:
    kind: str
    source: str
    content: str
    priority: int


@dataclass
class ContextBundle:
    repository_name: str
    task: str | None
    items: list[ContextItem]
    max_tokens: int


@dataclass
class CodeDocument:
    source: str
    content: str
    language: str
    project: str | None
