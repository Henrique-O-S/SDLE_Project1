# --------------------------------------------------------------

from collections import defaultdict
from datetime import datetime

# --------------------------------------------------------------

class ListsCRDT:
    def __init__(self):
        self.add_set = set()
        self.remove_set = set()
        self.items_crdt = {}

    def add(self, element):
        self.add_set.add(element)
        self.items_crdt[element[0]] = ItemsCRDT()

    def add_item(self, list_id, element, timestamp=None):
        self.items_crdt[list_id].add(element, timestamp)

    def remove(self, element):
        self.remove_set.add(element)

    def remove_item(self, list_id, element, timestamp=None):
        self.items_crdt[list_id].remove(element, timestamp)

    def merge(self, other_set):
        self.add_set = self.add_set.union(other_set.add_set)
        self.remove_set = self.remove_set.union(other_set.remove_set)
        for list_id, items_crdt in other_set.items_crdt.items():
            if list_id in self.items_crdt:
                self.items_crdt[list_id].merge(items_crdt)
            else:
                self.items_crdt[list_id] = items_crdt

    def removal_merge(self, other_set):
        self.remove_set = self.remove_set.union(other_set.remove_set)
        self.remove_set = self.remove_set.intersection(self.add_set)
        for list_id, items_crdt in other_set.items_crdt.items():
            if list_id in self.items_crdt:
                self.items_crdt[list_id].merge(items_crdt)
            else:
                self.items_crdt[list_id] = items_crdt
    
    def to_json(self):
        items_crdt_json = {list_key: self.items_crdt[list_key].to_json() for list_key in self.items_crdt}
        return {
            'add_set': list(self.add_set),
            'remove_set': list(self.remove_set),
            'items': items_crdt_json
        }

    @classmethod
    def from_json(cls, json_data):
        crdt = cls()
        if json_data == None:
            return crdt
        for element in json_data['add_set']:
            crdt.add_set.add((element[0], element[1]))
        for element in json_data['remove_set']:
            crdt.remove_set.add((element[0], element[1]))

        items_crdt_json = json_data.get('items', {})
        for list_key, items_data in items_crdt_json.items():
            crdt.items_crdt[list_key] = ItemsCRDT.from_json(items_data)
        return crdt
    
# --------------------------------------------------------------
    
class ItemsCRDT:
    def __init__(self):
        self.add_set = defaultdict(lambda: (0, datetime.min))
        self.remove_set = defaultdict(lambda: (0, datetime.min))

    def add(self, element, timestamp=None):
        timestamp = timestamp or datetime.now()
        if element[0] in self.add_set:
            if self.add_set[element[0]][1].isoformat() < timestamp.isoformat():
                self.add_set[element[0]] = (element[1], datetime.fromisoformat(str(timestamp)))
        else:
            self.add_set[element[0]] = (element[1], datetime.fromisoformat(str(timestamp)))

    def remove(self, element, timestamp = None):
        timestamp = timestamp or datetime.now()
        if element[0] in self.remove_set:
            if self.remove_set[element[0]][1].isoformat() < timestamp.isoformat():
                self.remove_set[element[0]] = (element[1], datetime.fromisoformat(str(timestamp)))
        else:
            self.remove_set[element[0]] = (element[1], datetime.fromisoformat(str(timestamp)))        

    def merge(self, other_set):
        for item, (quantity, timestamp) in other_set.add_set.items():
            timestamp = datetime.fromisoformat(str(timestamp))
            if item in self.add_set:
                if self.add_set[item][1].isoformat() < timestamp.isoformat():
                    self.add_set[item] = (quantity, timestamp)
            else:
                self.add_set[item] = (quantity, timestamp)
        for item, (quantity, timestamp) in other_set.remove_set.items():
            timestamp = datetime.fromisoformat(str(timestamp))
            if item in self.remove_set:
                if self.remove_set[item][1].isoformat() < timestamp.isoformat():
                    self.remove_set[item] = (quantity, timestamp)
            else:
                self.remove_set[item] = (quantity, timestamp)
        for item, (quantity, timestamp) in self.add_set.items():
            if item in self.remove_set:
                if self.remove_set[item][1].isoformat() < timestamp.isoformat():
                    del self.remove_set[item]
    
    def to_json(self):
        return {
            'add_set': [(item, (quantity, str(timestamp))) for item, (quantity, timestamp) in self.add_set.items()],
            'remove_set': [(item, (quantity, str(timestamp))) for item, (quantity, timestamp) in self.remove_set.items()]
        }
    
    @classmethod
    def from_json(cls, json_data):
        crdt = cls()
        if json_data == None:
            return crdt
        for item, (quantity, timestamp) in json_data['add_set']:
            crdt.add_set[item] = (quantity, datetime.fromisoformat(str(timestamp)))
        for item, (quantity, timestamp) in json_data['remove_set']:
            crdt.remove_set[item] = (quantity, datetime.fromisoformat(str(timestamp)))
        return crdt

# --------------------------------------------------------------
