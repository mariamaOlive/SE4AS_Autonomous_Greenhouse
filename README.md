# Greenhouse Autonomous System - README

## Introduction
The Greenhouse Autonomous System optimizes crop growth using the MAPE-K framework (Monitor, Analyze, Plan, Execute, Knowledge). It autonomously manages temperature, humidity, light, and CO₂ levels to maintain optimal plant growth conditions. A microservice architecture with Docker containers is employed, and components communicate via an MQTT broker for real-time data exchange.

<p align="center">
  <img src="system_autonomous_arch.png" alt="System Architecture" width="800">
</p>

---

## Technologies Used
- **Docker:** Manages microservice containerization.
- **Eclipse Mosquitto:** Handles real-time MQTT messaging.
- **InfluxDB:** Stores time-series environmental data.
- **Grafana:** Displays real-time and historical data on dashboards.
- **Python:** Implements monitoring, analysis, and execution services.

---

## Getting Started
### Prerequisites
- Docker and Docker Compose installed.

### Installation Steps
1. Clone the project repository:
   ```bash
   git clone https://github.com/yourusername/greenhouse-autonomous-system.git
   cd greenhouse-autonomous-system
   ```
2. Start the Docker containers:
   ```bash
   docker-compose up --build
   ```
3. Access the Grafana Dashboard:
   - URL: `http://localhost:3000`
   - Default credentials: `admin` / `admin`

---

## Usage
- **View Real-Time Data:** Use the Grafana dashboard.
- **Modify Thresholds:** Edit configuration files.
- **Check Logs:** View Docker container logs.

---

## Authors
- Mariama Celi S. de Oliveira
- Motunrayo Osatohanmen Ibiyo

## Professor
- Davide Di Ruscio (Software Engineering for Autonomous Systems)

