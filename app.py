"""
Library Management System - Flask Backend
A college mini-project demonstrating Python concepts:
- Lists for storing records
- Dictionaries for book/reader data  
- Functions for all operations
- File handling using JSON files
"""

from flask import Flask, render_template, request, jsonify, session
import json
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'library_secret_key_2024'

# ============================================================
# FILE PATHS - JSON files for persistent storage
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.json')
READERS_FILE = os.path.join(DATA_DIR, 'readers.json')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')


# ============================================================
# FILE HANDLING FUNCTIONS - Read/Write JSON files
# ============================================================
def ensure_data_dir():
    """Create data directory if it doesn't exist."""
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_json_file(filepath):
    """Load data from a JSON file. Returns a list of dictionaries."""
    ensure_data_dir()
    if not os.path.exists(filepath):
        # Create file with empty list if it doesn't exist
        with open(filepath, 'w') as f:
            json.dump([], f)
        return []
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data  # Returns a list of dictionaries


def save_json_file(filepath, data):
    """Save a list of dictionaries to a JSON file."""
    ensure_data_dir()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def generate_id(records_list):
    """Generate the next ID based on existing records in the list."""
    if len(records_list) == 0:
        return 1
    # Use a list comprehension to find the max id
    ids = [record['id'] for record in records_list]
    return max(ids) + 1


# ============================================================
# BOOK FUNCTIONS - CRUD operations for books
# ============================================================
def get_all_books():
    """Get all books from the JSON file. Returns a list of book dictionaries."""
    books_list = load_json_file(BOOKS_FILE)
    return books_list


def add_book(title, author, genre, isbn, total_copies):
    """Add a new book dictionary to the books list and save."""
    books_list = get_all_books()
    new_book = {
        'id': generate_id(books_list),
        'title': title,
        'author': author,
        'genre': genre,
        'isbn': isbn,
        'total_copies': int(total_copies),
        'available_copies': int(total_copies),
        'date_added': datetime.now().strftime('%Y-%m-%d')
    }
    books_list.append(new_book)  # Append dictionary to list
    save_json_file(BOOKS_FILE, books_list)
    return new_book


def search_books(query):
    """Search books by title, author, genre, or ISBN. Returns filtered list."""
    books_list = get_all_books()
    query = query.lower()
    # List comprehension to filter matching books
    results = [
        book for book in books_list
        if query in book['title'].lower()
        or query in book['author'].lower()
        or query in book['genre'].lower()
        or query in book['isbn'].lower()
    ]
    return results


def get_book_by_id(book_id):
    """Find a book dictionary by its ID."""
    books_list = get_all_books()
    for book in books_list:
        if book['id'] == book_id:
            return book
    return None


def update_book(book_id, title, author, genre, isbn, total_copies):
    """Update a book's information in the list."""
    books_list = get_all_books()
    for i in range(len(books_list)):
        if books_list[i]['id'] == book_id:
            diff = int(total_copies) - books_list[i]['total_copies']
            books_list[i]['title'] = title
            books_list[i]['author'] = author
            books_list[i]['genre'] = genre
            books_list[i]['isbn'] = isbn
            books_list[i]['total_copies'] = int(total_copies)
            books_list[i]['available_copies'] = max(0, books_list[i]['available_copies'] + diff)
            save_json_file(BOOKS_FILE, books_list)
            return books_list[i]
    return None


def delete_book(book_id):
    """Remove a book dictionary from the list."""
    books_list = get_all_books()
    # Filter out the book with matching id
    updated_list = [book for book in books_list if book['id'] != book_id]
    if len(updated_list) < len(books_list):
        save_json_file(BOOKS_FILE, updated_list)
        return True
    return False


# ============================================================
# READER FUNCTIONS - CRUD operations for readers
# ============================================================
def get_all_readers():
    """Get all readers from JSON file. Returns a list of reader dictionaries."""
    readers_list = load_json_file(READERS_FILE)
    return readers_list


def add_reader(name, email, phone, address):
    """Add a new reader dictionary to the readers list."""
    readers_list = get_all_readers()
    new_reader = {
        'id': generate_id(readers_list),
        'name': name,
        'email': email,
        'phone': phone,
        'address': address,
        'date_registered': datetime.now().strftime('%Y-%m-%d')
    }
    readers_list.append(new_reader)
    save_json_file(READERS_FILE, readers_list)
    return new_reader


