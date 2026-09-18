# SIH PS 013 - Real-Time Passive Detection Mode & Demo Guide

This system supports a **Real-Time Passive Detection Mode** that seamlessly analyzes live network traffic flowing through the host machine's interface without altering or blocking any packets.

The live collector is fully passive: it does **NOT** inject, drop, intercept, or modify packets in any way. It aggregates observed traffic into configurable temporal windows and evaluates the exact same Feature Engineering, Rule Engine, and ML Engine (Random Forest + Isolation Forest) as the offline PCAP analyzer.

---

## 1. Prerequisites & Permissions

Because this system uses raw sockets to sniff layer-2/layer-3 traffic, it requires appropriate OS-level permissions.

### **Windows**
1. **Npcap / WinPcap:** You must install [Npcap](https://npcap.com/) (recommended) or legacy WinPcap. Make sure to check "Install Npcap in WinPcap API-compatible Mode" during installation.
2. **Administrator Privileges:** The backend Python process (`uvicorn`) **must** be launched from a terminal running as **Administrator**. Without elevation, the capture engine will immediately throw a layer 2 permission error.

### **Linux**
1. Ensure `libpcap` is installed (`sudo apt install libpcap-dev`).
2. Run the backend with `sudo` or grant the python binary network capabilities: 
   `sudo setcap cap_net_raw,cap_net_admin=eip /path/to/python`

---

## 2. Identifying the Correct Network Interface

The Live Monitor UI will automatically query the OS for available network interfaces and populate a dropdown list. 
On Windows, these appear as unique UUID strings (e.g., `\Device\NPF_{UUID}`). 

**How to find your active interface:**
1. Open PowerShell or Command Prompt.
2. Run `ipconfig /all` (Windows) or `ifconfig` / `ip a` (Linux).
3. Identify the interface connected to the network you intend to monitor (e.g., "Ethernet 2" or "Wi-Fi").
4. If testing locally, you can select your loopback interface.

---

## 3. How to Perform the Authorized Real-Time Demo

To demonstrate real-time detection without affecting production services, use **two isolated machines** on a private subnet (or virtual network).

*   **Machine A (Detector):** The machine running this SIH prototype backend and frontend.
*   **Machine B (Attacker/Tester):** A separate, authorized lab machine generating controlled traffic.

### **Demo Execution Steps:**
1. **Start the SIH Stack on Machine A:**
   * Launch the FastAPI backend as Administrator: `python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
   * Launch the Vite React frontend: `npm run dev`
2. **Initialize Capture:**
   * Open the React UI and navigate to the **Live Monitor** page (`/monitor`).
   * Select the correct listening network interface from the dropdown in the top right.
   * Click the **Start Passive Capture** button.
   * *Verify that the status changes to "CAPTURE ACTIVE" and "Packets Observed" begins to increment.*
3. **Generate Controlled Traffic (Machine B):**
   * Execute an authorized port scan targeting Machine A using Nmap:
     `nmap -sS -p 1-1000 <MACHINE_A_IP>`
   * *Or*, execute a controlled volumetric SYN flood using hping3:
     `sudo hping3 -S -p 80 --flood <MACHINE_A_IP>`
4. **Observe Detection (Machine A):**
   * Watch the Live Monitor UI. Every 5 seconds, the engine flushes the aggregated packet buffer into flow features.
   * If the traffic crosses the rule/ML thresholds (e.g., Risk > 30), a Live Detection event will instantly appear in the "Recent Live Alerts" table.
   * Click **Investigate** to jump to the detailed threat forensics page showing specific evidence.
5. **Conclude Test:**
   * Stop the test traffic on Machine B.
   * Click **Stop Capture** on the Live Monitor UI on Machine A.

---

## 4. Troubleshooting

*   **"CAPTURE ERROR: Sniffing and sending packets is not available at layer 2"**
    *   **Cause:** Npcap is not installed, or the backend terminal lacks Administrator privileges.
    *   **Fix:** Install Npcap and run the command prompt as Administrator.
*   **Capture is Active, but "Packets Observed" stays at 0:**
    *   **Cause:** You selected the wrong network interface (e.g., a disconnected virtual adapter), or Windows Firewall is blocking incoming raw packets.
    *   **Fix:** Try a different interface from the dropdown list. If testing from Machine B, ensure Machine A's firewall allows ICMP/TCP traffic on the testing ports.
*   **Alerts are not generating during a test:**
    *   **Cause:** The traffic isn't severe enough to cross the risk threshold, or the Machine B is targeting an IP address not associated with the selected capture interface.
    *   **Fix:** Verify Machine B is actually reaching Machine A. Increase the intensity of the test script to ensure `packets_per_second` > 500 or `unique_dst_ports` > 15.
