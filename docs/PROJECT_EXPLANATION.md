# Project Explanation

## Threat Detection Methodology

This system relies on a hybrid detection pipeline designed specifically for unidirectional IP traffic where bidirectional TCP handshakes (SYN-ACK) may not be observable.

### 1. Ingestion Layer
- **Live Capture**: Uses `scapy.sniff` wrapping the Npcap driver. Interfaces are dynamically resolved to prevent staleness.
- **Offline PCAP**: Uses a fully isolated `pcap_worker.py` subprocess. This prevents global `scapy.arch` initializations from hanging the main server if the Npcap kernel driver is locked, ensuring robust file uploads.

### 2. Feature Engineering
Flows are aggregated using a 5-tuple (source IP, dest IP, source port, dest port, protocol) over a time window. To prevent false positives (such as "volumetric floods" from a single HTTP GET request that lasts 0.001 seconds), we aggregate destination-level metrics:
- `dst_packet_count`
- `dst_syn_count`

### 3. Detection Engine
1. **Rule-Based Engine**: Fast, deterministic rules for known threat signatures (e.g., > 200 SYN packets to a single destination within the time window triggers a `POSSIBLE_SYN_FLOOD`).
2. **Random Forest (Supervised ML)**: Evaluates the engineered features to classify the flow into known categories (NORMAL, SYN_FLOOD, PORT_SCAN).
3. **Isolation Forest (Unsupervised ML)**: Calculates an anomaly score. Flow vectors that deviate significantly from the training baseline receive high anomaly scores.

### 4. Risk Fusion
The `calculate_risk` function bounds all inputs logically. The final risk score (0-100) dictates the severity (LOW, MEDIUM, HIGH, CRITICAL). Real factual evidence (e.g., Random forest probability, Isolation forest score, SYN ratios) is persisted to the database to explain the alert to the SOC analyst.
