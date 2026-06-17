from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional
import subprocess
import sys


def _current_repo() -> str:
    try:
        remote = subprocess.check_output(
            ["git", "remote", "get-url", "origin"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        return remote.split("/")[-1].replace(".git", "")
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"WriterLore: could not detect repo: {e}\n")
        return "unknown"


def _current_ticket() -> Optional[str]:
    try:
        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL
        ).decode().strip()
        parts = branch.split("-")
        if len(parts) >= 2 and parts[0].isupper():
            return f"{parts[0]}-{parts[1]}"
        return None
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"WriterLore: could not detect ticket: {e}\n")
        return None


@dataclass
class Memory:
    content: str
    primary_repo: str = field(default_factory=_current_repo)
    also_relevant_for: list[str] = field(default_factory=list)
    ticket: Optional[str] = field(default_factory=_current_ticket)
    components: list[str] = field(default_factory=list)
    saved_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    embedding: list[float] = field(default_factory=list)

    def to_document(self) -> dict:
        return {
            "content": self.content,
            "primary_repo": self.primary_repo,
            "also_relevant_for": self.also_relevant_for,
            "ticket": self.ticket,
            "components": self.components,
            "saved_at": self.saved_at,
            "embedding": self.embedding,
        }
