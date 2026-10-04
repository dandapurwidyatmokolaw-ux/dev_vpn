import time
import os
import sys
import argparse
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from vpn_fetcher import run_scraper
from vpn_speedtest import run_speedtest_benchmark

def update_cycle():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"\n[{timestamp}] Menjalankan siklus update server VPN & speed test...")
    try:
        run_scraper()
        run_speedtest_benchmark()
        print(f"[{timestamp}] Siklus update selesai dengan sukses!")
    except Exception as e:
        print(f"[{timestamp}] Error saat menjalankan siklus update: {e}")

def main():
    parser = argparse.ArgumentParser(description="VPN Server Auto-Update Scheduler")
    parser.add_argument("--interval", type=int, default=1800, help="Interval update dalam detik (default: 1800s / 30 menit)")
    parser.add_argument("--once", action="store_true", help="Jalankan satu kali saja tanpa looping")
    args = parser.parse_args()

    if args.once:
        update_cycle()
        return

    print(f"Auto-Update Scheduler aktif. Interval pembaruan: {args.interval} detik ({args.interval // 60} menit).")
    while True:
        update_cycle()
        print(f"\nMenunggu {args.interval} detik hingga pembaruan berikutnya (tekan Ctrl+C untuk berhenti)...")
        time.sleep(args.interval)

if __name__ == "__main__":
    main()
