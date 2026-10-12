import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs
from html import escape

books = [
    {
        "id": 1,
        "title": "In Cold Blood",
        "author": "Truman Capote",
        "available": True
    },
    {
        "id": 2,
        "title": "Of Mice and Men",
        "author": "John Steinbeck",
        "available": True
    }
]

message = ""

def get_next_id():
    """Generate the next available book ID."""

    if not books:
        return 1

    highest_id = 0

    for book in books:
        if book["id"] > highest_id:
            highest_id = book["id"]

    return highest_id + 1


def get_book_by_id(book_id):
    """Find a book using its ID."""

    for book in books:
        if book["id"] == book_id:
            return book

    return None


def validate_book(title, author):
    """Check whether the book details are valid."""

    title = title.strip()
    author = author.strip()

    if title == "":
        return False, "Book title cannot be empty."

    if author == "":
        return False, "Author name cannot be empty."

    if len(title) < 2:
        return False, "Book title is too short."

    if len(author) < 2:
        return False, "Author name is too short."

    return True, "Valid"


def add_book(title, author):
    """Add a new book to the library."""

    valid, result = validate_book(title, author)

    if not valid:
        return result

    new_book = {
        "id": get_next_id(),
        "title": title.strip(),
        "author": author.strip(),
        "available": True
    }

    books.append(new_book)

    return "Book added successfully."


def search_books(query):
    """Search books by title or author."""

    query = query.strip().lower()

    if query == "":
        return books.copy()

    results = []

    for book in books:

        title = book["title"].lower()
        author = book["author"].lower()

        if query in title or query in author:
            results.append(book)

    return results


def search_by_author(author):
    """Search specifically by author name."""

    author = author.strip().lower()

    results = []

    for book in books:

        if author in book["author"].lower():
            results.append(book)

    return results


def search_by_title(title):
    """Search specifically by book title."""

    title = title.strip().lower()

    results = []

    for book in books:

        if title in book["title"].lower():
            results.append(book)

    return results


def filter_by_status(book_list, status):
    """Filter books according to availability."""

    if status == "":
        return book_list

    results = []

    for book in book_list:

        if status == "available" and book["available"]:
            results.append(book)

        elif status == "issued" and not book["available"]:
            results.append(book)

    return results


def get_available_books():
    """Return all currently available books."""

    results = []

    for book in books:

        if book["available"]:
            results.append(book)

    return results


def get_issued_books():
    """Return all currently issued books."""

    results = []

    for book in books:

        if not book["available"]:
            results.append(book)

    return results


def issue_book(book_id):
    """Issue a book if it is currently available."""

    book = get_book_by_id(book_id)

    if book is None:
        return "Book not found."

    if not book["available"]:
        return "This book is already issued."

    book["available"] = False

    return "Book issued successfully."


def return_book(book_id):
    """Return a book if it is currently issued."""

    book = get_book_by_id(book_id)

    if book is None:
        return "Book not found."

    if book["available"]:
        return "This book is already available."

    book["available"] = True

    return "Book returned successfully."


def toggle_book(book_id):
    """Issue or return a book depending on its current status."""

    book = get_book_by_id(book_id)

    if book is None:
        return "Book not found."

    if book["available"]:
        return issue_book(book_id)

    return return_book(book_id)


def get_statistics():
    """Calculate total, available and issued book counts."""

    total = len(books)
    available = 0
    issued = 0

    for book in books:

        if book["available"]:
            available += 1
        else:
            issued += 1

    return total, available, issued


def get_status(book):
    """Return a readable status for a book."""

    if book["available"]:
        return "Available"

    return "Issued"


def get_action(book):
    """Return the correct action button text."""

    if book["available"]:
        return "Issue"

    return "Return"


# ============================================================
# HTML GENERATION
# ============================================================

