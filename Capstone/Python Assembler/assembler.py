import sys
import re

COMP_TABLE = {
    "0":   "0101010", "1":   "0111111", "-1":  "0111010",
    "D":   "0001100", "A":   "0110000", "M":   "1110000",
    "!D":  "0001101", "!A":  "0110001", "!M":  "1110001",
    "-D":  "0001111", "-A":  "0110011", "-M":  "1110011",
    "D+1": "0011111", "A+1": "0110111", "M+1": "1110111",
    "D-1": "0001110", "A-1": "0110010", "M-1": "1110010",
    "D+A": "0000010", "D+M": "1000010",
    "D-A": "0010011", "D-M": "1010011",
    "A-D": "0000111", "M-D": "1000111",
    "D&A": "0000000", "D&M": "1000000",
    "D|A": "0010101", "D|M": "1010101",
}

DEST_TABLE = {
    "":    "000", "M":   "001", "D":   "010", "MD":  "011",
    "A":   "100", "AM":  "101", "AD":  "110", "AMD": "111",
}

JUMP_TABLE = {
    "":    "000", "JGT": "001", "JEQ": "010", "JGE": "011",
    "JLT": "100", "JNE": "101", "JLE": "110", "JMP": "111",
}

VALID_SYMBOL = re.compile(r"^[A-Za-z_.$:][A-Za-z0-9_.$:]*$")


def build_default_symbols():
    symbols = {
        "SP": 0, "LCL": 1, "ARG": 2, "THIS": 3, "THAT": 4,
        "SCREEN": 16384, "KBD": 24576,
    }
    for i in range(16):
        symbols[f"R{i}"] = i
    return symbols


def assemble(input_path):
    symbols = build_default_symbols()
    cleaned_lines = []  # list of (original_line_num, instruction_text)
    rom_address = 0

    with open(input_path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    # Pass 1: strip comments/whitespace and record (LABEL) positions
    for line_num, raw in enumerate(raw_lines, start=1):
        code = raw.split("//")[0].strip()
        if not code:
            continue

        if code.startswith("(") and code.endswith(")"):
            label = code[1:-1].strip()
            if not VALID_SYMBOL.match(label):
                print(f"Line {line_num}: invalid instruction")
                sys.exit(1)
            symbols[label] = rom_address
        else:
            cleaned_lines.append((line_num, code))
            rom_address += 1

    # Pass 2: translate instructions to 16-bit binary
    next_ram_address = 16
    machine_code = []

    for line_num, code in cleaned_lines:
        # A-instruction
        if code.startswith("@"):
            symbol = code[1:]
            if not symbol:
                print(f"Line {line_num}: invalid instruction")
                sys.exit(1)

            if symbol.isdigit():
                val = int(symbol)
                if val < 0 or val > 32767:
                    print(f"Line {line_num}: invalid instruction")
                    sys.exit(1)
            else:
                if not VALID_SYMBOL.match(symbol):
                    print(f"Line {line_num}: invalid instruction")
                    sys.exit(1)
                if symbol not in symbols:
                    symbols[symbol] = next_ram_address
                    next_ram_address += 1
                val = symbols[symbol]

            machine_code.append(f"0{val:015b}")

        # C-instruction
        else:
            if "(" in code or ")" in code:
                print(f"Line {line_num}: invalid instruction")
                sys.exit(1)

            dest, rest = ("", code)
            if "=" in code:
                parts = code.split("=")
                if len(parts) != 2 or not parts[0].strip():
                    print(f"Line {line_num}: invalid instruction")
                    sys.exit(1)
                dest, rest = parts[0].strip(), parts[1].strip()

            comp, jump = (rest, "")
            if ";" in rest:
                parts = rest.split(";")
                if len(parts) != 2 or not parts[1].strip():
                    print(f"Line {line_num}: invalid instruction")
                    sys.exit(1)
                comp, jump = parts[0].strip(), parts[1].strip()

            # Remove internal spaces inside expressions like "D + 1"
            comp = comp.replace(" ", "")

            if dest not in DEST_TABLE or comp not in COMP_TABLE or jump not in JUMP_TABLE:
                print(f"Line {line_num}: invalid instruction")
                sys.exit(1)

            binary = "111" + COMP_TABLE[comp] + DEST_TABLE[dest] + JUMP_TABLE[jump]
            machine_code.append(binary)

    output_path = input_path.rsplit(".", 1)[0] + ".hack"
    with open(output_path, "w", encoding="utf-8") as out_f:
        out_f.write("\n".join(machine_code) + "\n")
    print(f"Successfully assembled {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python assembler.py <file.asm>")
        sys.exit(1)
    assemble(sys.argv[1])