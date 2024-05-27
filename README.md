
# News Groqqer

## Description
This project focuses on creating an end-to-end, rag-enabled News Generation and Summarization Pipeline. The infrastructure will be hosted on AWS and I'll soon provide Terraform templates. I will be using groq, an insanely fast API provider for Open Source LLMs. The free tier provides 30 requests per minute which is enough when compared to the scope of this project.


## Architecture Diagram

![groqqer_architecture](https://github.com/vinamrgrover/news-groqqer/assets/100070155/96300eeb-20d6-4fb5-a8f4-20937c730b8f)


## Prerequisites

- Vector Databases (PGVector, Pinecone, etc.)
- NDTV RSS Feeds (Non-Commercial use)
	NDTV provides access to their various RSS Feeds. Below is an RSS Feeds that contains content about Technology:
	
	https://feeds.feedburner.com/gadgets360-latest
- An AWS Account **(Note : your cloud expenses might spike up)**
- Groq API Key (create one [here](https://console.groq.com/login))
- Langchain
- Discord Webhook

## Get started


### Building docker image
```
docker build -t groqqer:latest .
```

## Creating an RDS Instance

Create an AWS RDS Instance by going to RDS Console.
- Select PostgreSQL.
- Select t3.micro as Instance Type.

## Requesting Bedrock Access

Go to the Bedrock Console and under base models request access for **Titan Multimodal Embeddings Generation 1**

## Deploying Image to ECR


1. Create an ECR Repository either via console or via AWS CLI 

```
aws ecr create-repository \
    --repository-name <repo_name>
    --region <region_name>
```
2. Push the Docker Image to your ECR Repository. Refer to this guide on [How to push images to an ECR Repository](https://docs.aws.amazon.com/AmazonECR/latest/userguide/docker-push-ecr-image.html)


### Creating a discord server and getting Webhook URL

Open Discord and create a server. Under server, go to settings -> integrations. Create a webhook and select a channel, that would serve as a destination for your webhook.

### Deploying container to ECS (Fargate)
   
 3.1 Create an ECS Cluster.

<img width="500" alt="Screenshot 2024-05-28 at 2 00 10 AM" src="https://github.com/vinamrgrover/news-groqqer/assets/100070155/f139ed63-4308-4b7b-830c-0f905fae4236">

 3.2 Create a Task Definition Family.

- Select AWS Fargate as launch type.
- Under task size select the following values
	- CPU -  2vCPU
	- Memory - 4GB
- Under Task Execution Role:
	- Go to the IAM Console and create an IAM Role for AWS ECS - Elastic Container Service Task.
	- Attach [AmazonBedrockFullAccess] IAM Policy to your IAM Role
	- Now select the newly created role.
- Under Container - 1, enter your preferred container name and enter the ECR Image URI under Image URI.

- Leave all other fields as default and click create.

 <img width="500" alt="Screenshot 2024-05-28 at 1 49 24 AM" src="https://github.com/vinamrgrover/news-groqqer/assets/100070155/6eecd96d-4fb9-40bc-b2e5-23f128671d40">

 
 3.3 Create an ECS Service under your ECS cluster created in step 3.1.

<img width="500" alt="Screenshot 2024-05-28 at 1 51 29 AM" src="https://github.com/vinamrgrover/news-groqqer/assets/100070155/ba9dfad2-0270-48e4-ba3b-6b10b250bd87">
 
 3.4 Now still in ECS Cluster, finally run a task.

 <img width="500" alt="Screenshot 2024-05-28 at 1 52 54 AM" src="https://github.com/vinamrgrover/news-groqqer/assets/100070155/abd04aab-74c4-4275-9cf4-0c51bc3a1eca">

## Attach a Chat Interface (Optional)
coming soon


