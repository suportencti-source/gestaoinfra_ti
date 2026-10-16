import sqlite3

conn = sqlite3.connect('database/ativos.db')
try:
    conn.execute("ALTER TABLE ping_hosts ADD COLUMN tipo VARCHAR(20) NOT NULL DEFAULT 'PC'")
    conn.commit()
    print('ok: coluna tipo criada')
except sqlite3.OperationalError as e:
    print('erro:', e)
finally:
    conn.close()

conn = sqlite3.connect('database/ativos.db')
print(conn.execute('PRAGMA table_info(ping_hosts)').fetchall())
conn.close()