STYLE = """
body {
    font-family: Georgia, serif;
    background: #f0f0f0;
    color: #877b7a;
    margin: 0;
}

main {
    max-width: 720px;
    margin: auto;
    padding: 20px 16px;
}

section {
    background: #ffffff;
    border: 1px solid #cfd9d5;
    border-radius: 10px;
    padding: 16px;
    margin-bottom: 16px;
}

input, button {
    font: inherit;
    padding: 10px;
    border-radius: 6px;
    border: 1px solid #cfd9d5;
}

input {
    width: 100%;
    box-sizing: border-box;
    margin-bottom: 8px;
}

button {
    background: #544C4B;
    color: #ffffff;
    border: 0;
    cursor: pointer;
}

button:hover {
    opacity: 0.85;
}

.row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-top: 1px solid #cfd9d5;
    padding: 10px 0;
    gap: 10px;
}

.row:first-child {
    border-top: 0;
}

.m {
    color: #544C4B;
    font-size: .9rem;
}

.ok {
    color: #6F6462;
}

.out {
    color: #B2AAA9;
}

a {
    color: #9D9290;
    margin-right: 10px;
    text-decoration: none;
}

a:hover {
    text-decoration: underline;
}

.stats {
    display: flex;
    gap: 10px;
}

.stat {
    flex: 1;
    text-align: center;
    background: #f7f7f7;
    padding: 12px;
    border-radius: 8px;
}

.stat-number {
    font-size: 1.5rem;
    font-weight: bold;
    color: #544C4B;
}

.stat-label {
    font-size: .85rem;
}

.search-options {
    display: flex;
    gap: 10px;
    align-items: center;
    margin-bottom: 8px;
}

.search-options input {
    width: auto;
    margin: 0;
}

.search-options label {
    font-size: .9rem;
}

h1, h2 {
    color: #544C4B;
    text-transform: uppercase;
}

small {
    color: #877b7a;
}
"""


def render_statistics():
    """Create the statistics section using Python-generated values."""

    total, available, issued = get_statistics()

    return f"""
    <div class="stats">

        <div class="stat">
            <div class="stat-number">{total}</div>
            <div class="stat-label">Total Books</div>
        </div>

        <div class="stat">
            <div class="stat-number">{available}</div>
            <div class="stat-label">Available</div>
        </div>

        <div class="stat">
            <div class="stat-number">{issued}</div>
            <div class="stat-label">Issued</div>
        </div>

    </div>
    """


def render_book(book):
    """Convert one Python book dictionary into HTML."""

    status = get_status(book)
    action = get_action(book)

    if book["available"]:
        css_class = "ok"
    else:
        css_class = "out"

    return f"""
    <div class="row">

        <div>
            <strong>{escape(book["title"])}</strong>

            <div class="m">
                {escape(book["author"])}
                &nbsp; | &nbsp;
                ID {book["id"]}
            </div>
        </div>

        <div>
            <span class="{css_class}">
                {status}
            </span>

            <form method="post"
                  action="/toggle"
                  style="display:inline">

                <input
                    type="hidden"
                    name="id"
                    value="{book["id"]}"
                >

                <button type="submit">
                    {action}
                </button>

            </form>
        </div>

    </div>
    """


def render_books(book_list):
    """Create HTML for all books in a list."""

    if not book_list:
        return '<p class="m">No books match your search.</p>'

    rows = ""

    for book in book_list:
        rows += render_book(book)

    return rows


