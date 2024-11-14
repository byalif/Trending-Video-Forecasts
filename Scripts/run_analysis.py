import pandas as pd
import re
from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
import gc
import json
import numpy as np
from sklearn.preprocessing import MinMaxScaler
import pytz
from tensorflow.keras import backend as K
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping

# Database connection setup
host = "165.22.183.241"
user = ""
password = ""
db = "scraper"
connection_string = f"mysql+pymysql://{user}:{password}@{host}/{db}"
engine = create_engine(connection_string)

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

    # Insertion of data into 'growth_rate_tracking' table
    with engine.begin() as connection:
        create_table_query = text("""
            CREATE TABLE IF NOT EXISTS growth_rate_tracking (
                id INT AUTO_INCREMENT PRIMARY KEY,
                artist_type VARCHAR(255),
                average_growth_score FLOAT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.execute(create_table_query)

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
    with engine.begin() as connection:
        connection.execute(text("SET SQL_SAFE_UPDATES = 0;"))

        delete_metrics_query = text("DELETE FROM metrics WHERE timestamp < :cutoff_time")
        connection.execute(delete_metrics_query, {"cutoff_time": cutoff_time})

        delete_videos_query = text("""
            DELETE FROM videos WHERE video_id NOT IN (SELECT video_id FROM metrics)
        """)
        connection.execute(delete_videos_query)
        connection.execute(text("SET SQL_SAFE_UPDATES = 1;"))

    # Load the growth_rate_tracking table
    query = "SELECT artist_type, average_growth_score, timestamp FROM growth_rate_tracking"
    growth_df = pd.read_sql(query, con=engine)

    artist_forecasts = {}
    for artist in growth_df['artist_type'].unique():
        if artist not in top_artists:
            continue

        artist_data = growth_df[growth_df['artist_type'] == artist].copy()
        artist_data = artist_data.sort_values(by='timestamp', ascending=False).head(25).sort_values(by='timestamp')
        LOOK_BACK = 12
        adjusted_look_back = min(LOOK_BACK, len(artist_data))

        if len(artist_data) < 3:
            continue

        artist_data['growth_rate_diff'] = artist_data['average_growth_score'].diff()
        artist_data.dropna(inplace=True)

        scaler = MinMaxScaler(feature_range=(0, 1))
        artist_data[['growth_rate_diff']] = scaler.fit_transform(artist_data[['growth_rate_diff']])
        
        sequences = []
        targets = []
        for i in range(adjusted_look_back, len(artist_data)):
            sequence = artist_data[['growth_rate_diff']].iloc[i - adjusted_look_back:i].values
            sequences.append(sequence)
            targets.append(artist_data['growth_rate_diff'].iloc[i])

        sequences = np.array(sequences)
        targets = np.array(targets).reshape(-1, 1)
        
        split = int(0.8 * len(sequences))
        X_train, X_test = sequences[:split], sequences[split:]
        y_train, y_test = targets[:split], targets[split:]

        model = Sequential([
            Input(shape=(adjusted_look_back, 1)), 
            LSTM(10, return_sequences=True),
            Dropout(0.2),
            LSTM(10, return_sequences=False),
            Dropout(0.2),
            Dense(16),
            Dense(1)
        ])
        model.compile(optimizer='adam', loss='mean_squared_error')
        early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

        if X_train.shape[0] == 0 or X_test.shape[0] == 0:
            continue

        model.fit(X_train, y_train, validation_data=(X_test, y_test), epochs=10, batch_size=4, callbacks=[early_stop])

        last_sequence = sequences[-1]
        future_predictions = []
        for _ in range(24):
            next_pred = model.predict(last_sequence.reshape(1, adjusted_look_back, 1))
            future_predictions.append(next_pred[0, 0])
            last_sequence = np.roll(last_sequence, -1, axis=0)
            last_sequence[-1] = [next_pred[0, 0]]

        future_predictions = scaler.inverse_transform(np.column_stack([future_predictions, np.zeros(len(future_predictions))]))[:, 0]
        last_actual_score = artist_data['average_growth_score'].iloc[-1]
        cumulative_forecast = [last_actual_score + np.sum(future_predictions[:i+1]) for i in range(len(future_predictions))]
        artist_forecasts[artist] = cumulative_forecast

    enhanced_artist_data = []
    for artist, forecast_values in artist_forecasts.items():
        initial_value = forecast_values[0]
        final_value = forecast_values[-1]
        growth_rate = (final_value - initial_value) / initial_value * 100 if initial_value else 0
        projected_growth = final_value - initial_value
        growth_speed = np.mean(np.diff(forecast_values))
        
        current_views = initial_value
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

    # Insert results into `artist_forecasts` table
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
                forecast_values VARCHAR(5000),
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))

        for artist_data in ranked_artist_data:
            try:
                forecast_values_str = ",".join(map(str, artist_data['forecast_values']))
                insert_forecast_query = text("""
                    INSERT INTO artist_forecasts (
                        artist_type, current_views, projected_growth, growth_rate, growth_speed,
                        top_potential_rank, growth_rate_rank, fastest_risers_rank, forecast_values, timestamp
                    ) VALUES (
                        :artist_type, :current_views, :projected_growth, :growth_rate, :growth_speed,
                        :top_potential_rank, :growth_rate_rank, :fastest_risers_rank, :forecast_values, CURRENT_TIMESTAMP
                    )
                """)
                
                forecast_values = {
                    "artist_type": artist_data['artist_type'],
                    "current_views": artist_data['current_views'],
                    "projected_growth": artist_data['projected_growth'],
                    "growth_rate": artist_data['growth_rate'],
                    "growth_speed": artist_data['growth_speed'],
                    "top_potential_rank": artist_data['top_potential_rank'],
                    "growth_rate_rank": artist_data['growth_rate_rank'],
                    "fastest_risers_rank": artist_data['fastest_risers_rank'],
                    "forecast_values": forecast_values_str
                }
                
                connection.execute(insert_forecast_query, forecast_values)
            except Exception as e:
                print(f"Error inserting forecast for artist {artist_data['artist_type']}: {e}")

    # Clean up old records in `artist_forecasts`, keeping only the 60 most recent records
    with engine.begin() as connection:
        connection.execute(text("SET SQL_SAFE_UPDATES = 0;"))
        delete_query = """
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
            result = connection.execute(text(delete_query))
            print(f"Deleted {result.rowcount} old rows from `artist_forecasts`.")
        except Exception as e:
            print(f"An error occurred during deletion: {e}")
        finally:
            connection.execute(text("SET SQL_SAFE_UPDATES = 1;"))

    # Cleanup Keras session and memory
    K.clear_session()
    gc.collect()
    del model

    print("Analysis complete.")

# Run the script directly
if __name__ == '__main__':
    run_analysis()
