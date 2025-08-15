# AWS Serverless YouTube Popularity Predictor

![Amazon AWS](https://img.shields.io/badge/Amazon_AWS-232F3E?style=for-the-badge&logo=amazon-aws&logoColor=white)
![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=for-the-badge&logo=aws-lambda&logoColor=white)
![Amazon API Gateway](https://img.shields.io/badge/Amazon_API_Gateway-FF4F8B?style=for-the-badge&logo=amazon-api-gateway&logoColor=white)
![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

This project is a complete, end-to-end Machine Learning Operations (MLOps) pipeline built on Amazon Web Services (AWS). It trains a model to predict the potential view count of a YouTube video and deploys it as a scalable, cost-effective, serverless API.

This backend is now served by a **modern and interactive React & TypeScript frontend**.

The entire architecture is designed to run with **zero ongoing monthly costs**, leveraging the AWS "Always Free" Tier.

**► Live Demo:** [http://youtube-predictor-frontend-ehsanul-72525.s3-website-us-east-1.amazonaws.com/](http://youtube-predictor-frontend-ehsanul-72525.s3-website-us-east-1.amazonaws.com/)

## 📸 Application Preview

![Application Preview](assets/youtube-popularity-predictor.png)

## 🏆 Key Achievements & MLOps Concepts Demonstrated

This project showcases a full range of modern MLOps skills, from automated cloud-based builds to a fully serverless, user-facing application.

-   **Full-Stack Decoupled Architecture:** A clear separation between the serverless Python backend and the modern React frontend, communicating via a REST API.
-   **Modern Frontend Application:** Deployed a stunning, fully responsive frontend built with **React and TypeScript**, and hosted on AWS S3 for high performance and low cost. The code is available in its own [dedicated repository](https://github.com/MdEhsanulHaqueKanan/youtube-predictor-frontend).
-   **CI/CD for Machine Learning:** Implemented a complete CI/CD pipeline using **AWS CodeBuild** and **GitHub**. Pushing code to this repository automatically triggers a cloud-based process that builds and pushes a new Lambda-compatible Docker image to **Amazon ECR**.
-   **Serverless First:** Deployed the model as a highly-available, auto-scaling serverless function using **AWS Lambda** and **API Gateway**, eliminating the need for idle servers.
-   **Cost-Effective Architecture:** Engineered the entire prediction service and frontend to operate on the **AWS Always Free Tier** (Lambda, API Gateway, S3), resulting in **$0/month ongoing costs**.
-   **Containerized Training:** Orchestrated model training as a one-off, containerized batch job on **AWS ECS Fargate**, showcasing the ability to use powerful compute for short-term tasks without incurring continuous costs.

## 📊 Model Performance

A baseline Random Forest Regressor was trained on features engineered from video metadata. Evaluated on an unseen test set, the model achieved an **R-squared (R²) of 0.63**.

-   **R-squared (R²):**  0.63
-   **Mean Absolute Error (MAE):**  ~5.2 million views
-   **Root Mean Squared Error (RMSE):**  ~19.0 million views

## 🏛️ Project Architecture

1.  **Code (Backend):** Source code for the ML model (`train.py`), Lambda function (`lambda_function.py`), and CI/CD (`buildspec.yml`) is stored in **this GitHub repository**.
2.  **Storage:** The dataset and trained model artifact (.joblib file) are stored in **AWS S3**.
3.  **Model Training:** A containerized script is run as a one-off task on **AWS ECS Fargate** to train the model and save the artifact to S3.
4.  **CI/CD Pipeline:** A push to this repository triggers **AWS CodeBuild**, which builds a container image for the Lambda function and pushes it to **Amazon ECR**.
5.  **Serverless Inference:**  **AWS Lambda** runs the container from ECR, serving predictions.
6.  **API Layer:**  **Amazon API Gateway** provides a public HTTP endpoint that triggers the Lambda function.
7.  **Frontend:** A separate, modern frontend application built with **React & TypeScript** provides the user interface. It is hosted on **AWS S3** and communicates with the API Gateway endpoint. The code is available in its own [dedicated repository](https://github.com/MdEhsanulHaqueKanan/youtube-predictor-frontend).

## 🛠️ Tech Stack

-   **Cloud Platform:** AWS (Amazon Web Services)
-   **MLOps & CI/CD:** AWS CodeBuild, Docker, GitHub
-   **Compute:** AWS Lambda (Serverless), AWS ECS Fargate
-   **Storage & Hosting:** AWS S3
-   **API:** Amazon API Gateway
-   **Machine Learning (Backend):** Python, Scikit-learn, Pandas
-   **Frontend:** React, TypeScript, Vite, Tailwind CSS
-   **Infrastructure & Security:** AWS IAM
-   **Monitoring:** AWS CloudWatch

## 🚀 How to Use the API

The deployed model is available at the following endpoint:

**Endpoint URL:**  https://3bd5z76vu0.execute-api.us-east-1.amazonaws.com/v1/predict
**Method:**  POST
**Body (JSON):**
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

## ⚙️ Setting Up and Running the Project

This is an advanced MLOps project that requires a configured AWS environment. For instructions on how to run the user interface, please visit [the frontend repository](https://github.com/MdEhsanulHaqueKanan/youtube-predictor-frontend). While a simple local run is not possible due to the cloud-native architecture, here are the high-level steps to replicate the deployment:

### Prerequisites
*   An AWS Account with appropriate IAM permissions.
*   AWS CLI configured locally.
*   Docker installed locally.
*   A GitHub account.

### Setup and Deployment Steps

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/MdEhsanulHaqueKanan/aws-serverless-youtube-predictor.git
    cd aws-serverless-youtube-predictor
    ```

2.  **AWS Infrastructure Setup:**
    *   **Create S3 Bucket:** Manually create an S3 bucket to store the dataset and the trained model artifact.
    *   **Create ECR Repositories:** Manually create two private ECR repositories: one for the training image (e.g., `youtube-popularity-trainer`) and one for the inference image (`youtube-popularity-predictor`).

3.  **Run the Training Job:**
    *   The model can be trained by building the `Dockerfile.train` and running it as a one-off task on **AWS ECS Fargate**. This task reads the data from S3, trains the model, and saves the `youtube_popularity_model.joblib` artifact back to S3.

4.  **Set Up the CI/CD Pipeline:**
    *   Create an **AWS CodeBuild** project, connecting it to your forked GitHub repository.
    *   Configure the project's service role with permissions to push images to ECR.
    *   The `buildspec.yml` in this repository will automatically be used by CodeBuild.

5.  **Build the Lambda Image:**
    *   Trigger a build in CodeBuild. This will use the `Dockerfile.lambda` to build a Lambda-compatible container image and push it to your ECR repository.

6.  **Deploy the Serverless API:**
    *   Create an **AWS Lambda function** from the container image in ECR.
    *   Configure the Lambda's IAM role with permissions to read the model artifact from S3.
    *   Create an **Amazon API Gateway** (REST API) with a `/predict` resource and a `POST` method.
    *   Integrate the `POST` method with your Lambda function using Lambda Proxy Integration.
    *   Manually add and configure an `OPTIONS` method on the `/predict` resource to enable CORS.
    *   Deploy the API to a stage (e.g., `v1`).

7.  **Run the Frontend:**
    The frontend is a separate React application. To set it up, please clone its repository and follow the instructions in its README file.

    **Frontend Repository:** https://github.com/MdEhsanulHaqueKanan/youtube-predictor-frontend

    ___

    Developed by Md. Ehsanul Haque Kanan