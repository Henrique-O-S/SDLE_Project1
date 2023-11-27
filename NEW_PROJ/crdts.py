# -----------------------------------------------------------------------------

class ListsCRDT:
    def __init__(self):
        self.add_set = set()
        self.remove_set = set()

    def add(self, shopping_list):
        self.add_set.add(shopping_list)

    def remove(self, shopping_list):
        if shopping_list in self.add_set:
            self.remove_set.add(shopping_list)

    def lookup(self):
        return self.add_set - self.remove_set
    
# -----------------------------------------------------------------------------

class ItemsCRDT:
    def __init__(self, logs):
        self.add_set = {}
        self.remove_set = {}
        self.register(logs)

    def register(self, logs):
        for actions in logs:
            for action in actions:
                timestamp, action_type, element, quantity = action
                if action_type == 'update':
                    self.update(timestamp, element, quantity)
                elif action_type == 'remove':
                    self.remove(timestamp, element, quantity)

    def update(self, timestamp, element, quantity):
        if element not in self.add_set:
            self.add_set[element] = {'timestamp': timestamp, 'quantity': quantity}
        elif self.add_set[element]['timestamp'] <= timestamp:
            self.add_set[element] = {'timestamp': timestamp, 'quantity': quantity}

    def remove(self, timestamp, element, quantity):
        if element not in self.remove_set:
            self.remove_set[element] = {'timestamp': timestamp, 'quantity': quantity}
        elif self.remove_set[element]['timestamp'] <= timestamp:
            self.remove_set[element] = {'timestamp': timestamp, 'quantity': quantity}

    def merge(self, *others):
        merged_set = ItemsCRDT([[]])
        sets_to_merge = [self] + list(others)
        for set_to_merge in sets_to_merge:
            for element, data in set_to_merge.add_set.items():
                if element not in merged_set.add_set or merged_set.add_set[element]['timestamp'] < data['timestamp']:
                    merged_set.add_set[element] = {'timestamp': data['timestamp'], 'quantity': data['quantity']}
            for element, data in set_to_merge.remove_set.items():
                if element not in merged_set.remove_set or merged_set.remove_set[element]['timestamp'] < data['timestamp']:
                    merged_set.remove_set[element] = {'timestamp': data['timestamp'], 'quantity': data['quantity']}
        return merged_set
    
    def lookup(self):
        final_set = {}
        for element, data in self.add_set.items():
            if element not in self.remove_set or self.remove_set[element]['timestamp'] < data['timestamp']:
                final_set[element] = data['quantity']
        return final_set
    
# -----------------------------------------------------------------------------