"""
US BTS Flight Delay Analytics & Prediction Dashboard Launcher
Starts both the FastAPI Python backend and Next.js frontend concurrently.
"""

import subprocess
import sys
import os
import time
import signal

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
FRONTEND_DIR = os.path.join(ROOT_DIR, "frontend")
V1_DIR = os.path.join(ROOT_DIR, "v1")

def main():
    print("=" * 70)
    print("  US BTS FLIGHT DELAY ANALYTICS & WAREHOUSE DASHBOARD")
    print("  Theme: Aesthetic Royal Blue & White")
    print("  Backend: FastAPI (Reusing v1 OLAP & Medallion Pipeline)")
    print("  Data Source: Databricks Unity Catalog Gold Fact (30.7M Flights)")
    print("  Frontend: Next.js 16 + Tailwind CSS")
    print("=" * 70)

    # 1. Start Python FastAPI Backend
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "src.api:app",
        "--app-dir",
        "v1",
        "--host",
        "127.0.0.1",
        "--port",
        "8000",
        "--reload"
    ]
    print("\n[1/2] Starting Python FastAPI Backend on http://127.0.0.1:8000 ...")
    backend_proc = subprocess.Popen(
        backend_cmd,
        cwd=ROOT_DIR,
        shell=False
    )

    time.sleep(2)

    # 2. Start Next.js Frontend
    frontend_cmd = "npm run dev"
    print("\n[2/2] Starting Next.js Frontend on http://localhost:3000 ...")
    frontend_proc = subprocess.Popen(
        frontend_cmd,
        cwd=FRONTEND_DIR,
        shell=True
    )

    print("\n" + "=" * 70)
    print("  SUCCESSFULLY LAUNCHED:")
    print("  -> Frontend: http://localhost:3000")
    print("  -> Backend API: http://127.0.0.1:8000/docs (Interactive Swagger)")
    print("  -> Data Source: Databricks Gold (flight_delay_dwm.gold.fact_flight)")
    print("  Press Ctrl+C to stop both servers.")
    print("=" * 70 + "\n")

    try:
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("[WARNING] Backend process stopped.")
                break
            if frontend_proc.poll() is not None:
                print("[WARNING] Frontend process stopped.")
                break
    except KeyboardInterrupt:
        print("\n[SHUTDOWN] Stopping all servers gracefully...")
    finally:
        try:
            backend_proc.terminate()
            backend_proc.wait(timeout=3)
        except Exception:
            pass

        try:
            # On Windows shell=True spawns a cmd/node child
            subprocess.run(f"taskkill /F /T /PID {frontend_proc.pid}", shell=True, capture_output=True)
        except Exception:
            pass

        print("[SHUTDOWN] Finished.")

if __name__ == "__main__":
    main()
