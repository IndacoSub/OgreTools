# command_extract.py

import argparse
import csv

START_OFFSET = 0xCC0
JAPANESE_OFFSET = 0x2000
JAPANESE = True

LINE_SIZE = 0x10

# elementi giapponesi: 火 風 山 林
JP_ELEMENTS = {0x95, 0x97, 0x8E, 0x89}

def decode(raw: bytes) -> str:
    return raw.decode("shift_jis", errors="ignore").replace("\x00", "").rstrip()

def is_valid_attribute(raw: bytes) -> bool:
    for i in range(len(raw)):
        if raw[i] == 0x5B:  # '['
            if i+1 < len(raw) and raw[i+1] in JP_ELEMENTS:
                for j in range(i+1, min(i+0x10, len(raw))):
                    if raw[j] == 0x5D:
                        return True
    return False

def is_valid_name(raw: bytes) -> bool:
    txt = decode(raw)
    if not txt:
        return False
    if "[" in txt or "]" in txt:
        return False
    return True

def extract_hissatsu(path_dat: str, path_csv: str) -> None:
    out = []
    seen = set()

    base = JAPANESE_OFFSET if JAPANESE else START_OFFSET

    with open(path_dat, "rb") as f:
        f.seek(0, 2)
        file_size = f.tell()

        pos = base

        while pos + LINE_SIZE <= file_size:
            f.seek(pos)
            raw = f.read(LINE_SIZE)

            if not is_valid_attribute(raw):
                pos += LINE_SIZE
                continue

            name_offset = None
            name = None

            for back in (0x20, 0x10, 0x00):
                off = pos - back
                if off < base:
                    continue

                f.seek(off)
                raw_name = f.read(LINE_SIZE)

                if is_valid_name(raw_name):
                    name_offset = off
                    name = decode(raw_name)
                    break

            if not name:
                pos += LINE_SIZE
                continue

            if name_offset not in seen:
                out.append(f"0x{name_offset:X},{name}")
                seen.add(name_offset)

            pos += LINE_SIZE

    with open(path_csv, "w", encoding="utf-8") as o:
        o.write("offset,name\n")
        for line in out:
            o.write(line + "\n")

    print(f"CSV salvato: {path_csv}")
    print(f"Totale estratti: {len(out)}")


# ------------------------------------------------------------
# 🔥 MODALITÀ REPACK
# ------------------------------------------------------------

def repack_hissatsu(path_dat: str, path_csv: str, path_out: str) -> None:
    # carica CSV
    entries = []
    with open(path_csv, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        next(reader)  # skip header
        for row in reader:
            offset = int(row[0], 16)
            name = row[1]
            entries.append((offset, name))

    # carica file dat
    with open(path_dat, "rb") as f:
        data = bytearray(f.read())

    # applica patch
    for offset, name in entries:
        # azzera 0x20 byte
        for i in range(0x20):
            data[offset + i] = 0x00

        # scrivi stringa shift-jis
        encoded = name.encode("shift_jis")
        max_len = 0x20
        if len(encoded) > max_len:
            encoded = encoded[:max_len]

        data[offset:offset+len(encoded)] = encoded

        print(f"Patch: 0x{offset:X} → {name}")

    # salva nuovo file
    with open(path_out, "wb") as f:
        f.write(data)

    print(f"Repack completato → {path_out}")


def main():
    parser = argparse.ArgumentParser(description="Extract/Repack JP Hissatsu")
    parser.add_argument("--extract-hissatsu", action="store_true")
    parser.add_argument("--repack-hissatsu", action="store_true")
    parser.add_argument("--dat", required=True)
    parser.add_argument("--csv")
    parser.add_argument("--out")
    args = parser.parse_args()

    if args.extract_hissatsu:
        extract_hissatsu(args.dat, args.csv)
    elif args.repack_hissatsu:
        repack_hissatsu(args.dat, args.csv, args.out)
    else:
        print("Use --extract-hissatsu or --repack-hissatsu")


if __name__ == "__main__":
    main()
