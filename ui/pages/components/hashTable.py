from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

@dataclass
class HashNode:
    key: Any
    value: Any
    next: Optional['HashNode'] = None

class HashTable:
    """
    A custom Hash Table implementation using Chaining for collision resolution.
    Stores portfolio assets where Key = Ticker Symbol, Value = Quantity.
    """
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.size = 0
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity

    def _hash(self, key: Any) -> int:
        """Computes the index for a given key."""
        return hash(key) % self.capacity

    def put(self, key: Any, value: Any):
        """
        Inserts a key-value pair. 
        If key exists, updates the value (Duplicate Key Handling).
        """
        index = self._hash(key)
        node = self.buckets[index]

        # Check if key exists in the chain (Update)
        while node:
            if node.key == key:
                node.value = value # Update existing value
                return
            node = node.next

        # Key not found, insert new node at head of chain (Insert)
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1

    def get(self, key: Any) -> Optional[Any]:
        """Retrieves the value for a given key, or None if not found."""
        index = self._hash(key)
        node = self.buckets[index]

        while node:
            if node.key == key:
                return node.value
            node = node.next
        
        return None

    def remove(self, key: Any) -> bool:
        """Removes a key-value pair. Returns True if removed, False if not found."""
        index = self._hash(key)
        node = self.buckets[index]
        prev = None

        while node:
            if node.key == key:
                if prev:
                    prev.next = node.next
                else:
                    self.buckets[index] = node.next
                self.size -= 1
                return True
            prev = node
            node = node.next
        
        return False

    def get_all(self) -> List[Tuple[Any, Any]]:
        """Returns a list of all (key, value) pairs in the table."""
        items = []
        for i in range(self.capacity):
            node = self.buckets[i]
            while node:
                items.append((node.key, node.value))
                node = node.next
        return items

    def clear(self):
        """Clears the hash table."""
        self.buckets = [None] * self.capacity
        self.size = 0
