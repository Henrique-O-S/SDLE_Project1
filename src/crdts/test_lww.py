from datetime import datetime, timedelta
from lww import LWWElementSet

timestamp_1 = datetime.now() - timedelta(days=7)  
timestamp_2 = datetime.now() - timedelta(days=14)  

list1 = {
    "id": 1,
    "content": {
        "items": {"apple": 3, "banana": 5, "orange": 2}
    },
    "created_at": timestamp_1
}

list2 = {
    "id": 2,
    "content": {
        "items": {"milk": 2, "bread": 1, "eggs": 6}
    },
    "created_at": timestamp_2
}

shopping_list_set1 = LWWElementSet()
shopping_list_set2 = LWWElementSet()

for item, quantity in list1['content']['items'].items():
    shopping_list_set1.add(item, quantity, list1['created_at'])

for item, quantity in list2['content']['items'].items():
    shopping_list_set2.add(item, quantity, list2['created_at'])

shopping_list_set1.merge(shopping_list_set2)

item_to_lookup = "apple"
print(f"Is '{item_to_lookup}' in the shopping list set? {shopping_list_set1.lookup(item_to_lookup)}")