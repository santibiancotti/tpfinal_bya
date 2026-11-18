"""Comprueba los XLSX versionados; permite actualizar su manifiesto tras renovarlos."""
import argparse
from hashlib import file_digest
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
CARPETA_DATOS = RAIZ / "data"
MANIFIESTO = CARPETA_DATOS / "SHA256SUMS"


def hashes(carpeta):
    resultado = {}
    for archivo in sorted(carpeta.rglob("*.xlsx")):
        if archivo.name.startswith("~$"):
            continue
        with archivo.open("rb") as contenido:
            resultado[archivo.relative_to(carpeta).as_posix()] = file_digest(contenido, "sha256").hexdigest()
    if not resultado:
        raise ValueError(f"No hay archivos XLSX en {carpeta}")
    return resultado


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--originales", type=Path, help="Carpeta opcional con las fuentes originales; solo se lee.")
    parser.add_argument("--actualizar-manifiesto", action="store_true",
                        help="Regenera SHA256SUMS para publicar fuentes nuevas ya revisadas.")
    args = parser.parse_args()
    actuales = hashes(CARPETA_DATOS)
    if args.originales is not None and actuales != hashes(args.originales):
        raise SystemExit("ERROR: las copias no coinciden con las fuentes originales.")
    if args.actualizar_manifiesto:
        MANIFIESTO.write_text("".join(f"{sha}  {nombre}\n" for nombre, sha in actuales.items()),
                             encoding="utf-8", newline="\n")
    esperados = dict(linea.split("  ", 1)[::-1] for linea in MANIFIESTO.read_text(encoding="utf-8").splitlines())
    if actuales != esperados:
        diferencias = sorted(nombre for nombre in actuales.keys() | esperados.keys()
                             if actuales.get(nombre) != esperados.get(nombre))
        raise SystemExit("ERROR: revisar fuentes y manifiesto: " + ", ".join(diferencias))
    print(f"OK: {len(actuales)} XLSX coinciden con SHA256SUMS."
          + (" Copias idénticas a los originales." if args.originales is not None else ""))


if __name__ == "__main__":
    main()
