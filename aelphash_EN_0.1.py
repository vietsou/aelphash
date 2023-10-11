import os
import subprocess
from datetime import datetime

print(r"""
                 __     __            __        
 ____  ___ ____ / /__  / /  ___ ____ / /    ____
/___/ / _ `/ -_) / _ \/ _ \/ _ `(_-</ _ \  /___/
      \_,_/\__/_/ .__/_//_/\_,_/___/_//_/       
               /_/                               
""")

# Ask the user for the hash and hash ID
hash_input = input("Please enter the hash: ")
id_hash = input("Please give a name to identify this hash: ")

# Create directories if they don't exist
if not os.path.exists(os.path.expanduser('~/aelphash.d')):
    os.makedirs(os.path.expanduser('~/aelphash.d'))

now = datetime.now()
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
hash_dir = os.path.join(os.path.expanduser('~/aelphash.d'), f"{id_hash}_{date_time}")

os.makedirs(hash_dir)

# Write the hash into a file
with open(os.path.join(hash_dir, f"{id_hash}.txt"), 'w') as f:
    f.write(hash_input)

# Use hashid
subprocess.run(f"hashid {hash_input} -m > {hash_dir}/hash_hc", shell=True)
subprocess.run(f"hashid {hash_input} -j > {hash_dir}/hash_j", shell=True)

# Use cut to isolate the modes
subprocess.run(f"awk -F 'Hashcat Mode: ' '{{print $2}}' {hash_dir}/hash_hc | cut -d']' -f1 | sed '/^$/d' > {hash_dir}/modes_hc", shell=True)
subprocess.run(f"awk -F 'JtR Format: ' '{{print $2}}' {hash_dir}/hash_j | cut -d']' -f1 | sed '/^$/d' > {hash_dir}/modes_j", shell=True)

# Ask the choice between John and Hashcat and for the wordlist
choice = input("Do you want to use (1) JohnTheRipper or (2) Hashcat? : ")
wordlist_path = input("If you want to use a specific wordlist, enter the path; otherwise, hit Enter: \n")

# Use John or Hashcat
if choice == '1':
    with open(os.path.join(hash_dir, "modes_j"), 'r') as f:
        modes = [line.strip() for line in f if line.strip()]
    print("Available modes: ")
    for i, mode in enumerate(modes, 1):
        print(f"{i}. {mode}")
    selected_mode_index = int(input("Which mode would you like to use? : ")) - 1
    selected_mode = modes[selected_mode_index]

    cmd = f"john {hash_dir}/{id_hash}.txt --format={selected_mode}"
    if wordlist_path:
        cmd += f" --wordlist={wordlist_path}"

    subprocess.run(cmd, shell=True)

elif choice == '2':
    subprocess.run(f"cat {os.path.join(hash_dir, 'hash_hc')}", shell=True)

    with open(os.path.join(hash_dir, "modes_hc"), 'r') as f:
        modes = [line.strip() for line in f if line.strip()]
    print("Available modes: ")
    for i, mode in enumerate(modes, 1):
        print(f"{i}. {mode}")
    selected_mode_index = int(input("Which mode would you like to use? : ")) - 1
    selected_mode = modes[selected_mode_index]

    cmd = f"hashcat -a 0 -m {selected_mode} {hash_dir}/{id_hash}.txt"
    if wordlist_path:
        cmd += f" {wordlist_path}"

    subprocess.run(cmd, shell=True)
