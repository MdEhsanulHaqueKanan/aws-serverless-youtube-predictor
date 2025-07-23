import joblib
import pandas as pd
import boto3
import os
import json
import traceback

# --- Environment Variables ---
# These are now baked into the container image by the Dockerfile
BUCKET_NAME = os.environ.get('BUCKET_NAME')
MODEL_KEY = os.environ.get('MODEL_KEY')

# --- AWS S3 Client ---
s3_client = boto3.client('s3')
model = None

def load_model():
    """
    This function loads the model from S3.
    It's called only if the global 'model' variable is None.
    """
    global model
    try:
        # Check if variables are present
        if not BUCKET_NAME or not MODEL_KEY:
            print("Error: BUCKET_NAME or MODEL_KEY environment variables are not set.")
            return False

        local_model_path = f'/tmp/{os.path.basename(MODEL_KEY)}'
        print(f"Downloading model from s3://{BUCKET_NAME}/{MODEL_KEY} to {local_model_path}")
        s3_client.download_file(BUCKET_NAME, MODEL_KEY, local_model_path)
        print("Model downloaded successfully.")
        
        model = joblib.load(local_model_path)
        print("Model loaded successfully.")
        return True

    except Exception as e:
        print(f"--- EXCEPTION IN load_model() ---")
        print(f"Error loading model: {e}")
        traceback.print_exc()
        print(f"--- END EXCEPTION ---")
        return False

def lambda_handler(event, context):
    """
    Main Lambda handler function to process API Gateway requests.
    """
    # --- CORS Headers ---
    # These headers are required to allow the frontend browser to call the API
    headers = {
        'Content-Type': 'application/json',
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Headers': 'Content-Type',
        'Access-Control-Allow-Methods': 'OPTIONS,POST'
    }

    # --- Handle CORS Preflight Request ---
    # The browser sends an OPTIONS request first to ask for permission.
    # We must respond to it with a 200 OK and the correct headers.
    if event.get('httpMethod') == 'OPTIONS':
        print("Handling OPTIONS preflight request")
        return {'statusCode': 200, 'headers': headers, 'body': ''}

    # --- Main Handler Logic ---
    global model
    if model is None:
        print("Model is not loaded. Attempting to load now.")
        if not load_model():
            print("load_model() failed. Returning error response.")
            return {
                'statusCode': 500,
                'headers': headers,
                'body': json.dumps({'error': 'Model could not be loaded.'})
            }

    try:
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        input_data = pd.DataFrame([body])
        if 'category_id' in input_data.columns:
             input_data['category_id'] = input_data['category_id'].astype('int64')

        prediction = model.predict(input_data)
        predicted_view_count = prediction[0]

        print(f"Prediction successful: {predicted_view_count}")

        return {
            'statusCode': 200,
            'headers': headers,
            'body': json.dumps({'predicted_view_count': predicted_view_count})
        }
    except Exception as e:
        print(f"--- EXCEPTION IN lambda_handler() ---")
        print(f"Error during prediction: {e}")
        traceback.print_exc()
        print(f"--- END EXCEPTION ---")
        return {
            'statusCode': 400,
            'headers': headers,
            'body': json.dumps({'error': f"Prediction failed: {str(e)}"})
        }