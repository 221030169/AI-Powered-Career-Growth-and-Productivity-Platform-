# AI Interview Taker

An intelligent, full-stack application that conducts technical interviews based on a candidate's resume. The platform provides a proctored environment with a time limit, interactive chat (with audio capabilities), and comprehensive feedback at the end of the session.

## 🚀 Tech Stack

### Frontend
- **React (v18)**: Core library for building the interactive user interface.
- **Vite**: Ultra-fast build tool and development server.
- **Axios**: Handling HTTP requests to the backend API.
- **Lucide React**: Providing clean and consistent UI icons.
- **React Markdown**: Rendering structured markdown responses from the AI.
- **Vanilla CSS**: Custom styling for a modern, responsive design.

### Backend
- **Node.js**: JavaScript runtime environment for the server.
- **Express.js**: Web framework for handling API routing and middleware.
- **Groq SDK (`groq-sdk`)**: Integrates with Groq's high-speed inference API to power the AI interviewer. Used to bypass standard rate limits and provide extremely low-latency conversational responses.
- **Google Generative AI (`@google/generative-ai`)**: Additional AI capabilities fallback/support.
- **Multer**: Middleware for handling file uploads, primarily used for receiving PDF resumes.
- **PDF-Parse (`pdf-parse`)**: Extracts raw text data from uploaded PDF resumes so the AI can analyze the candidate's background and tailor questions.
- **Cors**: Enables secure Cross-Origin Resource Sharing between the React frontend and Express backend.
- **Dotenv**: Manages environment variables securely (like API keys).

## 🎯 Key Features
- **Resume-Based Interviews**: Upload a PDF resume, and the AI tailors its technical questions to your specific experience and skills.
- **Proctored Environment**: Simulates a real interview with web-camera access and a strict automated session timer (e.g., 10 minutes).
- **Voice Capabilities**: Supports text-to-speech for the interviewer's questions and speech-to-text for the candidate's answers.
- **Comprehensive Evaluation**: Once the interview concludes or the time runs out, the AI generates detailed, constructive feedback and scoring based on your performance.

## 🛠️ How to Run Locally

### Prerequisites
- Node.js (v18 or higher recommended)
- A Groq API Key (and optionally a Google Gemini API Key)

### 1. Clone the Repository
```bash
git clone <your-repository-url>
cd ai-interview-taker
```

### 2. Backend Setup
Navigate to the backend directory, install dependencies, and configure environment variables.
```bash
cd backend
npm install
```

Create a `.env` file in the `backend` directory:
```env
# backend/.env
PORT=5000
GROQ_API_KEY=your_groq_api_key_here
GEMINI_API_KEY=your_gemini_api_key_here
```
*(Note: Replace the placeholder keys with your actual API keys. The Groq API is primarily used for the high-speed chat completion).*

Start the backend server:
```bash
# For development with auto-reload:
npm run dev

# Or for standard start:
npm start
```
The backend will typically run on `http://localhost:5000`.

### 3. Frontend Setup
Open a new terminal window, navigate to the frontend directory, and install dependencies.
```bash
cd frontend
npm install
```

Start the frontend development server:
```bash
npm run dev
```

### 4. Access the Application
Once both servers are running, open your browser and navigate to the local URL provided by Vite (typically `http://localhost:5173`).
