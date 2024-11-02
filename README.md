# FastAPI Blacklist Service

This project is a FastAPI-based service to manage a global blacklist of email addresses. It includes RESTful API endpoints for adding and checking emails in the blacklist. The service is Dockerized and can be run easily using Docker Compose.

## Prerequisites

Make sure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation and Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/fastapi-blacklist-service.git
   cd fastapi-blacklist-service
2. **Build the Docker Images: Run the following command to build the Docker images for the application**:
   ```bash
   docker-compose buil
3. **To start the FastAPI web service, run:**
   ```bash
   docker-compose up web
   
4. **To run the test suite, use the following command:**
   ```bash
    docker-compose up test
   
This command will execute the test cases defined in the tests folder.
The test results will be displayed in the terminal after the tests complete.
