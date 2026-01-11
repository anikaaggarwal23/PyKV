from core.node import Node

class LRUCache:
    def __init__(self, capacity: int):
        self.capacity = capacity
        self.cache = {}

        self.head = Node()
        self.tail = Node()
        self.head.next = self.tail
        self.tail.prev = self.head

    def _remove(self, node: Node):
        node.prev.next = node.next
        node.next.prev = node.prev

    def _add_front(self, node: Node):
        node.next = self.head.next
        node.prev = self.head
        self.head.next.prev = node
        self.head.next = node

    def get(self, key: str):
        if key not in self.cache:
            return None
        node = self.cache[key]
        self._remove(node)
        self._add_front(node)
        return node.value

    def set(self, key: str, value: str):
        if key in self.cache:
            node = self.cache[key]
            node.value = value
            self._remove(node)
            self._add_front(node)
            return None

        node = Node(key, value)
        self.cache[key] = node
        self._add_front(node)

        if len(self.cache) > self.capacity:
            return self._evict()
        return None

    def delete(self, key: str):
        if key not in self.cache:
            return False
        node = self.cache.pop(key)
        self._remove(node)
        return True

    def _evict(self):
        lru = self.tail.prev
        self._remove(lru)
        del self.cache[lru.key]
        return lru.key

    def keys(self):
        return list(self.cache.keys())
