from typing import Any, Optional

class Node:
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional['Node'] = None

class Stack:
    """
    A custom Stack implementation using a linked list (LIFO).
    """
    def __init__(self, max_size: Optional[int] = None):
        self.top: Optional[Node] = None
        self.size = 0
        self.max_size = max_size

    def push(self, item: Any):
        """Pushes an updated item onto the stack."""
        new_node = Node(item)
        new_node.next = self.top
        self.top = new_node
        self.size += 1

        # enforce maximum size restriction
        if self.max_size and self.size > self.max_size:
            self.__remove_bottom()

    def __remove_bottom(self):
        # traverses to the end and removes the last node
        if not self.top or not self.top.next:
            self.top = None
            self.size = 0
            return
        
        cur = self.top
        while cur.next and cur.next.next:
            cur = cur.next
        cur.next = None
        self.size -= 1

    def pop(self) -> Any:
        """Removes and returns the item from the top of the stack."""
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        
        item = self.top.data
        self.top = self.top.next
        self.size -= 1
        return item

    def peek(self) -> Any:
        # returns the top item without removing
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self.top.data

    def is_empty(self) -> bool:
        # checks if stack has no elements
        return self.top is None

    def to_list(self) -> list:
        # serialises stack to a list for persistence
        result = []
        cur = self.top
        while cur:
            result.append(cur.data)
            cur = cur.next
        return result

    def from_list(self, items: list):
        # reconstructs stack from a serialised list
        self.top = None
        self.size = 0
        # items should be in order from top to bottom
        for item in reversed(items):
            self.push(item)
