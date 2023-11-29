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
        crdt.add_set = set(json_data['add_set'])
        crdt.remove_set = set(json_data['remove_set'])
        return crdt