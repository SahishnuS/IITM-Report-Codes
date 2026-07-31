# IITM Report Codes

This repository contains the source code and supporting files developed during the IIT Madras project. It includes utilities for parsing ACL rules, converting them into ternary format, generating TCAM/BRAM memory files, and related hardware implementations.

---

## Folder Structure

```
.
├── Custom Rule Parser/
├── TCAM/
│   ├── Rules/
│   ├── TCAM_104/
│   └── mem_files/
├── TCAM-SRAM Mapping Matrix Engine/
├── Full Lifecycle Operations Simulator/
└── IEEE 32 Floating Point Adder Source Folder/
```

---

# 1. Custom Rule Parser

Converts ACL rules into binary/ternary rules that can later be used by the TCAM tools.

## Input

A text file containing one ACL rule per line.

Example:

```
@64.91.107.21/32 128.222.130.81/32 0 : 65535 1221 : 1221 0x06/0xFF
```

## Output

A list of binary/ternary rules where each rule contains:

- Source IP
- Destination IP
- Source Port
- Destination Port
- Protocol

The generated rules are later stored in a text file (for example `rules_binary.txt`).

---

# 2. TCAM Rule Loader

Converts ternary rules into BRAM initialization files.

## Input

A text file containing one ternary rule per line.

Example

```
10110***0011***101001
111000***11001**00111
```

### Supported characters

| Character | Meaning |
|-----------|---------|
| 0 | Logic 0 |
| 1 | Logic 1 |
| * | Don't care |
| x/X/? | Also treated as don't care |

Spaces are ignored.

---

## Output

Multiple memory initialization files:

```
mem_<rank>_<bank>.mem
```

Example

```
mem_1_1.mem
mem_1_2.mem
mem_2_1.mem
...
```

Each file contains BRAM initialization data.

---

# 3. TCAM-SRAM Mapping Matrix Engine

Populates SRAM according to ternary rules.

## Input

A file named

```
ternary_rules.txt
```

containing one ternary rule per line.

Example

```
10110X001*0110010011001101010011
11111*0000110X100001101010001110
```

Supported wildcard characters:

- `X`
- `*`

---

## Output

First, the program generates

```
mem1.txt
mem2.txt
mem3.txt
mem4.txt
```

Each file stores one SRAM segment.

These files are then split into:

```
mem1A.txt
mem1B.txt
mem2A.txt
mem2B.txt
mem3A.txt
mem3B.txt
mem4A.txt
mem4B.txt
```

These are the final SRAM memory files.

---

# 4. TCAM Hardware

Contains the Vivado project and SystemVerilog implementation of the TCAM.

Main modules include:

- TCAM
- BRAM Manager
- Word Parser
- Priority Encoder
- Testbenches

---

# 5. Full Lifecycle Operations Simulator

Python simulator for testing the complete TCAM-SRAM workflow.

---

# 6. IEEE 32-bit Floating Point Adder

Bluespec implementation of an IEEE-754 Floating Point Adder.

Includes:

- Floating Point Adder
- Comparator
- Shifter
- Infinity/NaN Flagger
- Testbenches

---

# Requirements

- Python 3.x
- Xilinx Vivado (for hardware implementation)
- Bluespec Compiler (for floating-point adder)

---

# Input File Summary

| Program | Input File | Format |
|----------|------------|--------|
| Custom Rule Parser | ACL text file | One ACL rule per line |
| TCAM Rule Loader | Ternary rule file | One ternary rule per line |
| SRAM Mapping Engine | `ternary_rules.txt` | One ternary rule per line |

---

# Output File Summary

| Program | Output |
|----------|--------|
| Custom Rule Parser | Binary/Ternary rule list (`rules_binary.txt`) |
| TCAM Rule Loader | `mem_<rank>_<bank>.mem` files |
| SRAM Mapping Engine | `mem1.txt`–`mem4.txt`, then `mem1A.txt`–`mem4B.txt` |

---

## Notes

- Each input file should contain **one rule per line**.
- Blank lines are ignored.
- Spaces inside rules are ignored.
- `*`, `X`, `x`, and `?` are treated as **don't-care bits** where applicable.
- Generated memory files can be directly used for TCAM/BRAM initialization.
