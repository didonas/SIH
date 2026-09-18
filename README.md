# SIH PS 013 - Threat Detection in Unidirectional IP Traffic

## Overview
This project is an AI-based system designed to detect cyber threats in unidirectional network traffic. It is built using a FastAPI backend, a React/Vite frontend, and a hybrid detection engine utilizing Scapy, rule-based heuristics, Random Forest, and Isolation Forest models.

## Current Capabilities
- **Passive Live Capture**: Capable of passively capturing traffic via Windows Npcap. (Note: Npcap must be cleanly installed and accessible).
- **Offline PCAP Analysis**: Completely isolated from live capture. Supports analysis of small and large PCAP files (tested up to 120MB IoT-23 datasets).
- **Threat Detection**:
  - **Volumetric/SYN Floods**: Detected using host-based target aggregation to avoid false positives on short flows.
  - **Port Scans / Reconnaissance**: Detected via feature engineering.
  - **Anomalies**: Scored using Isolation Forest for outlier detection.
- **Risk Scoring**: Fuses rule scores, Random Forest probabilities, and Isolation Forest scores into a bounded 0-100 risk metric.

## Architecture
- **Frontend**: React 18, Tailwind CSS, Lucide Icons, Vite.
- **Backend**: Python 3, FastAPI, SQLAlchemy, SQLite, Scapy, scikit-learn.
- **Machine Learning**: Random Forest Classifier (supervised), Isolation Forest (unsupervised anomaly detection).

## Limitations & Boundaries
- **No Active Mitigation**: This is a passive monitoring and detection system. It does not drop packets or modify firewall rules.
- **Traffic Scope**: Designed for unidirectional analysis (e.g., analyzing inbound taps without requiring bidirectional session handshakes).
- **Not Production Scale**: Uses SQLite and local memory. Suitable for authorized laboratory traffic and research datasets, but not enterprise-scale inline production data without architecture scaling.
