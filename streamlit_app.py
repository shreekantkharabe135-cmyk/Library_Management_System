"""
Library Management System - Streamlit Version
A college mini-project demonstrating Python concepts:
- Lists for storing records
- Dictionaries for book/reader data
- Functions for all operations
- File handling using JSON files
"""

import streamlit as st
import json
import os
from datetime import datetime

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Library Management System",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

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
        with open(filepath, 'w') as f:
            json.dump([], f)
        return []
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def save_json_file(filepath, data):
    """Save a list of dictionaries to a JSON file."""
    ensure_data_dir()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def generate_id(records_list):
    """Generate the next ID based on existing records in the list."""
    if len(records_list) == 0:
        return 1
    ids = [record['id'] for record in records_list]
    return max(ids) + 1


# ============================================================
# BOOK FUNCTIONS
# ============================================================
def get_all_books():
    return load_json_file(BOOKS_FILE)


def add_book(title, author, genre, isbn, total_copies):
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
    books_list.append(new_book)
    save_json_file(BOOKS_FILE, books_list)
    return new_book


def search_books(query):
    books_list = get_all_books()
    query = query.lower()
    results = [
        book for book in books_list
        if query in book['title'].lower()
        or query in book['author'].lower()
        or query in book['genre'].lower()
        or query in book['isbn'].lower()
    ]
    return results


def get_book_by_id(book_id):
    books_list = get_all_books()
    for book in books_list:
        if book['id'] == book_id:
            return book
    return None


def update_book(book_id, title, author, genre, isbn, total_copies):
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
    books_list = get_all_books()
    updated_list = [book for book in books_list if book['id'] != book_id]
    if len(updated_list) < len(books_list):
        save_json_file(BOOKS_FILE, updated_list)
        return True
    return False


# ============================================================
# READER FUNCTIONS
# ============================================================
def get_all_readers():
    return load_json_file(READERS_FILE)


def add_reader(name, email, phone, address):
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
    readers_list = get_all_readers()
    for reader in readers_list:
        if reader['id'] == reader_id:
            return reader
    return None


def update_reader(reader_id, name, email, phone, address):
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
    readers_list = get_all_readers()
    updated_list = [reader for reader in readers_list if reader['id'] != reader_id]
    if len(updated_list) < len(readers_list):
        save_json_file(READERS_FILE, updated_list)
        return True
    return False


# ============================================================
# TRANSACTION FUNCTIONS
# ============================================================
def get_all_transactions():
    return load_json_file(TRANSACTIONS_FILE)


def issue_books(reader_id, book_ids_list):
    transactions_list = get_all_transactions()
    books_list = get_all_books()
    reader = get_reader_by_id(reader_id)

    if reader is None:
        return {'success': False, 'message': 'Reader not found'}

    issued = []
    errors = []

    for book_id in book_ids_list:
        book = get_book_by_id(book_id)
        if book is None:
            errors.append(f'Book ID {book_id} not found')
            continue
        if book['available_copies'] <= 0:
            errors.append(f'"{book["title"]}" is not available')
            continue

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

        for i in range(len(books_list)):
            if books_list[i]['id'] == book_id:
                books_list[i]['available_copies'] -= 1
                break

        issued.append(book['title'])

    save_json_file(TRANSACTIONS_FILE, transactions_list)
    save_json_file(BOOKS_FILE, books_list)

    return {'success': len(issued) > 0, 'issued': issued, 'errors': errors}


def return_book(transaction_id):
    transactions_list = get_all_transactions()
    books_list = get_all_books()

    for i in range(len(transactions_list)):
        if transactions_list[i]['id'] == transaction_id:
            if transactions_list[i]['status'] == 'returned':
                return {'success': False, 'message': 'Book already returned'}

            transactions_list[i]['status'] = 'returned'
            transactions_list[i]['return_date'] = datetime.now().strftime('%Y-%m-%d')

            book_id = transactions_list[i]['book_id']
            for j in range(len(books_list)):
                if books_list[j]['id'] == book_id:
                    books_list[j]['available_copies'] += 1
                    break

            save_json_file(TRANSACTIONS_FILE, transactions_list)
            save_json_file(BOOKS_FILE, books_list)
            return {'success': True, 'message': 'Book returned successfully'}

    return {'success': False, 'message': 'Transaction not found'}