def search_readers(query):
    """Search readers by name, email, or phone."""
    readers_list = get_all_readers()
    query = query.lower()
    results = [
        reader for reader in readers_list
        if query in reader['name'].lower()
        or query in reader['email'].lower()
        or query in reader['phone'].lower()
    ]
    return results


def get_reader_by_id(reader_id):
    """Find a reader dictionary by ID."""
    readers_list = get_all_readers()
    for reader in readers_list:
        if reader['id'] == reader_id:
            return reader
    return None


def update_reader(reader_id, name, email, phone, address):
    """Update reader information."""
    readers_list = get_all_readers()
    for i in range(len(readers_list)):
        if readers_list[i]['id'] == reader_id:
            readers_list[i]['name'] = name
            readers_list[i]['email'] = email
            readers_list[i]['phone'] = phone
            readers_list[i]['address'] = address
            save_json_file(READERS_FILE, readers_list)
            return readers_list[i]
    return None


def delete_reader(reader_id):
    """Remove a reader from the list."""
    readers_list = get_all_readers()
    updated_list = [reader for reader in readers_list if reader['id'] != reader_id]
    if len(updated_list) < len(readers_list):
        save_json_file(READERS_FILE, updated_list)
        return True
    return False


# ============================================================
# TRANSACTION FUNCTIONS - Issue and return books
# ============================================================
def get_all_transactions():
    """Get all transactions from JSON file."""
    transactions_list = load_json_file(TRANSACTIONS_FILE)
    return transactions_list


def issue_books(reader_id, book_ids_list):
    """Issue multiple books to a reader. Uses list of book IDs."""
    transactions_list = get_all_transactions()
    books_list = get_all_books()
    reader = get_reader_by_id(reader_id)
    
    if reader is None:
        return {'success': False, 'message': 'Reader not found'}
    
    issued = []  # List to track issued books
    errors = []  # List to track errors
    
    for book_id in book_ids_list:
        book = get_book_by_id(book_id)
        if book is None:
            errors.append(f'Book ID {book_id} not found')
            continue
        if book['available_copies'] <= 0:
            errors.append(f'"{book["title"]}" is not available')
            continue
        
        # Check if reader already has this book
        already_issued = False
        for txn in transactions_list:
            if (txn['reader_id'] == reader_id and 
                txn['book_id'] == book_id and 
                txn['status'] == 'issued'):
                already_issued = True
                break
        
        if already_issued:
            errors.append(f'"{book["title"]}" already issued to this reader')
            continue
        
        # Create transaction dictionary
        new_transaction = {
            'id': generate_id(transactions_list),
            'reader_id': reader_id,
            'reader_name': reader['name'],
            'book_id': book_id,
            'book_title': book['title'],
            'issue_date': datetime.now().strftime('%Y-%m-%d'),
            'return_date': None,
            'status': 'issued'
        }
        transactions_list.append(new_transaction)
        
        # Update available copies in books list
        for i in range(len(books_list)):
            if books_list[i]['id'] == book_id:
                books_list[i]['available_copies'] -= 1
                break
        
        issued.append(book['title'])
    
    save_json_file(TRANSACTIONS_FILE, transactions_list)
    save_json_file(BOOKS_FILE, books_list)
    
    return {
        'success': len(issued) > 0,
        'issued': issued,
        'errors': errors
    }


def return_book(transaction_id):
    """Return a book by updating the transaction status."""
    transactions_list = get_all_transactions()
    books_list = get_all_books()
    
    for i in range(len(transactions_list)):
        if transactions_list[i]['id'] == transaction_id:
            if transactions_list[i]['status'] == 'returned':
                return {'success': False, 'message': 'Book already returned'}
            
            transactions_list[i]['status'] = 'returned'
            transactions_list[i]['return_date'] = datetime.now().strftime('%Y-%m-%d')
            
            # Increase available copies
            book_id = transactions_list[i]['book_id']
            for j in range(len(books_list)):
                if books_list[j]['id'] == book_id:
                    books_list[j]['available_copies'] += 1
                    break
            
            save_json_file(TRANSACTIONS_FILE, transactions_list)
            save_json_file(BOOKS_FILE, books_list)
            return {'success': True, 'message': 'Book returned successfully'}
    
    return {'success': False, 'message': 'Transaction not found'}


