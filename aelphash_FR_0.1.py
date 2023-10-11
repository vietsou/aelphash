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

# Demande de hash et d'un moyen de l'identifier
hash_input = input("Veuillez entrer le hash: ")
id_hash = input("Veuillez donner un nom pour identifier ce hash: ")

# Création des dossiers
if not os.path.exists(os.path.expanduser('~/aelphash.d')):
    os.makedirs(os.path.expanduser('~/aelphash.d'))

now = datetime.now()
date_time = now.strftime("%Y-%m-%d_%H-%M-%S")
hash_dir = os.path.join(os.path.expanduser('~/aelphash.d'), f"{id_hash}_{date_time}")

os.makedirs(hash_dir)

# Écrire le hash dans un fichier
with open(os.path.join(hash_dir, f"{id_hash}.txt"), 'w') as f:
    f.write(hash_input)

# Identification des modes/formats
subprocess.run(f"hashid {hash_input} -m > {hash_dir}/hash_hc", shell=True)
subprocess.run(f"hashid {hash_input} -j > {hash_dir}/hash_j", shell=True)

# Isolement des formats
subprocess.run(f"awk -F 'Hashcat Mode: ' '{{print $2}}' {hash_dir}/hash_hc | cut -d']' -f1 | sed '/^$/d' > {hash_dir}/modes_hc", shell=True)
subprocess.run(f"awk -F 'JtR Format: ' '{{print $2}}' {hash_dir}/hash_j | cut -d']' -f1 | sed '/^$/d' > {hash_dir}/modes_j", shell=True)

# Choix entre John et Hashcat + si wordlist
choice = input("Voulez-vous utiliser (1) JohnTheRipper ou (2) Hashcat? : ")
wordlist_path = input("Si vous souhaitez utiliser une wordlist spécifique, indiquez le chemin, sinon appuyez sur Entrée: \n")

# Utilisation de John ou Hashcat
if choice == '1':
    with open(os.path.join(hash_dir, "modes_j"), 'r') as f:
        modes = [line.strip() for line in f if line.strip()]
    print("Modes disponibles : ")
    for i, mode in enumerate(modes, 1):
        print(f"{i}. {mode}")
    selected_mode_index = int(input("Quel mode souhaitez-vous utiliser ? : ")) - 1
    selected_mode = modes[selected_mode_index]

    cmd = f"john {hash_dir}/{id_hash}.txt --format={selected_mode}"
    if wordlist_path:
        cmd += f" --wordlist={wordlist_path}"

    subprocess.run(cmd, shell=True)
    
elif choice == '2':
    subprocess.run(f"cat {os.path.join(hash_dir, f'hash_hc')}", shell=True)

    with open(os.path.join(hash_dir, "modes_hc"), 'r') as f:
        modes = [line.strip() for line in f if line.strip()]
    print("Modes disponibles : ")
    for i, mode in enumerate(modes, 1):
        print(f"{i}. {mode}")
    selected_mode_index = int(input("Quel mode souhaitez-vous utiliser ? : ")) - 1
    selected_mode = modes[selected_mode_index]

    cmd = f"hashcat -a 0 -m {selected_mode} {hash_dir}/{id_hash}.txt"
    if wordlist_path:
        cmd += f" {wordlist_path}"

    subprocess.run(cmd, shell=True)
