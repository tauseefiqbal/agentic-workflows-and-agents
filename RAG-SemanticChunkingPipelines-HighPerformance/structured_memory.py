from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict, List, Optional
import asyncio
import json
import os
import time


@dataclass
class MemorySearchResult:
    fact: str
    source_tier: str
    relevance: float
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None


@dataclass
class MemoryEntry:
    fact: str
    source: str
    category: str = "general"
    timestamp: float = field(default_factory=time.time)


class ShortTermMemory:
    """In-session memory buffer with a size limit."""

    def __init__(self, limit: int = 100):
        self._entries: List[MemoryEntry] = []
        self._limit = limit

    def add(self, fact: str, source: str, category: str = "general"):
        entry = MemoryEntry(fact=fact, source=source, category=category)
        self._entries.append(entry)
        if len(self._entries) > self._limit:
            self._entries = self._entries[-self._limit:]

    def search(self, query: str, limit: int = 5) -> List[MemorySearchResult]:
        query_lower = query.lower()
        scored = []
        for e in self._entries:
            words = query_lower.split()
            matches = sum(1 for w in words if w in e.fact.lower())
            if matches > 0:
                relevance = matches / max(len(words), 1)
                scored.append(MemorySearchResult(
                    fact=e.fact,
                    source_tier="short_term",
                    relevance=relevance,
                ))
        scored.sort(key=lambda r: r.relevance, reverse=True)
        return scored[:limit]

    def recent(self, n: int = 5) -> List[MemoryEntry]:
        return self._entries[-n:]


class LocalMemory:
    """Persistent JSON-backed memory store."""

    def __init__(self, storage_path: str = "memory_store.json"):
        self._path = storage_path
        self._entries: List[dict] = []
        self._load()

    def _load(self):
        if os.path.exists(self._path):
            try:
                with open(self._path, "r", encoding="utf-8") as f:
                    self._entries = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._entries = []

    def _save(self):
        with open(self._path, "w", encoding="utf-8") as f:
            json.dump(self._entries, f, indent=2)

    def add(self, fact: str, source: str, category: str = "general"):
        self._entries.append({
            "fact": fact,
            "source": source,
            "category": category,
            "timestamp": time.time(),
        })
        self._save()

    def search(self, query: str, limit: int = 5) -> List[MemorySearchResult]:
        query_lower = query.lower()
        scored = []
        for e in self._entries:
            words = query_lower.split()
            matches = sum(1 for w in words if w in e["fact"].lower())
            if matches > 0:
                relevance = matches / max(len(words), 1)
                scored.append(MemorySearchResult(
                    fact=e["fact"],
                    source_tier="local",
                    relevance=relevance,
                ))
        scored.sort(key=lambda r: r.relevance, reverse=True)
        return scored[:limit]


class StructuredMemory:
    """Three-tier memory: short-term, local persistent, and knowledge graph (Graphiti/Neo4j)."""

    def __init__(
        self,
        graphiti_client=None,
        storage_path: str = "memory_store.json",
        short_term_limit: int = 100,
    ):
        self.short_term = ShortTermMemory(limit=short_term_limit)
        self.local = LocalMemory(storage_path=storage_path)
        self._graphiti = graphiti_client
        self._kg_available = False

    async def initialize(self) -> Dict[str, bool]:
        """Initialize all tiers and return status dict."""
        status = {
            "short_term": True,
            "local": True,
            "knowledge_graph": False,
        }
        if self._graphiti is not None:
            try:
                # Try a lightweight operation with a short timeout so we don't hang
                await asyncio.wait_for(
                    self._graphiti.build_indices_and_constraints(),
                    timeout=5.0,
                )
                self._kg_available = True
                status["knowledge_graph"] = True
            except Exception:
                self._kg_available = False
        return status

    def remember(self, fact: str, source: str, category: str = "general", persist: bool = True):
        self.short_term.add(fact=fact, source=source, category=category)
        if persist:
            self.local.add(fact=fact, source=source, category=category)

    async def search(self, query: str, limit: int = 10) -> List[MemorySearchResult]:
        results: List[MemorySearchResult] = []
        results.extend(self.short_term.search(query, limit=limit))
        results.extend(self.local.search(query, limit=limit))

        if self._kg_available and self._graphiti is not None:
            try:
                kg_results = await self._graphiti.search(query, num_results=limit)
                for r in kg_results:
                    fact_text = r.fact if hasattr(r, "fact") else str(r)
                    results.append(MemorySearchResult(
                        fact=fact_text,
                        source_tier="knowledge_graph",
                        relevance=0.8,
                    ))
            except Exception:
                pass

        results.sort(key=lambda r: r.relevance, reverse=True)
        return results[:limit]

    def get_status(self) -> Dict[str, str]:
        return {
            "short_term": f"active ({len(self.short_term._entries)} entries)",
            "local": f"active ({len(self.local._entries)} entries)",
            "knowledge_graph": "connected" if self._kg_available else "unavailable",
        }

    def get_conversation_context(self, n: int = 3) -> str:
        recent = self.short_term.recent(n)
        if not recent:
            return ""
        lines = [f"- {e.fact}" for e in recent]
        return "Recent context:\n" + "\n".join(lines)

    async def close(self):
        if self._kg_available and self._graphiti is not None:
            try:
                await self._graphiti.close()
            except Exception:
                pass
