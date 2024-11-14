
# Type Beats Trend Prediction

## Overview

This project is a **distributed forecasting system** designed to predict trending **type beats** on YouTube. The system scrapes real-time data, processes it using machine learning models, and provides up-to-date insights into which beats are likely to trend in the next 24 hours. This application is perfect for beatmakers who want to stay ahead of trends and quickly identify the most popular beats on YouTube to save time and capitalize on emerging trends.

The system consists of the following components:
- **Spring Boot API** for scraping YouTube's API, storing metadata in a MySQL database, and serving APIs for the frontend.
- **Python** scripts for machine learning, data cleaning, preprocessing, and custom SQL queries.
- **Nginx** reverse proxy for serving the HTML frontend.

The architecture is distributed across multiple **droplets** (or virtual machines) to separate concerns and scale each component independently.

## Key Features
- **Trending Type Beats Prediction**: Predicts the top 'type beats' based on YouTube engagement data such as views, likes, and comments.
- **Real-time Data Processing**: Continuously scrapes and aggregates data on trending beats, providing up-to-date predictions.
- **Machine Learning**: Uses an LSTM model to forecast trends based on historical engagement data.
- **Cron Jobs**: Automated Python scripts run every 2 hours to clean, preprocess, and analyze data using custom SQL queries for trend prediction.
- **Nginx Reverse Proxy**: Exposes APIs and serves the frontend through a reverse proxy for enhanced performance.

## System Architecture

This application is distributed across multiple droplets:
1. **Spring Boot Instance (Droplet 1)**: Scrapes YouTube's API and exposes an API for the frontend.
2. **MySQL Instance (Droplet 2)**: Stores metadata scraped from YouTube in a MySQL database.
3. **Python Instance (Droplet 3)**: Runs a cron job every 2 hours to clean and preprocess data, execute custom SQL queries, and run the machine learning model for trend prediction.

### Distributed Data Flow
- The Spring Boot application scrapes YouTube data every hour, storing the results in a MySQL database.
- Every 2 hours, a Python script runs a cron job that aggregates, cleans, and preprocesses the data, running machine learning models to predict trends.
- The predictions are stored and served by the Spring Boot API, which the frontend consumes for real-time insights.
- Data communication between the services is handled over HTTP/HTTPS with each component running on a separate server instance for better scalability and performance.

## Getting Started

To get started with this project and use it for your own 'type beats' trend predictions, follow the instructions below.

### Prerequisites

Before you begin, you will need the following:
- **Java 11 or later**: For running Spring Boot applications.
- **MySQL**: Set up a MySQL database to store YouTube metadata.
- **Python 3.7+**: Required for running the machine learning model and data processing.
- **YouTube API Key**: To access YouTube's API and gather data.
- **Nginx**: For reverse proxying requests and serving the frontend.
- **Cron Jobs**: For automating periodic tasks.

### Setting Up the Spring Boot Application

1. Clone the repository and build the Spring Boot application:
   ```bash
   git clone <repository_url>
   cd <project_directory>
   ./mvnw clean install
   ```

2. Update the configuration files with your YouTube API credentials and MySQL database details:
   - `application.properties` in `src/main/resources`:
     ```properties
     youtube.api.key=<YOUR_YOUTUBE_API_KEY>
     spring.datasource.url=jdbc:mysql://<MYSQL_HOST>:<MYSQL_PORT>/<DATABASE_NAME>
     spring.datasource.username=<MYSQL_USERNAME>
     spring.datasource.password=<MYSQL_PASSWORD>
     ```

3. Run the Spring Boot application:
   ```bash
   ./mvnw spring-boot:run
   ```

### Setting Up the Python Script for Machine Learning

1. Clone the repository and set up a Python virtual environment:
   ```bash
   git clone <repository_url>
   cd <project_directory>
   python3 -m venv myenv
   source myenv/bin/activate
   ```

2. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Update the configuration files for the cron job and MySQL credentials.

4. Set up a cron job for the Python script:
   - Edit your crontab to run the script every 2 hours:
     ```bash
     crontab -e
     ```
     Add the following line to execute the script every 2 hours:
     ```bash
     0 */2 * * * source /home/scripts/myenv/bin/activate && /home/scripts/myenv/bin/python /home/scripts/run_analysis.py >> /home/scripts/log.txt 2>&1
     ```

5. The Python script will now run every 2 hours to preprocess and analyze the data, executing custom SQL queries and running the machine learning model.

### Setting Up Nginx Reverse Proxy

1. Install Nginx on your server:
   ```bash
   sudo apt update
   sudo apt install nginx
   ```

2. Configure Nginx to reverse proxy requests to the Spring Boot application and serve the frontend:
   - Edit the default configuration file:
     ```bash
     sudo nano /etc/nginx/sites-available/default
     ```
   - Replace the contents with the following:
     ```nginx
     server {
         listen 80;
         server_name <YOUR_DOMAIN_OR_IP>;

         location / {
             root /var/www/html;
             index index.html;
         }

         # Reverse proxy for Spring Boot API
         location /api/ {
             proxy_pass http://<SPRING_BOOT_IP>:8080/;
             proxy_set_header Host $host;
             proxy_set_header X-Real-IP $remote_addr;
             proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
             proxy_set_header X-Forwarded-Proto $scheme;
         }
     }
     ```

3. Restart Nginx:
   ```bash
   sudo systemctl restart nginx
   ```

### Testing the System

- After setting up the system, you can access the **frontend** via the Nginx reverse proxy on `http://<YOUR_DOMAIN_OR_IP>`.
- The Spring Boot application will continue scraping data every hour, and the Python cron job will run every 2 hours to update the predictions.
- The machine learning model will provide real-time insights into which 'type beats' are trending and forecast the next top beats.

## Future Enhancements
- **Real-Time Data Updates**: Incorporate WebSockets or other real-time data streaming technologies to push updates instantly to the frontend.
- **More Advanced Machine Learning Models**: Enhance the model by incorporating additional features or training on larger datasets.
- **Dashboard and Visualizations**: Create a more interactive dashboard for content creators to explore trend predictions.

