"""
Crop Recommendation & Yield Prediction System
Self-Healing Root Runner & Zero-Failure Launcher Entrypoint.
Bennett University • TEAM ROCKET (2025-2026)
"""

import os
import sys
import time
import socket
import urllib.request
import urllib.error
import subprocess
import threading
import webbrowser

# Project Paths
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if sys.platform == "win32":
    VENV_DIR = os.path.join(PROJECT_ROOT, "venv", "Scripts")
    VENV_PYTHON = os.path.join(VENV_DIR, "python.exe")
    VENV_PYTHONW = os.path.join(VENV_DIR, "pythonw.exe")
else:
    VENV_DIR = os.path.join(PROJECT_ROOT, "venv", "bin")
    VENV_PYTHON = os.path.join(VENV_DIR, "python")
    VENV_PYTHONW = os.path.join(VENV_DIR, "python")

# Always operate from the project root directory
os.chdir(PROJECT_ROOT)


class SafeLogWriter:
    """Safe writer for windowless background execution (pythonw.exe) that logs to file and never crashes."""
    def __init__(self, log_path):
        self.log_path = log_path
        self._f = None
        try:
            self._f = open(log_path, "a", encoding="utf-8", errors="replace", buffering=1)
        except Exception:
            pass

    def write(self, msg):
        if self._f and msg:
            try:
                self._f.write(msg)
            except Exception:
                pass

    def flush(self):
        if self._f:
            try:
                self._f.flush()
            except Exception:
                pass

    def reconfigure(self, **kwargs):
        pass


is_windowless = "pythonw" in sys.executable.lower()

if is_windowless or sys.stdout is None or not hasattr(sys.stdout, "write"):
    log_file = os.path.join(PROJECT_ROOT, "server.log")
    sys.stdout = SafeLogWriter(log_file)
    sys.stderr = SafeLogWriter(log_file)
else:
    # Configure safe encoding for standard Windows Console (prevent CP1252 charmap crashes)
    if sys.platform == "win32":
        try:
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', errors='replace')
                sys.stderr.reconfigure(encoding='utf-8', errors='replace')
        except Exception:
            pass

# Auto-redirect to dedicated virtual environment if run with system/global python
if os.path.exists(VENV_DIR):
    current_exe = os.path.abspath(sys.executable).lower()
    known_venvs = [os.path.abspath(VENV_PYTHON).lower(), os.path.abspath(VENV_PYTHONW).lower()]
    if current_exe not in known_venvs:
        target_exe = VENV_PYTHONW if is_windowless else VENV_PYTHON
        print("[*] Re-launching Crop Recommendation & Yield Prediction System inside dedicated virtual environment...")
        try:
            ret = subprocess.call([target_exe, __file__] + sys.argv[1:])
            sys.exit(ret)
        except Exception as e:
            print(f"[!] Error switching to virtual environment: {e}")

