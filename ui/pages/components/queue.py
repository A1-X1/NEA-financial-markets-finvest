from typing import Any, Optional

class Node:
    def __init__(self, data: Any):
        self.data = data
        self.next: Optional['Node'] = None

class Queue:
    """
    A custom Queue implementation using a linked list (FIFO).
    """
    def __init__(self):
        self.front: Optional[Node] = None
        self.rear: Optional[Node] = None
        self.size = 0

    def enqueue(self, item: Any):
        """Adds an item to the end of the queue."""
        new_node = Node(item)
        if self.rear is None:
            self.front = self.rear = new_node
            self.size += 1
            return
        
        self.rear.next = new_node
        self.rear = new_node
        self.size += 1

    def dequeue(self) -> Any:
        """Removes and returns the item from the front of the queue."""
        if self.is_empty():
            raise IndexError("Dequeue from empty queue")
        
        temp = self.front
        self.front = temp.next
        
        if self.front is None:
            self.rear = None
            
        self.size -= 1
        return temp.data

    def is_empty(self) -> bool:
        """Returns True if the queue is empty, False otherwise."""
        return self.front is None
