import os
import re
import requests
from app.config import HOSTS, BOT_TOKEN, CHAT_ID
import time
import threading
import subprocess
import sqlite3
from collections import defaultdict
from app.database import get_db
from collections import defaultdict
from datetime import datetime
from app import state
from ping3 import ping



DB_NAME = 'log.db'

def check_host(ip):
    """Cek status host dengan ping3, return latency (detik) atau None."""
    try:
        latency = ping(ip, timeout=1)
        return latency  # float (detik) jika UP, None jika DOWN
    except Exception:
        return None
   
def monitor_hosts(interval_seconds=60):
    """Loop monitoring yang berjalan setiap interval detik"""
    def monitor():
        while True:
            print("⏱️ Menjalankan monitoring...")
            for host in HOSTS:
                ip = host['ip']
                name = host['name']
                latency = check_host(ip)
                is_up = latency is not None
                status = 'UP' if is_up else 'DOWN'
                status_icon = '🟢' if is_up else '❌'
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')

                insert_log(timestamp, name, ip, status)

                # Hanya kirim notifikasi jika status DOWN
                if status == 'DOWN':
                    message = f"{status_icon} {name} ({ip}) masih DOWN pada {timestamp}"
                    send_telegram_message(message)

            time.sleep(interval_seconds)

    # Jalankan sebagai thread daemon
    thread = threading.Thread(target=monitor, daemon=True)
    thread.start()

def send_telegram_message(message):
    """Kirim pesan ke bot Telegram"""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {'chat_id': CHAT_ID, 'text': message}
    try:
        requests.post(url, data=payload)
    except Exception as e:
        print(f"Error sending message: {e}")

def ping_host(ip):
    """Cek status host dengan ping3, return latency (detik) atau None."""
    try:
        latency = ping(ip, timeout=1)
        return latency  # float (detik) jika UP, None jika DOWN
    except Exception:
        return None
    
def get_all_logs():
    conn = sqlite3.connect('log.db')
    conn.row_factory = sqlite3.Row  # Mengubah hasil query menjadi dictionary
    c = conn.cursor()
    c.execute("SELECT timestamp, host_name, host_ip, status FROM logs ORDER BY id DESC LIMIT 100")
    rows = c.fetchall()
    conn.close()
    return rows

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            host_name TEXT,
            host_ip TEXT,
            status TEXT
        )
    ''')
    conn.commit()
    conn.close()

def insert_log(timestamp, host_name, host_ip, status):
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        INSERT INTO logs (timestamp, host_name, host_ip, status)
        VALUES (?, ?, ?, ?)
    ''', (timestamp, host_name, host_ip, status))
    conn.commit()
    conn.close()

