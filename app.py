import streamlit as st
import json
import os
import plotly.express as px
import pandas as pd

# =========================
# Custom CSS for improved UI
# =========================
st.markdown("""
    <style>
    /* Change background color */
    .reportview-container {
        background: #f0f2f6;
    }
    /* Center header text */
    .css-18e3th9 {
        text-align: center;
    }
    /* Main container style */
    .main {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        margin: 20px;
        box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }
    /* Sidebar style */
    .sidebar .sidebar-content {
        background: #ffffff;
        border-radius: 10px;
        padding: 10px;
    }
    /* Buttons */
    div.stButton > button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 24px;
        border-radius: 5px;
        cursor: pointer;
    }
    div.stButton > button:hover {
        background-color: #45a049;
    }
    </style>
    """, unsafe_allow_html=True)

# =========================
# Banner Image
# =========================
st.image("https://images.unsplash.com/photo-1512820790803-83ca734da794?ixlib=rb-1.2.1&auto=format&fit=crop&w=1350&q=80",
         use_container_width=True)

# =========================
# Simple Built-In Authentication
# =========================

# File to store user credentials
USERS_FILE = "users.json"

def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return {}
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def signup(full_name, username, password):
    users = load_users()
    if username in users:
        return False, "Username already exists."
    users[username] = {"name": full_name, "password": password}
    save_users(users)
    return True, "User created successfully!"

def login(username, password):
    users = load_users()
    if username in users and users[username]["password"] == password:
        return True, users[username]["name"]
    return False, "Invalid username or password."

# Initialize session state for authentication if not set.
if "logged_in_user" not in st.session_state:
    st.session_state.logged_in_user = None
    st.session_state.user_name = None

# If user is not logged in, show authentication forms.
if st.session_state.logged_in_user is None:
    st.title("Sign In / Sign Up")
    auth_mode = st.radio("Select Option", ["Sign In", "Sign Up"])
    
    if auth_mode == "Sign Up":
        with st.form("signup_form"):
            full_name = st.text_input("Full Name")
            username_signup = st.text_input("Choose a Username")
            password_signup = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_submitted = st.form_submit_button("Sign Up")
            if signup_submitted:
                if password_signup != confirm_password:
                    st.error("Passwords do not match.")
                else:
                    success, msg = signup(full_name, username_signup, password_signup)
                    if success:
                        st.success(msg)
                        # Automatically log the user in after sign up.
                        st.session_state.logged_in_user = username_signup
                        st.session_state.user_name = full_name
                    else:
                        st.error(msg)
                        
    else:  # Sign In
        with st.form("signin_form"):
            username_signin = st.text_input("Username")
            password_signin = st.text_input("Password", type="password")
            signin_submitted = st.form_submit_button("Sign In")
            if signin_submitted:
                success, result = login(username_signin, password_signin)
                if success:
                    st.success("Logged in successfully!")
                    st.session_state.logged_in_user = username_signin
                    st.session_state.user_name = result
                else:
                    st.error(result)
    st.stop()

# =========================
# Logged In: Show Logout Button
# =========================
if st.sidebar.button("Logout"):
    st.session_state.logged_in_user = None
    st.session_state.user_name = None
    st.experimental_rerun()

