"""
Library Management System - Streamlit Version
Fully integrated with:
- Books & Readers Management
- My Bag with Return Due Date & Time Picker
- Configurable Penalty Charges (default ₹10/day)
- Overdue Days & Fine Calculation
- Book Returns with Real-time & Final Penalty Assessment
- Penalty Payment Tracking (Paid / Unpaid)
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta

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
# PENALTY RATE CONFIGURATION (Session & Global)
# ============================================================
if 'penalty_rate' not in st.session_state:
    st.session_state.penalty_rate = 10

# ============================================================
# FILE PATHS - JSON files for persistent storage
# ============================================================
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
BOOKS_FILE = os.path.join(DATA_DIR, 'books.json')
READERS_FILE = os.path.join(DATA_DIR, 'readers.json')
TRANSACTIONS_FILE = os.path.join(DATA_DIR, 'transactions.json')


def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)


def load_json_file(filepath):
    ensure_data_dir()
    if not os.path.exists(filepath):
        with open(filepath, 'w') as f:
            json.dump([], f)
        return []
    with open(filepath, 'r') as f:
        data = json.load(f)
    return data


def save_json_file(filepath, data):
    ensure_data_dir()
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)


def generate_id(records_list):
    if len(records_list) == 0:
        return 1
    ids = [record['id'] for record in records_list]
    return max(ids) + 1


def parse_datetime(dt_str):
    if not dt_str:
        return None
    for fmt in ('%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M', '%Y-%m-%d %H:%M:%S', '%Y-%m-%d'):
        try:
            return datetime.strptime(dt_str, fmt)
        except ValueError:
            pass
    return None


def calculate_penalty(due_date_str, return_date_str=None, rate=None):
    if rate is None:
        rate = st.session_state.penalty_rate
    due_date = parse_datetime(due_date_str)
    if not due_date:
        return {'overdue_days': 0, 'penalty_amount': 0, 'is_overdue': False}

    if return_date_str:
        return_date = parse_datetime(return_date_str) or datetime.now()
    else:
        return_date = datetime.now()

    diff = return_date - due_date
    if diff.total_seconds() > 0:
        day_diff = (return_date.date() - due_date.date()).days
        overdue_days = day_diff if day_diff > 0 else 1
    else:
        overdue_days = 0

    return {
        'overdue_days': overdue_days,
        'penalty_amount': overdue_days * rate,
        'is_overdue': overdue_days > 0
    }


# ============================================================
# BOOKS OPERATIONS
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
    return [
        b for b in books_list
        if query in b['title'].lower()
        or query in b['author'].lower()
        or query in b['genre'].lower()
        or query in b['isbn'].lower()
    ]


def get_book_by_id(book_id):
    for book in get_all_books():
        if book['id'] == book_id:
            return book
    return None


def delete_book(book_id):
    books_list = get_all_books()
    updated = [b for b in books_list if b['id'] != book_id]
    if len(updated) < len(books_list):
        save_json_file(BOOKS_FILE, updated)
        return True
    return False


# ============================================================
# READERS OPERATIONS
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
    return [
        r for r in readers_list
        if query in r['name'].lower()
        or query in r['email'].lower()
        or query in r['phone'].lower()
    ]


def get_reader_by_id(reader_id):
    for reader in get_all_readers():
        if reader['id'] == reader_id:
            return reader
    return None


def delete_reader(reader_id):
    readers_list = get_all_readers()
    updated = [r for r in readers_list if r['id'] != reader_id]
    if len(updated) < len(readers_list):
        save_json_file(READERS_FILE, updated)
        return True
    return False


# ============================================================
# TRANSACTIONS & RETURNS
# ============================================================
def get_all_transactions():
    return load_json_file(TRANSACTIONS_FILE)


def issue_books(reader_id, book_ids_list, due_date_str):
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
            if txn['reader_id'] == reader_id and txn['book_id'] == book_id and txn['status'] == 'issued':
                already_issued = True
                break

        if already_issued:
            errors.append(f'"{book["title"]}" already issued to this reader')
            continue

        new_txn = {
            'id': generate_id(transactions_list),
            'reader_id': reader_id,
            'reader_name': reader['name'],
            'book_id': book_id,
            'book_title': book['title'],
            'issue_date': datetime.now().strftime('%Y-%m-%d'),
            'due_date': due_date_str,
            'return_date': None,
            'status': 'issued',
            'overdue_days': 0,
            'penalty_amount': 0,
            'penalty_paid': False
        }
        transactions_list.append(new_txn)

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

            due_date = transactions_list[i].get('due_date')
            if due_date:
                pen = calculate_penalty(due_date, transactions_list[i]['return_date'])
                transactions_list[i]['overdue_days'] = pen['overdue_days']
                transactions_list[i]['penalty_amount'] = pen['penalty_amount']
            else:
                transactions_list[i]['overdue_days'] = 0
                transactions_list[i]['penalty_amount'] = 0

            transactions_list[i]['penalty_paid'] = False

            book_id = transactions_list[i]['book_id']
            for j in range(len(books_list)):
                if books_list[j]['id'] == book_id:
                    books_list[j]['available_copies'] += 1
                    break

            save_json_file(TRANSACTIONS_FILE, transactions_list)
            save_json_file(BOOKS_FILE, books_list)

            msg = 'Book returned successfully.'
            if transactions_list[i]['penalty_amount'] > 0:
                msg += f' Overdue by {transactions_list[i]["overdue_days"]} day(s). Fine: ₹{transactions_list[i]["penalty_amount"]}'
            return {'success': True, 'message': msg}

    return {'success': False, 'message': 'Transaction not found'}


def pay_penalty(transaction_id):
    transactions_list = get_all_transactions()
    for i in range(len(transactions_list)):
        if transactions_list[i]['id'] == transaction_id:
            transactions_list[i]['penalty_paid'] = True
            save_json_file(TRANSACTIONS_FILE, transactions_list)
            return True
    return False


# ============================================================
# BAG (CART)
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
    return [get_book_by_id(bid) for bid in get_bag() if get_book_by_id(bid) is not None]


# ============================================================
# DASHBOARD STATS
# ============================================================
def get_dashboard_stats():
    books_list = get_all_books()
    readers_list = get_all_readers()
    transactions_list = get_all_transactions()

    total_books = sum(b['total_copies'] for b in books_list)
    available_books = sum(b['available_copies'] for b in books_list)
    issued_books = total_books - available_books

    genre_count = {}
    for b in books_list:
        g = b['genre']
        genre_count[g] = genre_count.get(g, 0) + b['total_copies']

    return {
        'total_books': total_books,
        'available_books': available_books,
        'issued_books': issued_books,
        'total_readers': len(readers_list),
        'total_titles': len(books_list),
        'genre_distribution': genre_count
    }


def seed_data():
    sample_books = [
        {'title': 'To Kill a Mockingbird', 'author': 'Harper Lee', 'genre': 'Fiction', 'isbn': '978-0061120084', 'copies': 5},
        {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'genre': 'Fiction', 'isbn': '978-0743273565', 'copies': 3},
        {'title': 'Data Structures Using C', 'author': 'Reema Thareja', 'genre': 'Computer Science', 'isbn': '978-0198099307', 'copies': 8},
        {'title': 'Introduction to Algorithms', 'author': 'Thomas H. Cormen', 'genre': 'Computer Science', 'isbn': '978-0262033848', 'copies': 4},
        {'title': 'Physics for Engineers', 'author': 'R.K. Gaur', 'genre': 'Science', 'isbn': '978-8131517468', 'copies': 6},
    ]
    sample_readers = [
        {'name': 'Aarav Sharma', 'email': 'aarav@email.com', 'phone': '9876543210', 'address': 'Delhi'},
        {'name': 'Priya Patel', 'email': 'priya@email.com', 'phone': '9876543211', 'address': 'Mumbai'},
        {'name': 'Rohan Gupta', 'email': 'rohan@email.com', 'phone': '9876543212', 'address': 'Bangalore'},
    ]
    if len(get_all_books()) > 0 or len(get_all_readers()) > 0:
        return False, 'Data already exists. Clear data first.'
    for b in sample_books:
        add_book(b['title'], b['author'], b['genre'], b['isbn'], b['copies'])
    for r in sample_readers:
        add_reader(r['name'], r['email'], r['phone'], r['address'])
    return True, f'Loaded {len(sample_books)} books and {len(sample_readers)} readers.'


# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.markdown("## 📚 Library OS")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🏠 Home", "📖 Books", "👥 Readers", "🛒 My Bag", "🔄 Returns & Penalties", "📊 Dashboard"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.subheader("⚙️ Settings")
    st.session_state.penalty_rate = st.number_input("Penalty Rate (₹/day)", min_value=0, max_value=500, value=st.session_state.penalty_rate)
    st.caption(f"Active Rate: **₹{st.session_state.penalty_rate} / day**")
    st.markdown("---")
    bag_count = len(get_bag())
    if bag_count > 0:
        st.info(f"🛒 **{bag_count}** book(s) in bag")


# ============================================================
# 1. HOME PAGE
# ============================================================
if page == "🏠 Home":
    st.title("📚 Library Management System")
    st.markdown("A modern, efficient platform for managing books, readers, checkout due dates, and penalty fines.")

    stats = get_dashboard_stats()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Books", stats['total_books'])
    c2.metric("Available", stats['available_books'])
    c3.metric("Currently Borrowed", stats['issued_books'])
    c4.metric("Registered Readers", stats['total_readers'])

    st.markdown("---")
    colA, colB = st.columns(2)
    with colA:
        if st.button("📥 Load Sample Data", use_container_width=True):
            ok, msg = seed_data()
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.warning(msg)
    with colB:
        if st.button("🗑️ Clear All Data", use_container_width=True):
            save_json_file(BOOKS_FILE, [])
            save_json_file(READERS_FILE, [])
            save_json_file(TRANSACTIONS_FILE, [])
            clear_bag()
            st.success("All data cleared successfully!")
            st.rerun()


# ============================================================
# 2. BOOKS PAGE
# ============================================================
elif page == "📖 Books":
    st.header("📖 Books Catalog")

    c1, c2 = st.columns([4, 1])
    with c1:
        search_query = st.text_input("Search catalog", placeholder="Search by title, author, genre or ISBN...", label_visibility="collapsed")
    with c2:
        if st.button("➕ Add Book", use_container_width=True):
            st.session_state.show_add_book = True

    if st.session_state.get('show_add_book', False):
        with st.expander("Add New Book", expanded=True):
            with st.form("book_form"):
                t = st.text_input("Title")
                col_a, col_b = st.columns(2)
                with col_a:
                    a = st.text_input("Author")
                    i = st.text_input("ISBN")
                with col_b:
                    g = st.text_input("Genre")
                    copies = st.number_input("Total Copies", min_value=1, value=5)
                sub = st.form_submit_button("Save Book")
                if sub and t and a and g and i:
                    add_book(t, a, g, i, copies)
                    st.session_state.show_add_book = False
                    st.success(f'Book "{t}" added!')
                    st.rerun()

    books = search_books(search_query) if search_query else get_all_books()
    st.caption(f"{len(books)} books available.")

    for b in books:
        c1, c2, c3, c4 = st.columns([1, 6, 2, 1])
        with c1:
            st.markdown("📕")
        with c2:
            st.markdown(f"**{b['title']}**")
            st.caption(f"By {b['author']} · Genre: {b['genre']} · ISBN: {b['isbn']}")
            color = "green" if b['available_copies'] > 0 else "red"
            st.markdown(f":{color}[{b['available_copies']} / {b['total_copies']} copies available]")
        with c3:
            if st.button("🛒 Add to Bag", key=f"add_{b['id']}", disabled=b['available_copies'] <= 0):
                res = add_to_bag(b['id'])
                if res['success']:
                    st.success(res['message'])
                    st.rerun()
                else:
                    st.warning(res['message'])
        with c4:
            if st.button("🗑️", key=f"del_{b['id']}"):
                delete_book(b['id'])
                st.success("Deleted")
                st.rerun()
        st.divider()


# ============================================================
# 3. READERS PAGE
# ============================================================
elif page == "👥 Readers":
    st.header("👥 Readers Directory")

    c1, c2 = st.columns([4, 1])
    with c1:
        rq = st.text_input("Search readers", placeholder="Search by name, email or phone...", label_visibility="collapsed")
    with c2:
        if st.button("➕ Register Reader", use_container_width=True):
            st.session_state.show_add_reader = True

    if st.session_state.get('show_add_reader', False):
        with st.expander("Register Reader", expanded=True):
            with st.form("reader_form"):
                name = st.text_input("Full Name")
                ca, cb = st.columns(2)
                with ca:
                    email = st.text_input("Email")
                with cb:
                    phone = st.text_input("Phone")
                address = st.text_input("Address")
                sub = st.form_submit_button("Register")
                if sub and name and email and phone:
                    add_reader(name, email, phone, address)
                    st.session_state.show_add_reader = False
                    st.success(f'Reader "{name}" registered!')
                    st.rerun()

    readers = search_readers(rq) if rq else get_all_readers()
    st.caption(f"{len(readers)} readers registered.")
    for r in readers:
        c1, c2, c3 = st.columns([1, 7, 1])
        with c1:
            st.markdown("👤")
        with c2:
            st.markdown(f"**{r['name']}** (#{r['id']})")
            st.caption(f"📧 {r['email']} · 📱 {r['phone']} · 📍 {r['address']} · Registered: {r['date_registered']}")
        with c3:
            if st.button("🗑️", key=f"del_r_{r['id']}"):
                delete_reader(r['id'])
                st.rerun()
        st.divider()


# ============================================================
# 4. MY BAG & CHECKOUT PAGE
# ============================================================
elif page == "🛒 My Bag":
    st.header("🛒 My Bag")

    bag_books = get_bag_books()
    col_left, col_right = st.columns([3, 2])

    with col_left:
        st.subheader(f"Books in your bag — {len(bag_books)}")
        if len(bag_books) == 0:
            st.info("Your bag is currently empty. Browse books to add items.")
        else:
            for b in bag_books:
                ca, cb, cc = st.columns([1, 6, 1])
                with ca:
                    st.markdown("📕")
                with cb:
                    st.markdown(f"**{b['title']}**")
                    st.caption(f"Author: {b['author']} · Genre: {b['genre']}")
                with cc:
                    if st.button("❌", key=f"rem_{b['id']}"):
                        remove_from_bag(b['id'])
                        st.rerun()
                st.divider()

    with col_right:
        st.subheader("Ready for Checkout?")
        readers = get_all_readers()

        if len(readers) == 0:
            st.warning("No readers registered. Please register a reader first.")
        else:
            reader_map = {f"{r['name']} (#{r['id']})": r for r in readers}
            selected_reader_key = st.selectbox("Reader ID *", ["-- Select a Reader --"] + list(reader_map.keys()))

            if selected_reader_key != "-- Select a Reader --":
                reader_obj = reader_map[selected_reader_key]
                st.markdown(f"**Name:** {reader_obj['name']}")
                st.markdown(f"**Contact:** {reader_obj['phone']}")

            st.markdown(f"**Issue Date:** {datetime.now().strftime('%B %d, %Y, %I:%M %p')}")

            # Return Due Date & Time Picker
            st.markdown("---")
            st.markdown("##### 📅 Return Due Date & Time")
            default_due_date = datetime.now() + timedelta(days=14)
            due_d = st.date_input("Due Date *", value=default_due_date.date())
            due_t = st.time_input("Due Time *", value=default_due_date.time().replace(second=0, microsecond=0))

            combined_due_dt = datetime.combine(due_d, due_t)
            due_date_iso = combined_due_dt.strftime('%Y-%m-%dT%H:%M')

            # Penalty Charges & Real-time Overdue preview
            st.markdown("---")
            st.markdown("##### 💰 Penalty Charges")
            st.markdown(f"**Penalty Rate:** ₹{st.session_state.penalty_rate} per day")

            now = datetime.now()
            if now > combined_due_dt:
                diff_days = max(1, (now.date() - combined_due_dt.date()).days or 1)
                fine_preview = diff_days * st.session_state.penalty_rate
                st.markdown(f"**Overdue Days:** :red[{diff_days} day(s) overdue]")
                st.markdown(f"**Total Fine:** :red[₹{fine_preview}]")
                st.markdown("**Payment Status:** :red[Unpaid]")
            else:
                st.markdown("**Overdue Days:** :green[0 days (On Time)]")
                st.markdown("**Total Fine:** :green[₹0]")
                st.markdown("**Payment Status:** :green[No Fine Due]")

            st.markdown("---")
            # Issue Book Button with full validation
            if st.button("📖 Issue Book", use_container_width=True, type="primary"):
                # 1. Validate reader
                if selected_reader_key == "-- Select a Reader --":
                    st.error("Validation Error: Please select a Reader ID before issuing.")
                # 2. Validate bag books
                elif len(bag_books) == 0:
                    st.error("Validation Error: Your bag is empty. Please add books to issue.")
                else:
                    reader_obj = reader_map[selected_reader_key]
                    result = issue_books(reader_obj['id'], [b['id'] for b in bag_books], due_date_iso)
                    if result['success']:
                        clear_bag()
                        st.success(f"Success! Book(s) issued: {', '.join(result['issued'])}")
                        st.rerun()
                    else:
                        st.error(result.get('message', 'Issue failed'))


# ============================================================
# 5. RETURNS & PENALTIES PAGE
# ============================================================
elif page == "🔄 Returns & Penalties":
    st.header("🔄 Book Returns & Overdue Penalties")

    txns = get_all_transactions()

    c1, c2 = st.columns(2)
    with c1:
        st_filter = st.selectbox("Status Filter", ["All", "issued", "returned"])
    with c2:
        all_r = get_all_readers()
        r_choices = ["All Readers"] + [f"{r['name']} (#{r['id']})" for r in all_r]
        rf_filter = st.selectbox("Reader Filter", r_choices)

    filtered_txns = txns
    if st_filter != "All":
        filtered_txns = [t for t in filtered_txns if t['status'] == st_filter]
    if rf_filter != "All Readers":
        target_id = int(rf_filter.split('#')[1].rstrip(')'))
        filtered_txns = [t for t in filtered_txns if t['reader_id'] == target_id]

    st.caption(f"{len(filtered_txns)} transaction(s) found.")

    if len(filtered_txns) == 0:
        st.info("No matching transactions found.")
    else:
        for t in sorted(filtered_txns, key=lambda x: x['id'], reverse=True):
            is_issued = t['status'] == 'issued'
            due_str = t.get('due_date', '')

            # Calculate real-time penalty if currently issued
            if is_issued and due_str:
                pen = calculate_penalty(due_str)
                overdue_days = pen['overdue_days']
                fine_amount = pen['penalty_amount']
            else:
                overdue_days = t.get('overdue_days', 0)
                fine_amount = t.get('penalty_amount', 0)

            is_paid = t.get('penalty_paid', False)

            colA, colB, colC, colD = st.columns([3, 2, 2, 2])
            with colA:
                st.markdown(f"**#{t['id']} · {t['book_title']}**")
                st.caption(f"Reader: {t['reader_name']} (ID #{t['reader_id']})")
                st.caption(f"Issued: {t['issue_date']} · Due: {due_str or 'N/A'}")
            with colB:
                if t['return_date']:
                    st.caption(f"Returned on: **{t['return_date']}**")
                else:
                    st.markdown(":orange[Currently Issued]")

                if overdue_days > 0:
                    st.markdown(f":red[{overdue_days} day(s) overdue]")
                else:
                    st.markdown(":green[On Time]")
            with colC:
                if fine_amount > 0:
                    st.markdown(f"Fine: **:red[₹{fine_amount}]**")
                    if is_paid:
                        st.markdown(":green[Status: Paid]")
                    else:
                        st.markdown(":red[Status: Unpaid]")
                else:
                    st.markdown(":green[No Fine]")
            with colD:
                if is_issued:
                    if st.button("Return Book", key=f"ret_{t['id']}", use_container_width=True):
                        res = return_book(t['id'])
                        if res['success']:
                            st.success(res['message'])
                            st.rerun()
                elif fine_amount > 0 and not is_paid:
                    if st.button("💵 Mark Paid", key=f"pay_{t['id']}", use_container_width=True, type="primary"):
                        if pay_penalty(t['id']):
                            st.success("Fine marked as Paid!")
                            st.rerun()
                else:
                    st.caption("✅ Completed")
            st.divider()


# ============================================================
# 6. DASHBOARD PAGE
# ============================================================
elif page == "📊 Dashboard":
    st.header("📊 Library Statistics Dashboard")
    stats = get_dashboard_stats()

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Volumes", stats['total_books'])
    m2.metric("Available", stats['available_books'])
    m3.metric("Issued", stats['issued_books'])
    m4.metric("Registered Readers", stats['total_readers'])

    st.markdown("---")
    genre_data = stats['genre_distribution']
    if genre_data:
        import pandas as pd
        df = pd.DataFrame(list(genre_data.items()), columns=['Genre', 'Count'])
        st.subheader("📚 Books by Genre")
        st.bar_chart(df.set_index('Genre'))
