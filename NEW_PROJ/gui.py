# --------------------------------------------------------------

import tkinter as tk

# --------------------------------------------------------------

class ArmazonGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("ARMAZON")
        self.shopping_lists = [
            {
                "id": 0,
                "name": "Groceries",
                "items": [
                    {
                        "name": "Apples",
                        "quantity": 3
                    },
                    {
                        "name": "Milk",
                        "quantity": 2
                    },
                    {
                        "name": "Bread",
                        "quantity": 1
                    }
                ]
            }    
        ]
        self.build()

    def clear(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def build(self):
        self.header()
        self.home_button()
        self.admin_button()
        self.frame()
        self.home()

    def frame(self):
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(padx=100, pady=10)

# --------------------------------------------------------------

    def header(self):
        self.header = tk.Label(self.root, text="ARMAZON", font=("Arial", 18, "bold"), bg="#3498db", fg="white", pady=15)
        self.header.pack(fill=tk.X)

    def home_button(self):
        self.home_btn = tk.Button(self.root, text="Home Page", font=("Arial", 10), command=self.home)
        self.home_btn.pack(pady=10)

    def admin_button(self):	
        self.admin_btn = tk.Button(self.root, text="Admin Page", font=("Arial", 10), command=self.admin)
        self.admin_btn.pack(pady=10)

# --------------------------------------------------------------

    def home(self):
        self.clear()
        label = tk.Label(self.content_frame, text="Home Page", font=("Arial", 14, "bold"))
        label.pack()
        self.create_list_input()
        self.view_list_input()

    def create_list_input(self):
        new_list_label = tk.Label(self.content_frame, text="Create New Shopping List:")
        new_list_label.pack()
        self.new_list_entry = tk.Entry(self.content_frame)
        self.new_list_entry.pack()
        add_list_button = tk.Button(self.content_frame, text="Add List", command=self.add_shopping_list)
        add_list_button.pack()

    def add_shopping_list(self):
        new_list_name = self.new_list_entry.get()
        if new_list_name:
            new_list_id = len(self.shopping_lists)
            self.shopping_lists.append({"id": new_list_id, "name": new_list_name, "items": []})
            self.new_list_entry.delete(0, tk.END)
            self.admin()

    def view_list_input(self):
        view_list_label = tk.Label(self.content_frame, text="View Shopping List:")
        view_list_label.pack()
        self.view_list_entry = tk.Entry(self.content_frame)
        self.view_list_entry.pack()
        view_list_button = tk.Button(self.content_frame, text="View List", command=self.get_view_list_entry)
        view_list_button.pack()

    def get_view_list_entry(self):
        list_id = int(self.view_list_entry.get())
        self.shopping_list(list_id)

# --------------------------------------------------------------

    def admin(self):
        self.clear()
        label = tk.Label(self.content_frame, text="Admin Page", font=("Arial", 14, "bold"))
        label.pack()
        self.lists()

    def lists(self):
        if self.shopping_lists:
            for shopping_list in self.shopping_lists:
                self.shopping_list_item(shopping_list)
        else:
            empty_label = tk.Label(self.content_frame, text="No shopping lists available.")
            empty_label.pack()

    def shopping_list_item(self, shopping_list):
        id = shopping_list["id"]
        list_button = tk.Button(self.content_frame, text=f"{id}. {shopping_list['name']}", command=lambda: self.shopping_list(shopping_list['id']))
        list_button.pack()
        self.delete_list_button(shopping_list['id'])

    def delete_list_button(self, id):
        delete_button = tk.Button(self.content_frame, text="Delete List", command=lambda: self.delete_list(id))
        delete_button.pack()
    def delete_list(self, id):
        del self.shopping_lists[id]
        self.admin()

# --------------------------------------------------------------

    def shopping_list(self, list_id):
        if self.get_list(list_id):
            shopping_list = self.get_list(list_id)
            self.clear()
            label = tk.Label(self.content_frame, text=f"Shopping List: {shopping_list['name']}", font=("Arial", 14, "bold"))
            label.pack()
            self.items(shopping_list)
            self.add_item_input(shopping_list)
            self.delete_list_button(shopping_list['id'])
        else:
            error_label = tk.Label(self.content_frame, text="Shopping list not found.")
            error_label.pack()
            self.root.after(1000, error_label.destroy)
    
    def items(self, shopping_list):
        self.item_entries = {}
        for item in shopping_list['items']:
            self.item(shopping_list, item)

    def item(self, shopping_list, item):
        item_label = tk.Label(self.content_frame, text=f"{item['name']}")
        item_label.pack()
        self.update_item_input(shopping_list, item) 

    def update_item_input(self, shopping_list, item):
        self.item_entries[item['name']] = tk.Entry(self.content_frame) 
        self.item_entries[item['name']].pack()
        self.item_entries[item['name']].insert(0, str(int(item['quantity'])))
        modify_item_button = tk.Button(self.content_frame, text="Update Quantity", command=lambda: self.update_item(shopping_list, item))
        modify_item_button.pack()

    def update_item(self, shopping_list, item):
        quantity_value = self.item_entries[item['name']].get()  
        if quantity_value.isdigit() and int(quantity_value) >= 0:
            for i in range(len(shopping_list['items'])):
                if shopping_list['items'][i]['name'] == item['name']:
                    shopping_list['items'][i]['quantity'] = int(quantity_value)
                    self.shopping_list(shopping_list['id'])
                    break
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid quantity")
            error_label.pack()
            self.root.after(1000, error_label.destroy)

    def delete_item_button(self, shopping_list, item):
        delete_button = tk.Button(self.content_frame, text="Delete", command=lambda: self.delete_item(shopping_list, item))
        delete_button.pack()

    def delete_item(self, shopping_list, item):
        for i in range(len(shopping_list['items'])):
            if shopping_list['items'][i]['name'] == item['name']:
                del shopping_list['items'][i]
                self.shopping_list(shopping_list['id'])
                break
    
    def add_item_input(self, shopping_list):
        label = tk.Label(self.content_frame, text="Add Item:", font=("Arial", 12, "bold"))
        label.pack()
        name_label = tk.Label(self.content_frame, text="Name:")
        name_label.pack()
        self.new_item_name_entry = tk.Entry(self.content_frame)
        self.new_item_name_entry.pack()
        quantity_label = tk.Label(self.content_frame, text="Quantity:")
        quantity_label.pack()
        self.new_item_quantity_entry = tk.Entry(self.content_frame)
        self.new_item_quantity_entry.pack()
        add_item_button = tk.Button(self.content_frame, text="Add Item", command=lambda: self.add_item(shopping_list))
        add_item_button.pack()

    def add_item(self, shopping_list):
        new_item_name = self.new_item_name_entry.get()
        new_item_quantity = self.new_item_quantity_entry.get()
        if new_item_name and new_item_quantity.isdigit() and int(new_item_quantity) >= 0:
            for i in range(len(self.shopping_lists)):
                if self.shopping_lists[i]['id'] == shopping_list['id']:
                    self.shopping_lists[i]['items'].append({"name": new_item_name, "quantity": int(new_item_quantity)})
                    self.shopping_list(shopping_list['id'])
                    break
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid item name and quantity")
            error_label.pack()
            self.root.after(1000, error_label.destroy)

# --------------------------------------------------------------

    def get_list(self, id):
        for shopping_list in self.shopping_lists:
            if shopping_list.get("id") == id:
                return shopping_list
        return None
    
    def get_item(self, list_id, item_name):
        shopping_list = self.get_list(list_id)
        for item in shopping_list['items']:
            if item.get("name") == item_name:
                return item
        return None

# --------------------------------------------------------------

root = tk.Tk()
app = ArmazonGUI(root)
root.mainloop()