def render_page(query="", status="", search_type="all"):
    """Build the complete library webpage."""

    # ----------------------------
    # SEARCH
    # ----------------------------

    if search_type == "author":
        results = search_by_author(query)

    elif search_type == "title":
        results = search_by_title(query)

    else:
        results = search_books(query)

    # ----------------------------
    # STATUS FILTER
    # ----------------------------

    results = filter_by_status(results, status)

    # ----------------------------
    # BOOK HTML
    # ----------------------------

    rows = render_books(results)

    # ----------------------------
    # STATUS MESSAGE
    # ----------------------------

    message_html = ""

    if message:
        message_html = f"""
        <p class="ok">
            {escape(message)}
        </p>
        """

    # ----------------------------
    # COMPLETE PAGE
    # ----------------------------

    return f"""
    <!doctype html>

    <html lang="en">

    <head>

        <meta charset="utf-8">

        <meta
            name="viewport"
            content="width=device-width,
                     initial-scale=1"
        >

        <title>Library Management</title>

        <style>
            {STYLE}
        </style>

    </head>

    <body>

        <main>

            <h1>Library Management</h1>

            {message_html}

            <!-- STATISTICS -->

            <section>

                <h2>Library Statistics</h2>

                {render_statistics()}

            </section>


            <!-- ADD BOOK -->

            <section>

                <h2>Add a Book</h2>

                <form method="post" action="/add">

                    <input
                        name="title"
                        placeholder="Book Title"
                        required
                    >

                    <input
                        name="author"
                        placeholder="Author"
                        required
                    >

                    <button type="submit">
                        Add Book
                    </button>

                </form>

            </section>


            <!-- SEARCH -->

            <section>

                <h2>Search Books</h2>

                <form method="get" action="/">

                    <input
                        name="q"
                        value="{escape(query)}"
                        placeholder="Search by title or author"
                    >

                    <div class="search-options">

                        <label>
                            <input
                                type="radio"
                                name="search_type"
                                value="all"
                                {"checked" if search_type == "all" else ""}
                            >
                            All
                        </label>

                        <label>
                            <input
                                type="radio"
                                name="search_type"
                                value="title"
                                {"checked" if search_type == "title" else ""}
                            >
                            Title
                        </label>

                        <label>
                            <input
                                type="radio"
                                name="search_type"
                                value="author"
                                {"checked" if search_type == "author" else ""}
                            >
                            Author
                        </label>

                    </div>

                    <input
                        type="hidden"
                        name="status"
                        value="{escape(status)}"
                    >

                    <button type="submit">
                        Search
                    </button>

                </form>

            </section>


            <!-- BOOK LIST -->

            <section>

                <h2>Books</h2>

                <p>

                    <a href="/">
                        All
                    </a>

                    <a href="/?status=available">
                        Available
                    </a>

                    <a href="/?status=issued">
                        Issued
                    </a>

                </p>

                {rows}

            </section>

        </main>

    </body>

    </html>
    """


# ============================================================
# HTTP SERVER
# ============================================================

class Handler(BaseHTTPRequestHandler):

    def send_page(self, body):
        """Send an HTML page to the browser."""

        data = body.encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.end_headers()

        self.wfile.write(data)


    def redirect(self):
        """Redirect the browser back to the home page."""

        self.send_response(303)

        self.send_header(
            "Location",
            "/"
        )

        self.end_headers()


    def do_GET(self):
        """Handle GET requests such as searching and filtering."""

        global message

        parsed_url = urlparse(self.path)

        query_data = parse_qs(parsed_url.query)

        query = query_data.get("q", [""])[0].strip()

        status = query_data.get(
            "status",
            [""]
        )[0].strip()

        search_type = query_data.get(
            "search_type",
            ["all"]
        )[0].strip()

        page = render_page(
            query,
            status,
            search_type
        )

        self.send_page(page)

        message = ""


    def do_POST(self):
        """Handle actions such as adding, issuing and returning."""

        global message

        # ----------------------------
        # READ FORM DATA
        # ----------------------------

        length = int(
            self.headers.get(
                "Content-Length",
                0
            )
        )

        form_data = self.rfile.read(
            length
        ).decode("utf-8")

        form = parse_qs(form_data)

        path = urlparse(self.path).path

        # ----------------------------
        # ADD BOOK
        # ----------------------------

        if path == "/add":

            title = form.get(
                "title",
                [""]
            )[0].strip()

            author = form.get(
                "author",
                [""]
            )[0].strip()

            message = add_book(
                title,
                author
            )

        # ----------------------------
        # ISSUE / RETURN BOOK
        # ----------------------------

        elif path == "/toggle":

            try:

                book_id = int(
                    form.get(
                        "id",
                        ["0"]
                    )[0]
                )

                message = toggle_book(
                    book_id
                )

            except ValueError:

                message = "Invalid book ID."

        # ----------------------------
        # UNKNOWN REQUEST
        # ----------------------------

        else:

            message = "Unknown request."

        self.redirect()


# ============================================================
# START SERVER
# ============================================================

if __name__ == "__main__":

    # Hosting platforms such as Render provide the port through PORT.
    # Locally, the app defaults to port 8000.
    port = int(os.environ.get("PORT", "8000"))

    print(f"Library Management System running on port {port}.")
    print("Press Ctrl+C to stop the server.")

    # 0.0.0.0 allows the hosting platform to route public requests to the app.
    server = ThreadingHTTPServer(
        ("0.0.0.0", port),
        Handler
    )

    server.serve_forever()
