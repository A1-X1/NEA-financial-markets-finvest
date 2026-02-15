from dataclasses import dataclass
from typing import Any, List, Optional, Tuple


# custom hash node implementation
@dataclass
class HashNode:
    key: Any
    value: Any
    next: Optional['HashNode'] = None

class HashTable:
    # custom hash table implementation avoiding collisions with chaining
    def __init__(self, capacity: int = 50):
        self.capacity = capacity
        self.size = 0
        self.buckets: List[Optional[HashNode]] = [None] * self.capacity

    # custom hash function
    def _hash(self, key: Any) -> int:
        return hash(key) % self.capacity

    # custom put method to handle collisions
    def put(self, key: Any, value: Any):
        # hash key to get index
        index = self._hash(key)
        node = self.buckets[index]

        # check if key exists in the chain
        while node:
            if node.key == key:
                # update existing value
                node.value = value 
                return
            node = node.next

        # key not found then insert new node at head of chain
        new_node = HashNode(key, value)
        new_node.next = self.buckets[index]
        self.buckets[index] = new_node
        self.size += 1

    # custom get method
    def get(self, key: Any) -> Optional[Any]:
        index = self._hash(key)
        node = self.buckets[index]

        while node:
            if node.key == key:
                return node.value
            node = node.next
        
        return None

    # custom remove method that returns true if removed, false if not found
    def remove(self, key: Any) -> bool:
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

    # custom get all method that gets all key-value pairs
    def get_all(self) -> List[Tuple[Any, Any]]:
        items = []
        for i in range(self.capacity):
            node = self.buckets[i]
            while node:
                items.append((node.key, node.value))
                node = node.next
        return items

    # custom clear method that clears the hash table
    def clear(self):
        self.buckets = [None] * self.capacity
        self.size = 0
