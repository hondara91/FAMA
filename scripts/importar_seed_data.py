"""
Importa los datos de seed_data/ a MongoDB.
Uso: python scripts/importar_seed_data.py
"""
import json
import os
import subprocess
import sys

COLECCIONES = [
    "usuarios",
    "compraventa",
    "ocio",
    "viviendas",
    "servicios",
    "foro_canales",
    "foro_posts",
    "foro_respuestas",
    "novedades",
    "reportes",
    "logs",
]

SEED_DIR = os.path.join(os.path.dirname(__file__), "seed_data")
CONTAINER = "fama_mongo1"
DB = "fama_db"


def importar_coleccion(coleccion):
    archivo = os.path.join(SEED_DIR, f"{coleccion}.json")
    if not os.path.exists(archivo):
        print(f"  [SKIP] {coleccion}: archivo no encontrado")
        return

    with open(archivo, encoding="utf-8") as f:
        datos = json.load(f)

    if not datos:
        print(f"  [SKIP] {coleccion}: sin datos")
        return

    result = subprocess.run(
        [
            "docker", "exec", "-i", CONTAINER,
            "mongoimport",
            "--db", DB,
            "--collection", coleccion,
            "--jsonArray",
            "--mode=upsert",
            "--upsertFields=_id",
        ],
        input=json.dumps(datos, ensure_ascii=False).encode("utf-8"),
        capture_output=True,
    )

    if result.returncode == 0:
        print(f"  [OK] {coleccion}: {len(datos)} documentos importados")
    else:
        print(f"  [ERROR] {coleccion}: {result.stderr.decode()}")


def main():
    print(f"Importando seed data en {CONTAINER}/{DB}...\n")
    for col in COLECCIONES:
        importar_coleccion(col)
    print("\nImportacion completada.")


if __name__ == "__main__":
    main()
