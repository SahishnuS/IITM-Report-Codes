"""
TCAM Rule Loader — BRAM .mem File Generator  (ternary / per-segment encoding)
==============================================================================

TCAM Configuration
──────────────────
  Rule width    : N bits  (e.g. 144)
  Num rules     : M       (e.g. 1012)
  BRAM size     : BRAM_DEPTH × BRAM_WIDTH  (e.g. 512 × 72)
  Segment width : log2(BRAM_DEPTH)         (e.g. log2(512) = 9 bits)
  Num banks     : ceil(N / segment_width)  (per rank)
  Num ranks     : ceil(M / BRAM_WIDTH)

Ternary Encoding — Per-Segment Expansion
─────────────────────────────────────────
Rules may contain don't-care bits ('*', 'x', 'X', '?').  Rather than
expanding the *whole* rule into 2^(total_dc) binary variants (catastrophically
expensive for 25 don't-cares), this encoder expands each *segment* separately:

  • Split the ternary rule into segments of `segment_width` bits.
  • For each segment, enumerate only the 2^(dc_in_that_segment) matching
    addresses (typically 1–4 per segment for typical rules).
  • Set bit (rule_index % BRAM_WIDTH) at every matching address in that
    bank's BRAM.

Complexity comparison (1012 rules, 25 avg DCs, 144-bit rule, 9-bit segments):
  Old whole-rule expansion : 1012 × 2^25  ≈ 34 billion ops   (~3.6 days)
  New per-segment expansion : 1012 × 16 banks × ~3 addrs/seg ≈ 48 K ops  (<1 s)

Hardware match condition
────────────────────────
A rule R matches input I when, for EVERY bank b:

    BRAM[rank][b][ I_segment_b ]  has bit (R % BRAM_WIDTH) set

The BRAM stores exactly the set of input addresses that satisfy the ternary
match for each segment independently:

    (I_seg_b  XOR  data_seg_b)  AND  mask_seg_b  ==  0

Output files
────────────
  mem_<rank>_<bank>.mem   (1-indexed for both rank and bank)

Each line is a BRAM_WIDTH-bit binary string (or hex) for one BRAM address.
Dense output : one line per address (0 … BRAM_DEPTH-1).
Sparse output: only non-zero addresses, each prefixed with @<hex_addr>.

Input file format
─────────────────
  • One rule per line.
  • Spaces allowed for readability (stripped before processing).
  • Lines starting with '#' are comments.
  • Don't-care characters: '*', 'x', 'X', '?'  (all treated identically).
  • Example:
        1**0 *1*0 00*1        (spaces stripped → "1**0*1*000*1")
"""

import math
import os
import itertools
import time


# ══════════════════════════════════════════════════════════════════════════════
# Parsing
# ══════════════════════════════════════════════════════════════════════════════

def parse_rules(filepath: str) -> list[str]:
    """
    Read ternary rules from *filepath*.

    Returns a list of rule strings with spaces stripped and all don't-care
    variants normalised to '*'.  Length validation happens in
    build_bram_memories().
    """
    rules = []
    with open(filepath, "r") as fh:
        for lineno, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            bits = line.replace(" ", "")
            bits = bits.replace('x', '*').replace('X', '*').replace('?', '*')
            if not all(c in "01*" for c in bits):
                raise ValueError(
                    f"Line {lineno}: invalid character in rule '{line}'. "
                    "Only '0', '1', and don't-care ('*'/'x'/'X'/'?') are allowed."
                )
            rules.append(bits)
    return rules


# ══════════════════════════════════════════════════════════════════════════════
# Segment helpers
# ══════════════════════════════════════════════════════════════════════════════

def split_into_segments(rule_bits: str, segment_width: int, num_banks: int) -> list[str]:
    """
    Split *rule_bits* (ternary string, may contain '*') into *num_banks*
    segments of *segment_width* bits each.

    The final segment is left-padded with '0' (care bits, not don't-cares)
    when the rule width is not an exact multiple of segment_width.
    """
    segments = []
    for b in range(num_banks):
        start = b * segment_width
        chunk = rule_bits[start : start + segment_width]
        if not chunk:
            chunk = '0' * segment_width
        elif len(chunk) < segment_width:
            chunk = '0' * (segment_width - len(chunk)) + chunk   # left-pad with zeros
        segments.append(chunk)
    return segments


