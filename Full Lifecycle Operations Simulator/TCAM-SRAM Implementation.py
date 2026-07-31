#Creating SRAM blocks
def my_create_SRAM(N,W):
  sram=[]
  if (W%2==0):
    num_segments=W//2
  else:
    num_segments=(W+1)//2
  #num_segments is the number of segments or blocks we get, when we perform width based segmentation into 2 bits each
  for i in range(num_segments):
    segment=[]
    for location in range(4):
      data=[]
      for j in range(N):
        data.append(0)
      segment.append(data)
    sram.append(segment)
  return sram

'''*   **Time Complexity** :

O(WN) [we may take the time complexity of the append() operation to be amortized O(1)]
*   **Space Complexity** :

O(WN) [since the segmentation is always done into groups of two bits each, we get W/2 x 2^2 x N memory locations]'''

#Populating the SRAM
def populate_SRAM(N, W, created_SRAM):
  rules=[]
  #receiving the rules as input
  for i in range (N):
    rule=input("Enter rule: ") #input as string because rule will have 0,1 and x
    if len(rule)!=W:
      print("Incorrect rule width. Please retry")
      return
    else :
      if (W%2)==1:
        rule+="X" #padding X for odd rule length
      rules.append(rule)
    #directly populating the rule into the SRAM before proceeding to get the next rule
    for sram_seg_no in range(len(created_SRAM)):
      rule_bits_start=sram_seg_no*2
      rule_bits_end=rule_bits_start+1
      curr_sram_segment=created_SRAM[sram_seg_no]
      if rule[rule_bits_start]=='0' and rule[rule_bits_end] =='0':
        curr_sram_segment[0][i]=1
        curr_sram_segment[1][i]=0
        curr_sram_segment[2][i]=0
        curr_sram_segment[3][i]=0
      elif rule[rule_bits_start]=='0' and rule[rule_bits_end]=='1':
        curr_sram_segment[0][i]=0
        curr_sram_segment[1][i]=1
        curr_sram_segment[2][i]=0
        curr_sram_segment[3][i]=0
      elif rule[rule_bits_start]=='0' and rule[rule_bits_end]=='X':
        curr_sram_segment[0][i]=1
        curr_sram_segment[1][i]=1
        curr_sram_segment[2][i]=0
        curr_sram_segment[3][i]=0
      elif rule[rule_bits_start]=='1' and rule[rule_bits_end]=='0':
        curr_sram_segment[0][i]=0
        curr_sram_segment[1][i]=0
        curr_sram_segment[2][i]=1
        curr_sram_segment[3][i]=0
      elif rule[rule_bits_start]=='1' and rule[rule_bits_end]=='1':
        curr_sram_segment[0][i]=0
        curr_sram_segment[1][i]=0
        curr_sram_segment[2][i]=0
        curr_sram_segment[3][i]=1
      elif rule[rule_bits_start]=='1' and rule[rule_bits_end]=='X':
        curr_sram_segment[0][i]=0
        curr_sram_segment[1][i]=0
        curr_sram_segment[2][i]=1
        curr_sram_segment[3][i]=1
      elif rule[rule_bits_start]=='X'and rule[rule_bits_end]=='0':
        curr_sram_segment[0][i]=1
        curr_sram_segment[1][i]=0
        curr_sram_segment[2][i]=1
        curr_sram_segment[3][i]=0
      elif rule[rule_bits_start]=='X'and rule[rule_bits_end]=='1':
        curr_sram_segment[0][i]=0
        curr_sram_segment[1][i]=1
        curr_sram_segment[2][i]=0
        curr_sram_segment[3][i]=1
      else:
        curr_sram_segment[0][i]=1
        curr_sram_segment[1][i]=1
        curr_sram_segment[2][i]=1
        curr_sram_segment[3][i]=1
  return created_SRAM, rules

'''*   **Time Complexity:**

O(NW)

*   **Auxiliary Space Complexity:**

O(NW) [N rules, each of length W bits each]'''

#Lookup : Bit Vector Generation
def generate_bit_vector(sram,searchkey,N,W):
  result=[]
  for sram_seg_no in range(len(sram)):
    sram_segment=sram[sram_seg_no]
    start_idx=sram_seg_no*2
    end_idx=start_idx+1
    part=0 #which of the four (00,01,10,11) locations we must look at
    if searchkey[start_idx]=="0" and searchkey[end_idx]=="0":
      part=0
    elif searchkey[start_idx]=="0" and searchkey[end_idx]=="1":
      part=1
    elif searchkey[start_idx]=="1" and searchkey[end_idx]=="0":
      part=2
    else :
      part=3
    #Now we go to that location and take its contents
    result.append(sram_segment[part])
  return result #must have 'sram_seg_no' number of N bit vectors

