# ⚡ Free VPN Gateway & Auto-Failover Manager (Per-Browser Dedicated)

A dedicated, lightweight local proxy gateway and auto-failover manager designed to route internet traffic for **specific applications or browsers (e.g. Mozilla Firefox)** through fast, verified public VPN nodes — while keeping your normal system traffic (Google Chrome, Edge, games, office apps) on your direct ISP internet connection.

---

## 🌟 Key Features

1. **Application-Level Isolation (No System-Wide Network Override):**
   - Keeps your primary network connection intact.
   - Provides local proxy gateways:
     - **HTTP Proxy:** `127.0.0.1:10808`
     - **SOCKS5 Proxy:** `127.0.0.1:10809`
   - Point any browser (Firefox, Chromium profile) or CLI tool (`curl -x http://127.0.0.1:10808`) to route traffic through foreign IP nodes (Singapore, Japan, US, Europe) while the rest of your system stays on your local IP.
2. **Auto-Scraping & Verification:**
   - Scrapes and tests active public proxy nodes (VLESS, Shadowsocks, Trojan, Hysteria2) from maintained daily feeds.
   - Measures real HTTP round-trip latency and active exit IPs.
3. **Smart Auto-Failover Daemon:**
   - Continuously monitors connection health. If the active VPN node drops or encounters timeout errors, the background watcher immediately switches to the next fastest server in `< 2 seconds` without requiring browser reconfiguration.
4. **Interactive Modern Web Dashboard:**
   - Clean UI running on `http://localhost:8088`.
   - Displays real-time connection status, exit IP, latency ping, country flags, Quick Connect button, manual failover button, and searchable server lists.

---

## 📁 Project Structure

```
dev_vpn/
├── dashboard.html          # Responsive Web UI dashboard
├── vpn_server.py           # HTTP Server & REST API backend (:8088)
├── vpn_controller.py       # Mihomo proxy process management & switching logic
├── vpn_fetcher_v2.py       # Scrapes & probes public proxy node feeds
├── vpn_speedtest.py        # Latency & ping tester
├── vpn_scheduler.py        # Automated update scheduler
├── download_binaries.sh    # Script to download Mihomo (Clash.Meta) binary
├── run_vpn.sh              # Quick start runner
├── stop_vpn.sh             # Quick stop script
├── requirements.txt        # Python dependencies
└── vpn.json                # Pre-seeded verified servers list
```

---

## 🚀 Getting Started

### 1. Prerequisites
- Linux or WSL (Windows Subsystem for Linux)
- Python 3.10+
- `curl` and `gzip`

### 2. Installation

Clone this repository and install Python dependencies:

```bash
git clone https://github.com/dandapurwidyatmokolaw-ux/dev_vpn.git
cd dev_vpn

pip install -r requirements.txt
```

### 3. Download Mihomo Core Binary

Download the compiled Mihomo (Clash.Meta) proxy core:

```bash
chmod +x download_binaries.sh
./download_binaries.sh
```

---

## 💻 Usage

### 1. Start the VPN Server & Dashboard

Run:
```bash
python3 vpn_server.py
```
*(Or in background via `./run_vpn.sh`)*

Open your browser and navigate to:
👉 **`http://localhost:8088`**

Click **"Quick Connect"** or choose any specific country/server from the list.

### 2. Configure Firefox for Dedicated VPN Access

To route only Firefox through the proxy while other apps use your normal internet:

1. Open **Mozilla Firefox**.
2. Go to **Settings** &rarr; search for **`proxy`**.
3. Under *Network Settings*, click **Settings...**.
4. Choose **Manual proxy configuration**:
   - **HTTP Proxy:** `127.0.0.1` | **Port:** `10808`
   - Check the box: **"Also use this proxy for HTTPS"**
5. Click **OK**.

**Verification:**
- In Firefox, open [ipinfo.io](https://ipinfo.io) &rarr; Shows your VPN Country & IP (e.g. Singapore / Japan).
- In Chrome or Edge, open [ipinfo.io](https://ipinfo.io) &rarr; Shows your original local ISP IP.

### 3. Updating Server List

To fetch fresh server nodes and run speed benchmarks:
- Click the **"🔄 Update Servers"** button in the Web Dashboard, or
- Run via terminal:
  ```bash
  python3 vpn_scheduler.py --once
  ```

---

## 🛡️ WSL to Windows Host Port Forwarding (Optional)

If running inside WSL2 and accessing from a Windows host browser, ensure port `10808` and `8088` are accessible from Windows localhost:
```powershell
# Run in Windows PowerShell (Admin) if needed:
netsh interface portproxy add v4tov4 listenaddress=127.0.0.1 listenport=10808 connectaddress=127.0.0.1 connectport=10808
```

---

## 📄 License
MIT License. Free for open-source and personal use.
