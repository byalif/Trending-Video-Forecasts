# Beat Forecasting Tool - README

Welcome to the **Beat Forecasting Tool**! This project aims to predict the performance and trends of various music production videos and type beats on YouTube, focusing on key metrics like view counts, likes, and comments. This tool uses machine learning models to forecast future growth and performance based on past data, providing producers and beatmakers with valuable insights on potential future trends. Whether you're an aspiring music producer or just someone passionate about the music industry, this tool can help you better understand and predict the future success of your videos.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Technologies Used](#technologies-used)
- [How It Works](#how-it-works)
- [Setting Up and Running the Project](#setting-up-and-running-the-project)
  - [Spring Boot Backend Setup](#spring-boot-backend-setup)
  - [Python Flask App Setup](#python-flask-app-setup)
  - [Changing API Keys and Credentials](#changing-api-keys-and-credentials)
  - [Commands to Run](#commands-to-run)
- [Machine Learning Model](#machine-learning-model)
  - [LSTM Model Architecture](#lstm-model-architecture)
- [Future Improvements](#future-improvements)
- [License](#license)

## Project Overview

The **Beat Forecasting Tool** analyzes YouTube data related to music production videos and type beats. It collects data on videos and metrics like views, likes, and comments to calculate growth rates over the past 24 hours. This data is then used to predict future growth and trends for various artist types, including **type beats** like **Lil Baby Type Beat** or **Free Veeze X Lucki Type Beat**.

Key goals of this project:

- **Predict Future Growth**: By using historical data, the tool predicts future performance metrics (like view growth, like count, and comment count).
- **Categorize by Artist Type**: It automatically categorizes music videos based on artist names extracted from the video titles, which is essential for producers looking for trends in specific genres.
- **Track Video and Artist Performance**: It tracks the performance of videos and artist types over time, providing valuable insights to help producers make informed decisions.

## Features

- **Real-Time Data Collection**: The tool collects real-time metrics from YouTube videos, including view counts, like counts, comment counts, and timestamps.
- **Growth Prediction**: Using machine learning models, it predicts the future performance of each video based on current data.
- **Data Storage**: All historical and forecast data is stored in a MySQL database for efficient querying and analysis.
- **Artist Categorization**: Based on the video title, it dynamically categorizes the music type (e.g., “Lil Baby Type Beat”) to help track trends per genre.
- **API Integration**: The project integrates with external APIs for data retrieval (e.g., YouTube Data API) and stores results for later analysis.

## Technologies Used

- **Backend**: Spring Boot (Java)
  - MySQL for database management
  - Spring Data JPA for interacting with the database
  - REST APIs for integrating data
- **Machine Learning**: Python with TensorFlow
  - LSTM (Long Short-Term Memory) Model for time-series forecasting
  - Data pre-processing with **Pandas**, **NumPy**, and **MinMaxScaler**
- **Frontend**: Flask (Python)
  - Display analytics and forecasts
- **Deployment**: Docker for containerization
- **Database**: MySQL
- **Environment Variables**: For securely managing sensitive information (e.g., database credentials, API keys)

## How It Works

1. **Data Collection**: The system queries a MySQL database to retrieve videos and metrics (like view count, like count, etc.) from the `videos` and `metrics` tables.
2. **Artist Type Extraction**: Based on video titles, the system extracts the artist types (e.g., “Lil Baby Type Beat”) and adds them to the data.

3. **Growth Rate Calculation**: Growth rate is calculated based on changes in views, likes, and comments over the past 24 hours, using weighted values.

4. **Forecasting with Machine Learning**: An LSTM model is trained on the growth rate data to predict future growth for the top artist types. This involves creating sequences from historical data, scaling the data, and then using the model to predict the next 24 hours of growth.

5. **Database Storage**: The forecasted values are stored in the database for further analysis and tracking.

6. **API Integration**: The project integrates with a YouTube Data API to retrieve the necessary video metrics. The API key for accessing this API is configurable.

## Setting Up and Running the Project

To run this project, you'll need to set up two main components:

### Spring Boot Backend Setup

1. **Clone the repository**:

   ```bash
   git clone https://github.com/your-repository/beat-forecasting-tool.git
   cd beat-forecasting-tool
   ```

2. **Set up environment variables**:

   - Create a `.env` file in the root directory to securely store sensitive credentials such as your YouTube API key and database credentials. Example:

     ```
     DB_HOST=165.22.183.241
     DB_PORT=3306
     DB_USER=your-username
     DB_PASSWORD=your-password
     API_KEY=your-api-key
     ```

3. **Configure Spring Boot**:

   - In `application.properties`, replace sensitive values with references to the environment variables:

     ```properties
     spring.application.name=scraper
     spring.datasource.url=jdbc:mysql://${DB_HOST}:${DB_PORT}/scraper?useSSL=false&serverTimezone=UTC
     spring.datasource.username=${DB_USER}
     spring.datasource.password=${DB_PASSWORD}
     spring.jpa.hibernate.ddl-auto=update
     spring.jpa.show-sql=true
     spring.jpa.properties.hibernate.dialect=org.hibernate.dialect.MySQLDialect
     ```

4. **Run the Spring Boot Application**:
   - Run the Spring Boot backend application:
     ```bash
     mvn spring-boot:run
     ```

### Python Flask App Setup

1. **Install required dependencies**:

   - Install Python dependencies using `pip`:
     ```bash
     pip install -r requirements.txt
     ```

2. **Set up environment variables**:

   - Create a `.env` file for your Python app to store credentials, similar to the Spring Boot setup.

     Example for `.env`:

     ```
     DB_HOST=165.22.183.241
     DB_USER=your-username
     DB_PASSWORD=your-password
     API_KEY=your-api-key
     ```

3. **Run the Flask Application**:

   - Start the Flask application:
     ```bash
     python app.py
     ```

4. **EndPoints**:

   - The `/run-analysis` endpoint will trigger the analysis and forecasting process. You can use tools like Postman or simply access it from a browser.

   Example:

   ```bash
   curl http://localhost:5000/run-analysis
   ```

### Changing API Keys and Credentials

- **API Key in Spring Boot**:

  - The YouTube Data API key needs to be updated in your environment variables.
  - You can replace `${API_KEY}` in `application.properties` to dynamically load the correct value.

- **Database Credentials**:
  - In the `.env` files, you should replace the database credentials (`DB_HOST`, `DB_USER`, `DB_PASSWORD`) with your own values to ensure secure database access.

### Commands to Run

1. **Spring Boot Application**:

   ```bash
   mvn spring-boot:run
   ```

2. **Python Flask Application**:

   ```bash
   python app.py
   ```

3. **Run the Analysis Endpoint**:

   - Trigger the analysis by accessing the `/run-analysis` endpoint via your browser or using Postman.

   Example:

   ```bash
   curl http://localhost:5000/run-analysis
   ```

## Machine Learning Model

The **LSTM (Long Short-Term Memory)** model is used for time-series forecasting to predict the future growth of the top artist types based on historical data.

### LSTM Model Architecture

The model is built using the **Keras** library in Python. It consists of the following layers:

- **Input Layer**: Accepts the data sequence from the past growth metrics.
- **LSTM Layer**: Captures long-term dependencies in the time-series data.
- **Dropout Layers**: Helps prevent overfitting.
- **Dense Layer**: Outputs the predicted value for future growth.

```python
model = Sequential([
    Input(shape=(adjusted_look_back, 1)),
    LSTM(10, return_sequences=True),
    Dropout(0.2),
    LSTM(10, return_sequences=False),
    Dropout(0.2),
    Dense(16),
    Dense(1)  # Final output layer for growth score prediction
])
```