'''*   **Time Complexity:**

O(W)

*   **Auxiliary Space Complexity:**

O(WN)

'''

#AND-ing the bit vectors; match vs. mismatch?
def match_or_not(results, N):
  flag=False
  idx=-1
  for rule_no in range(N):
    answer=True
    for segment in results:
      answer = answer and segment[rule_no]
    if answer:
      flag=True
      idx=rule_no
      break
  if flag :
    print("Match found at Rule #",rule_no)
  else:
    print("No match found")

'''*   **Time Complexity :**

O(NW)

*   **Auxiliary Space Complexity :**

O(1)'''

#Update : Adding a new rule
def add_rule(rule, rules_list, sram, N):
  N=N+1
  rules_list.append(rule)
  for sram_seg_no in range(len(sram)):
    sram_segment=sram[sram_seg_no]
    start_idx=2*sram_seg_no
    end_idx=start_idx+1
    if rule[start_idx]=="0" and rule[end_idx]=="0":
      sram_segment[0].append(1)
      sram_segment[1].append(0)
      sram_segment[2].append(0)
      sram_segment[3].append(0)
    elif rule[start_idx]=="0" and rule[end_idx]=="1":
      sram_segment[0].append(0)
      sram_segment[1].append(1)
      sram_segment[2].append(0)
      sram_segment[3].append(0)
    elif rule[start_idx]=="0" and rule[end_idx]=="X":
      sram_segment[0].append(1)
      sram_segment[1].append(1)
      sram_segment[2].append(0)
      sram_segment[3].append(0)
    elif rule[start_idx]=="1" and rule[end_idx]=="0":
      sram_segment[0].append(0)
      sram_segment[1].append(0)
      sram_segment[2].append(1)
      sram_segment[3].append(0)
    elif rule[start_idx]=="1" and rule[end_idx]=="1":
      sram_segment[0].append(0)
      sram_segment[1].append(0)
      sram_segment[2].append(0)
      sram_segment[3].append(1)
    elif rule[start_idx]=="1" and rule[end_idx]=="X":
      sram_segment[0].append(0)
      sram_segment[1].append(0)
      sram_segment[2].append(1)
      sram_segment[3].append(1)
    elif rule[start_idx]=="X" and rule[end_idx]=="0":
      sram_segment[0].append(1)
      sram_segment[1].append(0)
      sram_segment[2].append(1)
      sram_segment[3].append(0)
    elif rule[start_idx]=="X" and rule[end_idx]=="1":
      sram_segment[0].append(0)
      sram_segment[1].append(1)
      sram_segment[2].append(0)
      sram_segment[3].append(1)
    else:
      sram_segment[0].append(1)
      sram_segment[1].append(1)
      sram_segment[2].append(1)
      sram_segment[3].append(1)
  return sram, rules_list, N

'''*   **Time Complexity :**

O(W)

*   **Auxiliary Space Complexity :**

O(1)

'''

#Update : Deleting an existing rule
def delete_rule(rule, rules_list, sram, N):
  if rule not in rules_list :
    print("You are trying to delete a rule which does not exist.")
  else :
    rule_number=rules_list.index(rule) #rule number
    #remove the rule from rules_list
    rules_list.remove(rule)
    N-N-1
    #changing the sram values
    for sram_segment_no in range(len(sram)):
      sram_segment=sram[sram_segment_no]
      start=2*sram_segment_no
      end=start+1
      if rule[start]=="0" and rule[end]=="0":
        sram_segment[0][rule_number]=0
      elif rule[start]=="0" and rule[end]=="1":
        sram_segment[1][rule_number]=0
      elif rule[start]=="0" and rule[end]=="X":
        sram_segment[0][rule_number]=0
        sram_segment[1][rule_number]=0
      elif rule[start]=="1" and rule[end]=="0":
        sram_segment[2][rule_number]=0
      elif rule[start]=="1" and rule[end]=="1":
        sram_segment[3][rule_number]=0
      elif rule[start]=="1" and rule[end]=="X":
        sram_segment[2][rule_number]=0
        sram_segment[3][rule_number]=0
      elif rule[start]=="X" and rule[end]=="0":
        sram_segment[0][rule_number]=0
        sram_segment[2][rule_number]=0
      elif rule[start]=="X" and rule[end]=="1":
        sram_segment[1][rule_number]=0
        sram_segment[3][rule_number]=0
      else :
        sram_segment[0][rule_number]=0
        sram_segment[1][rule_number]=0
        sram_segment[2][rule_number]=0
        sram_segment[3][rule_number]=0
  return sram, rules_list, N