# =========================
# Main Library Manager UI
# =========================
# Wrap main content in a styled container.
with st.container():
    st.markdown("<div class='main'>", unsafe_allow_html=True)
    st.title("📚 Personal Library Manager")
    st.write(f"Welcome, **{st.session_state.user_name}**!")
    
    # Each user gets a separate library file.
    LIBRARY_FILE = f"library_{st.session_state.logged_in_user}.json"
    
    # ----- File Handling Functions -----
    def load_library():
        if os.path.exists(LIBRARY_FILE):
            try:
                with open(LIBRARY_FILE, "r") as file:
                    return json.load(file)
            except json.JSONDecodeError:
                return []
        return []

    def save_library(library):
        with open(LIBRARY_FILE, "w") as file:
            json.dump(library, file, indent=4)

    library = load_library()

    # ----- Library Management Functions -----
    def add_book(title, author, year, genre, read, favorite):
        book = {
            "title": title,
            "author": author,
            "year": int(year),
            "genre": genre,
            "read": read,
            "favorite": favorite
        }
        library.append(book)
        save_library(library)
        st.success("Book added successfully!")

    def remove_book(title):
        updated_library = [book for book in library if book["title"].lower() != title.lower()]
        if len(updated_library) < len(library):
            library.clear()
            library.extend(updated_library)
            save_library(library)
            st.success("Book removed successfully!")
        else:
            st.warning("Book not found!")

    def update_book(old_title, new_title, new_author, new_year, new_genre, new_read, new_favorite):
        updated = False
        for book in library:
            if book["title"].lower() == old_title.lower():
                book["title"] = new_title
                book["author"] = new_author
                book["year"] = int(new_year)
                book["genre"] = new_genre
                book["read"] = new_read
                book["favorite"] = new_favorite
                updated = True
                break
        if updated:
            save_library(library)
            st.success("Book updated successfully!")
        else:
            st.warning("Book not found!")

    def search_books(search_term, search_by):
        return [book for book in library if search_term.lower() in book[search_by].lower()]

    def advanced_search(title_term, author_term, genre_term, year_min, year_max):
        results = library
        if title_term:
            results = [b for b in results if title_term.lower() in b["title"].lower()]
        if author_term:
            results = [b for b in results if author_term.lower() in b["author"].lower()]
        if genre_term:
            results = [b for b in results if genre_term.lower() in b["genre"].lower()]
        results = [b for b in results if year_min <= b["year"] <= year_max]
        return results

    def display_statistics():
        total_books = len(library)
        read_books = sum(1 for book in library if book["read"])
        avg_year = sum(book["year"] for book in library) / total_books if total_books > 0 else 0
        percentage_read = (read_books / total_books * 100) if total_books > 0 else 0
        genre_count = {}
        for book in library:
            genre = book.get("genre", "Unknown")
            genre_count[genre] = genre_count.get(genre, 0) + 1
        common_genre = max(genre_count, key=genre_count.get) if genre_count else "N/A"
        return total_books, percentage_read, avg_year, common_genre

    # ----- Visualization Functions -----
    def create_genre_bar_chart():
        genre_count = {}
        for book in library:
            genre = book.get("genre", "Unknown")
            genre_count[genre] = genre_count.get(genre, 0) + 1
        if genre_count:
            df = pd.DataFrame(list(genre_count.items()), columns=["Genre", "Count"])
            fig = px.bar(df, x="Genre", y="Count", title="Books per Genre", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data to visualize.")

    def create_read_status_pie_chart():
        read_count = sum(1 for book in library if book["read"])
        unread_count = len(library) - read_count
        data = {"Status": ["Read", "Unread"], "Count": [read_count, unread_count]}
        df = pd.DataFrame(data)
        fig = px.pie(df, names="Status", values="Count", title="Read vs Unread Books", template="plotly_white")
        st.plotly_chart(fig, use_container_width=True)

    def create_publication_year_histogram():
        years = [book["year"] for book in library if "year" in book]
        if years:
            df = pd.DataFrame(years, columns=["Year"])
            fig = px.histogram(df, x="Year", nbins=20, title="Publication Year Distribution", template="plotly_white")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data for publication years.")

    # ----- Export & Import Functions -----
    def export_library_as_csv():
        if library:
            df = pd.DataFrame(library)
            return df.to_csv(index=False).encode('utf-8')
        return None

    def import_library_from_csv(uploaded_file):
        try:
            df = pd.read_csv(uploaded_file)
            new_library = df.to_dict(orient="records")
            library.clear()
            library.extend(new_library)
            save_library(library)
            st.success("Library imported successfully!")
        except Exception as e:
            st.error(f"Error importing library: {e}")

    # ----- Sidebar Menu -----
    st.sidebar.markdown("<div class='sidebar'>", unsafe_allow_html=True)
    st.sidebar.subheader("Library Menu")
    menu_options = [
        "Add a Book", 
        "Remove a Book", 
        "Update a Book",
        "Search for a Book",
        "Advanced Search",
        "Display All Books", 
        "Sort & Filter Books",
        "Display Statistics",
        "Dashboard",
        "Export Library",
        "Import Library"
    ]
    choice = st.sidebar.selectbox("Choose an option", menu_options)
    st.sidebar.markdown("</div>", unsafe_allow_html=True)

    # ----- Main App Functionality -----
    if choice == "Add a Book":
        st.header("Add a New Book")
        with st.form("add_book_form"):
            col1, col2 = st.columns(2)
            with col1:
                title = st.text_input("Title")
                author = st.text_input("Author")
            with col2:
                year = st.number_input("Publication Year", min_value=1000, max_value=9999, step=1)
                genre = st.text_input("Genre")
            read = st.checkbox("Have you read this book?")
            favorite = st.checkbox("Mark as Favorite")
            submitted = st.form_submit_button("Add Book")
            if submitted:
                if title and author and genre:
                    add_book(title, author, year, genre, read, favorite)
                else:
                    st.error("Please fill in all fields.")

    elif choice == "Remove a Book":
        st.header("Remove a Book")
        title = st.text_input("Enter the title of the book to remove")
        if st.button("Remove Book"):
            remove_book(title)

    elif choice == "Update a Book":
        st.header("Update Book Details")
        st.info("Enter the current title and new details to update.")
        col1, col2 = st.columns(2)
        with col1:
            old_title = st.text_input("Current Title")
            new_title = st.text_input("New Title")
            new_author = st.text_input("New Author")
        with col2:
            new_year = st.number_input("New Publication Year", min_value=1000, max_value=9999, step=1)
            new_genre = st.text_input("New Genre")
            new_read = st.checkbox("Mark as Read")
            new_favorite = st.checkbox("Mark as Favorite")
        if st.button("Update Book"):
            if old_title and new_title and new_author and new_genre:
                update_book(old_title, new_title, new_author, new_year, new_genre, new_read, new_favorite)
            else:
                st.error("Please fill in all required fields.")

    elif choice == "Search for a Book":
        st.header("Search for a Book")
        search_by = st.radio("Search by", ["title", "author", "genre"])
        search_term = st.text_input("Enter search term")
        if st.button("Search"):
            results = search_books(search_term, search_by)
            if results:
                st.subheader("Matching Books:")
                for book in results:
                    st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} - " +
                             f"{'Read' if book['read'] else 'Unread'}, " +
                             f"{'Favorite' if book.get('favorite', False) else ''}")
            else:
                st.warning("No books found!")

    elif choice == "Advanced Search":
        st.header("Advanced Search")
        title_term = st.text_input("Title contains")
        author_term = st.text_input("Author contains")
        genre_term = st.text_input("Genre contains")
        col1, col2 = st.columns(2)
        with col1:
            year_min = st.number_input("Publication Year From", value=1000, step=1)
        with col2:
            year_max = st.number_input("Publication Year To", value=2025, step=1)
        if st.button("Search"):
            results = advanced_search(title_term, author_term, genre_term, year_min, year_max)
            if results:
                st.subheader("Matching Books:")
                for book in results:
                    st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} - " +
                             f"{'Read' if book['read'] else 'Unread'}, " +
                             f"{'Favorite' if book.get('favorite', False) else ''}")
            else:
                st.warning("No books match the criteria.")

    elif choice == "Display All Books":
        st.header("Your Library")
        if library:
            for book in library:
                st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} - " +
                         f"{'Read' if book['read'] else 'Unread'}, " +
                         f"{'Favorite' if book.get('favorite', False) else ''}")
        else:
            st.info("Your library is empty.")

    elif choice == "Sort & Filter Books":
        st.header("Sort & Filter Books")
        sort_by = st.selectbox("Sort by", ["Title", "Author", "Publication Year"])
        favorites_only = st.checkbox("Show Favorites Only")
        filtered_books = library.copy()
        if favorites_only:
            filtered_books = [book for book in filtered_books if book.get("favorite", False)]
        if sort_by == "Title":
            filtered_books.sort(key=lambda x: x["title"].lower())
        elif sort_by == "Author":
            filtered_books.sort(key=lambda x: x["author"].lower())
        elif sort_by == "Publication Year":
            filtered_books.sort(key=lambda x: x["year"])
        if filtered_books:
            for book in filtered_books:
                st.write(f"**{book['title']}** by {book['author']} ({book['year']}) - {book['genre']} - " +
                         f"{'Read' if book['read'] else 'Unread'}, " +
                         f"{'Favorite' if book.get('favorite', False) else ''}")
        else:
            st.info("No books match the filter criteria.")

    elif choice == "Display Statistics":
        st.header("Library Statistics")
        total, percent, avg_year, common_genre = display_statistics()
        st.write(f"**Total Books:** {total}")
        st.write(f"**Percentage Read:** {percent:.2f}%")
        st.write(f"**Average Publication Year:** {avg_year:.1f}")
        st.write(f"**Most Common Genre:** {common_genre}")

    elif choice == "Dashboard":
        st.header("Dashboard & Visualizations")
        st.subheader("Books per Genre")
        create_genre_bar_chart()
        st.subheader("Read vs Unread")
        create_read_status_pie_chart()
        st.subheader("Publication Year Distribution")
        create_publication_year_histogram()

    elif choice == "Export Library":
        st.header("Export Library as CSV")
        csv = export_library_as_csv()
        if csv:
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name="library_export.csv",
                mime="text/csv"
            )
        else:
            st.info("No data available to export.")

    elif choice == "Import Library":
        st.header("Import Library from CSV")
        uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            import_library_from_csv(uploaded_file)

    st.markdown("</div>", unsafe_allow_html=True)