def segment_matching_addresses(seg: str) -> list[int]:
    """
    Return every integer address matched by the ternary segment *seg*.

    For k don't-care bits this produces 2^k integers; for a fully-specified
    segment it returns a single-element list.

    Examples:
        '10*1'       →  [9, 11]   (binary 1001, 1011)
        '000000000'  →  [0]
        '***'        →  [0,1,2,3,4,5,6,7]
    """
    dc_positions = [i for i, c in enumerate(seg) if c == '*']
    if not dc_positions:
        return [int(seg, 2)]

    addrs = []
    for combo in itertools.product('01', repeat=len(dc_positions)):
        chars = list(seg)
        for pos, bit in zip(dc_positions, combo):
            chars[pos] = bit
        addrs.append(int(''.join(chars), 2))
    return addrs


# ══════════════════════════════════════════════════════════════════════════════
# Core BRAM builder
# ══════════════════════════════════════════════════════════════════════════════

def build_bram_memories(
    rules: list[str],
    rule_width: int,
    bram_depth: int,
    bram_width: int,
) -> tuple[dict, int, int, int]:
    """
    Build BRAM memory contents using per-segment ternary expansion.

    For each ternary rule at index *rule_idx*:
      • Split into segments (preserving '*' characters).
      • For each bank, expand only *that* segment's don't-cares to get the
        set of matching addresses (2^k_b entries, k_b = DCs in segment b).
      • Set bit (rule_idx % bram_width) at every matching address.

    All addresses produced for a given rule share the same bit position,
    preserving the correct rule index regardless of don't-care count.

    Returns
    -------
    memories      : dict[(rank, bank)] → list[int] of length bram_depth
    num_ranks     : int
    num_banks     : int
    segment_width : int
    """
    if bram_depth <= 0 or (bram_depth & (bram_depth - 1)) != 0:
        raise ValueError(f"BRAM depth {bram_depth} must be a positive power of 2.")

    segment_width = int(math.log2(bram_depth))
    num_banks     = math.ceil(rule_width / segment_width)
    num_ranks     = math.ceil(len(rules) / bram_width)

    print(f"\n{'='*62}")
    print(f"  TCAM Configuration")
    print(f"{'='*62}")
    print(f"  Rule width         : {rule_width} bits")
    print(f"  Number of rules    : {len(rules)}")
    print(f"  BRAM size          : {bram_depth} × {bram_width}")
    print(f"  Segment width      : {segment_width} bits  (= log2({bram_depth}))")
    print(f"  Banks per rank     : {num_banks}")
    print(f"  Number of ranks    : {num_ranks}")
    print(f"  Total BRAMs        : {num_banks * num_ranks}")
    print(f"  Encoding           : per-segment ternary expansion")
    print(f"{'='*62}\n")

    # Initialise all BRAM memories to 0
    memories: dict[tuple[int, int], list[int]] = {
        (rank, bank): [0] * bram_depth
        for rank in range(num_ranks)
        for bank in range(num_banks)
    }

    t0 = time.perf_counter()
    total_writes = 0

    for rule_idx, rule_bits in enumerate(rules):
        if len(rule_bits) != rule_width:
            raise ValueError(
                f"Rule {rule_idx + 1} has {len(rule_bits)} bits, "
                f"expected {rule_width}."
            )

        rank    = rule_idx // bram_width
        bit_pos = rule_idx %  bram_width
        bitmask = 1 << bit_pos

        segments = split_into_segments(rule_bits, segment_width, num_banks)

        for bank_idx, seg in enumerate(segments):
            for addr in segment_matching_addresses(seg):
                memories[(rank, bank_idx)][addr] |= bitmask
                total_writes += 1

    elapsed = time.perf_counter() - t0
    print(f"  Encoding complete   : {elapsed * 1000:.1f} ms")
    print(f"  Total BRAM writes   : {total_writes:,}")
    print(f"  Avg writes per rule : {total_writes / len(rules):.1f}\n")

    return memories, num_ranks, num_banks, segment_width


# ══════════════════════════════════════════════════════════════════════════════
# File writer
# ══════════════════════════════════════════════════════════════════════════════