# ============================================================
# DASHBOARD FUNCTIONS
# ============================================================
def get_dashboard_stats():
    books_list = get_all_books()
    readers_list = get_all_readers()
    transactions_list = get_all_transactions()

    total_books = sum(book['total_copies'] for book in books_list)
    available_books = sum(book['available_copies'] for book in books_list)
    issued_books = total_books - available_books
    total_readers = len(readers_list)

    recent_transactions = sorted(
        transactions_list, key=lambda x: x['id'], reverse=True
    )[:10]

    genre_count = {}
    for book in books_list:
        genre = book['genre']
        if genre in genre_count:
            genre_count[genre] += book['total_copies']
        else:
            genre_count[genre] = book['total_copies']

    return {
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'total_readers': total_readers,
        'total_titles': len(books_list),
        'recent_transactions': recent_transactions,
        'genre_distribution': genre_count
    }


# ============================================================
# BAG FUNCTIONS (Session-based)
# ============================================================
def get_bag():
    if 'bag' not in st.session_state:
        st.session_state.bag = []
    return st.session_state.bag


def add_to_bag(book_id):
    bag = get_bag()
    if book_id in bag:
        return {'success': False, 'message': 'Book already in bag'}
    book = get_book_by_id(book_id)
    if book is None:
        return {'success': False, 'message': 'Book not found'}
    if book['available_copies'] <= 0:
        return {'success': False, 'message': 'Book not available'}
    bag.append(book_id)
    st.session_state.bag = bag
    return {'success': True, 'message': f'"{book["title"]}" added to bag'}


def remove_from_bag(book_id):
    bag = get_bag()
    if book_id in bag:
        bag.remove(book_id)
        st.session_state.bag = bag
        return True
    return False


def clear_bag():
    st.session_state.bag = []


def get_bag_books():
    bag = get_bag()
    return [get_book_by_id(bid) for bid in bag if get_book_by_id(bid) is not None]


# ============================================================
# SEED DATA
# ============================================================
def seed_data():
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

    sample_readers = [
        {'name': 'Aarav Sharma', 'email': 'aarav@email.com', 'phone': '9876543210', 'address': 'Delhi'},
        {'name': 'Priya Patel', 'email': 'priya@email.com', 'phone': '9876543211', 'address': 'Mumbai'},
        {'name': 'Rohan Gupta', 'email': 'rohan@email.com', 'phone': '9876543212', 'address': 'Bangalore'},
        {'name': 'Sneha Reddy', 'email': 'sneha@email.com', 'phone': '9876543213', 'address': 'Hyderabad'},
        {'name': 'Vikram Singh', 'email': 'vikram@email.com', 'phone': '9876543214', 'address': 'Pune'},
    ]

    if len(get_all_books()) > 0 or len(get_all_readers()) > 0:
        return False, 'Data already exists. Clear data first.'

    for book in sample_books:
        add_book(book['title'], book['author'], book['genre'], book['isbn'], book['copies'])
    for reader in sample_readers:
        add_reader(reader['name'], reader['email'], reader['phone'], reader['address'])

    return True, f'Added {len(sample_books)} books and {len(sample_readers)} readers'


def clear_all_data():
    save_json_file(BOOKS_FILE, [])
    save_json_file(READERS_FILE, [])
    save_json_file(TRANSACTIONS_FILE, [])
    clear_bag()


# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
    .main-header { font-size: 2.5rem; font-weight: 800; text-align: center; 
        background: linear-gradient(135deg, #4f46e5, #ec4899);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem; }
    .sub-header { text-align: center; color: #64748b; margin-bottom: 2rem; }
    .stat-box { background: white; border-radius: 12px; padding: 24px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.06); text-align: center; border: 1px solid #f0f0f0; }
    .stat-number { font-size: 2.2rem; font-weight: 800; color: #1e293b; }
    .stat-label { font-size: 0.85rem; color: #64748b; font-weight: 600; letter-spacing: 0.5px; }
    .book-row { background: white; border-radius: 10px; padding: 16px 20px;
        margin-bottom: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        border-left: 4px solid #4f46e5; }
    .bag-item { background: white; border-radius: 10px; padding: 16px 20px;
        margin-bottom: 8px; box-shadow: 0 1px 6px rgba(0,0,0,0.04);
        border-left: 4px solid #ec4899; }
    .stButton>button { border-radius: 8px; }
    div[data-testid="stSidebar"] { background: linear-gradient(180deg, #f8fafc, #eef2ff); }
</style>
""", unsafe_allow_html=True)


# ============================================================
# SIDEBAR NAVIGATION
# ============================================================
with st.sidebar:
    st.markdown("## 📚 Library OS")
    st.markdown("---")
    page = st.radio(
        "Navigate",
        ["🏠 Home", "📖 Books", "👥 Readers", "🛒 My Bag", "🔄 Returns", "📊 Dashboard"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    bag_count = len(get_bag())
    if bag_count > 0:
        st.info(f"🛒 **{bag_count}** book(s) in bag")


# ============================================================
# HOME PAGE
# ============================================================
if page == "🏠 Home":
    st.markdown('<h1 class="main-header">Library Management System</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">A modern, efficient system to manage books, readers, and transactions.</p>', unsafe_allow_html=True)

    stats = get_dashboard_stats()
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_books"]}</div><div class="stat-label">TOTAL BOOKS</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["available_books"]}</div><div class="stat-label">AVAILABLE</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["issued_books"]}</div><div class="stat-label">ISSUED</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown(f'<div class="stat-box"><div class="stat-number">{stats["total_readers"]}</div><div class="stat-label">READERS</div></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Quick Start")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📥 Load Sample Data", use_container_width=True):
            success, msg = seed_data()
            if success:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)
    with col2:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            clear_all_data()
            st.success("All data cleared!")
            st.rerun()


# ============================================================
# BOOKS PAGE
# ============================================================
elif page == "📖 Books":
    st.header("📖 Books Management")

    # Search
    col1, col2 = st.columns([4, 1])
    with col1:
        search_query = st.text_input("Search", placeholder="Search by title, author, genre or ISBN...", label_visibility="collapsed")
    with col2:
        add_book_btn = st.button("➕ Add Book", use_container_width=True)

    if add_book_btn:
        st.session_state.show_add_book = True

    # Add Book Form
    if st.session_state.get('show_add_book', False):
        with st.expander("📝 Add New Book", expanded=True):
            with st.form("add_book_form"):
                title = st.text_input("Book Title")
                col1, col2 = st.columns(2)
                with col1:
                    author = st.text_input("Author")
                    isbn = st.text_input("ISBN")
                with col2:
                    genre = st.text_input("Genre")
                    total_copies = st.number_input("Total Copies", min_value=1, value=1)

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Save Book", use_container_width=True)
                with col2:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)

                if submitted and title and author and genre and isbn:
                    add_book(title, author, genre, isbn, total_copies)
                    st.session_state.show_add_book = False
                    st.success(f'"{title}" added successfully!')
                    st.rerun()
                if cancel:
                    st.session_state.show_add_book = False
                    st.rerun()

    # Book list
    books = search_books(search_query) if search_query else get_all_books()
    st.caption(f"{len(books)} book(s) available.")

    for book in books:
        col1, col2, col3, col4 = st.columns([1, 5, 2, 2])
        with col1:
            st.markdown("📕")
        with col2:
            st.markdown(f"**{book['title']}**")
            st.caption(f"Written by {book['author']} · {book['genre']} · ISBN: {book['isbn']}")
            avail = book['available_copies']
            total = book['total_copies']
            color = "green" if avail > 0 else "red"
            st.markdown(f":{color}[{avail}/{total} available]")
        with col3:
            if st.button("🛒 Add to bag", key=f"bag_{book['id']}", disabled=book['available_copies'] <= 0):
                result = add_to_bag(book['id'])
                if result['success']:
                    st.success(result['message'])
                else:
                    st.warning(result['message'])
                st.rerun()
        with col4:
            if st.button("🗑️ Delete", key=f"del_{book['id']}"):
                delete_book(book['id'])
                st.success("Book deleted")
                st.rerun()
        st.divider()


# ============================================================
# READERS PAGE
# ============================================================
elif page == "👥 Readers":
    st.header("👥 Readers Management")

    col1, col2 = st.columns([4, 1])
    with col1:
        reader_search = st.text_input("Search", placeholder="Search by name, email or phone...", label_visibility="collapsed", key="reader_search")
    with col2:
        if st.button("➕ Register Reader", use_container_width=True):
            st.session_state.show_add_reader = True

    # Add Reader Form
    if st.session_state.get('show_add_reader', False):
        with st.expander("📝 Register New Reader", expanded=True):
            with st.form("add_reader_form"):
                name = st.text_input("Full Name")
                col1, col2 = st.columns(2)
                with col1:
                    email = st.text_input("Email")
                with col2:
                    phone = st.text_input("Phone")
                address = st.text_input("Address")

                col1, col2 = st.columns(2)
                with col1:
                    submitted = st.form_submit_button("💾 Save Reader", use_container_width=True)
                with col2:
                    cancel = st.form_submit_button("Cancel", use_container_width=True)

                if submitted and name and email and phone and address:
                    add_reader(name, email, phone, address)
                    st.session_state.show_add_reader = False
                    st.success(f'"{name}" registered!')
                    st.rerun()
                if cancel:
                    st.session_state.show_add_reader = False
                    st.rerun()

    # Readers list
    readers = search_readers(reader_search) if reader_search else get_all_readers()
    st.caption(f"{len(readers)} reader(s) registered.")

    if len(readers) > 0:
        for reader in readers:
            col1, col2, col3 = st.columns([1, 6, 1])
            with col1:
                st.markdown("👤")
            with col2:
                st.markdown(f"**{reader['name']}** (#{reader['id']})")
                st.caption(f"📧 {reader['email']} · 📱 {reader['phone']} · 📍 {reader['address']} · Registered: {reader['date_registered']}")
            with col3:
                if st.button("🗑️", key=f"del_r_{reader['id']}"):
                    delete_reader(reader['id'])
                    st.success("Reader deleted")
                    st.rerun()
            st.divider()


# ============================================================
# MY BAG PAGE
# ============================================================
elif page == "🛒 My Bag":
    st.header("🛒 My Bag")

    bag_books = get_bag_books()

    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader(f"Books in your bag — {len(bag_books)}")
        if len(bag_books) == 0:
            st.info("Your bag is empty. Browse the **Books** page to add some!")
        else:
            for book in bag_books:
                col1, col2, col3 = st.columns([1, 5, 1])
                with col1:
                    st.markdown("📕")
                with col2:
                    st.markdown(f"**{book['title']}**")
                    st.caption(f"Written by {book['author']} · {book['genre']}")
                with col3:
                    if st.button("❌", key=f"rem_{book['id']}"):
                        remove_from_bag(book['id'])
                        st.rerun()
                st.divider()

    with col_right:
        st.subheader("Ready for Checkout?")
        readers = get_all_readers()

        if len(readers) == 0:
            st.warning("No readers registered. Register a reader first!")
        else:
            reader_options = {f"{r['name']} (#{r['id']})": r for r in readers}
            selected = st.selectbox("Select Reader", ["-- Select --"] + list(reader_options.keys()))

            if selected != "-- Select --":
                r = reader_options[selected]
                st.markdown(f"**Name:** {r['name']}")
                st.markdown(f"**Contact:** {r['phone']}")

            st.markdown(f"**Issue Date:** {datetime.now().strftime('%B %d, %Y, %I:%M %p')}")
            st.markdown(f"**Return Due Date:** {(datetime.now().replace(day=datetime.now().day)).strftime('%B %d, %Y')}")

            if st.button("✅ Issue Books", use_container_width=True, type="primary", disabled=len(bag_books) == 0):
                if selected == "-- Select --":
                    st.error("Please select a reader!")
                else:
                    r = reader_options[selected]
                    result = issue_books(r['id'], [b['id'] for b in bag_books])
                    if result['success']:
                        clear_bag()
                        st.success("Books issued: " + ", ".join(result['issued']))
                        st.rerun()
                    else:
                        st.error(result.get('message', 'Checkout failed'))

        st.markdown("---")
        st.caption("**Library Rules:**")
        st.caption("• Readers should not mark, underline, write, or tear pages.")
        st.caption("• No Library material can be taken out without permission.")
        st.caption("• Books are issued for a maximum of two weeks.")


# ============================================================
# RETURNS PAGE
# ============================================================
elif page == "🔄 Returns":
    st.header("🔄 Book Returns")

    transactions = get_all_transactions()

    col1, col2 = st.columns(2)
    with col1:
        status_filter = st.selectbox("Filter by Status", ["All", "issued", "returned"])
    with col2:
        readers = get_all_readers()
        reader_filter_options = ["All Readers"] + [f"{r['name']} (#{r['id']})" for r in readers]
        reader_filter = st.selectbox("Filter by Reader", reader_filter_options)

    if status_filter != "All":
        transactions = [t for t in transactions if t['status'] == status_filter]
    if reader_filter != "All Readers":
        rid = int(reader_filter.split('#')[1].rstrip(')'))
        transactions = [t for t in transactions if t['reader_id'] == rid]

    st.caption(f"{len(transactions)} transaction(s) found.")

    if len(transactions) == 0:
        st.info("No transactions found.")
    else:
        for txn in sorted(transactions, key=lambda x: x['id'], reverse=True):
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            with col1:
                st.markdown(f"**{txn['book_title']}**")
                st.caption(f"Reader: {txn['reader_name']}")
            with col2:
                st.caption(f"Issued: {txn['issue_date']}")
                if txn['return_date']:
                    st.caption(f"Returned: {txn['return_date']}")
            with col3:
                if txn['status'] == 'issued':
                    st.warning("Issued")
                else:
                    st.success("Returned")
            with col4:
                if txn['status'] == 'issued':
                    if st.button("Return", key=f"ret_{txn['id']}"):
                        result = return_book(txn['id'])
                        if result['success']:
                            st.success(result['message'])
                            st.rerun()
                        else:
                            st.error(result['message'])
            st.divider()


# ============================================================
# DASHBOARD PAGE
# ============================================================
elif page == "📊 Dashboard":
    st.header("📊 Dashboard")

    stats = get_dashboard_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Books", stats['total_books'])
    with col2:
        st.metric("Available", stats['available_books'])
    with col3:
        st.metric("Issued", stats['issued_books'])
    with col4:
        st.metric("Readers", stats['total_readers'])

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.subheader("📚 Genre Distribution")
        genre_data = stats['genre_distribution']
        if genre_data:
            import pandas as pd
            df = pd.DataFrame(list(genre_data.items()), columns=['Genre', 'Count'])
            st.bar_chart(df.set_index('Genre'))
        else:
            st.info("No books available for genre distribution.")

    with col_right:
        st.subheader("🕐 Recent Transactions")
        recent = stats['recent_transactions']
        if len(recent) == 0:
            st.info("No recent transactions.")
        else:
            for txn in recent:
                icon = "🔶" if txn['status'] == 'issued' else "✅"
                st.markdown(f"{icon} **{txn['book_title']}** → {txn['reader_name']} ({txn['issue_date']})")
