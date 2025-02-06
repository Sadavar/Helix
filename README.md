# Helix AI

Welcome to **Helix AI**, a conversational AI platform built to be an HR assistant for generating campaigns. This guide will walk you through the steps to set up and run the project locally.


![alt lowfi_diagram](/images/interface.jpg)
![alt lowfi_diagram](/images/image.webp)

## Installation Guide

To get started, follow the instructions below to set up the backend and frontend.

### Step 1: Set up the Backend

1. **Navigate to the backend directory**:
    ```bash
    cd backend
    ```

2. **Create and activate a Python virtual environment**:
    ```bash
    python3 -m venv env
    source env/bin/activate  # For macOS/Linux
    # source env\Scripts\activate  # For Windows
    ```

3. **Install the required Python packages**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Flask backend**:
    ```bash
    flask run
    ```

The Flask backend should now be running on `http://localhost:5000`.

---

### Step 2: Set up the Frontend

1. **Navigate to the frontend directory**:
    ```bash
    cd frontend
    ```

2. **Install the required Node.js dependencies**:
    ```bash
    npm install
    ```

3. **Run the frontend application**:
    ```bash
    npm run dev
    ```

The frontend should now be running on `http://localhost:5173`.

---

### Step 3: Access the Application

1. Open your browser and navigate to:
    ```
    http://localhost:5173
    ```

2. **Login** with any username (e.g., `user1` or `guest`).

3. Start chatting and experience the magic of Helix AI!

---

## Project Structure

- **Backend**: 
  - Python Flask and Websocket to serve the API. Langgraph to handle the core AI logic.
  
- **Frontend**: 
  - ReactJS combined with Websocket for a dynamic interface

---

Happy chatting with Helix AI! ✨
