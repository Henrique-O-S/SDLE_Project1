class LWWElementSet:
    def __init__(self):
        self.addSet = {}
        self.removeSet = {}

    def add(self, key, value, timestamp):
        self.addSet[key] = (value, timestamp)

    def remove(self, key, timestamp):
        if key in self.addSet:
            self.removeSet[key] = timestamp

    def lookup(self, key):
        if key in self.addSet:
            if key not in self.removeSet or self.addSet[key][1] > self.removeSet[key]:
                return True
        return False

    def merge(self, other_set):
        for key, (value, timestamp) in other_set.addSet.items():
            if key not in self.addSet or timestamp > self.addSet[key][1]:
                self.addSet[key] = (value, timestamp)

        for key, timestamp in other_set.removeSet.items():
            if key not in self.removeSet or timestamp > self.removeSet[key]:
                self.removeSet[key] = timestamp
