// --- Configuration ---
const API_ENDPOINT = 'https://7pxjw3lx1m.execute-api.us-east-1.amazonaws.com/predict';

// --- Get DOM Elements ---
const form = document.getElementById('prediction-form');
const resultContainer = document.getElementById('result-container');
const predictionResultSpan = document.getElementById('prediction-result');
const loadingSpinner = document.getElementById('loading-spinner');

// --- Event Listener for Form Submission ---
form.addEventListener('submit', async (event) => {
    // Prevent the default form submission which reloads the page
    event.preventDefault();

    // Show loading state and hide previous results
    resultContainer.classList.add('hidden');
    // We don't have a visual spinner in this simple version, but this is where you'd show it
    
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

        if (!response.ok) {
            // If the server response is not 2xx, throw an error
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        console.log("Received result:", result);

        // --- Display the Result ---
        // Format the number with commas for readability
        const formattedPrediction = Math.round(result.predicted_view_count).toLocaleString();
        predictionResultSpan.textContent = formattedPrediction;
        resultContainer.classList.remove('hidden');

    } catch (error) {
        // --- Display an Error ---
        console.error("Error making prediction:", error);
        predictionResultSpan.textContent = "An error occurred. Please check the console for details.";
        resultContainer.classList.remove('hidden');
    }
});