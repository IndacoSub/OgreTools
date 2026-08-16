#!/usr/bin/env python3
# mastermind.py

import argparse
import subprocess
import sys
from pathlib import Path

CTPK_OFFSET = 0x80  # magic CTPK confermata

# ============================================================
#  TROVA PACCHETTI
# ============================================================

def find_ctpk_folder_candidates(root: Path):
    for ctpk_folder in root.rglob("00000000_ctpk"):
        if not ctpk_folder.is_dir():
            continue

        pngs = list(ctpk_folder.glob("*.png"))
        if not pngs:
            continue

        preferred = [p for p in pngs if "ie03o" in p.name]
        png = preferred[0] if preferred else pngs[0]

        arc_folder = ctpk_folder.parent
        yield (ctpk_folder, arc_folder, png)


# ============================================================
#  MATCH ARC ⇄ CARTELLA
# ============================================================

def find_corresponding_arc(root: Path, arc_folder: Path):
    print("\n[DEBUG] Cerco ARC corrispondente per:", arc_folder)

    folder_name = arc_folder.name
    print("[DEBUG] Nome cartella:", folder_name)

    if not folder_name.endswith("_arc"):
        print("[DEBUG] La cartella NON finisce con _arc → nessun ARC corrispondente.")
        return None

    expected_arc = folder_name.replace("_arc", ".arc")
    print("[DEBUG] Nome ARC atteso:", expected_arc)

    print("[DEBUG] Cerco nel root:", root)
    for arc in root.rglob("*.arc"):
        print("  [SCAN] Trovato:", arc)
        if arc.name == expected_arc:
            print("[DEBUG] MATCH trovato nel root:", arc)
            return arc

    print("[DEBUG] Cerco nella cartella superiore:", arc_folder.parent)
    for arc in arc_folder.parent.glob("*.arc"):
        print("  [SCAN] Trovato:", arc)
        if arc.name == expected_arc:
            print("[DEBUG] MATCH trovato nella cartella superiore:", arc)
            return arc

    print("[DEBUG] Ricerca globale del nome esatto:", expected_arc)
    for arc in root.rglob(expected_arc):
        print("[DEBUG] MATCH trovato globalmente:", arc)
        return arc

    print("[ERRORE] Nessun ARC trovato con nome:", expected_arc)
    return None


# ============================================================
#  CTPKTOOL
# ============================================================

def call_ctpktool(ctpktool_path: str, bin_path: Path, ctpk_folder: Path):
    cmd = [
        ctpktool_path,
        "-ivfd",
        str(bin_path),
        str(ctpk_folder)
    ]

    print("Eseguo ctpktool:", " ".join(cmd))

    res = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    print("=== STDOUT ===")
    print(res.stdout)

    print("=== STDERR ===")
    print(res.stderr)

    if res.returncode != 0:
        print("=== ERRORE: ctpktool ha restituito", res.returncode, "===")
        raise RuntimeError("ctpktool ha fallito")


# ============================================================
#  REPLACE CTPK IN ARC
# ============================================================

def replace_ctpk_in_arc(arc_path: Path, bin_path: Path):
    print(f"Sostituisco CTPK dentro {arc_path}")

    with open(arc_path, "rb") as f:
        arc = bytearray(f.read())

    with open(bin_path, "rb") as f:
        new_ctpk = f.read()

    if arc[CTPK_OFFSET:CTPK_OFFSET+4] != b"CTPK":
        raise RuntimeError(f"Magic CTPK non trovata a offset 0x{CTPK_OFFSET:X}")

    arc[CTPK_OFFSET:CTPK_OFFSET+len(new_ctpk)] = new_ctpk

    with open(arc_path, "wb") as f:
        f.write(arc)

    print("ARC aggiornato con successo:", arc_path)


# ============================================================
#  TROVA ESEGUIBILE
# ============================================================

def find_executable(name: str):
    p = Path(name)
    if p.exists():
        return str(p.resolve())

    from shutil import which
    w = which(name)
    if w:
        return w

    return None


