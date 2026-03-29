import json
import csv
import os

DATA_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'static', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

TXT_FILE  = os.path.join(DATA_DIR, 'productos.txt')
JSON_FILE = os.path.join(DATA_DIR, 'productos.json')
CSV_FILE  = os.path.join(DATA_DIR, 'productos.csv')


# ── TXT ──────────────────────────────────────────
def guardar_txt(registro: dict):
    with open(TXT_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{registro['nombre']}|{registro['cantidad']}|{registro['precio']}\n")


def leer_txt() -> list:
    if not os.path.exists(TXT_FILE):
        return []
    datos = []
    with open(TXT_FILE, 'r', encoding='utf-8') as f:
        for linea in f:
            partes = linea.strip().split('|')
            if len(partes) == 3:
                datos.append({'nombre': partes[0], 'cantidad': partes[1], 'precio': partes[2]})
    return datos


# ── JSON ─────────────────────────────────────────
def guardar_json(registro: dict):
    datos = leer_json()
    datos.append(registro)
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)


def leer_json() -> list:
    if not os.path.exists(JSON_FILE):
        return []
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# ── CSV ──────────────────────────────────────────
def guardar_csv(registro: dict):
    existe = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['nombre', 'cantidad', 'precio'])
        if not existe:
            writer.writeheader()
        writer.writerow(registro)


def leer_csv() -> list:
    if not os.path.exists(CSV_FILE):
        return []
    with open(CSV_FILE, 'r', encoding='utf-8') as f:
        return list(csv.DictReader(f))
