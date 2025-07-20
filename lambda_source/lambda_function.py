import joblib
import pandas as pd
import boto3
import os
import json

# --- Environment Variables ---
BUCKET_NAME = os.environ.get('BUCKET_NAME')
MODEL_KEY = os.environ.get('MODEL_KEY')

# --- AWS S3 Client ---
s3_client = boto3.client('s3')

# --- Global Model Variable ---
# Initialize the model as a global variable so it can be cached.
model = None

def load_model():
    """
    This function loads the model from S3.
    It's called only if the global 'model' variable is None.
    """
    global model
    try:
        local_model_path = f'/tmp/{os.path.basename(MODEL_KEY)}'
        print(f"Downloading model from s3://{BUCKET_NAME}/{MODEL_KEY} to {local_model_path}")
        s3_client.download_file(BUCKET_NAME, MODEL_KEY, local_model_path)
        print("Model downloaded successfully.")
        
        model = joblib.load(local_model_path)
        print("Model loaded successfully.")
        return True

    except Exception as e:
        print(f"Error loading model: {e}")
        return False

def lambda_handler(event, context):
    """
    Main Lambda handler function to process API Gateway requests.
    """
    global model
    
    # --- Load Model if Not Already Loaded ---
    # This check ensures the model is loaded only once per container instance.
    if model is None:
        if not load_model():
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
                'body': json.dumps({'error': 'Model could not be loaded.'})
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
        print(f"Error during prediction: {e}")
        return {
            'statusCode': 400,
            'headers': {'Content-Type': 'application/json', 'Access-Control-Allow-Origin': '*'},
            'body': json.dumps({'error': f"Prediction failed: {str(e)}"})
        }