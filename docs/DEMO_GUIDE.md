# Demo Guide

This guide outlines how to demonstrate the SIH PS 013 Threat Detection project.

## Prerequisites
1. Start the backend: `cd backend && python -m uvicorn app.main:app --host 0.0.0.0 --port 8000`
2. Start the frontend: `cd frontend && npm run dev`
3. Access the dashboard at `http://localhost:5173`.

## Demo A: SYN Flood (Offline PCAP)
**Objective**: Show detection of a volumetric attack.
1. Navigate to **PCAP Analysis**.
2. Upload `test_traffic/syn_flood/syn_flood.pcap` (Controlled test PCAP).
3. Observe the analysis completing without blocking the UI.
4. Verify `POSSIBLE_SYN_FLOOD` alerts are generated.
5. Click **Investigate** on an alert to show the evidence (high SYN count, high risk score).

## Demo B: Port Scan (Offline PCAP)
**Objective**: Show reconnaissance detection.
1. Navigate to **PCAP Analysis**.
2. Upload `test_traffic/port_scan/port_scan.pcap` (Controlled test PCAP).
3. Verify `PORT_SCAN_RECONNAISSANCE` alerts are generated.

## Demo C: IoT-23 Research PCAP (Massive File Handling)
**Objective**: Demonstrate system resilience against large files.
1. Navigate to **PCAP Analysis**.
2. Upload `test_traffic/iot-23/2018-12-21-15-50-14-192.168.1.195.pcap`.
3. The system will safely parse the first 10,000 packets to prevent out-of-memory crashes and return a result rapidly, detecting anomalies from the research dataset.

## Demo D: Live Capture (Authorized Laboratory Traffic)
**Objective**: Show real-time passive ingestion.
*Note: This requires a healthy Npcap driver on Windows.*
1. Navigate to **Live Monitor**.
2. If the interface dropdown loads, select your active adapter and click **Start Capture**.
3. Generate normal HTTP traffic (e.g., browse a website). Observe that the traffic is classified as `NORMAL` and no false flood alerts are generated.
4. If Npcap is deadlocked at the OS level, the UI will cleanly display a "Live Capture Error" and the rest of the application (Dashboard, offline analysis) will remain fully operational.
