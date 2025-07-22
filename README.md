# AWS Serverless YouTube Popularity Predictor

This project is a complete, end-to-end Machine Learning Operations (MLOps) pipeline built on Amazon Web Services (AWS). It trains a model to predict the potential view count of a YouTube video based on its metadata and deploys it as a scalable, cost-effective, and serverless API endpoint.

The entire architecture is designed to run with **zero ongoing monthly costs**, leveraging the AWS "Always Free" Tier for long-running services and demonstrating a cost-conscious approach to cloud ML deployment.

## 🏆 Key Achievements & MLOps Concepts Demonstrated

This project showcases a full range of modern MLOps skills, from automated cloud-based builds to fully serverless inference.

*   **Cost-Effective Architecture:** Engineered the entire prediction service to operate on the **AWS Always Free Tier**, resulting in **$0/month ongoing costs**.
*   **CI/CD for Machine Learning:** Implemented a complete Continuous Integration/Continuous Deployment pipeline using **AWS CodeBuild** and **GitHub**. Pushing code to GitHub automatically triggers a secure, cloud-based process that builds a new, Lambda-compatible Docker image.
*   **Infrastructure as Code Principles:** Utilized a `buildspec.yml` file to define the build process declaratively, ensuring a repeatable and consistent build environment.
*   **Separation of Training and Inference:**
    *   **Training:** Performed as a one-off, containerized batch job on **AWS ECS Fargate**, demonstrating the ability to use powerful compute for short-term tasks without incurring costs for idle servers.
    *   **Inference:** Deployed as a highly-available, auto-scaling serverless function using **AWS Lambda** and **API Gateway**.
*   **Containerization for Reproducibility:** Used **Docker** to create separate, consistent, and portable environments for both the training script and the inference API, solving dependency and compatibility issues.

## 🏛️ Project Architecture

This project follows a professional, industry-standard MLOps workflow:

1.  **Code:** All source code (`lambda_function.py`, `train.py`) and configuration (`Dockerfile`, `buildspec.yml`) is stored in **GitHub**.
2.  **Storage:** The YouTube dataset and the trained model artifact (`.joblib` file) are stored securely in **AWS S3**.
3.  **Model Training (One-Time Task):**
    *   The training script is containerized using Docker.
    *   This container is run as a short-lived batch task on **AWS ECS Fargate**. It pulls the dataset from S3, trains the model, and pushes the final model artifact back to S3.
4.  **CI/CD Build Pipeline (Automated):**
    *   A push to the GitHub repository automatically triggers **AWS CodeBuild**.
    *   CodeBuild uses a separate `Dockerfile.lambda` to build a Lambda-compatible container image.
    *   The new image is pushed to the **Amazon Elastic Container Registry (ECR)**.
5.  **Serverless Deployment & Inference:**
    *   **AWS Lambda** is configured to run the container image from ECR. The code loads the model from S3 on its first invocation.
    *   **Amazon API Gateway** provides a public HTTP endpoint that triggers the Lambda function, making the prediction service available to any client or frontend application.

```
[GitHub Repo] ---> [AWS CodeBuild] ---> [Amazon ECR] ---> [AWS Lambda] <--- [API Gateway] <--- [User]
      ^                                                            |
      |                                                            v
      +------------------ [AWS S3 (Model & Data)] <-----------------+
```

## 🛠️ Tech Stack

*   **Cloud Platform:** AWS (Amazon Web Services)
*   **MLOps & CI/CD:** AWS CodeBuild, Docker, GitHub
*   **Compute:** AWS Lambda (Serverless), AWS ECS Fargate (Container Orchestration)
*   **Storage:** AWS S3
*   **API:** Amazon API Gateway
*   **Machine Learning:** Python, Scikit-learn, Pandas
*   **Infrastructure & Security:** AWS IAM (Identity and Access Management)
*   **Monitoring:** AWS CloudWatch

## 🚀 How to Use the API

The deployed model is available at the following endpoint:

**Endpoint URL:** `https://7pxjw3lx1m.execute-api.us-east-1.amazonaws.com/predict`

**Method:** `POST`

**Body (JSON):**
You must provide a JSON object with all the features the model was trained on.

```json
{
    "like_count": 5000,
    "comment_count": 200,
    "duration_seconds": 300,
    "tag_count": 15,
    "category_id": 24,
    "publish_hour": 14,
    "publish_day_of_week": 3,
    "channel_title": "Some Channel"
}
```

**Success Response (200):**
```json
{
    "predicted_view_count": 568924.08
}
```