def get_issued_transactions():
    """Get all currently issued (not returned) transactions."""
    transactions_list = get_all_transactions()
    # Filter using list comprehension
    issued = [txn for txn in transactions_list if txn['status'] == 'issued']
    return issued


def get_reader_transactions(reader_id):
    """Get all transactions for a specific reader."""
    transactions_list = get_all_transactions()
    reader_txns = [txn for txn in transactions_list if txn['reader_id'] == reader_id]
    return reader_txns


# ============================================================
# DASHBOARD FUNCTIONS - Statistics
# ============================================================
def get_dashboard_stats():
    """Calculate dashboard statistics. Returns a dictionary of stats."""
    books_list = get_all_books()
    readers_list = get_all_readers()
    transactions_list = get_all_transactions()
    
    total_books = sum(book['total_copies'] for book in books_list)
    available_books = sum(book['available_copies'] for book in books_list)
    issued_books = total_books - available_books
    total_readers = len(readers_list)
    total_titles = len(books_list)
    
    # Recent transactions (last 10)
    recent_transactions = sorted(
        transactions_list, 
        key=lambda x: x['id'], 
        reverse=True
    )[:10]
    
    # Genre distribution using dictionary
    genre_count = {}
    for book in books_list:
        genre = book['genre']
        if genre in genre_count:
            genre_count[genre] += book['total_copies']
        else:
            genre_count[genre] = book['total_copies']
    
    stats = {
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'total_readers': total_readers,
        'total_titles': total_titles,
        'recent_transactions': recent_transactions,
        'genre_distribution': genre_count
    }
    return stats


# ============================================================
# BAG (CART) FUNCTIONS - Session-based bag
# ============================================================
def get_bag():
    """Get the current bag (list of book IDs) from session."""
    if 'bag' not in session:
        session['bag'] = []  # Initialize empty list
    return session['bag']


def add_to_bag(book_id):
    """Add a book ID to the bag list."""
    bag = get_bag()
    if book_id in bag:
        return {'success': False, 'message': 'Book already in bag'}
    book = get_book_by_id(book_id)
    if book is None:
        return {'success': False, 'message': 'Book not found'}
    if book['available_copies'] <= 0:
        return {'success': False, 'message': 'Book not available'}
    bag.append(book_id)
    session['bag'] = bag
    session.modified = True
    return {'success': True, 'message': f'"{book["title"]}" added to bag'}


def remove_from_bag(book_id):
    """Remove a book ID from the bag list."""
    bag = get_bag()
    if book_id in bag:
        bag.remove(book_id)
        session['bag'] = bag
        session.modified = True
        return {'success': True, 'message': 'Book removed from bag'}
    return {'success': False, 'message': 'Book not in bag'}


def clear_bag():
    """Clear all items from the bag."""
    session['bag'] = []
    session.modified = True


def get_bag_books():
    """Get full book details for all books in the bag."""
    bag = get_bag()
    bag_books = []
    for book_id in bag:
        book = get_book_by_id(book_id)
        if book is not None:
            bag_books.append(book)
    return bag_books


# ============================================================
# FLASK ROUTES - Page routes
# ============================================================
@app.route('/')
def home():
    """Home page route."""
    stats = get_dashboard_stats()
    return render_template('home.html', stats=stats)


@app.route('/books')
def books_page():
    """Books management page."""
    return render_template('books.html')


@app.route('/readers')
def readers_page():
    """Readers management page."""
    return render_template('readers.html')


@app.route('/bag')
def bag_page():
    """My Bag page."""
    return render_template('bag.html')


@app.route('/returns')
def returns_page():
    """Returns page."""
    return render_template('returns.html')


@app.route('/dashboard')
def dashboard_page():
    """Dashboard page."""
    return render_template('dashboard.html')


# ============================================================
# API ROUTES - Book operations
# ============================================================
@app.route('/api/books', methods=['GET'])
def api_get_books():
    """API to get all books or search books."""
    query = request.args.get('q', '')
    if query:
        books = search_books(query)
    else:
        books = get_all_books()
    return jsonify(books)


