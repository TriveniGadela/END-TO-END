# AI Learning Platform

A personalized learning platform powered by OpenAI that provides explanations tailored to different academic levels.

## Features

- User registration and authentication
- Personalized explanations based on academic level (School, College, Graduate)
- AI-powered content generation using OpenAI GPT
- Clean, responsive web interface
- Secure session management

## Setup Instructions

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Create a `.env` file with:
```
OPENAI_API_KEY=your_openai_api_key_here
FLASK_SECRET_KEY=your_secret_key_here
DATABASE_URL=learning_platform.db
```

### 3. OpenAI Setup
1. Get your API key from https://platform.openai.com/api-keys
2. Add it to your .env file
3. Ensure you have credits in your OpenAI account

### 4. Run the Application
```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Usage

1. Register a new account with your academic level
2. Login to access the dashboard
3. Enter any topic you want to learn about
4. Get AI-generated explanations tailored to your level
5. Update your academic level anytime for different complexity