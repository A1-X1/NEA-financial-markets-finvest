from typing import Any, Optional

class Node:
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional['Node'] = None

class Stack:
    """
    A custom Stack implementation using a linked list (LIFO).
    """
    def __init__(self):
        self.top: Optional[Node] = None
        self.size = 0

    def push(self, item: Any):
        """Pushes an updated item onto the stack."""
        new_node = Node(item)
        new_node.next = self.top
        self.top = new_node
        self.size += 1

    def pop(self) -> Any:
        """Removes and returns the item from the top of the stack."""
        if self.is_empty():
            raise IndexError("Pop from empty stack")
        
        item = self.top.data
        self.top = self.top.next
        self.size -= 1
        return item

    def peek(self) -> Any:
        """Returns the item at the top of the stack without removing it."""
        if self.is_empty():
            raise IndexError("Peek from empty stack")
        return self.top.data

    def is_empty(self) -> bool:
        """Returns True if the stack is empty, False otherwise."""
        return self.top is None
