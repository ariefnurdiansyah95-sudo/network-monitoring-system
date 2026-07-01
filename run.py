from threading import Thread
from app.database import init_db
from app.scheduler import run_scheduler
from app import create_app  # Tidak perlu import socketio
from app import state
from app.monitor import start_monitoring_loop
import threading

app = create_app()

# Start thread (loop-nya akan idle karena monitoring_active = False)
threading.Thread(target=start_monitoring_loop, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)