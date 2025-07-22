import joblib
import pandas as pd
import boto3
import os
import json
import traceback

print("--- Loading function and all libraries ---")

# --- Environment Variables ---
# We log these immediately to see if they are available at cold start
BUCKET_NAME = os.environ.get('BUCKET_NAME')
MODEL_KEY = os.environ.get('MODEL_KEY')
print(f"ENV VAR BUCKET_NAME at cold start: {BUCKET_NAME}")
print(f"ENV VAR MODEL_KEY at cold start: {MODEL_KEY}")


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
        # Re-read env vars inside the function just in case they are populated later
        bucket = os.environ.get('BUCKET_NAME')
        key = os.environ.get('MODEL_KEY')
        print(f"load_model() is using bucket: {bucket}, key: {key}")

        if not bucket or not key:
            print("Error: BUCKET_NAME or MODEL_KEY environment variables are not set or are empty.")
            return False

        local_model_path = f'/tmp/{os.path.basename(key)}'
        print(f"Downloading model from s3://{bucket}/{key} to {local_model_path}")
        s3_client.download_file(bucket, key, local_model_path)
        print("Model downloaded successfully.")
        
        model = joblib.load(local_model_path)
        print("Model loaded successfully.")
        return True

    except Exception as e:
        # Print the full traceback for detailed debugging
        print(f"--- EXCEPTION IN load_model() ---")
        print(f"Error loading model: {e}")
        traceback.print_exc()
        print(f"--- END EXCEPTION ---")
        return False

def lambda_handler(event, context):
    """
    Main Lambda handler function to process API Gateway requests.
    """
    global model
    print(f"--- Handler received event ---")
    
    # --- Load Model if Not Already Loaded ---
    # This check ensures the model is loaded only once per container instance.
    if model is None:
        print("Model is not loaded. Attempting to load now.")
        if not load_model():
            print("load_model() failed. Returning error response.")
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Model could not be loaded due to initialization failure. Check logs.'})
            }

    try:
        # API Gateway sends the request body as a JSON string. We need to parse it.
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', {})

        # --- Create DataFrame from input ---
        input_data = pd.DataFrame([body])
        
        if 'category_id' in input_data.columns:
             input_data['category_id'] = input_data['category_id'].astype('int64')

        print(f"Making prediction on input data: \n{input_data.to_string()}")

        # --- Make Prediction ---
        prediction = model.predict(input_data)
        predicted_view_count = prediction[0]

        print(f"Prediction successful. Predicted view count: {predicted_view_count}")

        # --- Return Response ---
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'predicted_view_count': predicted_view_count})
        }

    except Exception as e:
        print(f"--- EXCEPTION IN lambda_handler() ---")
        print(f"Error during prediction: {e}")
        traceback.print_exc()
        print(f"--- END EXCEPTION ---")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f"Prediction failed: {str(e)}"})
        }