# Ensure project root is in sys.path
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def is_port_in_use(port, host="127.0.0.1"):
    """Check if a TCP port is currently occupied or cannot be bound."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("0.0.0.0", port))
            return False
        except OSError:
            return True


def is_server_healthy(port=5000, host="127.0.0.1"):
    """Check if the Crop Recommendation Flask server is active and returning healthy status."""
    url = f"http://{host}:{port}/api/health"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "CropSystemHealthCheck/1.0"})
        with urllib.request.urlopen(req, timeout=1.5) as resp:
            if resp.status == 200:
                body = resp.read().decode('utf-8', errors='ignore')
                return "healthy" in body
    except Exception:
        return False
    return False


def free_port(port):
    """
    On Windows, finds and cleanly terminates any stale or zombie PID holding the target port.
    Prevents [WinError 10048] socket collisions.
    """
    if sys.platform != "win32":
        return

    try:
        cmd = 'netstat -ano -p tcp'
        output = subprocess.check_output(cmd, shell=True, text=True, errors='ignore')
        current_pid = os.getpid()
        killed_any = False

        for line in output.splitlines():
            line = line.strip()
            if not line:
                continue
            parts = line.split()
            if len(parts) >= 5 and parts[0].upper() == "TCP":
                local_addr = parts[1]
                state = parts[3].upper()
                pid = parts[4]
                if local_addr.endswith(f":{port}") and state == "LISTENING":
                    try:
                        pid_int = int(pid)
                        if pid_int != current_pid and pid_int > 4:
                            print(f"[*] Port {port} is occupied by stale process (PID: {pid_int}). Auto-terminating...")
                            subprocess.run(["taskkill", "/F", "/PID", str(pid_int)],
                                           capture_output=True, text=True)
                            killed_any = True
                    except ValueError:
                        pass

        if killed_any:
            time.sleep(1.0)
    except Exception as e:
        print(f"[!] Note: Automatic port cleanup encountered: {e}")


def get_available_port(preferred_port=5000):
    """
    Ensures an available port. Attempts preferred port first (freeing stale PIDs if needed).
    Falls back gracefully to alternative ports if necessary.
    """
    # 1. If preferred port is completely free, use it
    if not is_port_in_use(preferred_port):
        return preferred_port

    # 2. If preferred port is already running our healthy server, report it
    if is_server_healthy(preferred_port):
        return preferred_port

    # 3. Port is occupied but not healthy -> try to free it
    print(f"[*] Port {preferred_port} in use. Attempting self-healing recovery...")
    free_port(preferred_port)

    if not is_port_in_use(preferred_port):
        print(f"[+] Successfully recovered port {preferred_port}.")
        return preferred_port

    # 4. If still blocked, cycle through fallbacks
    for alt_port in [5001, 5002, 5050, 8080]:
        if not is_port_in_use(alt_port):
            print(f"[!] Preferred port {preferred_port} busy. Using fallback port {alt_port}.")
            return alt_port

    return preferred_port


def wait_and_launch_browser(port):
    """
    Monitors the server until it passes the health check, then opens the web browser.
    Ensures browser only opens when models and Flask routes are 100% ready.
    """
    url = f"http://localhost:{port}"
    max_wait_seconds = 15
    start_time = time.time()

    while time.time() - start_time < max_wait_seconds:
        if is_server_healthy(port):
            print(f"[+] Crop Recommendation & Yield Prediction System is LIVE at {url}")
            print(f"[*] Opening your default web browser...")
            try:
                webbrowser.open(url)
            except Exception as e:
                print(f"[!] Could not auto-launch browser ({e}). Please navigate to {url}")
            return
        time.sleep(0.3)

    # Fallback open if timeout reached
    try:
        webbrowser.open(url)
    except Exception:
        pass


def main():
    print("=" * 72)
    print("          Crop Recommendation & Yield Prediction System")
    print("             Bennett University - TEAM ROCKET (2025-2026)")
    print("=" * 72)

    target_port = int(os.environ.get("PORT", 5000))

    # Self-Healing Check: If server is already running and healthy, simply open browser!
    if is_port_in_use(target_port) and is_server_healthy(target_port):
        print(f"\n[+] The server is ALREADY running and healthy at http://localhost:{target_port}")
        print(f"[*] Bringing up web dashboard in your browser...")
        webbrowser.open(f"http://localhost:{target_port}")
        print("[+] Application is ready. (To shut down the background server, run STOP_APP.bat)\n")
        return

    # Resolve port conflicts
    chosen_port = get_available_port(target_port)

    # Start browser watcher in background thread
    threading.Thread(target=wait_and_launch_browser, args=(chosen_port,), daemon=True).start()

    # Import Flask application
    from web.app import app

    print(f"[*] Serving web dashboard at: http://localhost:{chosen_port}")
    print("[*] Press CTRL+C to stop the server.\n")

    try:
        app.run(host="0.0.0.0", port=chosen_port, debug=False)
    except OSError as e:
        if "10048" in str(e) or getattr(e, "errno", None) == 48 or "already in use" in str(e).lower():
            print(f"\n[!] Port collision detected ({e}). Running immediate self-healing recovery...")
            free_port(chosen_port)
            fallback_port = get_available_port(chosen_port + 1)
            time.sleep(0.5)
            app.run(host="0.0.0.0", port=fallback_port, debug=False)
        else:
            raise


if __name__ == "__main__":
    main()
