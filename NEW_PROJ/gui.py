import tkinter as tk

class ShoppingListApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Shopping List Application")
        self.header = tk.Label(self.root, text="Shopping List Application", font=("Arial", 18, "bold"), bg="#3498db", fg="white", pady=15)
        self.header.pack(fill=tk.X)
        self.home_btn = tk.Button(self.root, text="Home Page", font=("Arial", 10), command=self.show_home)
        self.home_btn.pack(pady=10)
        self.admin_btn = tk.Button(self.root, text="Admin Page", font=("Arial", 10), command=self.show_admin)
        self.admin_btn.pack(pady=10)
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(padx=100, pady=50)
        self.shopping_lists = [{"name": "Groceries", "items": [{"name": "Apples", "quantity": 3}, {"name": "Milk", "quantity": 2}, {"name": "Bread", "quantity": 1}]}]
        self.show_home()

    def clear_content_frame(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def show_home(self):
        self.clear_content_frame()
        label = tk.Label(self.content_frame, text="Home Page", font=("Arial", 14, "bold"))
        label.pack()
        new_list_label = tk.Label(self.content_frame, text="Create New Shopping List:")
        new_list_label.pack()
        self.new_list_entry = tk.Entry(self.content_frame)
        self.new_list_entry.pack()
        add_list_button = tk.Button(self.content_frame, text="Add List", command=self.add_shopping_list)
        add_list_button.pack()
        view_list_label = tk.Label(self.content_frame, text="View Shopping List:")
        view_list_label.pack()
        self.view_list_entry = tk.Entry(self.content_frame)
        self.view_list_entry.pack()
        view_list_button = tk.Button(self.content_frame, text="View List", command=self.view_shopping_list)
        view_list_button.pack()

    def show_admin(self):
        self.clear_content_frame()
        label = tk.Label(self.content_frame, text="Admin Page", font=("Arial", 14, "bold"))
        label.pack()
        if self.shopping_lists:
            list_label = tk.Label(self.content_frame, text="All Shopping Lists:")
            list_label.pack()
            for idx, shopping_list in enumerate(self.shopping_lists, start=1):
                list_button = tk.Button(self.content_frame, text=f"{idx}. {shopping_list['name']}", command=lambda idx=idx: self.delete_shopping_list(idx))
                list_button.pack()
        else:
            empty_label = tk.Label(self.content_frame, text="No shopping lists available.")
            empty_label.pack()

    def add_shopping_list(self):
        new_list_name = self.new_list_entry.get()
        if new_list_name:
            self.shopping_lists.append({"name": new_list_name, "items": []})
            self.new_list_entry.delete(0, tk.END)
            self.show_admin()

    def view_shopping_list(self):
        list_id = self.view_list_entry.get()
        if list_id and list_id.isdigit():
            list_id = int(list_id)
            if 1 <= list_id <= len(self.shopping_lists):
                shopping_list = self.shopping_lists[list_id - 1]
                self.clear_content_frame()
                label = tk.Label(self.content_frame, text=f"Shopping List: {shopping_list['name']}", font=("Arial", 14, "bold"))
                label.pack()
                items_label = tk.Label(self.content_frame, text="Items:")
                items_label.pack()
                for idx, item in enumerate(shopping_list['items'], start=1):
                    item_label = tk.Label(self.content_frame, text=f"{idx}. {item['name']} - Quantity: {item['quantity']}")
                    item_label.pack()
                add_item_label = tk.Label(self.content_frame, text="Add Item:")
                add_item_label.pack()
                self.new_item_name_entry = tk.Entry(self.content_frame)
                self.new_item_name_entry.pack()
                self.new_item_quantity_entry = tk.Entry(self.content_frame)
                self.new_item_quantity_entry.pack()
                add_item_button = tk.Button(self.content_frame, text="Add Item", command=lambda: self.add_item(list_id))
                add_item_button.pack()
                modify_item_label = tk.Label(self.content_frame, text="Modify Item Quantity:")
                modify_item_label.pack()
                self.modify_item_index_entry = tk.Entry(self.content_frame)
                self.modify_item_index_entry.pack()
                self.modify_item_quantity_entry = tk.Entry(self.content_frame)
                self.modify_item_quantity_entry.pack()
                modify_item_button = tk.Button(self.content_frame, text="Modify Item Quantity", command=lambda: self.modify_item_quantity(list_id))
                modify_item_button.pack()
                delete_item_label = tk.Label(self.content_frame, text="Delete Item:")
                delete_item_label.pack()
                self.delete_item_index_entry = tk.Entry(self.content_frame)
                self.delete_item_index_entry.pack()
                delete_item_button = tk.Button(self.content_frame, text="Delete Item", command=lambda: self.delete_item(list_id))
                delete_item_button.pack()
            else:
                error_label = tk.Label(self.content_frame, text="Invalid shopping list ID")
                error_label.pack()
                self.root.after(1000, error_label.destroy)
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid ID")
            error_label.pack()
            self.root.after(1000, error_label.destroy)

    def add_item(self, list_id):
        shopping_list = self.shopping_lists[list_id - 1]
        new_item_name = self.new_item_name_entry.get()
        new_item_quantity = self.new_item_quantity_entry.get()
        if new_item_name and new_item_quantity.isdigit():
            shopping_list['items'].append({"name": new_item_name, "quantity": int(new_item_quantity)})
            self.view_shopping_list()
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid item name and quantity")
            error_label.pack()
            self.root.after(1000, error_label.destroy)

    def modify_item_quantity(self, list_id):
        shopping_list = self.shopping_lists[list_id - 1]
        modify_item_index = self.modify_item_index_entry.get()
        modify_item_quantity = self.modify_item_quantity_entry.get()
        if modify_item_index and modify_item_quantity.isdigit():
            idx = int(modify_item_index) - 1
            if 0 <= idx < len(shopping_list['items']):
                shopping_list['items'][idx]['quantity'] = int(modify_item_quantity)
                self.view_shopping_list()
            else:
                error_label = tk.Label(self.content_frame, text="Invalid item index")
                error_label.pack()
                self.root.after(1000, error_label.destroy)
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid item index and quantity")
            error_label.pack()
            self.root.after(1000, error_label.destroy)

    def delete_item(self, list_id):
        shopping_list = self.shopping_lists[list_id - 1]
        delete_item_index = self.delete_item_index_entry.get()
        if delete_item_index and delete_item_index.isdigit():
            idx = int(delete_item_index) - 1
            if 0 <= idx < len(shopping_list['items']):
                del shopping_list['items'][idx]
                self.view_shopping_list()
            else:
                error_label = tk.Label(self.content_frame, text="Invalid item index")
                error_label.pack()
                self.root.after(1000, error_label.destroy)
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid item index")
            error_label.pack()
            self.root.after(1000, error_label.destroy)

    def delete_shopping_list(self, idx):
        if 1 <= idx <= len(self.shopping_lists):
            del self.shopping_lists[idx - 1]
            self.show_admin()

root = tk.Tk()
app = ShoppingListApp(root)
root.mainloop()
