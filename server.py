from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
import base64
import hashlib
import hmac
import json
import os
import secrets
import smtplib
import sqlite3
import sys
from email.message import EmailMessage


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "threadhaus.db"
CONFIRMATION_DIR = DATA_DIR / "order_confirmations"
HOST = "0.0.0.0"
DEFAULT_PORT = 8000

PRODUCTS = [
    {
        "id": "box-tee",
        "name": "Box Cut Graphic Tee",
        "category": "Clothing",
        "type": "tees",
        "price": 1499,
        "badge": "New",
        "image": "assets/product-tee.png",
        "description": "Heavy cotton tee with a straight drape.",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [
            {"name": "Ink", "value": "#1f2828"},
            {"name": "Rust", "value": "#ef6f4d"},
            {"name": "Bone", "value": "#ede8dc"},
        ],
    },
    {
        "id": "hoodie",
        "name": "Loopback Utility Hoodie",
        "category": "Clothing",
        "type": "hoodies",
        "price": 3299,
        "badge": "Warm",
        "image": "assets/product-hoodie.png",
        "description": "Relaxed fleece hoodie with a deep pocket.",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [
            {"name": "Plum", "value": "#6b48b3"},
            {"name": "Ink", "value": "#1f2828"},
            {"name": "Sky", "value": "#b8d2dc"},
        ],
    },
    {
        "id": "runner",
        "name": "Arc Runner Sneaker",
        "category": "Shoes",
        "type": "sneakers",
        "price": 5299,
        "badge": "Top",
        "image": "assets/product-sneaker.png",
        "description": "Cushioned everyday sneaker with a bold upper.",
        "sizes": ["7", "8", "9", "10", "11"],
        "colors": [
            {"name": "Signal Red", "value": "#f15154"},
            {"name": "Black", "value": "#1f2828"},
            {"name": "Cream", "value": "#f3ead8"},
        ],
    },
    {
        "id": "cap",
        "name": "Panel Logo Cap",
        "category": "Caps",
        "type": "caps",
        "price": 899,
        "badge": "Fresh",
        "image": "assets/product-cap.png",
        "description": "Structured cap with an adjustable back strap.",
        "sizes": ["OS"],
        "colors": [
            {"name": "Teal", "value": "#126c72"},
            {"name": "Ink", "value": "#1f2828"},
            {"name": "Rust", "value": "#ef6f4d"},
        ],
    },
    {
        "id": "jacket",
        "name": "Split Zip Coach Jacket",
        "category": "Clothing",
        "type": "jackets",
        "price": 4299,
        "badge": "Drop",
        "image": "assets/product-jacket.png",
        "description": "Water-resistant shell with contrast zip trim.",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [
            {"name": "Navy", "value": "#202f4d"},
            {"name": "Rust", "value": "#ef6f4d"},
            {"name": "Bone", "value": "#ede8dc"},
        ],
    },
    {
        "id": "tote",
        "name": "Market Day Tote",
        "category": "Accessories",
        "type": "bags",
        "price": 1299,
        "badge": "Carry",
        "image": "assets/product-tote.png",
        "description": "Canvas tote sized for daily gear and extras.",
        "sizes": ["OS"],
        "colors": [
            {"name": "Canvas", "value": "#d4b87c"},
            {"name": "Black", "value": "#1f2828"},
            {"name": "Olive", "value": "#59634d"},
        ],
    },
    {
        "id": "jogger",
        "name": "Tapered City Jogger",
        "category": "Clothing",
        "type": "pants",
        "price": 2499,
        "badge": "Easy",
        "image": "assets/product-joggers.png",
        "description": "Soft tapered pant with ribbed cuffs.",
        "sizes": ["S", "M", "L", "XL"],
        "colors": [
            {"name": "Olive", "value": "#59634d"},
            {"name": "Ink", "value": "#1f2828"},
            {"name": "Stone", "value": "#bab2a1"},
        ],
    },
    {
        "id": "slides",
        "name": "Softstep Pool Slide",
        "category": "Shoes",
        "type": "slides",
        "price": 1599,
        "badge": "Light",
        "image": "assets/product-slides.png",
        "description": "Molded slide with a cushioned footbed.",
        "sizes": ["7", "8", "9", "10", "11"],
        "colors": [
            {"name": "Rust", "value": "#ef6f4d"},
            {"name": "Ink", "value": "#1f2828"},
            {"name": "Teal", "value": "#126c72"},
        ],
    },
]


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with get_connection() as connection:
        connection.executescript(
            """
            PRAGMA foreign_keys = ON;

            CREATE TABLE IF NOT EXISTS users (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              name TEXT NOT NULL,
              email TEXT NOT NULL UNIQUE,
              password_hash TEXT NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
              token TEXT PRIMARY KEY,
              user_id INTEGER NOT NULL,
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              expires_at TEXT NOT NULL,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS products (
              id TEXT PRIMARY KEY,
              name TEXT NOT NULL,
              category TEXT NOT NULL,
              type TEXT NOT NULL,
              price INTEGER NOT NULL,
              badge TEXT NOT NULL,
              image TEXT NOT NULL,
              description TEXT NOT NULL,
              sizes_json TEXT NOT NULL,
              colors_json TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS orders (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              user_id INTEGER NOT NULL,
              total INTEGER NOT NULL,
              phone TEXT,
              address_json TEXT,
              payment_method TEXT,
              status TEXT NOT NULL DEFAULT 'placed',
              created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
              FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS order_items (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              order_id INTEGER NOT NULL,
              product_id TEXT NOT NULL,
              product_name TEXT NOT NULL,
              size TEXT NOT NULL,
              color TEXT NOT NULL,
              quantity INTEGER NOT NULL,
              unit_price INTEGER NOT NULL,
              FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
              FOREIGN KEY (product_id) REFERENCES products(id)
            );
            """
        )
        order_columns = {
            row["name"]
            for row in connection.execute("PRAGMA table_info(orders)").fetchall()
        }
        for column_name, column_type in (
            ("phone", "TEXT"),
            ("address_json", "TEXT"),
            ("payment_method", "TEXT"),
        ):
            if column_name not in order_columns:
                connection.execute(f"ALTER TABLE orders ADD COLUMN {column_name} {column_type}")
        for product in PRODUCTS:
            connection.execute(
                """
                INSERT OR REPLACE INTO products
                (id, name, category, type, price, badge, image, description, sizes_json, colors_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    product["id"],
                    product["name"],
                    product["category"],
                    product["type"],
                    product["price"],
                    product["badge"],
                    product["image"],
                    product["description"],
                    json.dumps(product["sizes"]),
                    json.dumps(product["colors"]),
                ),
            )


def hash_password(password):
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, 140000)
    return "pbkdf2_sha256$140000${}${}".format(
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(digest).decode("ascii"),
    )


def verify_password(password, stored):
    try:
        algorithm, rounds, salt_value, digest_value = stored.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        salt = base64.b64decode(salt_value.encode("ascii"))
        expected = base64.b64decode(digest_value.encode("ascii"))
        actual = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, int(rounds))
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def product_from_row(row):
    return {
        "id": row["id"],
        "name": row["name"],
        "category": row["category"],
        "type": row["type"],
        "price": row["price"],
        "badge": row["badge"],
        "image": row["image"],
        "description": row["description"],
        "sizes": json.loads(row["sizes_json"]),
        "colors": json.loads(row["colors_json"]),
    }


def send_order_confirmation(email, order):
    CONFIRMATION_DIR.mkdir(parents=True, exist_ok=True)
    subject = f"Threadhaus order #{order['id']} confirmed"
    address = order["address"]
    street = f", {address['street']}" if address.get("street") else ""
    body = (
        f"Hi {order['customer_name']},\n\n"
        f"Your Threadhaus order #{order['id']} is confirmed.\n"
        f"Total: INR {order['total']}\n"
        f"Payment: {order['payment']}\n"
        f"Phone: {order['phone']}\n"
        f"Delivery address: {address['house']}{street}, {address['pincode']}\n\n"
        "Thank you for shopping with Threadhaus Outfitters.\n"
    )
    message_path = CONFIRMATION_DIR / f"order-{order['id']}.txt"
    message_path.write_text(f"To: {email}\nSubject: {subject}\n\n{body}", encoding="utf-8")

    gmail_address = os.environ.get("THREADHAUS_GMAIL_ADDRESS")
    gmail_password = os.environ.get("THREADHAUS_GMAIL_APP_PASSWORD")
    if gmail_address and gmail_password:
        message = EmailMessage()
        message["From"] = gmail_address
        message["To"] = email
        message["Subject"] = subject
        message.set_content(body)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(gmail_address, gmail_password)
            smtp.send_message(message)
        return "sent"
    return "saved"


class ThreadhausHandler(SimpleHTTPRequestHandler):
    server_version = "ThreadhausBackend/1.0"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def log_message(self, format, *args):
        return

    def end_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type, Authorization")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(204)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            self.handle_api_get(path)
            return
        if path == "/":
            self.path = "/index.html"
        super().do_GET()

    def do_POST(self):
        path = urlparse(self.path).path
        if path.startswith("/api/"):
            self.handle_api_post(path)
            return
        self.send_error(404, "Not found")

    def read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length > 1_000_000:
            raise ValueError("Request body is too large.")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        return json.loads(raw or "{}")

    def write_json(self, payload, status=200):
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def write_error(self, message, status=400):
        self.write_json({"error": message}, status)

    def current_user(self):
        header = self.headers.get("Authorization", "")
        if not header.startswith("Bearer "):
            return None
        token = header.removeprefix("Bearer ").strip()
        if not token:
            return None
        with get_connection() as connection:
            row = connection.execute(
                """
                SELECT users.id, users.name, users.email
                FROM sessions
                JOIN users ON users.id = sessions.user_id
                WHERE sessions.token = ? AND sessions.expires_at > CURRENT_TIMESTAMP
                """,
                (token,),
            ).fetchone()
        return dict(row) if row else None

    def handle_api_get(self, path):
        if path == "/api/health":
            self.write_json({"ok": True})
            return
        if path == "/api/products":
            with get_connection() as connection:
                rows = connection.execute("SELECT * FROM products ORDER BY rowid").fetchall()
            self.write_json({"products": [product_from_row(row) for row in rows]})
            return
        if path == "/api/me":
            user = self.current_user()
            if not user:
                self.write_error("Not signed in.", 401)
                return
            self.write_json({"user": user})
            return
        if path == "/api/orders":
            user = self.current_user()
            if not user:
                self.write_error("Please log in to view orders.", 401)
                return
            with get_connection() as connection:
                rows = connection.execute(
                    "SELECT id, total, status, created_at FROM orders WHERE user_id = ? ORDER BY id DESC",
                    (user["id"],),
                ).fetchall()
            self.write_json({"orders": [dict(row) for row in rows]})
            return
        self.write_error("Unknown API endpoint.", 404)

    def handle_api_post(self, path):
        try:
            payload = self.read_json()
        except (ValueError, json.JSONDecodeError) as error:
            self.write_error(str(error), 400)
            return

        if path == "/api/register":
            self.register(payload)
            return
        if path == "/api/login":
            self.login(payload)
            return
        if path == "/api/logout":
            self.logout()
            return
        if path == "/api/orders":
            self.create_order(payload)
            return
        self.write_error("Unknown API endpoint.", 404)

    def create_session(self, user_id):
        token = secrets.token_urlsafe(32)
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO sessions (token, user_id, expires_at)
                VALUES (?, ?, datetime('now', '+7 days'))
                """,
                (token, user_id),
            )
        return token

    def register(self, payload):
        name = str(payload.get("name", "")).strip()
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", ""))
        if not name:
            self.write_error("Name is required.")
            return
        if "@" not in email or "." not in email:
            self.write_error("Use a valid email address.")
            return
        if len(password) < 6:
            self.write_error("Password must be at least 6 characters.")
            return
        try:
            with get_connection() as connection:
                cursor = connection.execute(
                    "INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)",
                    (name, email, hash_password(password)),
                )
                user_id = cursor.lastrowid
        except sqlite3.IntegrityError:
            self.write_error("That email is already registered.", 409)
            return
        token = self.create_session(user_id)
        self.write_json({"token": token, "user": {"id": user_id, "name": name, "email": email}}, 201)

    def login(self, payload):
        email = str(payload.get("email", "")).strip().lower()
        password = str(payload.get("password", ""))
        with get_connection() as connection:
            row = connection.execute(
                "SELECT id, name, email, password_hash FROM users WHERE email = ?",
                (email,),
            ).fetchone()
        if not row or not verify_password(password, row["password_hash"]):
            self.write_error("Email or password is incorrect.", 401)
            return
        token = self.create_session(row["id"])
        self.write_json({"token": token, "user": {"id": row["id"], "name": row["name"], "email": row["email"]}})

    def logout(self):
        header = self.headers.get("Authorization", "")
        token = header.removeprefix("Bearer ").strip() if header.startswith("Bearer ") else ""
        if token:
            with get_connection() as connection:
                connection.execute("DELETE FROM sessions WHERE token = ?", (token,))
        self.write_json({"ok": True})

    def create_order(self, payload):
        user = self.current_user()
        if not user:
            self.write_error("Please log in before checkout.", 401)
            return
        raw_items = payload.get("items")
        if not isinstance(raw_items, list) or not raw_items:
            self.write_error("Your cart is empty.")
            return
        checkout = payload.get("checkout") if isinstance(payload.get("checkout"), dict) else {}
        phone = str(checkout.get("phone", "")).strip()
        address = checkout.get("address") if isinstance(checkout.get("address"), dict) else {}
        house = str(address.get("house", "")).strip()
        street = str(address.get("street", "")).strip()
        pincode = str(address.get("pincode", "")).strip()
        payment = str(checkout.get("payment", "")).strip()
        if not phone.isdigit() or len(phone) != 10:
            self.write_error("Enter a valid 10 digit phone number.")
            return
        if not house:
            self.write_error("Enter your house number.")
            return
        if not pincode.isdigit() or len(pincode) != 6:
            self.write_error("Enter a valid 6 digit pincode.")
            return
        if payment not in {"Netbanking", "Card", "Pay on Delivery", "UPI"}:
            self.write_error("Choose a payment option before placing the order.")
            return

        order_items = []
        total = 0
        order_id = None
        with get_connection() as connection:
            for raw_item in raw_items:
                product_id = str(raw_item.get("product_id", "")).strip()
                size = str(raw_item.get("size", "")).strip()
                color = str(raw_item.get("color", "")).strip()
                quantity = int(raw_item.get("qty", 0))
                if quantity < 1 or quantity > 20:
                    self.write_error("Choose a valid quantity.")
                    return
                product = connection.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
                if not product:
                    self.write_error("A product in your cart is no longer available.", 404)
                    return
                sizes = json.loads(product["sizes_json"])
                color_names = [item["name"] for item in json.loads(product["colors_json"])]
                if size not in sizes or color not in color_names:
                    self.write_error("One selected size or color is unavailable.")
                    return
                line_total = product["price"] * quantity
                total += line_total
                order_items.append((product, size, color, quantity))

            cursor = connection.execute(
                """
                INSERT INTO orders (user_id, total, phone, address_json, payment_method)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    user["id"],
                    total,
                    phone,
                    json.dumps({"house": house, "street": street, "pincode": pincode}),
                    payment,
                ),
            )
            order_id = cursor.lastrowid
            for product, size, color, quantity in order_items:
                connection.execute(
                    """
                    INSERT INTO order_items
                    (order_id, product_id, product_name, size, color, quantity, unit_price)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """,
                    (order_id, product["id"], product["name"], size, color, quantity, product["price"]),
                )
        email_status = send_order_confirmation(
            user["email"],
            {
                "id": order_id,
                "total": total,
                "payment": payment,
                "phone": phone,
                "address": {"house": house, "street": street, "pincode": pincode},
                "customer_name": user["name"],
            },
        )
        self.write_json(
            {
                "order": {
                    "id": order_id,
                    "total": total,
                    "status": "placed",
                    "email": user["email"],
                    "email_status": email_status,
                }
            },
            201,
        )


def run_server():
    init_database()
    port = int(sys.argv[1]) if len(sys.argv) > 1 and sys.argv[1].isdigit() else DEFAULT_PORT
    server = ThreadingHTTPServer((HOST, port), ThreadhausHandler)
    print(f"Threadhaus backend running at http://{HOST}:{port}/")
    print("Keep this window open while using the website.")
    print(f"Database: {DB_PATH}")
    server.serve_forever()


if __name__ == "__main__":
    if "--init-db" in sys.argv:
        init_database()
        print(DB_PATH)
    else:
        run_server()
