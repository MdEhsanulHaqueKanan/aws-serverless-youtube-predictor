// --- Configuration ---
const API_ENDPOINT = 'https://ro2dr7an6j.execute-api.us-east-1.amazonaws.com/predict';

// --- Get DOM Elements ---
const form = document.getElementById('prediction-form');
const resultContainer = document.getElementById('result-container');
const predictionResultSpan = document.getElementById('prediction-result');
const submitButton = document.getElementById('submit-button');


// --- Event Listener for Form Submission ---
form.addEventListener('submit', async (event) => {
    // Prevent the default form submission which reloads the page
    event.preventDefault();

    // Disable button and show loading state
    submitButton.disabled = true;
    submitButton.textContent = 'Predicting...';
    resultContainer.classList.add('hidden');
    
    // --- Collect Data from Form ---
    const formData = {
        like_count: parseInt(document.getElementById('like_count').value),
        comment_count: parseInt(document.getElementById('comment_count').value),
        duration_seconds: parseInt(document.getElementById('duration_seconds').value),
        tag_count: parseInt(document.getElementById('tag_count').value),
        category_id: parseInt(document.getElementById('category_id').value),
        publish_hour: parseInt(document.getElementById('publish_hour').value),
        publish_day_of_week: parseInt(document.getElementById('publish_day_of_week').value),
        channel_title: document.getElementById('channel_title').value
    };

    console.log("Sending data:", formData);

    // --- Call the API ---
    try {
        const response = await fetch(API_ENDPOINT, {
            method: 'POST',
            body: JSON.stringify(formData),
            headers: {
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (!response.ok) {
            // If the server response is not 2xx, throw an error with the message from the lambda
            throw new Error(result.error || `HTTP error! status: ${response.status}`);
        }

        console.log("Received result:", result);

        // --- Display the Result ---
        // Format the number with commas for readability
        const formattedPrediction = Math.round(result.predicted_view_count).toLocaleString();
        predictionResultSpan.textContent = formattedPrediction;
        resultContainer.classList.remove('hidden');

    } catch (error) {
        // --- Display an Error ---
        console.error("Error making prediction:", error);
        predictionResultSpan.textContent = `An error occurred: ${error.message}`;
        resultContainer.classList.remove('hidden');
    } finally {
        // Re-enable the button regardless of success or failure
        submitButton.disabled = false;
        submitButton.textContent = 'Predict View Count';
    }
});