def write_mem_files(
    memories: dict[tuple[int, int], list[int]],
    num_ranks: int,
    num_banks: int,
    bram_depth: int,
    bram_width: int,
    output_dir: str,
    output_format: str = "binary",  # "binary" or "hex"
    sparse: bool = False,
) -> None:
    """
    Write one .mem file per (rank, bank) pair.

    File naming  : mem_<rank>_<bank>.mem  (1-indexed)
    Dense mode   : one line per address 0 … bram_depth-1
    Sparse mode  : only non-zero addresses, prefixed with @<hex_address>
    """
    os.makedirs(output_dir, exist_ok=True)
    hex_addr_digits = math.ceil(math.log2(bram_depth) / 4)
    hex_data_digits = bram_width // 4

    for rank in range(num_ranks):
        for bank in range(num_banks):
            filename = f"mem_{rank + 1}_{bank + 1}.mem"
            filepath = os.path.join(output_dir, filename)
            mem = memories[(rank, bank)]

            with open(filepath, "w") as fh:
                for addr in range(bram_depth):
                    val = mem[addr]
                    if sparse and val == 0:
                        continue

                    if output_format == "hex":
                        data_str = format(val, f"0{hex_data_digits}x")
                    else:
                        data_str = format(val, f"0{bram_width}b")

                    if sparse:
                        fh.write(f"@{addr:0{hex_addr_digits}x} {data_str}\n")
                    else:
                        fh.write(data_str + "\n")

            print(f"  Written: {filepath}")


# ══════════════════════════════════════════════════════════════════════════════
# Verification helper
# ══════════════════════════════════════════════════════════════════════════════

def verify_and_print(
    rules: list[str],
    memories: dict,
    num_ranks: int,
    num_banks: int,
    bram_depth: int,
    bram_width: int,
    segment_width: int,
    rule_width: int,
    max_rules: int = 20,
) -> None:
    """
    Print a human-readable table of rules → BRAM placements.
    Capped at *max_rules* to avoid flooding the terminal.
    """
    show = min(len(rules), max_rules)
    print(f"\nVerification — first {show} rule(s) and their BRAM placements:")
    print("─" * 80)

    for rule_idx, rule_bits in enumerate(rules[:show]):
        rank    = rule_idx // bram_width
        bit_pos = rule_idx %  bram_width
        dc_count = rule_bits.count('*')

        print(f"\n  Rule {rule_idx + 1:>4d} : {rule_bits}")
        print(f"           rank={rank + 1}  bit_pos={bit_pos}  don't-cares={dc_count}")

        segments = split_into_segments(rule_bits, segment_width, num_banks)
        for b_idx, seg in enumerate(segments):
            addrs = segment_matching_addresses(seg)
            preview = addrs[:8]
            suffix  = "…" if len(addrs) > 8 else ""
            print(f"    Bank {b_idx + 1:>2d}: seg={seg!r}  "
                  f"→ {len(addrs)} addr(s): {preview}{suffix}")

    if len(rules) > max_rules:
        print(f"\n  … ({len(rules) - max_rules} more rules not shown)")
    print("─" * 80)


# ══════════════════════════════════════════════════════════════════════════════
# Built-in self-test
# ══════════════════════════════════════════════════════════════════════════════

def self_test() -> None:
    """
    Reproduce the canonical worked example and assert exact bit patterns.

    BRAM 512×72, rule_width=32, segments = 9+9+9+5

    Rule 1 (idx 0): 00000000000000000000000000000000
    Rule 2 (idx 1): 00000000000000000000000000000001
    Rule 3 (idx 2): 000000001_000000000_000000001_00001
    Rule 4 (idx 3): 0000000000000000000000000000000*

    Expected (only non-zero addresses):
      Mem(1,1): addr 0 → bits {0,1,3}   addr 1 → bits {2}
      Mem(1,2): addr 0 → bits {0,1,2,3}
      Mem(1,3): addr 0 → bits {0,1,3}   addr 1 → bits {2}
      Mem(1,4): addr 0 → bits {0,3}     addr 1 → bits {1,2,3}
    """
    print("\n" + "=" * 62)
    print("  Built-in self-test")
    print("=" * 62)

    rules = [
        "00000000000000000000000000000000",
        "00000000000000000000000000000001",
        "000000001" + "000000000" + "000000001" + "00001",
        "0000000000000000000000000000000*",
    ]

    mems, nr, nb, sw = build_bram_memories(rules, 32, 512, 72)

    expected = {
        (0, 0, 0): 0b1011,
        (0, 0, 1): 0b0100,
        (0, 1, 0): 0b1111,
        (0, 2, 0): 0b1011,
        (0, 2, 1): 0b0100,
        (0, 3, 0): 0b1001,
        (0, 3, 1): 0b1110,
    }

    all_pass = True

    for (rank, bank, addr), exp in expected.items():
        got = mems[(rank, bank)][addr]
        ok  = got == exp
        all_pass = all_pass and ok
        print(f"  Mem({rank+1},{bank+1}) addr {addr}: "
              f"expected {exp:04b}  got {got:04b}  {'✔' if ok else '✘'}")

    # Verify all other addresses are zero
    for (rank, bank), mem in mems.items():
        for addr, val in enumerate(mem):
            if (rank, bank, addr) not in expected and val != 0:
                print(f"  ✘ Unexpected non-zero: Mem({rank+1},{bank+1}) addr {addr} = {val:b}")
                all_pass = False

    result = "ALL PASS ✔" if all_pass else "FAILURES ✘"
    print(f"\n  {result}\n")
    if not all_pass:
        raise AssertionError("Self-test failed — see output above.")


