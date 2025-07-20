import pandas as pd
import re
import os
import joblib  # For saving the model
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import mean_squared_error, r2_score

# --- Define the project root directory ---
# This makes the script runnable from any location and is robust
# __file__ is the path to the current script (train.py)
# os.path.dirname gets the directory of the script (src)
# os.path.dirname again gets the parent directory (the project root)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def clean_and_feature_engineer(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw YouTube dataset and engineers new features for modeling.
    """
    df_clean = df.copy()

    # Drop columns not useful for this model. We keep title for potential future NLP features.
    columns_to_drop = ['video_id', 'description', 'thumbnail']
    df_clean = df_clean.drop(columns=columns_to_drop)

    # Correct data types for numeric columns
    for col in ['view_count', 'like_count', 'comment_count']:
        df_clean[col] = df_clean[col].astype('int')

    # Feature Engineering from 'published_date'
    df_clean['published_date'] = pd.to_datetime(df_clean['published_date'], errors='coerce')
    df_clean['publish_day_of_week'] = df_clean['published_date'].dt.dayofweek
    df_clean['publish_hour'] = df_clean['published_date'].dt.hour
    
    # Feature Engineering from 'duration' (ISO 8601 format)
    def parse_duration(duration_str):
        match = re.match(r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?', str(duration_str))
        if not match: return 0
        hours, minutes, seconds = (int(g) if g else 0 for g in match.groups())
        return hours * 3600 + minutes * 60 + seconds
    df_clean['duration_seconds'] = df_clean['duration'].apply(parse_duration)

    # Feature Engineering from 'tags'
    def count_tags(tags_str):
        try:
            import ast
            return len(ast.literal_eval(tags_str))
        except (ValueError, SyntaxError):
            return 0
    df_clean['tag_count'] = df_clean['tags'].apply(count_tags)
    
    # Final Cleanup of original columns
    df_clean = df_clean.drop(columns=['published_date', 'duration', 'tags'])
    
    # Drop rows with NaT in published_date if any failed to parse
    df_clean.dropna(inplace=True)

    return df_clean

# --- Main execution block ---
if __name__ == "__main__":
    print("Starting the model training process...")

    # --- 1. Load and Process Data ---
    raw_data_path = os.path.join(PROJECT_ROOT, 'data', 'youtube_data.csv')
    df_raw = pd.read_csv(raw_data_path)
    df_processed = clean_and_feature_engineer(df_raw)

    # For this model, we'll drop title and channel_title as we use a simple regressor
    # A more advanced NLP model could use these text features.
    df_model = df_processed.drop(columns=['title'])

    # --- 2. Define Features (X) and Target (y) ---
    # We are predicting 'view_count'.
    X = df_model.drop('view_count', axis=1)
    y = df_model['view_count']

    # --- 3. Split Data into Training and Testing sets ---
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # --- 4. Define Preprocessing Steps for Different Column Types ---
    # We need to one-hot encode categorical features so the model can understand them.
    categorical_features = ['channel_title', 'category_id']
    numeric_features = X.select_dtypes(include=['int64', 'int32']).columns.drop(categorical_features, errors='ignore').tolist()

    # Create a preprocessor object using ColumnTransformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', 'passthrough', numeric_features),
            ('cat', OneHotEncoder(handle_unknown='ignore'), categorical_features)
        ],
        remainder='drop' # Drop any columns not specified
    )

    # --- 5. Create the Model Pipeline ---
    # A pipeline bundles preprocessing and the model together. This is a best practice.
    model_pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('regressor', RandomForestRegressor(n_estimators=100, random_state=42, n_jobs=-1))
    ])

    # --- 6. Train the Model ---
    print("Training the model...")
    model_pipeline.fit(X_train, y_train)

    # --- 7. Evaluate the Model ---
    print("Evaluating the model...")
    y_pred = model_pipeline.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    print(f"Model Performance on Test Set:")
    print(f"  - Mean Squared Error (MSE): {mse:,.2f}")
    print(f"  - R-squared (R²): {r2:.2f}")

    # --- 8. Save the Trained Model ---
    # The model will be saved in a new 'artifacts' directory.
    artifacts_dir = os.path.join(PROJECT_ROOT, 'artifacts')
    os.makedirs(artifacts_dir, exist_ok=True) # Ensure the directory exists
    model_path = os.path.join(artifacts_dir, 'youtube_popularity_model.joblib')
    joblib.dump(model_pipeline, model_path)
    
    print(f"\nModel training complete. Model saved to: {model_path}")