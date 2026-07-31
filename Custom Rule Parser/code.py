#Extracting the five different fields
def basic_info(rule):
  parts=rule.split()
  src_ip=parts[0][1:]
  dest_ip=parts[1]
  src_port=parts[2]+parts[3]+parts[4]
  dest_port=parts[5]+parts[6]+parts[7]
  protocol=parts[8].split("/")[0]
  protocol_wildcard=parts[8].split("/")[1]
  return src_ip, dest_ip, src_port, dest_port, protocol, protocol_wildcard

#Test
testrule="@64.91.107.21/32 128.222.130.81/32 0 : 65535 1221 : 1221 0x06/0xFF"
print(basic_info(testrule))

#Decimal to binary conversion function
def decimal_to_8bit(n):
    return format(n, "08b")

#Handling the IP addresses : conversion to binary + replacing with don't cares
def src_ip_handling(src_ip):
  src_ip_binary=""
  src_ip_address=src_ip.split("/")[0]
  src_ip_snm=int(src_ip.split("/")[1])
  for segment in src_ip_address.split("."):
    src_ip_binary+=decimal_to_8bit(int(segment))

  for i in range(src_ip_snm, len(src_ip_address)):
    src_ip_address[i]="*"
  return(src_ip_binary)

#Test
print(len(src_ip_handling("64.91.107.9/32")))

def dest_ip_handling(dest_ip):
  dest_ip_binary=""
  dest_ip_address=dest_ip.split("/")[0]
  dest_ip_snm=int(dest_ip.split("/")[1])
  for segment in dest_ip_address.split("."):
    dest_ip_binary+=decimal_to_8bit(int(segment))

  for i in range(dest_ip_snm, len(dest_ip_address)):
    dest_ip_address[i]="*"

  return(dest_ip_binary)

#Handling the port numbers
### Depth 2 (2 categories)

1. `01**************`
2. `10**************`

---

### Depth 3 (2)

3. `001*************`
4. `110*************`

---

### Depth 4 (2)

5. `0001************`
6. `1110************`

---

### Depth 5 (2)

7. `00001***********`
8. `11110***********`

---

### Depth 6 (2)

9. `000001**********`
10. `111110**********`

---

### Depth 7 (2)

11. `0000001*********`
12. `1111110*********`

---

### Depth 8 (2)

13. `00000001********`
14. `11111110********`

---

### Depth 9 (2)

15. `000000001*******`
16. `111111110*******`

---

### Depth 10 (2)

17. `0000000001******`
18. `1111111110******`

---

### Depth 11 (2)

19. `00000000001*****`
20. `11111111110*****`

---

### Depth 12 (2)

21. `000000000001****`
22. `111111111110****`

---

### Depth 13 (2)

23. `0000000000001***`
24. `1111111111110***`

---

### Depth 14 (2)

25. `00000000000001**`
26. `11111111111110**`

---

### Depth 15 (4)

27. `000000000000000*`
28. `000000000000001*`
29. `111111111111110*`
30. `111111111111111*`

---

#Handling protocol numbers
def hex_to_bin(hex_str, bits=8):
    """
    Converts hex string (like '0x06' or '06') to fixed-width binary string.
    """
    return format(int(hex_str, 16), f'0{bits}b')

def protocol_handling(protocol,protocol_wildcard):
  protocol_bin=hex_to_bin(protocol,8)
  mask_bin=hex_to_bin(protocol_wildcard, 8)
  protocol_bin_str = list(protocol_bin)

  for i in range(len(mask_bin)):
      if mask_bin[i] != '1':
          protocol_bin_str[i] = '*'

  protocol_bin_str = ''.join(protocol_bin_str)

  return(protocol_bin_str)

#Overall Rule Handling
lines = []

with open("/content/acl100.txt", "r") as f:
    for line in f:
        lines.append(line.strip())

rules_binary=[]
#lines[96] & lines[97] are a problem

for i in range(0,96):
  rule=lines[i]
  src_ip,dest_ip,src_port,dest_port,protocol,protocol_mask=basic_info(rule)
  start_d_port,end_d_port=find_port_indices(dest_port)
  matched_categories=matching_categories(start_d_port, end_d_port)
  for categ in matched_categories:
    binary_rule=""
    #Source IP
    binary_rule+=src_ip_handling(src_ip)
    binary_rule+=" "
    #Dest IP
    binary_rule+=dest_ip_handling(dest_ip)
    binary_rule+=" "
    #Source Port
    binary_rule+="**************** " #16 DCs for the source port number since everything from 0:65535 is included as per ur ACL
    #Dest Port
    binary_rule+=categ
    binary_rule+=" "
    #Protocol
    binary_rule+=protocol_handling(protocol, protocol_mask)
    rules_binary.append(binary_rule)

print(rules_binary)

#We have 98 rules originally. There seems to be some formatting issue in the last two rules, which for time being I have ignored. Of the 96 remaining, The last 21 of them have 0:65535 as the dest port range (meaning each of these 23 maps to 30 individual rules. 23x30=690). The other 75 map to approximately 4 rules each absed on the dest port wild card pattern matching. Thus we have a total of 1012 rules derived from the given 96.
rules_binary_clipped=rules_binary[0:101]
with open("rules_binary.txt", "w") as f:
    for rule in rules_binary:
        f.write(rule + "\n")