@app.route('/api/books', methods=['POST'])
def api_add_book():
    """API to add a new book."""
    data = request.json
    book = add_book(
        data['title'], data['author'], data['genre'],
        data['isbn'], data['total_copies']
    )
    return jsonify({'success': True, 'book': book})


@app.route('/api/books/<int:book_id>', methods=['GET'])
def api_get_book(book_id):
    """API to get a single book."""
    book = get_book_by_id(book_id)
    if book:
        return jsonify(book)
    return jsonify({'error': 'Book not found'}), 404


@app.route('/api/books/<int:book_id>', methods=['PUT'])
def api_update_book(book_id):
    """API to update a book."""
    data = request.json
    book = update_book(
        book_id, data['title'], data['author'],
        data['genre'], data['isbn'], data['total_copies']
    )
    if book:
        return jsonify({'success': True, 'book': book})
    return jsonify({'success': False, 'message': 'Book not found'}), 404


@app.route('/api/books/<int:book_id>', methods=['DELETE'])
def api_delete_book(book_id):
    """API to delete a book."""
    if delete_book(book_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Book not found'}), 404


# ============================================================
# API ROUTES - Reader operations
# ============================================================
@app.route('/api/readers', methods=['GET'])
def api_get_readers():
    """API to get all readers or search readers."""
    query = request.args.get('q', '')
    if query:
        readers = search_readers(query)
    else:
        readers = get_all_readers()
    return jsonify(readers)


@app.route('/api/readers', methods=['POST'])
def api_add_reader():
    """API to register a new reader."""
    data = request.json
    reader = add_reader(
        data['name'], data['email'],
        data['phone'], data['address']
    )
    return jsonify({'success': True, 'reader': reader})


@app.route('/api/readers/<int:reader_id>', methods=['GET'])
def api_get_reader(reader_id):
    """API to get a single reader."""
    reader = get_reader_by_id(reader_id)
    if reader:
        return jsonify(reader)
    return jsonify({'error': 'Reader not found'}), 404


@app.route('/api/readers/<int:reader_id>', methods=['PUT'])
def api_update_reader(reader_id):
    """API to update a reader."""
    data = request.json
    reader = update_reader(
        reader_id, data['name'], data['email'],
        data['phone'], data['address']
    )
    if reader:
        return jsonify({'success': True, 'reader': reader})
    return jsonify({'success': False, 'message': 'Reader not found'}), 404


@app.route('/api/readers/<int:reader_id>', methods=['DELETE'])
def api_delete_reader(reader_id):
    """API to delete a reader."""
    if delete_reader(reader_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Reader not found'}), 404


# ============================================================
# API ROUTES - Bag operations
# ============================================================
@app.route('/api/bag', methods=['GET'])
def api_get_bag():
    """API to get bag contents."""
    books = get_bag_books()
    return jsonify({'books': books, 'count': len(books)})


@app.route('/api/bag/add/<int:book_id>', methods=['POST'])
def api_add_to_bag(book_id):
    """API to add a book to the bag."""
    result = add_to_bag(book_id)
    result['count'] = len(get_bag())
    return jsonify(result)


@app.route('/api/bag/remove/<int:book_id>', methods=['POST'])
def api_remove_from_bag(book_id):
    """API to remove a book from the bag."""
    result = remove_from_bag(book_id)
    result['count'] = len(get_bag())
    return jsonify(result)


@app.route('/api/bag/checkout', methods=['POST'])
def api_checkout():
    """API to checkout - issue all books in bag to a reader."""
    data = request.json
    reader_id = data.get('reader_id')
    if not reader_id:
        return jsonify({'success': False, 'message': 'Please select a reader'})
    
    bag = get_bag()
    if len(bag) == 0:
        return jsonify({'success': False, 'message': 'Bag is empty'})
    
    result = issue_books(reader_id, bag)
    if result['success']:
        clear_bag()
    return jsonify(result)


# ============================================================
# API ROUTES - Transaction/Return operations
# ============================================================
@app.route('/api/transactions', methods=['GET'])
def api_get_transactions():
    """API to get all transactions."""
    status_filter = request.args.get('status', '')
    reader_id = request.args.get('reader_id', '')
    transactions = get_all_transactions()
    
    if status_filter:
        transactions = [t for t in transactions if t['status'] == status_filter]
    if reader_id:
        transactions = [t for t in transactions if t['reader_id'] == int(reader_id)]
    
    return jsonify(transactions)


@app.route('/api/transactions/return/<int:txn_id>', methods=['POST'])
def api_return_book(txn_id):
    """API to return a book."""
    result = return_book(txn_id)
    return jsonify(result)


# ============================================================
# API ROUTES - Dashboard
# ============================================================
@app.route('/api/dashboard', methods=['GET'])
def api_dashboard():
    """API to get dashboard statistics."""
    stats = get_dashboard_stats()
    return jsonify(stats)


# ============================================================
# SEED DATA - Add sample data for testing
# ============================================================
@app.route('/api/seed', methods=['POST'])
def seed_data():
    """Add sample books and readers for testing."""
    # Sample books list - each item is a dictionary
    sample_books = [
        {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'genre': 'Fiction', 'isbn': '978-0061120084', 'copies': 5},
        {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'genre': 'Fiction', 'isbn': '978-0743273565', 'copies': 3},
        {'title': 'Data Structures Using C', 'author': 'Reema Thareja', 'genre': 'Computer Science', 'isbn': '978-0198099307', 'copies': 8},
        {'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'genre': 'Computer Science', 'isbn': '978-0262033848', 'copies': 4},
        {'title': 'Physics for Engineers', 'author': 'R.K. Gaur', 'genre': 'Science', 'isbn': '978-8131517468', 'copies': 6},
        {'title': 'Engineering Mathematics', 'author': 'B.S. Grewal', 'genre': 'Mathematics', 'isbn': '978-8174091154', 'copies': 10},
        {'title': 'The Alchemist', 'author': 'Paulo Coelho', 'genre': 'Fiction', 'isbn': '978-0062315007', 'copies': 4},
        {'title': 'Python Programming', 'author': 'Mark Lutz', 'genre': 'Computer Science', 'isbn': '978-1449355739', 'copies': 7},
        {'title': 'Discrete Mathematics', 'author': 'Kenneth H. Rosen', 'genre': 'Mathematics', 'isbn': '978-0073383095', 'copies': 5},
        {'title': 'Database System Concepts', 'author': 'Abraham Silberschatz', 'genre': 'Computer Science', 'isbn': '978-0078022159', 'copies': 6},
    ]
    
    # Sample readers list
    sample_readers = [
        {'name': 'Aarav Sharma', 'email': 'aarav@email.com', 'phone': '9876543210', 'address': 'Delhi'},
        {'name': 'Priya Patel', 'email': 'priya@email.com', 'phone': '9876543211', 'address': 'Mumbai'},
        {'name': 'Rohan Gupta', 'email': 'rohan@email.com', 'phone': '9876543212', 'address': 'Bangalore'},
        {'name': 'Sneha Reddy', 'email': 'sneha@email.com', 'phone': '9876543213', 'address': 'Hyderabad'},
        {'name': 'Vikram Singh', 'email': 'vikram@email.com', 'phone': '9876543214', 'address': 'Pune'},
    ]
    
    existing_books = get_all_books()
    existing_readers = get_all_readers()
    
    if len(existing_books) > 0 or len(existing_readers) > 0:
        return jsonify({'success': False, 'message': 'Data already exists. Clear data first.'})
    
    # Add sample books using the add_book function
    for book in sample_books:
        add_book(book['title'], book['author'], book['genre'], book['isbn'], book['copies'])
    
    # Add sample readers using the add_reader function
    for reader in sample_readers:
        add_reader(reader['name'], reader['email'], reader['phone'], reader['address'])
    
    return jsonify({'success': True, 'message': f'Added {len(sample_books)} books and {len(sample_readers)} readers'})


@app.route('/api/seed', methods=['DELETE'])
def clear_data():
    """Clear all data."""
    save_json_file(BOOKS_FILE, [])
    save_json_file(READERS_FILE, [])
    save_json_file(TRANSACTIONS_FILE, [])
    clear_bag()
    return jsonify({'success': True, 'message': 'All data cleared'})


# ============================================================
# RUN THE APPLICATION
# ============================================================
if __name__ == '__main__':
    ensure_data_dir()
    print('\n=== Library Management System ===')
    print('    Open http://127.0.0.1:5000 in your browser\n')
    app.run(debug=True, port=5000)
