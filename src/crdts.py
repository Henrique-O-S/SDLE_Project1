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
        self.add_set = defaultdict(lambda: (0, datetime.min))
        self.remove_set = defaultdict(lambda: (0, datetime.min))

    def add(self, element, timestamp=None):
        timestamp = timestamp or datetime.now()
        if element[0] in self.add_set:
            if self.add_set[element[0]][1] < timestamp:
                self.add_set[element[0]] = (element[1], timestamp)
        else:
            self.add_set[element[0]] = (element[1], timestamp)

    def remove(self, element, timestamp = None):
        timestamp = timestamp or datetime.now()
        if element[0] in self.remove_set:
            if self.remove_set[element[0]][1] < timestamp:
                self.remove_set[element[0]] = (element[1], timestamp)
        else:
            self.remove_set[element[0]] = (element[1], timestamp)        

    def merge(self, other_set):
        for item, (quantity, timestamp) in other_set.add_set.items():
            if item in self.add_set:
                if self.add_set[item][1] < timestamp:
                    self.add_set[item] = (quantity, timestamp)
            else:
                self.add_set[item] = (quantity, timestamp)
        for item, (quantity, timestamp) in other_set.remove_set.items():
            if item in self.remove_set:
                if self.remove_set[item][1] < timestamp:
                    self.remove_set[item] = (quantity, timestamp)
            else:
                self.remove_set[item] = (quantity, timestamp)

    def value(self):
        valid_elements = set()
        for item, (quantity, timestamp) in self.add_set.items():
            if item in self.remove_set:
                if self.remove_set[item][1] < timestamp:
                    valid_elements.add((item, quantity))
            else:
                valid_elements.add((item, quantity))
        return valid_elements
    
    def to_json(self):
        return {
            'add_set': list(self.add_set.items()),
            'remove_set': list(self.remove_set.items())
        }
    
    @classmethod
    def from_json(cls, json_data):
        crdt = cls()
        for item, (quantity, timestamp) in json_data['add_set']:
            crdt.add_set[item] = (quantity, timestamp)
        for item, (quantity, timestamp) in json_data['remove_set']:
            crdt.remove_set[item] = (quantity, timestamp)
        return crdt

# --------------------------------------------------------------
