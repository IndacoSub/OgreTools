# extract_arcs.py

import argparse
import subprocess
import sys
from pathlib import Path
import shutil
import logging

PLUGIN_ARC = "db8c2deb-f11d-43c8-bb9e-e271408fd896"

def run_export(kuriimu, file, plugin=None):
    cmd = [kuriimu, "export", str(file)]
    if plugin:
        cmd += ["-p", plugin]

    cwd = str(Path(kuriimu).parent)

    logging.info("Eseguo: %s", " ".join(cmd))
    p = subprocess.run(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=cwd
    )

    logging.info("stdout: %s", p.stdout.strip())
    logging.info("stderr: %s", p.stderr.strip())
    return p.returncode

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--kuriimu", required=True)
    parser.add_argument("-i", "--input", required=True)
    args = parser.parse_args()

    kuriimu = args.kuriimu
    base = Path(args.input)

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    arcs = sorted(base.glob("*.arc"))
    logging.info(f"Trovati {len(arcs)} file .arc")

    for arc in arcs:
        logging.info(f"\n=== Estraggo {arc.name} ===")

        out_dir = arc.parent / (arc.stem + "_arc")

        rc = run_export(kuriimu, arc, PLUGIN_ARC)
        if rc != 0:
            logging.error(f"ERRORE: export fallito per {arc}")
            continue

        if not out_dir.exists():
            logging.error(f"ERRORE: Kuriimu NON ha creato {out_dir}")
            sys.exit(1)

        bins = list(out_dir.glob("*.bin"))
        if not bins:
            logging.info("Nessun .bin trovato.")
            continue

        ctpk_files = []
        for b in bins:
            ctpk = b.with_suffix(".ctpk")
            shutil.move(str(b), str(ctpk))
            ctpk_files.append(ctpk)
            logging.info(f"Rinominato {b.name} → {ctpk.name}")

        for ctpk in ctpk_files:
            logging.info(f"Export CTPK {ctpk.name}")
            rc = run_export(kuriimu, ctpk, None)  # <<< NESSUN PLUGIN
            if rc != 0:
                logging.error(f"ERRORE: export fallito per {ctpk}")

if __name__ == "__main__":
    main()
