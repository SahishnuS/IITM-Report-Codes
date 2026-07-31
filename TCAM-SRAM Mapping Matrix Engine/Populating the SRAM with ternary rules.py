#Prerequisites
Please create a text file [preferably titled rules_ternary.txt] with 32-bit rules.

#Function to create SRAM space
def create_SRAM(N, W, Wi):
    """
    sram[segment][address][rule_index]
    """
    num_segments = (W + Wi - 1) // Wi  # ceiling division

    sram = []

    for _ in range(num_segments):
        segment = []
        for _ in range(2 ** Wi):
            segment.append([0] * N)
        sram.append(segment)

    return sram

#Function to populate SRAM as per Jiang's algorithm
def populate_SRAM_from_file(filename, W, Wi):

    with open(filename, 'r') as f:
        raw_rules = f.readlines()

    rules = []

    for line in raw_rules:
        clean_rule = line.strip().replace(" ", "")

        if not clean_rule:
            continue

        # Ensure rule is at least 32 bits
        if len(clean_rule) < W:
            raise ValueError("Rule shorter than expected.")

        # Take only first W bits (first 32 bits)
        truncated_rule = clean_rule[:W]

        rules.append(truncated_rule)

    N = len(rules)

    # Padding calculation
    padded_width = ((W + Wi - 1) // Wi) * Wi
    padding_needed = padded_width - W

    sram = create_SRAM(N, W, Wi)

    for i, rule in enumerate(rules):

        # Pad with X for even segmentation
        rule = rule + ("X" * padding_needed)

        for seg_index in range(len(sram)):

            start = seg_index * Wi
            end = start + Wi

            rule_slice = rule[start:end]
            segment = sram[seg_index]

            for address in range(2 ** Wi):

                address_bits = format(address, f'0{Wi}b')

                match = True
                for bit_rule, bit_addr in zip(rule_slice, address_bits):
                    if bit_rule not in ['X', '*'] and bit_rule != bit_addr:
                        match = False
                        break

                if match:
                    segment[address][i] = 1

    return sram, rules

#Function to write the populated SRAM contents to text files
def write_segments_to_files_limited(sram, limit=144, base_filename="mem"):

    num_segments = len(sram)

    for seg_index in range(num_segments):

        segment = sram[seg_index]
        filename = f"{base_filename}{seg_index+1}.txt"

        with open(filename, "w") as f:
            for address_row in segment:

                # Take only first `limit` bits
                limited_row = address_row[:limit]

                line = "".join(str(bit) for bit in limited_row)
                f.write(line + "\n")

    print(f"Segment files written with first {limit} rules only.")

#Function to split the 4 text files (512x144) into 8 files (512x72)
import os

def split_mem_files(num_segments=4, split_width=72):

    for i in range(1, num_segments + 1):

        input_file = f"mem{i}.txt"
        output_file_A = f"mem{i}A.txt"
        output_file_B = f"mem{i}B.txt"

        with open(input_file, "r") as f_in, \
             open(output_file_A, "w") as f_A, \
             open(output_file_B, "w") as f_B:

            for line in f_in:
                line = line.strip()  # remove newline

                first_half = line[:split_width]
                second_half = line[split_width:split_width*2]

                f_A.write(first_half + "\n")
                f_B.write(second_half + "\n")

    print("All files split successfully.")

#Calling all the above functions
W = 32
Wi = 9   # segmentation: 9 + 9 + 9 + 5 (last padded to 9)

sram, rules = populate_SRAM_from_file("ternary_rules.txt", W, Wi)
print("Number of rules (N):", len(rules))
print("Number of segments:", len(sram))
print("Addresses per segment:", len(sram[0]))

write_segments_to_files_limited(sram)

split_mem_files()

#Note :
#At this juncture, all eight files [titled mem1A.txt, mem1B.txt, mem2A.txt, ... mem4B.txt] should be available.

