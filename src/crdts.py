# --------------------------------------------------------------

from collections import defaultdict
from datetime import datetime

# --------------------------------------------------------------

class ListsCRDT:
    def __init__(self):
        self.add_set = set()
        self.remove_set = set()

    def add(self, element):
        self.add_set.add(element)

    def remove(self, element):
        self.remove_set.add(element)

    def merge(self, other_set):
        self.add_set = self.add_set.union(other_set.add_set)
        self.remove_set = self.remove_set.union(other_set.remove_set)

    def removal_merge(self, other_set):
        self.remove_set = self.remove_set.union(other_set.remove_set)
        self.remove_set = self.remove_set.intersection(self.add_set)

    def value(self):
        return self.add_set - self.remove_set
    
    def to_json(self):
            return {
                'add_set': list(self.add_set),
                'remove_set': list(self.remove_set)
            }

    @classmethod
    def from_json(cls, json_data):
        crdt = cls()
        for element in json_data['add_set']:
            crdt.add_set.add((element[0], element[1]))
        for element in json_data['remove_set']:
            crdt.remove_set.add((element[0], element[1]))
        return crdt
    
# --------------------------------------------------------------
    
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
    
# --------------------------------------------------------------
