from db import ShoppingListDB

class ListsCRDT:
    def __init__(self):
        self.add_set = set()
        self.remove_set = set()
        self.final_set = set()

    def loadDatabase(self, db):
        self.database = ShoppingListDB(db)
        for shopping_list in self.database.get_shopping_lists():
            self.add_set.add(shopping_list[0])
        for shopping_list in self.database.get_removed_lists():
            self.remove_set.add(shopping_list[0])

    def merge(self, other):
        merged_set = ListsCRDT()
        merged_set.add_set = self.add_set.union(other.add_set)
        merged_set.remove_set = self.remove_set.union(other.remove_set)
        merged_set.final_set = merged_set.add_set - merged_set.remove_set
        return merged_set

# create db 1 and insert some shopping lists
test1 = ShoppingListDB('test1.db')
test1.add_shopping_list('1', 'list1')
test1.add_shopping_list('2', 'list2')
test1.add_shopping_list('3', 'list3')

# create db 2 and insert some shopping lists
test2 = ShoppingListDB('test2.db')
test2.add_shopping_list('1', 'list1')
test2.add_shopping_list('2', 'list2')
test2.add_shopping_list('3', 'list3')
test2.delete_shopping_list('3')

crdt1 = ListsCRDT()
crdt1.loadDatabase('test1.db')

crdt2 = ListsCRDT()
crdt2.loadDatabase('test2.db')

new_data = crdt1.merge(crdt2)
print("Add set:", new_data.add_set)
print("Remove set:", new_data.remove_set)
print("Final set:", new_data.final_set)

test1.clear_data()
test1.close_connection()

test2.clear_data()
test2.close_connection()
