# Premium Supermarket Billing System (Python + Tkinter)

A desktop-based supermarket billing application built with Python and Tkinter.
The goal of this project is to demonstrate how core **Data Structures and Algorithms (DSA)** can be applied in a practical, GUI-driven system.

This is not just a billing app. It’s a DSA showcase with a real use case.

---

## Features

### Inventory Management

* Add new products with ID, name, price, and quantity
* View full inventory in a tabular format
* Fast product lookup by ID
* Low-stock alert for the 5 items with the least quantity

### Billing & Cart

* Add products to cart using Product ID and quantity
* Automatic stock update on add/remove
* Undo last cart operation
* Real-time subtotal, discount, and total calculation
* Checkout with a formatted bill preview
* Clear cart and restore stock

### UI

* Clean, light-theme Tkinter interface
* Tab-based layout (Inventory | Billing)
* Tables with scrollbars
* Status bar for user feedback

---

## Data Structures Used (and Why)

This project intentionally uses multiple DSA concepts together.

### 1. Singly Linked List

**Where:** Inventory storage
**Why:**

* Maintains insertion order of products
* Simple traversal for displaying inventory

Each product is wrapped in a `Node` and linked sequentially.

---

### 2. Hash Map (Dictionary)

**Where:** Inventory index and cart
**Why:**

* O(1) lookup for products by ID
* Efficient cart management

```text
Inventory Index: { product_id → Node }
Cart: { product_id → quantity }
```

---

### 3. Min Heap

**Where:** Low-stock alert system
**Why:**

* Quickly find products with the smallest quantity
* Efficient for “top-k lowest stock” queries

Uses lazy deletion to keep heap operations fast.

---

### 4. Stack

**Where:** Undo functionality
**Why:**

* Last action should be undone first (LIFO)

Every cart add operation is pushed onto a stack and can be reverted.

---

## Discount Logic

* Subtotal > ₹500 → 10% discount
* Subtotal > ₹200 → 5% discount
* Otherwise → no discount

Discounts are calculated automatically during checkout.

---

## Project Structure

```
billing_gui.py
```

Single-file design for simplicity:

* Domain models
* DSA implementations
* Billing logic
* GUI layer

Easy to read, easy to evaluate.

---

## How to Run

### Prerequisites

* Python 3.10+
* Tkinter (comes bundled with Python on most systems)

### Run the App

```bash
python billing_gui.py
```

The GUI window will open immediately.

---

## Example Workflow

1. Open **Inventory Management**
2. Add a few products
3. Switch to **Billing & Cart**
4. Enter customer name
5. Add items using Product ID
6. Undo if needed
7. Checkout and view bill

---

## Why This Project Matters

What this really shows is:

* How abstract DSA concepts map to real systems
* How multiple structures can coexist cleanly
* How backend logic and GUI stay separated but connected

This is ideal for:

* DSA practical submissions
* Mini-projects
* Portfolio demos
* Interview discussions

---

## Future Improvements (Optional Ideas)

* Save bills to file (PDF / TXT)
* Persistent inventory using a database
* Search and filter inventory
* Barcode scanner integration
* Role-based access (Admin / Cashier)

---

## Author

Built with Python, Tkinter, and a strong focus on fundamentals.

If you want, I can also:

* Add comments explaining DSA line-by-line
* Convert this into a college-style project report
* Add UML diagrams or flowcharts
