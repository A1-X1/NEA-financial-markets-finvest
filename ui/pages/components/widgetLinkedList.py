import uuid

class WidgetNode:
    def __init__(self, widget_type: str, config: dict, widget_id: str = None):
        self.widget_id = widget_id or str(uuid.uuid4())[:8]
        self.widget_type = widget_type
        self.config = config
        self.next: 'WidgetNode | None' = None


class WidgetLinkedList:
    def __init__(self):
        self.head: WidgetNode | None = None

    def append(self, node: WidgetNode):
        # add a node to the end of the list
        if not self.head:
            self.head = node
        else:
            cur = self.head
            while cur.next:
                cur = cur.next
            cur.next = node

    def remove(self, widget_id: str) -> bool:
        # remove node by id, relinks pointers around it
        if not self.head:
            return False
        if self.head.widget_id == widget_id:
            self.head = self.head.next
            return True
        prev = self.head
        while prev.next:
            if prev.next.widget_id == widget_id:
                prev.next = prev.next.next
                return True
            prev = prev.next
        return False

    def move_up(self, widget_id: str) -> bool:
        # swap node with its predecessor by relinking
        if not self.head or self.head.widget_id == widget_id:
            return False
        pp, prev, cur = None, self.head, self.head.next
        while cur:
            if cur.widget_id == widget_id:
                if pp:
                    pp.next = cur
                else:
                    self.head = cur
                prev.next = cur.next
                cur.next = prev
                return True
            pp, prev, cur = prev, cur, cur.next
        return False

    def move_down(self, widget_id: str) -> bool:
        # swap node with its successor by relinking
        prev, cur = None, self.head
        while cur:
            if cur.widget_id == widget_id:
                succ = cur.next
                if not succ:
                    return False
                if prev:
                    prev.next = succ
                else:
                    self.head = succ
                cur.next = succ.next
                succ.next = cur
                return True
            prev, cur = cur, cur.next
        return False

    def to_list(self) -> list[dict]:
        # serialise list to plain dicts for db storage
        result, cur = [], self.head
        while cur:
            result.append({'widget_id': cur.widget_id, 'widget_type': cur.widget_type, 'config': cur.config})
            cur = cur.next
        return result

    def from_list(self, items: list[dict]):
        # rebuild linked list from serialised dicts
        self.head = None
        for item in items:
            self.append(WidgetNode(item['widget_type'], item['config'], item['widget_id']))

    @property
    def size(self) -> int:
        count, cur = 0, self.head
        while cur:
            count += 1
            cur = cur.next
        return count