# ══════════════════════════════════════════════════════════════════════════════
# Interactive helpers
# ══════════════════════════════════════════════════════════════════════════════

def input_int(prompt: str, default: int = None, min_val: int = None) -> int:
    while True:
        display = f"{prompt} [{default}]: " if default is not None else f"{prompt}: "
        raw = input(display).strip()
        if raw == "" and default is not None:
            return default
        try:
            val = int(raw)
            if min_val is not None and val < min_val:
                print(f"  ✖  Value must be >= {min_val}.")
                continue
            return val
        except ValueError:
            print("  ✖  Please enter a valid integer.")


def input_str(prompt: str, default: str = None) -> str:
    display = f"{prompt} [{default}]: " if default is not None else f"{prompt}: "
    raw = input(display).strip()
    return raw if raw else (default or "")


def input_bool(prompt: str, default: bool = False) -> bool:
    hint = "Y/n" if default else "y/N"
    while True:
        raw = input(f"{prompt} ({hint}): ").strip().lower()
        if raw == "":
            return default
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        print("  ✖  Please enter 'y' or 'n'.")


def input_choice(prompt: str, choices: list[str], default: str = None) -> str:
    options = "/".join(c.upper() if c == default else c for c in choices)
    while True:
        raw = input(f"{prompt} ({options}): ").strip().lower()
        if raw == "" and default is not None:
            return default
        if raw in choices:
            return raw
        print(f"  ✖  Please enter one of: {', '.join(choices)}")


# ══════════════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    print("=" * 62)
    print("    TCAM Rule Loader — BRAM .mem File Generator")
    print("    (per-segment ternary encoding, no combinatorial explosion)")
    print("=" * 62)
    print("Press Enter to accept the default value shown in [brackets].\n")

    if input_bool("Run built-in self-test first?", default=False):
        self_test()

    # Input file
    while True:
        rules_file = input_str("Path to rules file (e.g. rules.txt)")
        if os.path.isfile(rules_file):
            break
        print(f"  ✖  File not found: '{rules_file}'. Please try again.")

    # TCAM / BRAM parameters
    rule_width = input_int("Rule width in bits", min_val=1)

    while True:
        bram_depth = input_int("BRAM depth (power of 2)", default=512, min_val=2)
        if (bram_depth & (bram_depth - 1)) == 0:
            break
        print(f"  ✖  {bram_depth} is not a power of 2.")

    bram_width = input_int("BRAM data width in bits", default=72, min_val=1)

    # Output options
    output_dir    = input_str("Output directory for .mem files", default="mem_files")
    output_format = input_choice("Output format", choices=["binary", "hex"], default="binary")
    sparse        = input_bool(
        "Sparse output? (only non-zero addresses, with @addr prefix)", default=False
    )
    do_verify = input_bool("Print rule-to-BRAM verification table?", default=False)

    print()

    # Parse rules
    print(f"Reading rules from : {rules_file}")
    rules = parse_rules(rules_file)
    print(f"Loaded             : {len(rules)} rule(s)")
    dc_counts = [r.count('*') for r in rules]
    print(f"Don't-care stats   : min={min(dc_counts)}  max={max(dc_counts)}  "
          f"avg={sum(dc_counts)/len(dc_counts):.1f}")

    # Build memories
    memories, num_ranks, num_banks, segment_width = build_bram_memories(
        rules=rules,
        rule_width=rule_width,
        bram_depth=bram_depth,
        bram_width=bram_width,
    )

    # Optional verification
    if do_verify:
        verify_and_print(
            rules, memories, num_ranks, num_banks,
            bram_depth, bram_width, segment_width, rule_width,
        )

    # Write .mem files
    print(f"Writing .mem files to : {output_dir}/")
    write_mem_files(
        memories=memories,
        num_ranks=num_ranks,
        num_banks=num_banks,
        bram_depth=bram_depth,
        bram_width=bram_width,
        output_dir=output_dir,
        output_format=output_format,
        sparse=sparse,
    )

    print("\nDone.")


if __name__ == "__main__":
    main()
