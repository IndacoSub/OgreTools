# make_pngs.py

import csv
import argparse
import subprocess
import sys
from pathlib import Path

FINAL_MOVES_CSV = "final_moves.csv"
MOSSE_JAP_CSV = "mossejap.csv"
WRITE_TEXT_PY = "write_text.py"

# === FUNZIONI DI CARICAMENTO ===

def load_final_moves(path):
    data = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        for row in reader:
            if len(row) < 4:
                continue
            offset, mid, name, flag = row[0].strip(), row[1].strip(), row[2].strip(), row[3].strip()
            data[offset] = (mid, name, flag)
    return data

def load_mosse_jap(path):
    data = {}
    with open(path, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            offset = row[0].strip()
            name = row[1].strip()
            data[offset] = name
    return data

# === FUNZIONE PER CHIAMARE write_text.py ===

def call_write_text(text, mode, output_path):
    cmd = [
        sys.executable,
        WRITE_TEXT_PY,
        "-t", text,
        "-m", str(mode),
        "-o", output_path
    ]
    
    print("Eseguo:", " ".join(cmd))

    try:
        res = subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        print(res.stdout.strip())
    except subprocess.CalledProcessError as e:
        print("Errore durante l'esecuzione di write_text.py:", e.stderr.strip(), file=sys.stderr)
        raise

def main():
    parser = argparse.ArgumentParser(description="Scrive PNG di testo (mode0/1/2) ignorando offset e CSV.")
    parser.add_argument("--output", default="", help="Directory base opzionale.")
    args = parser.parse_args()

    # Testo fisso
    testo = "Buona la pizza"

    # Percorsi di output (se l’utente non specifica --output, usa nomi locali)
    if args.output:
        base = args.output.rstrip("/\\") + "/"
        Path(base).mkdir(parents=True, exist_ok=True)
        out_mode0 = f"{base}mode0.png"
        out_mode1 = f"{base}mode1.png"
        out_mode2 = f"{base}mode2.png"
    else:
        out_mode0 = "mode0.png"
        out_mode1 = "mode1.png"
        out_mode2 = "mode2.png"

    # Genera i file ignorando tutto il resto
    try:
        call_write_text(testo, 0, out_mode0)
        call_write_text(testo, 1, out_mode1)
        call_write_text(testo, 2, out_mode2)
    except Exception as e:
        print("Errore durante la generazione dei file:", e, file=sys.stderr)
        sys.exit(1)

    print("Tutti i file generati con successo:")
    print(" ", out_mode0)
    print(" ", out_mode1)
    print(" ", out_mode2)


if __name__ == "__main__":
    main()
