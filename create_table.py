import sqlite3

conn = sqlite3.connect('db.sqlite3')
conn.execute('''
CREATE TABLE svodnaya_raskhod_dokhod_po_dnyam (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    objekt_id INTEGER NOT NULL,
    data DATE NOT NULL,
    raskhod DECIMAL(12,2) DEFAULT 0,
    dokhod DECIMAL(12,2) DEFAULT 0,
    balans DECIMAL(12,2) DEFAULT 0,
    UNIQUE(objekt_id, data)
)
''')
conn.commit()
conn.close()
print('Table created successfully')