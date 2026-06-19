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
import sys
from email.message import EmailMessage
import datetime

# --- MONGODB CLOUD DATABASE CONNECTION ---
from pymongo import MongoClient

BASE_DIR = Path(_file_).resolve().parent
DATA_DIR = BASE_DIR / "data"
CONFIRMATION_DIR = DATA_DIR / "order_confirmations"
HOST = "0.0.0.0"  # Opened up so Render can broadcast it live
DEFAULT_PORT = 8000

# Read the connection string from Render environment settings
MONGO_URI = os.environ.get("MONGO_URI")

if MONGO_URI:
    # Production: When running live on Render cloud
    client = MongoClient(MONGO_URI)
    db = client["threadhaus_shop"]
else:
    # Local Fallback: If running on your laptop
    client = MongoClient("mongodb://localhost:27017/")
    db = client["threadhaus_shop_local"]

# Setup collections instead of SQL tables
users_collection = db["users"]
sessions_collection = db["sessions"]
products_collection = db["products"]
orders_collection = db["orders"]

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
        "ty…