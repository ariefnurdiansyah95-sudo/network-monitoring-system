import re
from flask import Blueprint, app, flash, redirect, render_template, request, jsonify, send_file, url_for
from app import state
from app.database import get_db
from app.monitor import get_all_logs, insert_log, get_filtered_logs
from app.utils import add_host_to_config
import subprocess
import time
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
from io import BytesIO
from flask import jsonify
from app.config import HOSTS  # pastikan ini berisi daftar host seperti [{'name': ..., 'ip': ...}, ...]
from app.state import monitoring_active

web_bp = Blueprint('web_bp', __name__)

monitoring_active = False  # global status

def check_ip_status(ip):
    try:
        response = subprocess.call(['ping', '-n', '1', ip], 
                                stdout=subprocess.DEVNULL, 
                                stderr=subprocess.DEVNULL)
        return 'UP' if response == 0 else 'DOWN'
    except Exception:
        return 'DOWN'

@web_bp.route('/')
def index():
    logs = get_all_logs()
    return render_template('dashboard.html', logs=logs)

@web_bp.route('/add_ip_once', methods=['POST'])
def add_ip_once():
    try:
        ip = request.form['ip_address']  # Gunakan request.form[] untuk error handling
        name = request.form.get('host_name', ip)
        
        if not ip:
            flash('Alamat IP tidak boleh kosong', 'error')
            return redirect(url_for('web_bp.index'))
            
        # Validasi format IP
        if not re.match(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$', ip):
            flash('Format IP tidak valid', 'error')
            return redirect(url_for('web_bp.index'))
        
        status = check_ip_status(ip)
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        insert_log(timestamp, name, ip, status)
        
        flash(f'IP {ip} berhasil dicek: {status}', 'success')
        return redirect(url_for('web_bp.index'))
        
    except Exception as e:
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('web_bp.index'))

@web_bp.route('/add_host', methods=['POST'])
def add_host():
    ip = request.form.get('ip_address')
    name = request.form.get('host_name') or ip

    if ip:
        success = add_host_to_config(ip, name)
        if success:
            flash(f'IP {ip} berhasil ditambahkan ke config.py')
        else:
            flash(f'IP {ip} sudah ada atau gagal ditambahkan')
    else:
        flash('IP tidak valid')
    return redirect('/')
    
    return redirect('/')

# API Endpoints
@web_bp.route('/api/status_summary')
def api_status_summary():
    logs = get_all_logs()
    return jsonify({
        'total': len(logs),
        'up': sum(1 for log in logs if log['status'] == 'UP'),
        'down': sum(1 for log in logs if log['status'] == 'DOWN')
    })

@web_bp.route('/api/logs/summary_grouped')
def api_logs_summary_grouped():
    start = request.args.get('start')
    end = request.args.get('end')
    
    logs = get_filtered_logs(start, end) if (start and end) else get_all_logs()
    
    # Process data for Chart.js
    dates = sorted({log['timestamp'][:10] for log in logs})
    hosts = sorted({log['host_ip'] for log in logs})
    
    datasets = []
    colors = ['#4e73df', '#1cc88a', '#36b9cc', '#f6c23e', '#e74a3b']
    
    for i, host in enumerate(hosts):
        host_data = {
            'label': f"{host} - UP",
            'data': [sum(1 for log in logs 
                      if log['host_ip'] == host 
                      and log['status'] == 'UP'
                      and log['timestamp'].startswith(date)) 
                    for date in dates],
            'backgroundColor': colors[i % len(colors)]
        }
        datasets.append(host_data)
        
        host_data = {
            'label': f"{host} - DOWN",
            'data': [sum(1 for log in logs 
                      if log['host_ip'] == host 
                      and log['status'] == 'DOWN'
                      and log['timestamp'].startswith(date)) 
                    for date in dates],
            'backgroundColor': f"{colors[i % len(colors)]}80"  # Add transparency
        }
        datasets.append(host_data)
    
    return jsonify({
        'labels': dates,
        'datasets': datasets
    })

@web_bp.route('/api/ips')
def api_ips():
    conn = sqlite3.connect('log.db')
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT host_ip FROM logs")
    ips = [row[0] for row in cur.fetchall()]
    conn.close()
    return jsonify(ips)

@web_bp.route('/api/ip_history')
def api_ip_history():
    ip = request.args.get('ip')
    start = request.args.get('start')
    end = request.args.get('end')
    
    conn = sqlite3.connect('log.db')
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    query = """
        SELECT 
            DATE(timestamp) as date,
            host_ip,
            status,
            COUNT(*) as count
        FROM logs
        WHERE host_ip = ?
    """
    params = [ip]
    
    if start and end:
        query += " AND date BETWEEN ? AND ?"
        params.extend([start, end])
    
    query += " GROUP BY date, status ORDER BY date"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in rows])

@web_bp.route('/api/export_excel')
def api_export_excel():
    ip = request.args.get('ip')
    start = request.args.get('start')
    end = request.args.get('end')
    
    conn = sqlite3.connect('log.db')
    
    query = """
        SELECT 
            timestamp as "Timestamp",
            host_ip as "IP Address",
            host_name as "Hostname",
            status as "Status"
        FROM logs
    """
    params = []
    
    if ip:
        query += " WHERE host_ip = ?"
        params.append(ip)
        if start and end:
            query += " AND DATE(timestamp) BETWEEN ? AND ?"
            params.extend([start, end])
    elif start and end:
        query += " WHERE DATE(timestamp) BETWEEN ? AND ?"
        params.extend([start, end])
    
    query += " ORDER BY timestamp DESC"
    
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False)
    writer.close()
    output.seek(0)
    
    filename = f"network_logs_{ip or 'all'}_{start or ''}_to_{end or ''}.xlsx"
    return send_file(
        output,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=filename
    )

@web_bp.route('/api/trend_availability')
def api_trend_availability():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT DATE(timestamp) as date, COUNT(*) as total_down
        FROM logs
        WHERE status = 'DOWN'
        GROUP BY DATE(timestamp)
        ORDER BY date ASC
    """)
    rows = cur.fetchall()
    labels = [row['date'] for row in rows]
    data = [row['total_down'] for row in rows]
    return jsonify({"labels": labels, "data": data})

@web_bp.route('/api/status_config_only')
def status_config_only():
    from app.config import HOSTS
    from app.database import get_db
    db = get_db()
    cur = db.cursor()

    up = 0
    down = 0
    total = len(HOSTS)

    for host in HOSTS:
        ip = host['ip']
        cur.execute("""
            SELECT status FROM logs
            WHERE host_ip = ?
            ORDER BY timestamp DESC LIMIT 1
        """, (ip,))
        row = cur.fetchone()
        if row and row['status'] == 'UP':
            up += 1
        else:
            down += 1

    return jsonify({'total': total, 'up': up, 'down': down})

@web_bp.route('/api/registered_hosts')
def api_registered_hosts():
    return jsonify(HOSTS)

@web_bp.route('/api/toggle_monitoring', methods=['POST'])
def toggle_monitoring():
    state.monitoring_active = not state.monitoring_active
    return jsonify({"active": state.monitoring_active})

@web_bp.route('/api/monitoring_status')
def monitoring_status():
    return jsonify({"active": state.monitoring_active})