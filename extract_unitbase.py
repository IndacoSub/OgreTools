# extract_unitbase.py

import argparse
import csv
import os

START_OFFSET = 0x68
END_OFFSET   = 0x3C6E0
RECORD_SIZE  = 0x68

FULL_NAME_POS = 0x00
FULL_NAME_LEN = 0x1C

NICKNAME_POS = 0x1C
NICKNAME_LEN = 0x10


def decode_ascii(raw: bytes) -> str:
    return raw.split(b"\x00")[0].decode("utf-8", errors="ignore")


def decode_sjis(raw: bytes) -> str:
    return raw.split(b"\x00")[0].decode("shift_jis", errors="ignore")


def encode_ascii(text: str, length: int) -> bytes:
    raw = text.encode("utf-8", errors="ignore")
    return raw[:length].ljust(length, b"\x00")


def encode_sjis(text: str, length: int) -> bytes:
    raw = text.encode("shift_jis", errors="ignore")
    return raw[:length].ljust(length, b"\x00")


def extract_records(path_dat, path_csv, japanese=False):
    if not os.path.exists(path_dat):
        print(f"ERRORE: Il file DAT '{path_dat}' non esiste.")
        return

    rows = []

    with open(path_dat, "rb") as f:
        current_offset = START_OFFSET
        f.seek(current_offset)

        while current_offset < END_OFFSET:
            block = f.read(RECORD_SIZE)
            if len(block) < RECORD_SIZE:
                break

            if japanese:
                full_name = decode_sjis(block[FULL_NAME_POS:FULL_NAME_POS + FULL_NAME_LEN])
                nickname  = decode_sjis(block[NICKNAME_POS:NICKNAME_POS + NICKNAME_LEN])
            else:
                full_name = decode_ascii(block[FULL_NAME_POS:FULL_NAME_POS + FULL_NAME_LEN])
                nickname  = decode_ascii(block[NICKNAME_POS:NICKNAME_POS + NICKNAME_LEN])

            rows.append({
                "global_offset": f"0x{current_offset:X}",
                "full_name": full_name,
                "nickname": nickname,
            })

            current_offset += RECORD_SIZE

    with open(path_csv, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=["global_offset", "full_name", "nickname"])
        writer.writeheader()
        writer.writerows(rows)

    print(f"OK: Estratti {len(rows)} personaggi in '{path_csv}'.")


def repack_records(path_dat, path_csv, japanese=False):
    if not os.path.exists(path_csv):
        print(f"ERRORE: Il CSV '{path_csv}' non esiste.")
        return

    if not os.path.exists(path_dat):
        print(f"ERRORE: Il file DAT '{path_dat}' non esiste.")
        return

    edits = []
    with open(path_csv, "r", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                offset = int(row["global_offset"], 16)
            except ValueError:
                print(f"ERRORE: Offset non valido nel CSV: {row['global_offset']}")
                continue

            if offset < START_OFFSET or offset >= END_OFFSET:
                print(f"ERRORE: Offset fuori range: {row['global_offset']}")
                continue

            full_name = row["full_name"]
            nickname  = row["nickname"]

            edits.append((offset, full_name, nickname))

    with open(path_dat, "r+b") as f:
        for offset, full_name, nickname in edits:

            if japanese:
                f.seek(offset + FULL_NAME_POS)
                f.write(encode_sjis(full_name, FULL_NAME_LEN))

                f.seek(offset + NICKNAME_POS)
                f.write(encode_sjis(nickname, NICKNAME_LEN))
            else:
                f.seek(offset + FULL_NAME_POS)
                f.write(encode_ascii(full_name, FULL_NAME_LEN))

                f.seek(offset + NICKNAME_POS)
                f.write(encode_ascii(nickname, NICKNAME_LEN))

    print(f"OK: Modificati {len(edits)} personaggi nel DAT.")


def main():
    parser = argparse.ArgumentParser(description="Estrarre o reinserire nomi in unitbase.dat")

    parser.add_argument("--extract", action="store_true", help="Estrae i nomi in CSV")
    parser.add_argument("--repack", action="store_true", help="Reinserisce i nomi nel DAT")
    parser.add_argument("--dat", required=True, help="Percorso a unitbase.dat")
    parser.add_argument("--csv", required=True, help="Percorso al CSV")
    parser.add_argument("--japanese", action="store_true", help="Legge e scrive nomi giapponesi (Shift-JIS)")

    args = parser.parse_args()

    if args.extract:
        extract_records(args.dat, args.csv, args.japanese)
    elif args.repack:
        repack_records(args.dat, args.csv, args.japanese)
    else:
        print("ERRORE: Devi specificare --extract oppure --repack.")


if __name__ == "__main__":
    main()
