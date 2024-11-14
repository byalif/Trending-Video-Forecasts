from flask import Flask, jsonify
import pandas as pd
import re
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import gc
import requests
from datetime import datetime
import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pytz
import random
from tensorflow.keras import backend as K
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping

app = Flask(__name__)

# Database connection setup
host = "165.22.183.241"
user = ""
password = ""
db = "scraper"
connection_string = f"mysql+pymysql://{user}:{password}@{host}/{db}"
engine = create_engine(connection_string)


@app.route('/run-analysis', methods=['GET'])
def run_analysis():

    # Load videos and metrics tables
    videos_query = "SELECT video_id, title FROM videos"
    metrics_query = "SELECT video_id, view_count, like_count, comment_count, timestamp FROM metrics"
    videos_df = pd.read_sql(videos_query, con=engine)
    metrics_df = pd.read_sql(metrics_query, con=engine)

    # Merge tables on 'video_id' to have titles and metrics in one DataFrame
    df = pd.merge(metrics_df, videos_df, on='video_id', how='left')

    # Artist extraction function
    def extract_artist_type(title, known_artists=None):
        if known_artists is None:
            known_artists = set()

        title = title.lower()
        title = re.sub(r'[^\w\s]', '', title)
        pattern = re.compile(r"\b([a-z0-9]+(?:\s[a-z0-9]+)*)\b\s*(?:x\s*([a-z0-9]+(?:\s[a-z0-9]+)*))?\s*type beat")

        match = pattern.search(title)
        if match:
            artist_1 = match.group(1).title()
            artist_2 = match.group(2).title() if match.group(2) else None

            known_artists.add(artist_1)
            if artist_2:
                known_artists.add(artist_2)

            return f"{artist_1} X {artist_2} Type Beat" if artist_2 else f"{artist_1} Type Beat"
        return "Unknown Type Beat"

    # Process each title to dynamically identify and group artist types
    known_artists = set()
    df['artist_type'] = df['title'].apply(lambda title: extract_artist_type(title, known_artists))

    # Define weights
    VIEW_WEIGHT = 0.7
    LIKE_WEIGHT = 0.2
    COMMENT_WEIGHT = 0.1

    # Convert 'timestamp' to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Calculate 24-hour growth rate per video
    cutoff_time = df['timestamp'].max() - timedelta(hours=24)
    df_24h = df[df['timestamp'] >= cutoff_time].sort_values(['video_id', 'timestamp'])

    # Calculate growth rates for each video_id
    results = []
    for video_id, group in df_24h.groupby('video_id'):
        view_diff = group['view_count'].iloc[-1] - group['view_count'].iloc[0]
        like_diff = group['like_count'].iloc[-1] - group['like_count'].iloc[0]
        comment_diff = group['comment_count'].iloc[-1] - group['comment_count'].iloc[0]

        growth_score = (view_diff * VIEW_WEIGHT) + (like_diff * LIKE_WEIGHT) + (comment_diff * COMMENT_WEIGHT)

        artist_type = group['artist_type'].iloc[0]
        # new_release = check_artist_releases(artist_type) if artist_type != "Unknown Type Beat" else False
        results.append({
            'video_id': video_id,
            'artist_type': artist_type,
            'growth_score': growth_score
        })

    growth_df = pd.DataFrame(results)

    artist_scores = growth_df.groupby('artist_type').agg({'growth_score': 'mean'}).reset_index()
    artist_scores.columns = ['artist_type', 'average_growth_score']
    artist_scores = artist_scores.sort_values(by='average_growth_score', ascending=False).head(30)

    top_artists = artist_scores['artist_type'].tolist()

    print("Top 30 Artist scores with release info:")
    print(artist_scores)

    # Insertion of data into 'growth_rate_tracking' table
    with engine.begin() as connection:
        # Create 'growth_rate_tracking' table if it doesn't exist
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS growth_rate_tracking (
                id INT AUTO_INCREMENT PRIMARY KEY,
                artist_type VARCHAR(255),
                average_growth_score FLOAT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute(create_table_query)

        # Insert aggregated artist scores with release info
        for _, row in artist_scores.iterrows():
            insert_query = text("""
                INSERT INTO growth_rate_tracking (artist_type, average_growth_score)
                VALUES (:artist_type, :average_growth_score)
            """)
            connection.execute(insert_query, {
                "artist_type": row['artist_type'],
                "average_growth_score": row['average_growth_score']})

    # Data retention logic (deletion of old records)
    MINUTES_TO_KEEP = 720
    cutoff_time = datetime.now() - timedelta(minutes=MINUTES_TO_KEEP)
    print(f"Cutoff timestamp for deletion: {cutoff_time}")

    with engine.begin() as connection:
        connection.execute(text("SET SQL_SAFE_UPDATES = 0;"))

        delete_metrics_query = text("""
            DELETE FROM metrics
            WHERE timestamp < :cutoff_time
        """)
        metrics_result = connection.execute(delete_metrics_query, {"cutoff_time": cutoff_time})
        print(f"Rows deleted from `metrics`: {metrics_result.rowcount}")

        delete_videos_query = text("""
            DELETE FROM videos
            WHERE video_id NOT IN (SELECT video_id FROM metrics)
        """)
        videos_result = connection.execute(delete_videos_query)
        print(f"Rows deleted from `videos`: {videos_result.rowcount}")

        connection.execute(text("SET SQL_SAFE_UPDATES = 1;"))

    print(f"Deleted all records in `metrics` and `videos` tables older than {MINUTES_TO_KEEP} minutes.")



   
    # Insert generated data into the `growth_rate_tracking` table
    with engine.begin() as connection:
        # Check if the table exists and create if not
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS growth_rate_tracking (
                id INT AUTO_INCREMENT PRIMARY KEY,
                artist_type VARCHAR(255),
                average_growth_score FLOAT,
                new_release BOOLEAN,
                timestamp DATETIME
            )
        """)
        connection.execute(create_table_query)

        # # Insert generated data into the table
        # growth_df.to_sql('growth_rate_tracking', con=engine, if_exists='append', index=False)
        
    print("24 lookback records for each artist type have been successfully inserted.")
    # Perform the deletion query in a safe transaction block
    with engine.begin() as connection:
        
        connection.execute(text("SET SQL_SAFE_UPDATES = 0;"))

        delete_query = text("""
            DELETE FROM growth_rate_tracking
            WHERE timestamp < NOW() - INTERVAL 3 DAY;
        """)
        result = connection.execute(delete_query)
        print(f"Deleted {result.rowcount} rows older than 3 day.")

        connection.execute(text("SET SQL_SAFE_UPDATES = 1;"))
    


        # Load the growth_rate_tracking table
    query = "SELECT artist_type, average_growth_score, timestamp FROM growth_rate_tracking"
    growth_df = pd.read_sql(query, con=engine)

    # Step 1: Prepare data for each artist type for LSTM
    artist_forecasts = {}  # Dictionary to store predictions per artist

    for artist in growth_df['artist_type'].unique():
        # Filter data for the current artist type
        if artist not in top_artists:
            continue  # Skip if artist is not in the top 30

        artist_data = growth_df[growth_df['artist_type'] == artist].copy()
        # Sort by timestamp to maintain sequential order
        artist_data = artist_data.sort_values(by='timestamp', ascending=False)  # Sort in descending order

        # Take the top 25 most recent entries
        artist_data = artist_data.head(25).sort_values(by='timestamp')  # Keep chronological order

        # Check if there’s enough data for the LOOK_BACK period
        LOOK_BACK = 12
        adjusted_look_back = min(LOOK_BACK, len(artist_data))
        
        if len(artist_data) < 3:
            print(f"Skipping {artist} due to insufficient data")
            continue  # Skip to the next artist if there’s not enough data

                # Step 2: Calculate differenced growth rate
        artist_data['growth_rate_diff'] = artist_data['average_growth_score'].diff()  # Calculate differences
        artist_data.dropna(inplace=True)  # Remove rows with NaN values created by differencing

        # Step 3: Data Scaling
        scaler = MinMaxScaler(feature_range=(0, 1))  # Scale features to (0,1) range
        artist_data[['growth_rate_diff']] = scaler.fit_transform(
            artist_data[['growth_rate_diff']]
        )
           # Step 4: Create Sequences for LSTM
        sequences = []
        targets = []
        
        for i in range(adjusted_look_back, len(artist_data)):
            # Get sequence of last LOOK_BACK time steps
            sequence = artist_data[['growth_rate_diff']].iloc[i - adjusted_look_back:i].values
            sequences.append(sequence)
            # Target value is the growth rate diff at the next time step
            targets.append(artist_data['growth_rate_diff'].iloc[i])

        # Convert sequences and targets to numpy arrays
        sequences = np.array(sequences)
        targets = np.array(targets).reshape(-1, 1)  # Ensuring targets have correct shape as (samples, 1)
        
        # Verify shapes
        print(f"{artist} - X shape: {sequences.shape}, y shape: {targets.shape}")
        
        # Step 4: Split into Train and Test Sets
        split = int(0.8 * len(sequences))  # 80% train, 20% test
        X_train, X_test = sequences[:split], sequences[split:]
        y_train, y_test = targets[:split], targets[split:]

        # Step 5: Build the LSTM Model with Input layer
        model = Sequential([
            Input(shape=(adjusted_look_back, 1)), 
            LSTM(10, return_sequences=True),
            Dropout(0.2),
            LSTM(10, return_sequences=False),
            Dropout(0.2),
            Dense(16),
            Dense(1)  # Final output layer for growth score prediction
        ])

        model.compile(optimizer='adam', loss='mean_squared_error')
        
        # Early stopping to avoid overfitting
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

        if X_train.shape[0] == 0 or X_test.shape[0] == 0:
            print(f"Skipping {artist} due to insufficient data for training.")
            continue

        # Step 6: Train the Model
        history = model.fit(
            X_train, y_train,
            validation_data=(X_test, y_test),
            epochs=10,
            batch_size=4,
            callbacks=[early_stop],
            verbose=1
        )

        # Step 7: Forecast Future Growth Scores
        last_sequence = sequences[-1]  # Last available sequence
        future_predictions = []
        
        # Predict next 24 hours
        for _ in range(24):
            next_pred = model.predict(last_sequence.reshape(1, adjusted_look_back, 1))
            future_predictions.append(next_pred[0, 0])  # Collect the prediction
            
            # Update last_sequence with the predicted value and new release info
            last_sequence = np.roll(last_sequence, -1, axis=0)  # Shift sequence left
            last_sequence[-1] = [next_pred[0, 0]]  # Update with predicted value, assume no new release
        

        # Reverse Scaling of Predicted Growth Differences
        future_predictions = scaler.inverse_transform(
            np.column_stack([future_predictions, np.zeros(len(future_predictions))])
        )[:, 0]  # Only inverse-transform the growth differences

        # Start cumulative sum from the last actual value without adding it to the predictions array
        last_actual_score = artist_data['average_growth_score'].iloc[-1]
        cumulative_forecast = [last_actual_score + np.sum(future_predictions[:i+1]) for i in range(len(future_predictions))]

        # Store forecast results for this artist
        artist_forecasts[artist] = cumulative_forecast

         # Convert all numpy arrays to lists for JSON serialization
        for artist in artist_forecasts:
            artist_forecasts[artist] = list(artist_forecasts[artist])


    # Display forecast results
    for artist, predictions in artist_forecasts.items():
        print(f"Forecast for {artist}: {predictions}")


    # Assuming 'artist_forecasts' contains the forecast data
    enhanced_artist_data = []

    for artist, forecast_values in artist_forecasts.items():
        # Current and projected metrics
        initial_value = forecast_values[0]
        final_value = forecast_values[-1]
        growth_rate = (final_value - initial_value) / initial_value * 100 if initial_value else 0
        projected_growth = final_value - initial_value
        growth_speed = np.mean(np.diff(forecast_values))  # Avg hourly change
        
        # Determine initial popularity score (e.g., first forecast value) as a proxy for views
        current_views = initial_value
        
        # Add calculated data to enhanced artist data
        enhanced_artist_data.append({
            "artist_type": artist,
            "current_views": current_views,
            "projected_growth": projected_growth,
            "growth_rate": growth_rate,
            "growth_speed": growth_speed,
            "forecast_values": forecast_values
        })
    
    # Convert to DataFrame for easy sorting and ranking
    df = pd.DataFrame(enhanced_artist_data)
    # Assign ranks based on each metric
    df['top_potential_rank'] = df['projected_growth'].rank(ascending=False).astype(int)
    df['growth_rate_rank'] = df['growth_rate'].rank(ascending=False).astype(int)
    df['fastest_risers_rank'] = df['growth_speed'].rank(ascending=False).astype(int)

    # Convert the DataFrame back to a dictionary format for further processing
    enhanced_artist_data = df.to_dict(orient='records')

    # Sort by projected growth and current views for final ranking
    ranked_artist_data = sorted(
        enhanced_artist_data,
        key=lambda x: (x['projected_growth'], x['growth_speed'], x['current_views']),
        reverse=True
    )

    # Define "Top Recommendations" for the client based on projected trends
    top_recommendations = [artist["artist_type"] for artist in ranked_artist_data[:5]]


 # Create or modify the 'artist_forecasts' table and store forecast values as VARCHAR
    with engine.begin() as connection:
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS artist_forecasts (
                forecast_id INT AUTO_INCREMENT PRIMARY KEY,
                artist_type VARCHAR(255),
                current_views FLOAT,
                projected_growth FLOAT,
                growth_rate FLOAT,
                growth_speed FLOAT,
                top_potential_rank INT,
                growth_rate_rank INT,
                fastest_risers_rank INT,
                forecast_values VARCHAR(5000),  # Storing forecast values as a VARCHAR
                timestamp DATETIME  
            )
        """))

    for artist_data in ranked_artist_data:
                # Convert forecast values to a comma-separated string
                forecast_values_str = ",".join(map(str, artist_data['forecast_values']))
                ny_tz = pytz.timezone('America/New_York')
                current_timestamp = datetime.now(pytz.utc).astimezone(ny_tz)
                insert_forecast_query = text("""
                            INSERT INTO artist_forecasts (
                                artist_type, current_views, projected_growth, growth_rate, growth_speed,
                                top_potential_rank, growth_rate_rank, fastest_risers_rank, forecast_values, timestamp
                            ) VALUES (
                                :artist_type, :current_views, :projected_growth, :growth_rate, :growth_speed,
                                :top_potential_rank, :growth_rate_rank, :fastest_risers_rank, :forecast_values, :timestamp
                            )
                        """)

                # Prepare values for insertion
                forecast_values = {
                    "artist_type": artist_data['artist_type'],
                    "current_views": artist_data['current_views'],
                    "projected_growth": artist_data['projected_growth'],
                    "growth_rate": artist_data['growth_rate'],
                    "growth_speed": artist_data['growth_speed'],
                    "top_potential_rank": artist_data['top_potential_rank'],
                    "growth_rate_rank": artist_data['growth_rate_rank'],
                    "fastest_risers_rank": artist_data['fastest_risers_rank'],
                    "forecast_values": forecast_values_str,
                    "timestamp": current_timestamp  # Use Python's current timestamp
                }
                
                # Execute insertion
                connection.execute(insert_forecast_query, forecast_values)

    # Step 3: Clean up old records in `artist_forecasts`, keeping only the 60 most recent records
    # Disable safe update mode
    with engine.begin() as connection:
        # Use text() to wrap the raw SQL string
        connection.execute(text("SET SQL_SAFE_UPDATES = 0;"))  # Temporarily disable safe updates

        # The original DELETE query
        query = """
            DELETE artist_forecasts
            FROM artist_forecasts
            LEFT JOIN (
                SELECT forecast_id
                FROM artist_forecasts
                ORDER BY timestamp DESC
                LIMIT 60
            ) AS latest_forecasts
            ON artist_forecasts.forecast_id = latest_forecasts.forecast_id
            WHERE latest_forecasts.forecast_id IS NULL;
        """
        
        try:
            # Execute the DELETE query using text() to wrap the SQL statement
            the_result = connection.execute(text(query))
            print(f"Rows deleted from `videos`: {the_result.rowcount}")

        except pymysql.MySQLError as e:
            print(f"An error occurred: {e}")
        
        finally:
            # Re-enable safe update mode
            connection.execute(text("SET SQL_SAFE_UPDATES = 1;"))


    # Final JSON Output
    results = {
        "message": "Analysis complete"  # Recommended beats to focus on
    }

    # Clear Keras session and perform garbage collection
    K.clear_session()
    gc.collect() 
    del model

    # Convert to JSON and return
    return jsonify(results)

if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000)
