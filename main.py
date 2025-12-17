# billing_gui.py
# GUI Supermarket Billing with basic DSA: Linked List + Hash Map + Min-Heap + Stack
# Run: python billing_gui.py
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import heapq
from typing import Optional, Dict, List


# ----------------------------
# Domain Models + DSA Structures
# ----------------------------
@dataclass
class Product:
    id: int
    name: str
    price: float
    quantity: int


class Node:
    """Singly linked list node for inventory order."""

    def __init__(self, product: Product):
        self.product = product
        self.next: Optional["Node"] = None


class Inventory:
    """
    Inventory backed by:
      - Singly linked list (maintain insertion order / simple traversal)
      - Hash map {id: Node} for O(1) lookup by id
      - Min-heap of (quantity, id) for quick 'low stock' queries
    """

    def __init__(self):
        self.head: Optional[Node] = None
        self.tail: Optional[Node] = None
        self.index: Dict[int, Node] = {}
        self._low_stock_heap: List[tuple[int, int]] = []  # (qty, id)

    def add_product(self, prod: Product) -> bool:
        """Return False if id exists; True on success."""
        if prod.id in self.index:
            return False
        node = Node(prod)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self.index[prod.id] = node
        heapq.heappush(self._low_stock_heap, (prod.quantity, prod.id))
        return True

    def to_list(self) -> List[Product]:
        out = []
        cur = self.head
        while cur:
            out.append(cur.product)
            cur = cur.next
        return out

    def find(self, pid: int) -> Optional[Product]:
        node = self.index.get(pid)
        return node.product if node else None

    def update_quantity(self, pid: int, new_qty: int) -> None:
        node = self.index.get(pid)
        if not node:
            return
        node.product.quantity = new_qty
        # Push new snapshot to heap (lazy deletion)
        heapq.heappush(self._low_stock_heap, (new_qty, pid))

    def k_lowest_stock(self, k: int = 5) -> List[Product]:
        """Return k products with lowest stock (heap with lazy deletion)."""
        results = []
        seen = 0
        popped = []
        while self._low_stock_heap and seen < k:
            qty, pid = heapq.heappop(self._low_stock_heap)
            popped.append((qty, pid))
            prod = self.find(pid)
            if prod and prod.quantity == qty:
                results.append(prod)
                seen += 1
        # Push back popped items
        for item in popped:
            heapq.heappush(self._low_stock_heap, item)
        return results


class BillingSystem:
    """
    Billing logic:
      - Cart stored as {id: qty}
      - Stack for undo actions
      - Discount slabs
    """

    def __init__(self, inventory: Inventory):
        self.inventory = inventory
        self.cart: Dict[int, int] = {}
        self.undo_stack: List[tuple[str, int, int]] = []  # ("add", id, qty)
        self.customer_name: str = ""
        self.subtotal: float = 0.0
        self.discount: float = 0.0

    def add_to_cart(self, pid: int, qty: int) -> str:
        prod = self.inventory.find(pid)
        if not prod:
            return "Product not found."
        if qty <= 0:
            return "Quantity should be positive."
        if qty > prod.quantity:
            return "Not enough stock available."
        # Update inventory and cart
        prod.quantity -= qty
        self.cart[pid] = self.cart.get(pid, 0) + qty
        self.inventory.update_quantity(pid, prod.quantity)
        self.undo_stack.append(("add", pid, qty))
        return f"Added: {prod.name} x {qty} = Rs.{prod.price * qty:.2f}"

    def undo_last(self) -> str:
        if not self.undo_stack:
            return "Nothing to undo."
        action, pid, qty = self.undo_stack.pop()
        if action == "add":
            # Revert inventory and cart
            prod = self.inventory.find(pid)
            if not prod:
                return "Unexpected error: product missing."
            prod.quantity += qty
            self.inventory.update_quantity(pid, prod.quantity)
            self.cart[pid] -= qty
            if self.cart[pid] <= 0:
                self.cart.pop(pid, None)
            return f"Undone: returned {qty} of {prod.name}."
        return "Unknown action."

    def compute_totals(self) -> None:
        self.subtotal = 0.0
        for pid, qty in self.cart.items():
            prod = self.inventory.find(pid)
            if prod:
                self.subtotal += prod.price * qty
        # Discount slabs
        if self.subtotal > 500:
            self.discount = 0.10 * self.subtotal
        elif self.subtotal > 200:
            self.discount = 0.05 * self.subtotal
        else:
            self.discount = 0.0

    def checkout_summary(self) -> str:
        self.compute_totals()
        total = self.subtotal - self.discount
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d %H:%M:%S")
        lines = [
            "=====================================",
            " SUPERMARKET BILL ",
            "=====================================",
            f"Bill Date: {date_str}",
            f"Customer: {self.customer_name}",
            "",
            "Item Qty Price Total",
            "-------------------------------------"
        ]
        for pid, qty in self.cart.items():
            prod = self.inventory.find(pid)
            if prod:
                line_total = prod.price * qty
                item_line = f"{prod.name[:20]:<20} {qty:>3} ₹{prod.price:>6.2f} ₹{line_total:>6.2f}"
                lines.append(item_line)
        lines.extend([
            "-------------------------------------",
            f"{'Subtotal:':<24} ₹{self.subtotal:>6.2f}",
            f"{'Discount:':<24} ₹{self.discount:>6.2f}",
            "-------------------------------------",
            f"{'TOTAL:':<24} ₹{total:>6.2f}",
            "",
            "Thank you for shopping!",
            "====================================="
        ])
        return "\n".join(lines)

    def clear(self) -> None:
        self.cart.clear()
        self.undo_stack.clear()
        self.customer_name = ""
        self.subtotal = 0.0
        self.discount = 0.0


