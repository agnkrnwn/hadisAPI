import os

# Dapatkan semua file di direktori saat ini
files = [f for f in os.listdir() if f.endswith('.json')]

# Urutkan file berdasarkan nama asli (bisa diubah sesuai kebutuhan)
files.sort()

# Rename file satu per satu
for idx, filename in enumerate(files, start=1):
    new_name = f"hadist{idx}.json"
    os.rename(filename, new_name)
    print(f"{filename} -> {new_name}")

print("Selesai mengganti nama semua file JSON.")

