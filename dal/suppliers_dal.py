import json
import os
from datetime import datetime

DATA_FILE = "data/store.json"

def load_data():
    if not os.path.exists(DATA_FILE):
        return {
            "Suppliers": [],
            "Suppliers_catalog": [],
            "Supplier_invitations": [],
            "Products": []
        }
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