# ----------------------------
# GUI
# ----------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Premium Supermarket Billing System")
        self.geometry("1200x800")
        self.resizable(True, True)
        self.configure(bg='white')

        # Light White Theme
        self.tk_setPalette(background='white', foreground='black',
                           selectBackground='#e6f3ff', selectForeground='black')

        self.style = ttk.Style()
        self.style.theme_use('clam')

        # Premium font setup
        self.title_font = ('Segoe UI', 18, 'bold')
        self.heading_font = ('Segoe UI', 12, 'bold')
        self.default_font = ('Segoe UI', 10)
        self.style.configure('.', font=self.default_font)

        # Custom title label
        title_label = tk.Label(self, text="Premium Billing Suite", font=self.title_font,
                               bg='white', fg='black', pady=10)
        title_label.pack()

        # Frame for main content
        main_frame = tk.Frame(self, bg='white')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Notebook with enhanced styling
        self.style.configure('TNotebook', background='white', borderwidth=0,
                             focuscolor='none')
        self.style.configure('TNotebook.Tab', background='white', foreground='black',
                             padding=[25, 15], font=self.heading_font)
        self.style.map('TNotebook.Tab',
                       background=[('selected', '#e6f3ff'), ('active', '#f0f0f0')],
                       foreground=[('selected', 'black')])

        nb = ttk.Notebook(main_frame)
        nb.pack(fill=tk.BOTH, expand=True)

        self.inventory_frame = ttk.Frame(nb, style='TFrame')
        self.billing_frame = ttk.Frame(nb, style='TFrame')
        nb.add(self.inventory_frame, text="📦 Inventory Management")
        nb.add(self.billing_frame, text="🛒 Billing & Cart")

        # Enhanced Frame styling
        self.style.configure('TFrame', background='white')

        # Label styling
        self.style.configure('TLabel', background='white', foreground='black',
                             font=self.default_font)
        self.style.configure('Title.TLabel', font=self.title_font, foreground='black')

        # LabelFrame with premium look
        self.style.configure('TLabelframe', background='white', foreground='black',
                             borderwidth=1, relief='solid', padding=10)
        self.style.configure('TLabelframe.Label', background='white', foreground='black',
                             font=self.heading_font)

        # Entry with premium styling
        self.style.configure('TEntry', fieldbackground='white', foreground='black',
                             borderwidth=1, insertcolor='black',
                             font=self.default_font, relief='solid')
        self.style.map('TEntry', fieldbackground=[('focus', '#e6f3ff'), ('readonly', 'white')])

        # Button with blue hover
        self.style.configure('TButton', background='white', foreground='black',
                             borderwidth=1, focuscolor='none', padding=12,
                             font=self.heading_font, relief='solid')
        self.style.map('TButton',
                       background=[('active', '#e6f3ff'), ('pressed', '#d0e7ff')],
                       foreground=[('active', 'black'), ('pressed', 'black')])

        # Treeview with premium styling
        self.style.configure('Treeview', background='white', foreground='black',
                             fieldbackground='white', borderwidth=1, rowheight=30,
                             font=self.default_font, relief='solid')
        self.style.map('Treeview', background=[('selected', '#e6f3ff')],
                       foreground=[('selected', 'black')])
        self.style.configure('Treeview.Heading', background='#f0f0f0', foreground='black',
                             font=self.heading_font, relief='solid', borderwidth=1)
        self.style.map('Treeview.Heading', background=[('active', '#e6f3ff')],
                       foreground=[('active', 'black')])

        # Scrollbar
        self.style.configure('Vertical.TScrollbar', background='white', troughcolor='white',
                             borderwidth=1, arrowcolor='black')
        self.style.map('Vertical.TScrollbar', background=[('active', '#e6f3ff')])

        self.inventory = Inventory()
        self.billing = BillingSystem(self.inventory)
        self._build_ui()

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = tk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN,
                              anchor=tk.W, bg='#f0f0f0', fg='black', font=('Segoe UI', 9))
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

    # ----- UI Builders -----
    def _build_ui(self):
        self._build_inventory_tab(self.inventory_frame)
        self._build_billing_tab(self.billing_frame)

    def _build_inventory_tab(self, parent: ttk.Frame):
        # Form with enhanced layout
        form = ttk.LabelFrame(parent, text="➕ Add New Product")
        form.pack(fill=tk.X, padx=15, pady=15)
        self.pid_var = tk.StringVar()
        self.pname_var = tk.StringVar()
        self.price_var = tk.StringVar()
        self.qty_var = tk.StringVar()
        row = 0
        ttk.Label(form, text="🆔 ID").grid(row=row, column=0, padx=15, pady=12, sticky="w")
        ttk.Entry(form, textvariable=self.pid_var, width=18).grid(row=row, column=1, padx=15, pady=12)
        ttk.Label(form, text="📝 Name").grid(row=row, column=2, padx=15, pady=12, sticky="w")
        ttk.Entry(form, textvariable=self.pname_var, width=35).grid(row=row, column=3, padx=15, pady=12)
        row += 1
        ttk.Label(form, text="💰 Price").grid(row=row, column=0, padx=15, pady=12, sticky="w")
        ttk.Entry(form, textvariable=self.price_var, width=18).grid(row=row, column=1, padx=15, pady=12)
        ttk.Label(form, text="📊 Quantity").grid(row=row, column=2, padx=15, pady=12, sticky="w")
        ttk.Entry(form, textvariable=self.qty_var, width=18).grid(row=row, column=3, padx=15, pady=12)
        row += 1
        ttk.Button(form, text="✨ Add Product", command=self._on_add_product).grid(row=row, column=0, padx=15, pady=12,
                                                                                  sticky="w")
        ttk.Button(form, text="🔍 Low Stock Alert", command=self._on_show_low_stock).grid(row=row, column=1, padx=15,
                                                                                         pady=12, sticky="w")
        # Table with scrollbar
        table_frame = ttk.LabelFrame(parent, text="📋 Product Inventory")
        table_frame.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        tree_container = tk.Frame(table_frame)
        tree_container.pack(fill=tk.BOTH, expand=True)
        self.inv_table = ttk.Treeview(tree_container, columns=("id", "name", "price", "qty"), show="headings",
                                      height=18)
        v_scrollbar = ttk.Scrollbar(tree_container, orient=tk.VERTICAL, command=self.inv_table.yview)
        self.inv_table.configure(yscrollcommand=v_scrollbar.set)
        for col, text, w in [
            ("id", "ID", 100),
            ("name", "Product Name", 400),
            ("price", "Price (₹)", 150),
            ("qty", "Stock Qty", 150)
        ]:
            self.inv_table.heading(col, text=text)
            self.inv_table.column(col, width=w, anchor="center")
        self.inv_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self._refresh_inventory_table()

    def _build_billing_tab(self, parent: ttk.Frame):
        # Customer and scan with enhanced layout
        scan = ttk.LabelFrame(parent, text="👤 Customer Details & Quick Scan")
        scan.pack(fill=tk.X, padx=15, pady=15)
        self.cust_var = tk.StringVar()
        ttk.Label(scan, text="👤 Name").grid(row=0, column=0, padx=15, pady=12, sticky="w")
        ttk.Entry(scan, textvariable=self.cust_var, width=40).grid(row=0, column=1, padx=15, pady=12, columnspan=3)
        self.scan_id_var = tk.StringVar()
        self.scan_qty_var = tk.StringVar()
        ttk.Label(scan, text="🆔 Product ID").grid(row=1, column=0, padx=15, pady=12, sticky="w")
        ttk.Entry(scan, textvariable=self.scan_id_var, width=18).grid(row=1, column=1, padx=15, pady=12)
        ttk.Label(scan, text="📊 Qty").grid(row=1, column=2, padx=15, pady=12, sticky="w")
        ttk.Entry(scan, textvariable=self.scan_qty_var, width=18).grid(row=1, column=3, padx=15, pady=12)
        ttk.Button(scan, text="🛒 Add to Cart", command=self._on_add_to_cart).grid(row=1, column=4, padx=15, pady=12)
        ttk.Button(scan, text="↩️ Undo Last", command=self._on_undo).grid(row=1, column=5, padx=15, pady=12)
        ttk.Button(scan, text="✅ Checkout", command=self._on_checkout).grid(row=1, column=6, padx=15, pady=12)
        # Cart table with scrollbar
        cart_box = ttk.LabelFrame(parent, text="🛍️ Shopping Cart")
        cart_box.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        cart_container = tk.Frame(cart_box)
        cart_container.pack(fill=tk.BOTH, expand=True)
        self.cart_table = ttk.Treeview(cart_container, columns=("id", "name", "qty", "price", "total"), show="headings",
                                       height=15)
        v_scrollbar_cart = ttk.Scrollbar(cart_container, orient=tk.VERTICAL, command=self.cart_table.yview)
        self.cart_table.configure(yscrollcommand=v_scrollbar_cart.set)
        for col, text, w in [
            ("id", "ID", 80),
            ("name", "Product Name", 350),
            ("qty", "Qty", 80),
            ("price", "Price (₹)", 120),
            ("total", "Line Total (₹)", 150)
        ]:
            self.cart_table.heading(col, text=text)
            self.cart_table.column(col, width=w, anchor="center")
        self.cart_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        v_scrollbar_cart.pack(side=tk.RIGHT, fill=tk.Y)

        # Totals + Checkout - FIXED LAYOUT
        bottom = tk.Frame(parent, bg='white')
        bottom.pack(fill=tk.X, padx=15, pady=15)

        # Totals frame on the left
        totals_frame = tk.Frame(bottom, bg='white')
        totals_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.subtotal_var = tk.StringVar(value="0.00")
        self.discount_var = tk.StringVar(value="0.00")
        self.total_var = tk.StringVar(value="0.00")

        # Create labels in a row
        ttk.Label(totals_frame, text="💳 Subtotal:", background='white').pack(side=tk.LEFT, padx=20, pady=15)
        ttk.Label(totals_frame, textvariable=self.subtotal_var, font=self.heading_font,
                  foreground='black', background='white').pack(side=tk.LEFT, padx=10, pady=15)

        ttk.Label(totals_frame, text="🎁 Discount:", background='white').pack(side=tk.LEFT, padx=20, pady=15)
        ttk.Label(totals_frame, textvariable=self.discount_var, font=self.heading_font,
                  foreground='black', background='white').pack(side=tk.LEFT, padx=10, pady=15)

        ttk.Label(totals_frame, text="💰 Total:", background='white').pack(side=tk.LEFT, padx=20, pady=15)
        ttk.Label(totals_frame, textvariable=self.total_var, font=self.title_font,
                  foreground='black', background='white').pack(side=tk.LEFT, padx=10, pady=15)

        # Buttons frame on the right
        buttons_frame = tk.Frame(bottom, bg='white')
        buttons_frame.pack(side=tk.RIGHT, padx=10)

        checkout_btn = ttk.Button(buttons_frame, text="✅ Checkout", command=self._on_checkout)
        checkout_btn.pack(side=tk.RIGHT, padx=10)

        clear_btn = ttk.Button(buttons_frame, text="🗑️ Clear Cart", command=self._on_clear_cart)
        clear_btn.pack(side=tk.RIGHT)

        self._refresh_cart_table_and_totals()

    # ----- Inventory Actions -----
    def _on_add_product(self):
        try:
            pid = int(self.pid_var.get().strip())
            name = self.pname_var.get().strip()
            price = float(self.price_var.get().strip())
            qty = int(self.qty_var.get().strip())
        except ValueError:
            messagebox.showerror("❌ Invalid Input", "Please enter valid ID, Price, and Quantity.")
            self.status_var.set("Error: Invalid input")
            return
        if not name:
            messagebox.showerror("❌ Invalid Input", "Product name cannot be empty.")
            self.status_var.set("Error: Empty name")
            return
        if price < 0 or qty < 0:
            messagebox.showerror("❌ Invalid Input", "Price and Quantity must be non-negative.")
            self.status_var.set("Error: Negative values")
            return
        ok = self.inventory.add_product(Product(pid, name, price, qty))
        if not ok:
            messagebox.showerror("❌ Duplicate ID", f"Product ID {pid} already exists.")
            self.status_var.set("Error: Duplicate ID")
            return
        self._clear_inventory_form()
        self._refresh_inventory_table()
        messagebox.showinfo("✅ Success", "Product added successfully!")
        self.status_var.set("Product added")

    def _clear_inventory_form(self):
        self.pid_var.set("")
        self.pname_var.set("")
        self.price_var.set("")
        self.qty_var.set("")

    def _refresh_inventory_table(self):
        for row in self.inv_table.get_children():
            self.inv_table.delete(row)
        for p in self.inventory.to_list():
            self.inv_table.insert("", tk.END, values=(p.id, p.name, f"₹{p.price:.2f}", p.quantity))

    def _on_show_low_stock(self):
        prods = self.inventory.k_lowest_stock(5)
        if not prods:
            messagebox.showinfo("ℹ️ Low Stock", "No products found.")
            self.status_var.set("No low stock items")
            return
        msg = "\n".join([f"• {p.name} (ID {p.id}) — Stock: {p.quantity}" for p in prods])
        messagebox.showinfo("⚠️ 5 Lowest Stock Items", msg)
        self.status_var.set("Low stock checked")

    # ----- Billing Actions -----
    def _on_add_to_cart(self):
        self.billing.customer_name = self.cust_var.get().strip()
        try:
            pid = int(self.scan_id_var.get().strip())
            qty = int(self.scan_qty_var.get().strip())
        except ValueError:
            messagebox.showerror("❌ Invalid Input", "Enter valid Product ID and Quantity.")
            self.status_var.set("Error: Invalid scan input")
            return
        result = self.billing.add_to_cart(pid, qty)
        if result.startswith("Added"):
            self._refresh_inventory_table()
            self._refresh_cart_table_and_totals()
            self.scan_qty_var.set("")
            self.scan_id_var.set("")
            messagebox.showinfo("✅ Added to Cart", result)
            self.status_var.set("Item added to cart")
        else:
            messagebox.showwarning("⚠️ Notice", result)
            self.status_var.set("Add failed")

    def _on_undo(self):
        msg = self.billing.undo_last()
        self._refresh_inventory_table()
        self._refresh_cart_table_and_totals()
        messagebox.showinfo("↩️ Undo Complete", msg)
        self.status_var.set("Last action undone")

    def _refresh_cart_table_and_totals(self):
        for row in self.cart_table.get_children():
            self.cart_table.delete(row)
        subtotal = 0.0
        for pid, qty in self.billing.cart.items():
            prod = self.inventory.find(pid)
            if not prod:
                continue
            line_total = prod.price * qty
            subtotal += line_total
            self.cart_table.insert("", tk.END, values=(pid, prod.name, qty, f"₹{prod.price:.2f}", f"₹{line_total:.2f}"))
        # update totals via billing logic for consistency
        self.billing.compute_totals()
        self.subtotal_var.set(f"₹{self.billing.subtotal:.2f}")
        self.discount_var.set(f"₹{self.billing.discount:.2f}")
        total = self.billing.subtotal - self.billing.discount
        self.total_var.set(f"₹{total:.2f}")

    def _on_checkout(self):
        if not self.billing.cart:
            messagebox.showwarning("⚠️ Empty Cart", "No items in the cart.")
            self.status_var.set("Cart is empty")
            return
        summary = self.billing.checkout_summary()
        messagebox.showinfo("💳 Checkout Bill", summary)
        # After showing the bill, keep inventory updated and clear only the cart
        self.billing.clear()
        self._refresh_cart_table_and_totals()
        self.cust_var.set("")
        self.scan_id_var.set("")
        self.scan_qty_var.set("")
        self.status_var.set("Checkout complete")

    def _on_clear_cart(self):
        # return cart items to inventory
        for pid, qty in list(self.billing.cart.items()):
            prod = self.inventory.find(pid)
            if prod:
                prod.quantity += qty
                self.inventory.update_quantity(pid, prod.quantity)
        self.billing.clear()
        self._refresh_inventory_table()
        self._refresh_cart_table_and_totals()
        messagebox.showinfo("🗑️ Cart Cleared", "Cart has been cleared and stock restored.")
        self.status_var.set("Cart cleared")


# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    App().mainloop()