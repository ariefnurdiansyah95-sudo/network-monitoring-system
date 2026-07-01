import ast
import os

def add_host_to_config(ip_address, name=None, config_path='app/config.py'):
    with open(config_path, 'r') as f:
        code = f.read()

    # Parse kode dan cari variabel HOSTS
    tree = ast.parse(code)
    new_hosts = None

    for node in tree.body:
        if isinstance(node, ast.Assign) and node.targets[0].id == 'HOSTS':
            new_hosts = ast.literal_eval(node.value)
            break

    if new_hosts is None:
        return False  # HOSTS tidak ditemukan

    # Cek apakah IP sudah ada
    for host in new_hosts:
        if host['ip'] == ip_address:
            return False  # Sudah ada, tidak perlu ditambah

    # Tambah host baru
    if name is None:
        name = f"Client {len(new_hosts) + 1}"
    new_hosts.append({'name': name, 'ip': ip_address})

    # Tulis ulang config.py
    with open(config_path, 'w') as f:
        f.write("BOT_TOKEN = '7517776550:AAGjRlfGLxUS32p0C1p_VQBXrPhwYn7xejc'\n")
        f.write("CHAT_ID = '1124425166'\n")
        f.write(f"HOSTS = {new_hosts}\n")

    return True
