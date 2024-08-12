import sqlite3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

# Connect to SQLite database (creates a new database if it doesn't exist)
def get_db_connection():
    conn = sqlite3.connect('items.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create a table (run this once to set up your database)
def create_table():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        description TEXT,
        price REAL NOT NULL,
        tax REAL
    )
    ''')
    conn.commit()
    conn.close()

# Call the create_table function once to set up the database
create_table()

# Define the Pydantic model for an item
class Item(BaseModel):
    id: int = None
    name: str
    description: str = None
    price: float
    tax: float = None

# CRUD Operations
@app.post("/items/", response_model=Item)
async def create_item(item: Item):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('INSERT INTO items (name, description, price, tax) VALUES (?, ?, ?, ?)',
                   (item.name, item.description, item.price, item.tax))
    conn.commit()
    item.id = cursor.lastrowid
    conn.close()
    return item

@app.get("/items/", response_model=List[Item])
async def read_items():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items')
    items = cursor.fetchall()
    conn.close()
    return [dict(item) for item in items]

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM items WHERE id=?', (item_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Item not found")

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, updated_item: Item):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE items SET name=?, description=?, price=?, tax=? WHERE id=?',
                   (updated_item.name, updated_item.description, updated_item.price, updated_item.tax, item_id))
    conn.commit()
    conn.close()
    return updated_item

@app.delete("/items/{item_id}", response_model=dict)
async def delete_item(item_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM items WHERE id=?', (item_id,))
    conn.commit()
    conn.close()
    return {"message": "Item deleted"}


