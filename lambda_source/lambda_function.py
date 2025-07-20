import joblib
import pandas as pd
import boto3
import os
import json

# --- Environment Variables ---
# We will set these in the Lambda configuration
BUCKET_NAME = os.environ.get('BUCKET_NAME')
MODEL_KEY = os.environ.get('MODEL_KEY')

# --- AWS S3 Client ---
# Use a boto3 S3 client to download the model from S3
s3_client = boto3.client('s3')

# --- Load Model ---
# This part of the code runs only once, during the Lambda "cold start".
# It downloads the model from S3 to the temporary /tmp/ directory in the Lambda environment.
# Subsequent invocations can reuse the downloaded model if the container is still "warm".
try:
    local_model_path = f'/tmp/{os.path.basename(MODEL_KEY)}'
    print(f"Downloading model from s3://{BUCKET_NAME}/{MODEL_KEY} to {local_model_path}")
    s3_client.download_file(BUCKET_NAME, MODEL_KEY, local_model_path)
    print("Model downloaded successfully.")
    
    model = joblib.load(local_model_path)
    print("Model loaded successfully.")

except Exception as e:
    print(f"Error loading model: {e}")
    model = None

def lambda_handler(event, context):
    """
    Main Lambda handler function to process API Gateway requests.
    """
    print(f"Received event: {event}")

    if model is None:
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': 'Model could not be loaded.'})
        }

    try:
        # API Gateway sends the request body as a JSON string. We need to parse it.
        # If testing directly in Lambda, the body might already be a dict.
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        # --- Create DataFrame from input ---
        # The input data is a single dictionary. We convert it into a DataFrame
        # with a single row so it can be processed by the scikit-learn pipeline.
        input_data = pd.DataFrame([body])
        
        # Ensure correct data types for categorical features
        if 'category_id' in input_data.columns:
             input_data['category_id'] = input_data['category_id'].astype('int64')

        print(f"Making prediction on input data: \n{input_data.to_string()}")

        # --- Make Prediction ---
        prediction = model.predict(input_data)
        
        # The prediction is a numpy array with one element. We extract that number.
        predicted_view_count = prediction[0]

        print(f"Prediction successful. Predicted view count: {predicted_view_count}")

        # --- Return Response ---
        # The response must be in a specific format for API Gateway.
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*' # Allow cross-origin requests for our UI
            },
            'body': json.dumps({'predicted_view_count': predicted_view_count})
        }

    except Exception as e:
        print(f"Error during prediction: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f"Prediction failed: {str(e)}"})
        }