def get_all_logs():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Menggunakan Row Factory agar bisa mengakses kolom dengan nama
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, host_name, host_ip, status
        FROM logs
        ORDER BY id DESC  -- Mengambil data terbaru
        LIMIT 100
    ''')
    rows = c.fetchall()
    conn.close()
    return [dict(row) for row in rows]  # Mengubah hasil menjadi list of dict

def get_latest_status_per_ip():
    conn = sqlite3.connect('log.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM monitoring_log ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()

    latest = {}
    for row in rows:
        ip = row['host_ip']
        if ip not in latest:
            latest[ip] = {
                'host_name': row['host_name'],
                'host_ip': row['host_ip'],
                'status': row['status'],
                'timestamp': row['timestamp']
            }

    return list(latest.values())

def generate_grouped_summary(start_date, end_date):
    db = get_db()
    cur = db.cursor()

    # Ambil semua data log antara tanggal start dan end
    cur.execute("""
        SELECT host_name, status, DATE(timestamp) as date
        FROM logs
        WHERE DATE(timestamp) BETWEEN ? AND ?
        ORDER BY date ASC
    """, (start_date, end_date))

    rows = cur.fetchall()

    # Struktur: grouped[host_name][date]['UP'/'DOWN'] = jumlah
    grouped = defaultdict(lambda: defaultdict(lambda: {'UP': 0, 'DOWN': 0}))

    dates = set()
    hosts = set()

    for row in rows:
        host = row['host_name']
        date = row['date']
        status = row['status']
        
        grouped[host][date][status] += 1
        dates.add(date)
        hosts.add(host)

    all_dates = sorted(list(dates))
    all_hosts = sorted(list(hosts))

    # Persiapkan format untuk Chart.js
    result = {
        "labels": all_dates,
        "datasets": []
    }

    for host in all_hosts:
        up_data = []
        down_data = []
        for d in all_dates:
            up_data.append(grouped[host][d]['UP'])
            down_data.append(grouped[host][d]['DOWN'])

        result['datasets'].append({
            "label": f"{host} - UP",
            "data": up_data,
            "backgroundColor": "#28a745",
            "stack": host
        })

        result['datasets'].append({
            "label": f"{host} - DOWN",
            "data": down_data,
            "backgroundColor": "#dc3545",
            "stack": host
        })

    # Tambahkan garis tren total DOWN semua host
    trend_down = [
        sum(grouped[h][d]['DOWN'] for h in all_hosts)
        for d in all_dates
    ]

    result['datasets'].append({
        "label": "📉 Total DOWN (Trend)",
        "data": trend_down,
        "borderColor": "#000",
        "backgroundColor": "rgba(0,0,0,0.1)",
        "type": "line",
        "fill": False,
        "tension": 0.3,
        "yAxisID": 'y'
    })

    return result

def get_all_logs():
    """Get all logs without filtering"""
    conn = sqlite3.connect('log.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM logs ORDER BY timestamp DESC")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_filtered_logs(start_date=None, end_date=None):
    """Get logs with date filtering"""
    conn = sqlite3.connect('log.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    query = "SELECT * FROM logs"
    params = []
    
    if start_date and end_date:
        query += " WHERE date(timestamp) BETWEEN ? AND ?"
        params.extend([start_date, end_date])
    elif start_date:
        query += " WHERE date(timestamp) >= ?"
        params.append(start_date)
    elif end_date:
        query += " WHERE date(timestamp) <= ?"
        params.append(end_date)
    
    query += " ORDER BY timestamp DESC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return rows

def insert_log(timestamp, host_name, host_ip, status):
    """Insert new log entry"""
    conn = sqlite3.connect('log.db')
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO logs (timestamp, host_name, host_ip, status) VALUES (?, ?, ?, ?)",
        (timestamp, host_name, host_ip, status)
    )
    conn.commit()
    conn.close()

def validate_ip(ip):
    """Validasi format alamat IPv4"""
    pattern = r'^(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})$'
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(octet) <= 255 for octet in ip.split('.'))

def check_ip_status(ip):
    """Cek status IP dengan ping3, return 'UP' atau 'DOWN'."""
    if not validate_ip(ip):
        return 'INVALID'
    try:
        latency = ping(ip, timeout=1)
        return 'UP' if latency is not None else 'DOWN'
    except Exception:
        return 'ERROR'
    
def do_ping_all_hosts():
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for host in HOSTS:
        latency = ping_host(host['ip'])
        status = 'UP' if latency is not None else 'DOWN'
        insert_log(now, host['name'], host['ip'], status)
        if status == 'DOWN':
            send_telegram_message(f"❌ DOWN - {host['name']} ({host['ip']})")


def start_monitoring_loop():
    while True:
        if state.monitoring_active:
            for host in HOSTS:
                status = check_ip_status(host['ip'])
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                insert_log(timestamp, host['name'], host['ip'], status)

                # Kirim notifikasi hanya jika status DOWN
                if status == 'DOWN':
                    message = f"❌ DOWN - {host['name']} ({host['ip']})"
                    send_telegram_message(message)

        time.sleep(10)  # jeda antar pengecekan

