from collections import defaultdict
from datetime import datetime

class ItemsCRDT:
    def __init__(self):
        self.add_set = defaultdict(float)
        self.remove_set = defaultdict(float)

    def add(self, element, timestamp = None):
        timestamp = timestamp or datetime.now()
        self.add_set[element] = max(self.add_set[element], timestamp)

    def remove(self, element, timestamp = None):
        timestamp = timestamp or datetime.now()
        self.remove_set[element] = max(self.remove_set[element], timestamp)

    def merge(self, other_set):
        for element, timestamp in other_set.add_set.items():
            self.add_set[element] = max(self.add_set[element], timestamp)
        for element, timestamp in other_set.remove_set.items():
            self.remove_set[element] = max(self.remove_set[element], timestamp)

    def value(self):
        return {element for element, add_time in self.add_set.items() if add_time >= self.remove_set.get(element, 0)}
