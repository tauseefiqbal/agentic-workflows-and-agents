"""
Structured Memory Module - Three-Tier Memory Architecture

Tier 1: Short-Term Memory (in-memory) - Current conversation context
Tier 2: Long-Term Local Memory (JSON file) - Persistent facts, always available
Tier 3: Knowledge Graph Memory (Neo4j/Graphiti) - Rich relational data, when available

The system gracefully degrades: if Neo4j is down, Tiers 1+2 still work.
"""

from __future__ import annotations
import json
import os
import uuid
from collections import deque
from datetime import datetime, timezone
from difflib import SequenceMatcher
from pathlib import Path
from typing import Dict, List, Optional

from pydantic import BaseModel, Field


# ========== Memory Entry Models ==========

class MemoryEntry(BaseModel):
    """A single memory fact stored across tiers."""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    fact: str
    source: str = "user"  # user, agent, graphiti, system
    category: str = "general"  # general, entity, relationship, preference
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)

    def relevance_score(self, query: str) -> float:
        """Simple text similarity score against a query."""
        return SequenceMatcher(None, query.lower(), self.fact.lower()).ratio()


class MemorySearchResult(BaseModel):
    """Result from a memory search across tiers."""
    fact: str
    source_tier: str  # "short_term", "local", "knowledge_graph"
    relevance: float = 0.0
    created_at: Optional[str] = None
    valid_at: Optional[str] = None
    invalid_at: Optional[str] = None


# ========== Tier 1: Short-Term Memory ==========

class ShortTermMemory:
    """In-memory conversation buffer for the current session."""

    def __init__(self, max_entries: int = 100):
        self._entries: deque[MemoryEntry] = deque(maxlen=max_entries)

    def add(self, fact: str, source: str = "user", category: str = "general",
            metadata: Optional[Dict] = None) -> MemoryEntry:
        entry = MemoryEntry(
            fact=fact, source=source, category=category,
            metadata=metadata or {}
        )
        self._entries.append(entry)
        return entry

    def search(self, query: str, limit: int = 10) -> List[MemorySearchResult]:
        scored = []
        for entry in self._entries:
            score = entry.relevance_score(query)
            if score > 0.2:
                scored.append(MemorySearchResult(
                    fact=entry.fact,
                    source_tier="short_term",
                    relevance=score,
                    created_at=entry.created_at,
                    valid_at=entry.valid_at,
                    invalid_at=entry.invalid_at,
                ))
        scored.sort(key=lambda x: x.relevance, reverse=True)
        return scored[:limit]

    def get_recent(self, n: int = 5) -> List[MemoryEntry]:
        return list(self._entries)[-n:]

    def clear(self):
        self._entries.clear()


# ========== Tier 2: Long-Term Local Memory ==========

class LocalMemory:
    """JSON file-backed persistent memory. Always available, no Neo4j needed."""

    def __init__(self, storage_path: str = "memory_store.json"):
        self._path = Path(storage_path)
        self._entries: List[MemoryEntry] = []
        self._load()

    def _load(self):
        if self._path.exists():
            try:
                data = json.loads(self._path.read_text(encoding="utf-8"))
                self._entries = [MemoryEntry(**e) for e in data]
            except (json.JSONDecodeError, Exception):
                self._entries = []

    def _save(self):
        self._path.write_text(
            json.dumps([e.model_dump() for e in self._entries], indent=2),
            encoding="utf-8"
        )

    def add(self, fact: str, source: str = "user", category: str = "general",
            valid_at: Optional[str] = None, metadata: Optional[Dict] = None) -> MemoryEntry:
        entry = MemoryEntry(
            fact=fact, source=source, category=category,
            valid_at=valid_at, metadata=metadata or {}
        )
        self._entries.append(entry)
        self._save()
        return entry

    def add_batch(self, entries: List[Dict]) -> List[MemoryEntry]:
        results = []
        for e in entries:
            entry = MemoryEntry(**e) if isinstance(e, dict) else e
            self._entries.append(entry)
            results.append(entry)
        self._save()
        return results

    def search(self, query: str, limit: int = 10) -> List[MemorySearchResult]:
        scored = []
        for entry in self._entries:
            score = entry.relevance_score(query)
            if score > 0.2:
                scored.append(MemorySearchResult(
                    fact=entry.fact,
                    source_tier="local",
                    relevance=score,
                    created_at=entry.created_at,
                    valid_at=entry.valid_at,
                    invalid_at=entry.invalid_at,
                ))
        scored.sort(key=lambda x: x.relevance, reverse=True)
        return scored[:limit]

    def get_by_category(self, category: str) -> List[MemoryEntry]:
        return [e for e in self._entries if e.category == category]

    def get_all(self) -> List[MemoryEntry]:
        return list(self._entries)

    def remove(self, entry_id: str) -> bool:
        before = len(self._entries)
        self._entries = [e for e in self._entries if e.id != entry_id]
        if len(self._entries) < before:
            self._save()
            return True
        return False

    def clear(self):
        self._entries.clear()
        self._save()


