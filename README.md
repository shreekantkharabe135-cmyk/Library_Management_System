# Library Management System

A modern, full-stack Library Management System built with **Python Flask**, **HTML**, **CSS**, and **JavaScript**. Designed as a college mini-project demonstrating core Python concepts.

---

## Features

| Feature | Description |
|---------|-------------|
| **Home Page** | Hero section with quick stats, feature cards, and sample data loader |
| **Books Management** | Add, search, view, edit, and delete books |
| **Readers Management** | Register, search, edit, and delete readers |
| **My Bag** | Add/remove books and checkout (issue) to a reader |
| **Returns** | View issued books, filter by reader/status, and return books |
| **Dashboard** | Statistics overview, genre chart, and recent transactions |
| **Search** | Real-time search on books and readers |
| **Responsive Design** | Works on desktop, tablet, and mobile |

---

## Python Concepts Used

- **Lists** — storing collections of book, reader, and transaction records
- **Dictionaries** — representing each book/reader/transaction as key-value pairs
- **Functions** — every operation (CRUD, search, checkout, return) is a separate function
- **File Handling** — data is persisted in JSON files (`books.json`, `readers.json`, `transactions.json`)
- **List Comprehensions** — used for filtering and searching records
- **Modules** — `json`, `os`, `datetime` from Python standard library

---

## Project Structure

```
Library_Management_System/
├── app.py                  # Flask backend (all routes & logic)
├── README.md               # Project documentation
├── data/                   # JSON data files (auto-created)
│   ├── books.json
│   ├── readers.json
│   └── transactions.json
├── static/
│   ├── css/
│   │   └── style.css       # All styles (responsive)
│   └── js/
│       └── main.js         # Common JavaScript functions
└── templates/
    ├── base.html            # Base template (navbar, footer)
    ├── home.html            # Home page
    ├── books.html           # Books management
    ├── readers.html         # Readers management
    ├── bag.html             # My Bag & checkout
    ├── returns.html         # Book returns
    └── dashboard.html       # Dashboard & stats
```

---

## How to Run

### 1. Install Flask
```bash
pip install flask
```

### 2. Run the Application
```bash
python app.py
```

### 3. Open in Browser
```
http://127.0.0.1:5000
```

### 4. Load Sample Data
Click **"Load Sample Data"** on the home page to add 10 books and 5 readers.

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/books` | Get all books (or search with `?q=`) |
| POST | `/api/books` | Add a new book |
| GET | `/api/books/<id>` | Get a single book |
| PUT | `/api/books/<id>` | Update a book |
| DELETE | `/api/books/<id>` | Delete a book |
| GET | `/api/readers` | Get all readers (or search with `?q=`) |
| POST | `/api/readers` | Register a reader |
| GET | `/api/readers/<id>` | Get a single reader |
| PUT | `/api/readers/<id>` | Update a reader |
| DELETE | `/api/readers/<id>` | Delete a reader |
| GET | `/api/bag` | Get bag contents |
| POST | `/api/bag/add/<id>` | Add book to bag |
| POST | `/api/bag/remove/<id>` | Remove book from bag |
| POST | `/api/bag/checkout` | Checkout (issue books) |
| GET | `/api/transactions` | Get transactions |
| POST | `/api/transactions/return/<id>` | Return a book |
| GET | `/api/dashboard` | Get dashboard stats |
| POST | `/api/seed` | Load sample data |
| DELETE | `/api/seed` | Clear all data |

---

## Technologies

- **Backend:** Python 3, Flask
- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Storage:** JSON files (no database required)
- **Icons:** Font Awesome 6
- **Fonts:** Google Fonts (Inter)