# ============================================================
#  MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Mastermind: reinserisce PNG in .bin e ricostruisce .arc (multipli)."
    )

    parser.add_argument("--root", required=True, help="Directory radice degli ARC estratti")
    parser.add_argument("--ctpktool", default="", help="Percorso a ctpktool.exe (opzionale)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra cosa farebbe senza eseguire")

    args = parser.parse_args()

    root = Path(args.root)
    if not root.exists():
        print("Root non valida:", root)
        sys.exit(1)

    ctpktool_path = args.ctpktool or find_executable("ctpktool.exe") or find_executable("ctpktool")
    if not ctpktool_path:
        print("ctpktool.exe non trovato. Usa --ctpktool.")
        if not args.dry_run:
            sys.exit(1)

    # ============================================================
    #  GENERA PNG UNA SOLA VOLTA
    # ============================================================

    
    hissatsu_csv = Path("mossejap.csv")
    if not hissatsu_csv.exists():
        print("ATTENZIONE: hissatsu.csv non trovato, salto generazione PNG.")
    else:
        import csv

        print("Carico hissatsu.csv:", hissatsu_csv)

        with open(hissatsu_csv, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            for row in reader:
                offset = row["offset"].strip()
                name = row["name"].strip()

                print(f"\n=== Genero PNG per offset {offset} ({name}) ===")

                cmd = [
                    sys.executable,
                    "make_pngs.py",
                    "--offset", offset
                ]

                print("Eseguo:", " ".join(cmd))

                res = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True
                )

                if res.stdout.strip():
                    print(res.stdout.strip())
                if res.stderr.strip():
                    print("stderr:", res.stderr.strip())

                if res.returncode != 0:
                    print(f"ERRORE: make_pngs.py ha fallito per offset {offset}")
                    continue

    packages = list(find_ctpk_folder_candidates(root))

    if not packages:
        print("Nessun pacchetto valido trovato.")
        sys.exit(0)

    total = len(packages)
    print(f"\nTrovati {total} pacchetti da elaborare.\n")

    for idx, (ctpk_folder, arc_folder, png_path) in enumerate(packages, start=1):
        print("\n==============================================")
        print(f"[{idx}/{total}] Elaboro pacchetto:")
        print("  ctpk_folder:", ctpk_folder)
        print("  arc_folder:", arc_folder)
        print("  png:", png_path)
        print("==============================================\n")

        # trova bin
        bin_path = arc_folder / "00000000.bin"
        if not bin_path.exists():
            ctpk_file = arc_folder / "00000000.ctpk"
            if ctpk_file.exists():
                print("Trovato 00000000.ctpk → rinomino in 00000000.bin")
                ctpk_file.rename(bin_path)
            else:
                ctpk_list = list(arc_folder.glob("*.ctpk"))
                if ctpk_list:
                    print("Rinomino", ctpk_list[0], "→ 00000000.bin")
                    ctpk_list[0].rename(bin_path)
                else:
                    print("Nessun .bin o .ctpk trovato in", arc_folder)
                    print("SALTO questo pacchetto.")
                    continue

        print("BIN:", bin_path)

        # esegui ctpktool
        if args.dry_run:
            print("[DRY RUN] Avrei eseguito ctpktool")
        else:
            try:
                call_ctpktool(ctpktool_path, bin_path, ctpk_folder)
            except Exception as e:
                print("ERRORE ctpktool:", e)
                print("SALTO questo pacchetto.")
                continue

        # trova ARC originale
        arc_file = find_corresponding_arc(root, arc_folder)
        if not arc_file:
            print("ARC originale non trovato, ma ctpktool è stato eseguito.")
            print("SALTO questo pacchetto.")
            continue

        print("ARC originale:", arc_file)

        # sostituisci CTPK nell'ARC originale
        if args.dry_run:
            print("[DRY RUN] Avrei sostituito CTPK dentro", arc_file)
        else:
            try:
                replace_ctpk_in_arc(arc_file, bin_path)
            except Exception as e:
                print("ERRORE sostituzione CTPK:", e)
                print("SALTO questo pacchetto.")
                continue

        print(f"✔ [{idx}/{total}] Pacchetto completato:", arc_folder)

    print("\nFatto. Tutti i pacchetti elaborati.")


if __name__ == "__main__":
    main()