'''*   **Time Complexity :**

O(N+W) [O(N) to check whether rule exists; O(W) to perform deletion)]

*   **Auxiliary Space Complexity :**

O(1)

'''

#Testing
#Creating SRAM
N=int(input("Enter the number of rules: "))
W=int(input("Enter the width of a rule: "))
sram=my_create_SRAM(N,W)
print(sram)

#Populating the SRAM
sram, list_of_rules = populate_SRAM(N, W, sram)

#Adding a rule
rule_to_add=input("Enter rule to be added: ")
sram, list_of_rules, N = add_rule(rule_to_add, list_of_rules, sram, N)

#Deleting a rule
rule_to_delete=input("Enter rule to be deleted: ")
sram, list_of_rules, N = delete_rule (rule_to_delete,list_of_rules, sram, N)

#Lookup
key=input("Enter a search key: ")
bit_vectors = generate_bit_vector(sram, key, N, W)
match_or_not(bit_vectors, N)
#Overall Time and Space Complexity : O(NW) each

#Generalized version
def create_SRAM(N, W, Wi):

    # Number of segments after padding
    num_segments = (W + Wi - 1) // Wi

    sram = []

    for _ in range(num_segments):
        segment = []

        # 2^Wi possible addresses per segment
        for _ in range(2 ** Wi):
            segment.append([0] * N)

        sram.append(segment)

    return sram

created_sram=create_SRAM(2,4,2)
print(created_sram)

def populate_SRAM(N, W, Wi, created_SRAM):

    rules = []

    # Total width after padding
    padded_width = ((W + Wi - 1) // Wi) * Wi
    padding_needed = padded_width - W

    for i in range(N):

        rule = input(f"Enter rule {i}: ")

        if len(rule) != W:
            print("Incorrect rule width.")
            return

        # Pad with 'X' if necessary
        rule = rule + ("X" * padding_needed)
        rules.append(rule)

        # Process each segment
        for seg_index in range(len(created_SRAM)):

            start = seg_index * Wi
            end = start + Wi

            rule_slice = rule[start:end]
            segment = created_SRAM[seg_index]

            # For every possible address in this segment
            for address in range(2 ** Wi):

                address_bits = format(address, f'0{Wi}b')

                match = True
                for bit_rule, bit_addr in zip(rule_slice, address_bits):
                    if bit_rule != 'X' and bit_rule != bit_addr:
                        match = False
                        break

                if match:
                    segment[address][i] = 1

    return created_SRAM, rules

populated_sram, rules_list=populate_SRAM(2,4,2,created_sram)
print(populated_sram, rules_list)

#Converting ternary rules to TCAM SRAM : trial
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

W = 32
Wi = 9   # segmentation: 9 + 9 + 9 + 5 (last padded to 9)

sram, rules = populate_SRAM_from_file("ternary_rules.txt", W, Wi)
print("Number of rules (N):", len(rules))
print("Number of segments:", len(sram))
print("Addresses per segment:", len(sram[0]))

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

write_segments_to_files_limited(sram)

def verify_sram(sram, rules, W, Wi, num_tests=5):

    padded_width = ((W + Wi - 1) // Wi) * Wi
    padding_needed = padded_width - W

    for i in range(min(num_tests, len(rules))):

        rule = rules[i] + ("X" * padding_needed)

        for seg_index in range(len(sram)):

            start = seg_index * Wi
            end = start + Wi
            rule_slice = rule[start:end]

            # Build a concrete matching address
            test_address_bits = ""
            for bit in rule_slice:
                if bit in ['X', '*']:
                    test_address_bits += "0"
                else:
                    test_address_bits += bit

            address = int(test_address_bits, 2)

            if sram[seg_index][address][i] != 1:
                print(f"Mismatch found in rule {i}, segment {seg_index}")
                return

    print("SRAM verification passed for tested rules.")

verify_sram(sram, rules, W, Wi)

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

split_mem_files()
