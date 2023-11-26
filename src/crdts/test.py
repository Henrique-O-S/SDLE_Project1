import time
from datetime import datetime
from items_crdt import ItemsCRDT

logs_1 = []
logs_2 = []

t = datetime.now()
logs_1.append((t, 'update', "apple", 5))
print("[Client A] Updated apple - 5")
time.sleep(1)

t = datetime.now()
logs_2.append((t, 'remove', "apple", 3))
print("[Client B] Removed apple - 3")
time.sleep(1)

t = datetime.now()
logs_1.append((t, 'update', "apple", 8))
print("[Client A] Updated apple - 8")
time.sleep(1)

crdt = ItemsCRDT([logs_1, logs_2])
final_set = crdt.merge().get_final_set()
print("\nFinal Set:", final_set)
