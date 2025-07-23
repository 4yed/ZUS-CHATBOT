# ZUS Coffee Assistant Chatbot

This project is a sophisticated chatbot designed to act as a virtual assistant for ZUS Coffee. It provides a conversational interface for users to ask about products and store locations. The application is built with a Python backend using FastAPI and a Gradio-based user interface.

## Features

- **Conversational AI**: Utilizes Azure OpenAI for natural language understanding and generation.
- **Product Information**: Users can ask questions about ZUS Coffee products, and the AI will provide intelligent answers based on available data.
- **Outlet Locator**: Allows users to find information about ZUS Coffee outlet locations.
- **Calculator Tool**: A handy, built-in calculator for performing simple arithmetic.
- **Agentic Planning**: For general conversation, the chatbot uses a simple agentic planning model to structure its responses.
- **Microservice Architecture**: The application is split into two main components:
  1.  A **FastAPI backend** that handles data processing and communication with the Azure OpenAI service.
  2.  A **Gradio frontend** that provides a user-friendly chat interface.

## Project Setup

Follow these steps to set up and run the project locally.

### 1. Prerequisites

- Python 3.9+
- An active Azure subscription with access to Azure OpenAI services.

### 2. Installation

First, create and activate a virtual environment to manage project dependencies:

```bash
# Create a virtual environment
python -m venv .venv

# Activate the virtual environment
# On Windows
.venv\Scripts\activate
# On macOS/Linux
source .venv/bin/activate
```

Next, install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Environment Variables

This project requires credentials to connect to the Azure OpenAI service. Create a file named `.env` in the root of the project directory and add the following variables:

```
AZURE_API_KEY="your_azure_api_key"
AZURE_ENDPOINT="your_azure_endpoint"
AZURE_API_VERSION="your_api_version"
AZURE_OPENAI_MODEL="your_chat_model_deployment_name"
```

Replace the placeholder values with your actual credentials from the Azure AI Studio.

## How to Run

Because the application is split into a backend and a frontend, you will need to run two separate commands in two different terminals from the project root directory.

### 1. Start the Backend Server

In your first terminal, run the following command to start the FastAPI backend:

```bash
uvicorn api.main:app --host 127.0.0.1 --port 8000
```

The backend will be available at `http://127.0.0.1:8000`.

### 2. Start the Chatbot Interface

In your second terminal, run the following command to start the Gradio UI:

```bash
python api/chatbot.py
```

The chatbot interface will launch and be available at `http://127.0.0.1:7860`. You can now open this URL in your web browser to interact with the ZUS Coffee Assistant. 