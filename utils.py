import heapq

class PriorityQueue(object):
    """
    A more intuitive interface of priority queue based on python built-in module heapq
    """
    def __init__(self):
        self.queue = []

    def push(self, item):
        heapq.heappush(self.queue, item)

    def pop(self):
        return heapq.heappop(self.queue)

def test():
    pq = PriorityQueue()
    pq.push((1, 2))
    pq.push((2, 1))
    assert pq.pop() == (1, 2)

if __name__ == "__main__":
    test()
