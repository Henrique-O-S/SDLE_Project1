# --------------------------------------------------------------

import tkinter as tk

# --------------------------------------------------------------

class ArmazonGUI:
    def __init__(self, client):
        self.client = client
        self.root = tk.Tk()
        self.root.title("ARMAZON")
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.build()
        self.root.mainloop()

    def clear(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def build(self):
        self.header()
        self.refresh_button()
        self.home_button()
        self.admin_button()
        self.content_frame = tk.Frame(self.root)
        self.content_frame.pack(padx=100, pady=10)
        for i in range(0, 100):
            self.content_frame.rowconfigure(i, pad=10)
        self.home()

# --------------------------------------------------------------

    def header(self):
        self.header = tk.Label(self.root, text="ARMAZON", font=("Arial", 18, "bold"), bg="#3498db", fg="white", pady=15)
        self.header.pack(fill=tk.X)

    def refresh_button(self):
        self.refresh_btn = tk.Button(self.root, text="🔄", font=("Arial", 12))
        self.refresh_btn.pack(pady=5)

    def home_button(self):
        self.home_btn = tk.Button(self.root, text="Home Page", font=("Arial", 10), bg="#3498db", fg="white", command=self.home)
        self.home_btn.pack(pady=5)

    def admin_button(self):	
        self.admin_btn = tk.Button(self.root, text="Admin Page", font=("Arial", 10), bg="#3498db", fg="white", command=self.admin)
        self.admin_btn.pack(pady=5)

# --------------------------------------------------------------

    def home(self):
        self.clear()
        label = tk.Label(self.content_frame, text="Home Page", font=("Arial", 14, "bold"))
        label.grid(row=0, column=0, columnspan=4)
        self.create_list_input()
        self.view_list_input()

    def create_list_input(self):
        new_list_label = tk.Label(self.content_frame, text="Create New Shopping List:")
        new_list_label.grid(row=1, column=0)
        self.new_list_entry = tk.Entry(self.content_frame)
        self.new_list_entry.grid(row=1, column=1)
        add_list_button = tk.Button(self.content_frame, text="Add List", bg="#3dd142", command=self.add_shopping_list)
        add_list_button.grid(row=1, column=3)

    def add_shopping_list(self):
        new_list_name = self.new_list_entry.get()
        if new_list_name:
            self.client.add_shopping_list(new_list_name)
            self.new_list_entry.delete(0, tk.END)
            self.admin()

    def view_list_input(self):
        view_list_label = tk.Label(self.content_frame, text="View Shopping List:")
        view_list_label.grid(row=2, column=0)
        self.view_list_entry = tk.Entry(self.content_frame)
        self.view_list_entry.grid(row=2, column=1)
        paste_button = tk.Button(self.content_frame, text="📋", command=self.paste_content)
        paste_button.grid(row=2, column=2)
        view_list_button = tk.Button(self.content_frame, text="View List", bg="#3dd142", command=self.get_view_list_entry)
        view_list_button.grid(row=2, column=3)

    def paste_content(self):
        content = self.content_frame.clipboard_get()
        self.view_list_entry.insert(tk.END, content)

    def get_view_list_entry(self):
        list_id = self.view_list_entry.get()
        self.shopping_list(list_id)

# --------------------------------------------------------------

    def admin(self):
        self.clear()
        label = tk.Label(self.content_frame, text="Admin Page", font=("Arial", 14, "bold"))
        label.grid(row=0, column=0, columnspan=3)
        self.lists()

    def lists(self):
        row = 1
        shopping_lists = self.client.database.get_shopping_lists()
        if shopping_lists:
            for shopping_list in shopping_lists:
                self.shopping_list_item(shopping_list, row)
                row += 1
        else:
            empty_label = tk.Label(self.content_frame, text="No shopping lists available.")
            empty_label.grid(row=row, column=0)

    def shopping_list_item(self, shopping_list, row):
        id = shopping_list[0]
        name = shopping_list[1]
        list_button = tk.Button(self.content_frame, text=f"{name}", command=lambda: self.shopping_list(id))
        list_button.grid(row=row, column=0)
        copy_button = tk.Button(self.content_frame, text="📋", command=lambda: self.copy_content(shopping_list[0]))
        copy_button.grid(row=row, column=1)
        self.delete_list_button(id, row, 2)

    def copy_content(self, content):
        self.content_frame.clipboard_clear()
        self.content_frame.clipboard_append(content)
        print("Copied to clipboard: " + content)

    def delete_list_button(self, id, row, col = 1, span = 1):
        delete_button = tk.Button(self.content_frame, text="Delete List", bg="#cc2f2f", fg="white", command=lambda: self.delete_list(id))
        delete_button.grid(row=row, column=col, columnspan=span)

    def delete_list(self, id):
        shopping_list = self.client.database.get_shopping_list(id)
        name = shopping_list[1]
        self.client.delete_shopping_list(id, name)
        self.admin()

# --------------------------------------------------------------

    def get_list(self, id):
        shopping_list = self.client.database.get_shopping_list(id)
        return shopping_list
    
    def get_item(self, list_id, item_name):
        item = self.client.database.get_item(list_id, item_name)
        return item

# --------------------------------------------------------------

    def shopping_list(self, list_id):
        if self.get_list(list_id):
            shopping_list = self.get_list(list_id)
            self.clear()
            label = tk.Label(self.content_frame, text=f"{shopping_list[1]}", font=("Arial", 14, "bold"))
            label.grid(row=0, column=0, columnspan=4)
            id_label = tk.Label(self.content_frame, text=f"[{shopping_list[0]}]", font=("Arial", 12, "bold"))
            id_label.grid(row=1, column=0, columnspan=4)
            copy_button = tk.Button(self.content_frame, text="📋 Copy ID", command=lambda: self.copy_content(shopping_list[0]))
            copy_button.grid(row=2, columnspan=4)
            self.delete_list_button(shopping_list[0], 3, 0, 4)
            row = 5
            row = self.items(shopping_list, row)
            self.add_item_input(shopping_list, row)
        else:
            error_label = tk.Label(self.content_frame, text="Shopping list not found.")
            error_label.grid(row=3, column=0, columnspan=3)
            self.root.after(1000, error_label.destroy)
    
    def items(self, shopping_list, row):
        self.item_entries = {}
        items = self.client.database.get_items(shopping_list[0])
        if (len(items) > 0):
            for item in items:
                self.item(shopping_list, item, row)
                row += 1
        else:
            empty_label = tk.Label(self.content_frame, text="No items available.")
            empty_label.grid(row=row, column=0, columnspan=4)
            row += 1
        return row

    def item(self, shopping_list, item, row):
        item_label = tk.Label(self.content_frame, text=f"{item[1]}")
        item_label.grid(row=row, column=0)
        self.update_item_input(shopping_list, item, row)
        self.delete_item_button(shopping_list, item, row)

    def update_item_input(self, shopping_list, item, row):
        name = item[1]
        quantity = item[2]
        self.item_entries[name] = tk.Entry(self.content_frame) 
        self.item_entries[name].grid(row=row, column=1)
        self.item_entries[name].insert(0, str(int(quantity)))
        modify_item_button = tk.Button(self.content_frame, text="Update Quantity", bg="#3dd142", command=lambda: self.update_item(shopping_list, item, row))
        modify_item_button.grid(row=row, column=2)

    def update_item(self, shopping_list, item, row):
        name = item[1]
        quantity_value = self.item_entries[name].get()  
        if quantity_value.isdigit() and int(quantity_value) >= 0:
            self.client.update_item(shopping_list[0], name, int(quantity_value))
            self.shopping_list(shopping_list[0])
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid quantity")
            error_label.grid(row=row+1, column=0, columnspan=2)
            self.root.after(1000, error_label.destroy)

    def delete_item_button(self, shopping_list, item, row):
        delete_button = tk.Button(self.content_frame, text="Delete Item", bg="#cc2f2f", fg="white", command=lambda: self.delete_item(shopping_list, item))
        delete_button.grid(row=row, column=3)

    def delete_item(self, shopping_list, item):
        self.client.delete_item(shopping_list[0], item[1], item[2])
        self.shopping_list(shopping_list[0])
    
    def add_item_input(self, shopping_list, row):
        label = tk.Label(self.content_frame, text="Add Item:", font=("Arial", 10, "bold"))
        label.grid(row=row, column=0, columnspan=4)
        row += 1
        name_label = tk.Label(self.content_frame, text="Name:")
        name_label.grid(row=row, column=1)
        self.new_item_name_entry = tk.Entry(self.content_frame)
        self.new_item_name_entry.grid(row=row, column=2)
        row += 1
        quantity_label = tk.Label(self.content_frame, text="Quantity:")
        quantity_label.grid(row=row, column=1)
        self.new_item_quantity_entry = tk.Entry(self.content_frame)
        self.new_item_quantity_entry.grid(row=row, column=2)
        row += 1
        add_item_button = tk.Button(self.content_frame, text="Add Item", bg="#3dd142", command=lambda: self.add_item(shopping_list, row))
        add_item_button.grid(row=row, column=0, columnspan=4)

    def add_item(self, shopping_list, row):
        new_item_name = self.new_item_name_entry.get()
        new_item_quantity = self.new_item_quantity_entry.get()
        if new_item_name and new_item_quantity.isdigit() and int(new_item_quantity) >= 0:
            new_item = self.client.add_item(shopping_list[0], new_item_name, int(new_item_quantity))
            if (new_item):
                self.shopping_list(shopping_list[0])
            else:
                error_label = tk.Label(self.content_frame, text="This item already exists.")
                error_label.grid(row=row+1, column=1, columnspan=3)
                self.root.after(1000, error_label.destroy)
        else:
            error_label = tk.Label(self.content_frame, text="Please enter a valid item name and quantity")
            error_label.grid(row=row+1, column=1, columnspan=3)
            self.root.after(1000, error_label.destroy)

# --------------------------------------------------------------

    def on_closing(self):
        self.client.database.close_connection()
        self.root.destroy() 

# --------------------------------------------------------------
