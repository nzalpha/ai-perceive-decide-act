from pydantic import BaseModel
from typing import List, Optional
import re

# Define a structure for memory items
class MemoryItem(BaseModel):
    fact: str
    importance: float
    source: Optional[str] = None

# Initial memory store (you can load these from a file or database later)
memory: List[MemoryItem] = [
    MemoryItem(fact="I like the fonts in PowerPoint to be in blue color", importance=0.9),
    MemoryItem(fact="I like the background in PowerPoint to be in red color", importance=0.8)
]

def get_memory() -> List[MemoryItem]:
    """Return the list of stored memory items."""
    return memory

def get_memory_as_string() -> str:
    """Return all memory items as a readable formatted string."""
    if not memory:
        return "No memory items found."
    result = []
    for item in memory:
        source_text = f" (source: {item.source})" if item.source else ""
        result.append(f"- {item.fact} [importance: {item.importance}]{source_text}")
    return "\n".join(result)

def add_memory(fact: str, importance: float, source: Optional[str] = None):
    """Add a new memory item."""
    memory.append(MemoryItem(fact=fact, importance=importance, source=source))