# ========== Tier 3: Knowledge Graph Memory (Neo4j/Graphiti wrapper) ==========

class KnowledgeGraphMemory:
    """Wraps Graphiti client for knowledge graph operations with connection resilience."""

    def __init__(self, graphiti_client=None):
        self._client = graphiti_client
        self._available = False

    async def initialize(self) -> bool:
        """Try to connect and build indices. Returns True if successful."""
        if not self._client:
            return False
        try:
            await self._client.build_indices_and_constraints()
            self._available = True
            return True
        except Exception:
            self._available = False
            return False

    @property
    def is_available(self) -> bool:
        return self._available and self._client is not None

    async def search(self, query: str, limit: int = 10) -> List[MemorySearchResult]:
        if not self.is_available:
            return []
        try:
            results = await self._client.search(query)
            formatted = []
            for r in results[:limit]:
                formatted.append(MemorySearchResult(
                    fact=r.fact,
                    source_tier="knowledge_graph",
                    relevance=1.0,
                    valid_at=str(r.valid_at) if hasattr(r, 'valid_at') and r.valid_at else None,
                    invalid_at=str(r.invalid_at) if hasattr(r, 'invalid_at') and r.invalid_at else None,
                ))
            return formatted
        except Exception:
            self._available = False
            return []

    async def close(self):
        if self._client:
            try:
                await self._client.close()
            except Exception:
                pass


# ========== Unified Structured Memory Manager ==========

class StructuredMemory:
    """
    Three-tier memory manager that searches across all tiers and
    merges results by relevance.

    Usage:
        memory = StructuredMemory(graphiti_client=client)
        await memory.initialize()

        # Store a fact
        memory.remember("GPT-4.1 was released by OpenAI on April 14, 2025")

        # Search across all tiers
        results = await memory.search("When was GPT-4.1 released?")

        # Get conversation context
        recent = memory.get_conversation_context()
    """

    def __init__(self, graphiti_client=None, storage_path: str = "memory_store.json",
                 short_term_limit: int = 100):
        self.short_term = ShortTermMemory(max_entries=short_term_limit)
        self.local = LocalMemory(storage_path=storage_path)
        self.knowledge_graph = KnowledgeGraphMemory(graphiti_client=graphiti_client)

    async def initialize(self) -> Dict[str, bool]:
        """Initialize all memory tiers. Returns status of each tier."""
        kg_ok = await self.knowledge_graph.initialize()
        return {
            "short_term": True,  # always available
            "local": True,       # always available (file-based)
            "knowledge_graph": kg_ok,
        }

    def remember(self, fact: str, source: str = "user", category: str = "general",
                 persist: bool = True, metadata: Optional[Dict] = None) -> MemoryEntry:
        """Store a fact in short-term memory, and optionally persist to local storage."""
        entry = self.short_term.add(fact=fact, source=source, category=category, metadata=metadata)
        if persist:
            self.local.add(fact=fact, source=source, category=category, metadata=metadata)
        return entry

    async def search(self, query: str, limit: int = 10) -> List[MemorySearchResult]:
        """Search across all three memory tiers and merge results by relevance."""
        all_results: List[MemorySearchResult] = []

        # Tier 1: Short-term
        all_results.extend(self.short_term.search(query, limit=limit))

        # Tier 2: Local persistent
        all_results.extend(self.local.search(query, limit=limit))

        # Tier 3: Knowledge graph (if available)
        kg_results = await self.knowledge_graph.search(query, limit=limit)
        all_results.extend(kg_results)

        # Deduplicate by fact text (keep highest relevance)
        seen: Dict[str, MemorySearchResult] = {}
        for r in all_results:
            key = r.fact.strip().lower()
            if key not in seen or r.relevance > seen[key].relevance:
                seen[key] = r
        
        merged = sorted(seen.values(), key=lambda x: x.relevance, reverse=True)
        return merged[:limit]

    def get_conversation_context(self, n: int = 5) -> str:
        """Get recent conversation facts as context string."""
        recent = self.short_term.get_recent(n)
        if not recent:
            return ""
        lines = [f"- {e.fact}" for e in recent]
        return "Recent context:\n" + "\n".join(lines)

    def get_status(self) -> Dict[str, str]:
        """Return status summary of each memory tier."""
        return {
            "short_term": f"{len(self.short_term._entries)} entries (session)",
            "local": f"{len(self.local._entries)} entries (persistent)",
            "knowledge_graph": "connected" if self.knowledge_graph.is_available else "unavailable",
        }

    async def close(self):
        await self.knowledge_graph.close()
