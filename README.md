# SE4AS_Autonomous_Greenhouse
# SE4AS_Autonomous_Greenhouse

## Project Overview
The SE4AS Autonomous Greenhouse project aims to create an intelligent system for managing greenhouse environments autonomously using the MAPE-K architecture. The system leverages various sensors, data analysis, and machine learning to optimize plant growth conditions.

## Project Structure
The project is organized into several directories, each serving a specific purpose:

- **analyzer/**: Contains the analysis scripts and configurations.
  - `analyzer.py`: Main analysis script.
  - `Dockerfile`: Docker configuration for the analyzer.
  - `greenhouse_threshold.json`: Configuration file for greenhouse thresholds.
  - `requirements.txt`: Python dependencies for the analyzer.

- **executor/**: Contains the execution scripts and configurations.
  - `executor.py`: Main execution script.
  - `Dockerfile`: Docker configuration for the executor.
  - `sector_config.json`: Configuration file for sector-specific settings.
  - `requirements.txt`: Python dependencies for the executor.

- **grafana/**: Contains Grafana dashboards and provisioning configurations.

- **influxdb/**: Contains InfluxDB engine and database files.

- **Knowledge/**: Contains knowledge management scripts and configurations.
  - `manage_knowledge.py`: Script for managing knowledge base.
  - `Dockerfile`: Docker configuration for knowledge management.
  - `requirements.txt`: Python dependencies for knowledge management.

- **managed_resources/**: Contains managed resources and related configurations.

- **monitor/**: Contains monitoring scripts and configurations.

- **mosquitto/**: Contains Mosquitto MQTT broker configurations.

- **planner/**: Contains planning scripts and configurations.

- **shared_config/**: Contains shared configuration files.

- **shared_files/**: Contains shared files used across the project.

## Getting Started
To get started with the project, follow these steps:

1. Clone the repository:
    ```sh
    git clone <repository-url>
    ```

2. Navigate to the project directory:
    ```sh
    cd SE4AS_Autonomous_Greenhouse
    ```

3. Build and run the Docker containers:
    ```sh
    docker-compose up --build
    ```

## Requirements
- Docker
- Docker Compose
- Python 3.8+

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request.

## License
This project is licensed under the MIT License.