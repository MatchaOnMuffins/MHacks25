# MHacks25 FastAPI Server

A FastAPI-based backend server for the MHacks25 project.

## Setup

1. **Create a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the server:**
   ```bash
   python main.py
   ```
   
   Or using uvicorn directly:
   ```bash
   uvicorn main:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

- `GET /` - Root endpoint with welcome message
- `GET /health` - Health check endpoint
- `GET /api/v1/test` - Test endpoint for API functionality

## Development

The server runs on `http://localhost:8000` by default.

- Interactive API documentation: `http://localhost:8000/docs`
- Alternative API documentation: `http://localhost:8000/redoc`

## Features

- ✅ FastAPI framework
- ✅ CORS middleware configured
- ✅ Auto-reload in development
- ✅ Interactive API documentation
- ✅ Health check endpoint
- ✅ Structured response format