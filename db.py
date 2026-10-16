
import sqlite3
import config


def conectar():
    con = sqlite3.connect(config.DB_PATH, timeout=10)
    con.execute("PRAGMA journal_mode=WAL")  # permite ler (dashboard) enquanto a esteira grava
    return con


def iniciar():
    with conectar() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS leituras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            qr TEXT, cor TEXT, produto TEXT, saida_prevista INTEGER
        );
        CREATE TABLE IF NOT EXISTS contagens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ts TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            saida INTEGER NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_contagens_ts ON contagens(ts);
        """)


def registrar_leitura(qr, cor, produto, saida_prevista):
    con = conectar()
    try:
        with con:
            con.execute("INSERT INTO leituras (qr, cor, produto, saida_prevista) VALUES (?,?,?,?)",
                        (qr, cor, produto, saida_prevista))
    finally:
        con.close()


def registrar_contagem(saida):
    con = conectar()
    try:
        with con:
            con.execute("INSERT INTO contagens (saida) VALUES (?)", (saida,))
    finally:
        con.close()
