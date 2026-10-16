import sqlite3

con = sqlite3.connect("database/ativos.db")
cur = con.cursor()

colunas = [c[1] for c in cur.execute("PRAGMA table_info(ativos)")]
if "setor_id" not in colunas:
    cur.execute("ALTER TABLE ativos ADD COLUMN setor_id INTEGER REFERENCES setores(id)")
    cur.execute("CREATE INDEX IF NOT EXISTS ix_ativos_setor_id ON ativos (setor_id)")
    con.commit()
    print("Coluna setor_id adicionada.")
else:
    print("Coluna já existe, nada a fazer.")

con.close()