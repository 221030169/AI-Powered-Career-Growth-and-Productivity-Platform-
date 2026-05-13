# 🚀 AI-Powered Career Growth and Productivity Platform

An intelligent, full-stack platform that helps students and professionals prepare for their careers through **AI-powered resume analysis, cover letter generation, interview training, job application tracking, and career insights powered by machine learning**.

---
![ca](https://github.com/user-attachments/assets/eb7959ef-dfae-40a0-adf4-4dc916162478)
<img width="1682" height="925" alt="MP1" src="https://github.com/user-attachments/assets/f056f951-0154-4a63-bbbe-35fc81aac743" />
<img width="1637" height="904" alt="MP2" src="https://github.com/user-attachments/assets/2838b765-fb16-4c4a-b538-a29b9244433d" />
<img width="1915" height="871" alt="MP3" src="https://github.com/user-attachments/assets/d7b8d5ea-08f8-4938-bb96-f6fbb804be2a" />



## 📌 Project Description

The **AI-Powered Career Growth and Productivity Platform** is a comprehensive career preparation suite combining:
- **Career Companion Web Application** – A full-stack MERN application for job application tracking, interview preparation, and cover letter generation
- **AI/ML Resume Parser & Analyzer** – Python-based CV parsing with Ollama LLM for intelligent resume analysis and career recommendations

This unified platform streamlines the entire job search journey by automating document processing, generating personalized content, providing AI-driven interview practice, and delivering actionable career insights.

---

## ✨ Key Features

### 🌐 Career Companion Web Platform
- 📱 **Application Tracking System** – Track job applications with status updates, interview dates, and company details
- ✍️ **AI Cover Letter Generator** – Generate personalized cover letters using Gemini AI
- 🎤 **Interview Training Module** – Practice technical interviews with AI-generated questions and real-time feedback
- 📄 **Resume Builder** – Create ATS-optimized resumes with professional templates
- 👤 **User Management** – Secure authentication with JWT tokens and bcrypt password hashing
- 💬 **Feedback System** – Store and review company-specific interview feedback with ratings
- 📊 **Dashboard** – Track your job search progress and manage all documents in one place

### 🤖 AI/ML Resume Analysis Engine
- 🔍 **Intelligent CV Parsing** – Extract structured data from PDF/DOCX resumes using Ollama LLM
- 📈 **Career Growth Scoring** – AI-powered assessment of career potential (0-10 scale)
- 🎯 **ATS Compatibility Analysis** – Score resumes for Applicant Tracking System compatibility (0-100)
- 💼 **Job Recommendations** – Get personalized job role suggestions based on profile analysis
- 🧠 **Skill Extraction** – Automatically identify and categorize technical and professional skills
- 📚 **Experience & Education Parsing** – Extract and structure work history, education, certifications, and projects
- 🌍 **Language Detection** – Support for multi-language resumes

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│              Career Companion Web Application               │
│         (React Frontend + Express.js Backend)               │
├─────────────────────────────────────────────────────────────┤
│  • Job Application Tracking                                 │
│  • Interview Preparation (Gemini AI Integration)            │
│  • Cover Letter Generation                                  │
│  • Resume Builder                                           │
│  • User Authentication & Profiles                           │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│              MongoDB Database                               │
│  • Users  • Applications  • Cover Letters                    │
│  • Feedback  • Interview Records                            │
└─────────────────────────────────────────────────────────────┘
           ↓
┌─────────────────────────────────────────────────────────────┐
│       AI/ML Resume Parser & Analyzer (Python)               │
│            (Ollama LLM + OCR Processing)                    │
├─────────────────────────────────────────────────────────────┤
│  • CV File Processing (PDF/DOCX → Text)                     │
│  • Resume Parsing (Skills, Experience, Education)           │
│  • Career Analysis (Growth Score, ATS Score)                │
│  • Job Recommendations                                      │
└─────────────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
AI-Powered-Career-Growth-and-Productivity-Platform/
├── Career Companion/                    # Main MERN Application
│   ├── api/                             # Express.js Backend
│   │   ├── controllers/                 # Business logic
│   │   │   ├── users.js
│   │   │   ├── applications.js
│   │   │   ├── coverLetters.js
│   │   │   ├── feedbacks.js
│   │   │   ├── tokens.js (Authentication)
│   │   │   └── openaiController.js      # Gemini AI Integration
│   │   ├── models/                      # MongoDB Schemas
│   │   │   ├── user.js
│   │   │   ├── application.js
│   │   │   ├── coverLetter.js
│   │   │   ├── feedback.js
│   │   │   └── token_generator.js
│   │   ├── routes/                      # API Routes
│   │   ├── spec/                        # Jest Tests
│   │   ├── app.js                       # Express App Setup
│   │   ├── package.json
│   │   └── jest.config.js
│   ├── frontend/                        # React Frontend
│   │   ├── src/
│   │   │   ├── components/              # 25+ React Components
│   │   │   │   ├── app/
│   │   │   │   ├── auth/
│   │   │   │   ├── applications/
│   │   │   │   ├── Interview/
│   │   │   │   ├── coverLetterGen/
│   │   │   │   ├── resumeGenerator/
│   │   │   │   └── ...
│   │   │   ├── index.js
│   │   │   └── index.css
│   │   ├── cypress/                     # E2E Tests
│   │   ├── public/
│   │   ├── package.json
│   │   ├── tailwind.config.js
│   │   ├── config-overrides.js
│   │   └── cypress.config.js
│   ├── package.json
│   ├── README.md
│   └── build.sh
├── cv parser/                           # Python ML Module
│   ├── config.py                        # Configuration
│   ├── llm_parser.py                    # Ollama LLM Integration
│   ├── regex_parser.py                  # Regex-based Parsing
│   ├── preprocess_cv.py                 # CV File Processing
│   ├── resume_ai_analysis.py            # Career Analysis
│   ├── logger.py                        # Logging Utilities
│   ├── requirements.txt
│   ├── cv_files/                        # Input CV Files
│   ├── extracted_text/                  # Extracted Text
│   └── parsed_results/                  # Parsing Output
├── README.md                            # This File
├── requirements.txt                     # Python Dependencies
├── package.json                         # Node.js Dependencies
└── LICENSE
```

---

## 🔧 Technologies Used

### Frontend
- **React** 18.2.0 – UI Library
- **React Router** 6.3.0 – Client-side routing
- **Tailwind CSS** 3.x – Utility-first CSS framework
- **Daisy UI** – Component library
- **Material Tailwind React** – Advanced UI components
- **React Icons** – Icon library

### Backend
- **Node.js** ≥18.1.0 – JavaScript Runtime
- **Express.js** 4.18.2 – Web Framework
- **MongoDB** 3.4.1 & Mongoose 5.8.11 – Database & ODM
- **JWT (jsonwebtoken)** 9.0.0 – Authentication
- **Bcrypt** 5.1.0 – Password Hashing
- **Axios** 1.4.0 – HTTP Client
- **CORS** 2.8.5 – Cross-Origin Resource Sharing
- **Supertest** 6.2.4 – HTTP Assertion Library

### AI/ML & External APIs
- **Ollama** – Local LLM inference (llama3.2, mxbai-embed-large)
- **Google Gemini API** – AI-powered content generation (interview questions, cover letters)
- **Groq** – Alternative LLM option
- **Google Cloud Vision** – OCR for document processing
- **PDF Processing** – PyMuPDF, pdf2image, pdfminer.six, pypdf
- **Multer** - Middleware for handling file uploads, primarily used for receiving PDF resumes.

### Testing
- **Jest** 27.5.1 – JavaScript Unit Testing
- **Cypress** 10.7.0 – E2E Testing
- **Supertest** 6.2.4 – API Testing

### Python & Data Processing
- **OpenCV** – Image processing for CV analysis
- **Pytesseract** – OCR Engine
- **Pillow** – Image manipulation
- **Pandas** – Data processing
- **NumPy** – Numerical computing
- **NLTK** – Natural Language Processing
- **Regex** – Advanced pattern matching
- **python-dotenv** – Environment variable management

### Deployment & DevOps
- **Nodemon** – Development auto-reload
- **ESLint** – Code linting
- **Morgan** – HTTP request logging
- **Debug** – Debugging utility

---

## 🛠️ Installation & Setup

### Prerequisites
- **Node.js** ≥18.1.0
- **npm** (comes with Node.js)
- **MongoDB** 5.0+ (local or cloud instance like MongoDB Atlas)
- **Python** 3.8+
- **Ollama** (for CV Parser AI features) – [Download](https://ollama.com)

### Step 1: Clone the Repository
```bash
git clone https://github.com/221030169/AI-Powered-Career-Growth-and-Productivity-Platform-.git
cd AI-Powered-Career-Growth-and-Productivity-Platform
```

### Step 2: Setup Environment Variables

Create a `.env` file in the root and `Career Companion/api/` directories:

**Root `.env`:**
```env
# MongoDB Configuration
MONGODB_URL=mongodb://localhost:27017/career_companion

# JWT Configuration
JWT_SECRET=your_super_secret_jwt_key_here

# Gemini API (Google)
GEMINI_API_KEY=your_gemini_api_key_here

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL_NAME=llama3.2:latest
OLLAMA_EMBEDDING_MODEL_NAME=mxbai-embed-large

# Optional: Groq API
GROQ_API_KEY=your_groq_api_key_if_using
```

### Step 3: Install Dependencies

**Backend (Express.js API):**
```bash
cd "Career Companion/api"
npm install
```

**Frontend (React):**
```bash
cd "Career Companion/frontend"
npm install
```

**Python (CV Parser):**
```bash
pip install -r requirements.txt
```

### Step 4: Setup MongoDB

**Option A: Local MongoDB**
```bash
# On macOS with Homebrew
brew tap mongodb/brew
brew install mongodb-community@5.0
brew services start mongodb-community@5.0

# On Windows
# Download and install from: https://www.mongodb.com/try/download/community
```

**Option B: MongoDB Atlas (Cloud)**
- Create a cluster at https://www.mongodb.com/cloud/atlas
- Get your connection string and update `MONGODB_URL` in `.env`

### Step 5: Setup Ollama (for CV Parser)
```bash
# Download and install Ollama from https://ollama.com

# Start Ollama service
ollama serve

# In a new terminal, pull the required models:
ollama pull llama3.2
ollama pull mxbai-embed-large
```

### Step 6: Start the Application

**Terminal 1 - Backend API:**
```bash
cd "Career Companion/api"
JWT_SECRET=your_secret npm start
# Server runs on http://localhost:8080
```

**Terminal 2 - Frontend React:**
```bash
cd "Career Companion/frontend"
npm start
# App opens at http://localhost:3000
```

**Terminal 3 - Python CV Parser (Optional):**
```bash
cd "cv parser"
python resume_ai_analysis.py
# Or run specific parsing scripts as needed
```

---

## 🧪 Testing

### Backend Tests (Jest + Supertest)
```bash
cd "Career Companion/api"

# Run tests
JWT_SECRET=test_secret npm test

# Run with coverage
JWT_SECRET=test_secret npm run test-coverage

# Run in test mode (uses test DB)
JWT_SECRET=test_secret npm run start:test
```

### Frontend Tests (Cypress)
```bash
cd "Career Companion/frontend"

# Run E2E tests
npm run test:feature

# Run component tests
npm run test:unit

# Open Cypress test runner
npx cypress open
```

---

## 🚀 Usage Guide

### Career Companion Web Application

1. **Sign Up / Login**
   - Create a new account with email and password
   - Secure JWT-based authentication

2. **Track Applications**
   - Add job applications with company, role, location
   - Update application status (Applied, Interviewing, Offered, Rejected)
   - Set interview dates and view upcoming interviews

3. **Interview Preparation**
   - Select a job role
   - Generate AI interview questions using Gemini API
   - Answer questions and receive AI-powered feedback
   - Review suggestions for improvement

4. **Generate Cover Letters**
   - Provide job details and resume information
   - AI generates personalized cover letters (max 750 chars)
   - Save and manage multiple cover letters

5. **Resume Building**
   - Create ATS-optimized resumes
   - Get professional templates
   - Export and download resumes

6. **Leave Feedback**
   - Rate companies and interview experiences
   - Leave detailed feedback for future reference
   - Track hiring process quality

### AI/ML Resume Parser

1. **Upload CV**
   - Place PDF or DOCX files in `cv parser/cv_files/` directory
   - Supported formats: PDF, DOCX, DOC

2. **Process Resume**
   ```bash
   cd "cv parser"
   python regex_parser.py
   ```

3. **Get Analysis**
   - Career growth score (0-10)
   - ATS compatibility score (0-100)
   - Recommended job roles
   - Extracted structured data (skills, experience, education)

4. **Review Results**
   - Check `parsed_results/` for JSON output
   - Review extracted text in `extracted_text/`
   - Analyze AI-generated insights

---

## 🔗 Collaboration & Resources

- **Google Sheets** (Tracking): [Link](https://docs.google.com/spreadsheets/d/1D7d73RoPsWiXYDLpLn3yKUmkUo6Zbmsh0cgXwXYguF8/edit?usp=sharing)


---

## 🤝 Contributing

We welcome contributions! Follow these steps:

1. **Fork the repository**
   ```bash
   git fork https://github.com/221030169/AI-Powered-Career-Growth-and-Productivity-Platform-.git
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make your changes**
   - Follow existing code style and conventions
   - Write tests for new functionality
   - Update documentation as needed

4. **Commit your changes**
   ```bash
   git commit -m "Add feature: brief description"
   ```

5. **Push to your fork**
   ```bash
   git push origin feature/your-feature-name
   ```

6. **Create a Pull Request**
   - Provide clear description of changes
   - Reference related issues
   - Ensure all tests pass

---

## 📋 API Endpoints

### Authentication
- `POST /users` – Create new user
- `POST /tokens` – Login (returns JWT token)

### Job Applications
- `GET /applications` – Get all applications
- `POST /applications` – Create application
- `PUT /applications/:applicationId` – Update application
- `DELETE /applications/:applicationId` – Delete application

### Cover Letters
- `GET /coverLetterGen` – Get all cover letters
- `POST /coverLetterGen` – Save generated cover letter

### Interview Feedback
- `GET /feedback` – Get all feedback
- `POST /feedback` – Save feedback
- `DELETE /feedback/:feedbackId` – Delete feedback

### AI Features (Gemini)
- `POST /openai/interviewQuestions` – Generate interview questions
- `POST /openai/interviewFeedback` – Generate interview feedback
- `POST /openai/coverLetter` – Generate cover letter

---

## 📜 License

This project is licensed under the **CC BY-NC-SA 4.0 License** – see the [LICENSE](LICENSE) file for details.

**Key Terms:**
- ✅ Share and adapt for non-commercial purposes
- ✅ Must provide attribution
- ⚠️ Non-commercial use only
- ⚠️ Same license must be applied to derivatives

---

## 👥 Authors & Contributors

### Original Team
- **Priyansh Lunawat** (221030169) – AI/ML & Lead Developer
- **Udit Sharma** (221030199) – AI/ML Engineer
- **Naman Mittal** (221030359) – Full-Stack Developer
- **Ashish Agarwal** (221030420) – Full-Stack Developer



---

## 🆘 Troubleshooting

### MongoDB Connection Issues
- Ensure MongoDB is running: `mongosh` (or `mongo` for older versions)
- Check `MONGODB_URL` in `.env` file
- Verify connection string format: `mongodb://host:port/database`

### Ollama Connection Failed
- Ensure Ollama is installed and running: `ollama serve`
- Check `OLLAMA_HOST` configuration (default: http://localhost:11434)
- Pull required models: `ollama pull llama3.2`

### JWT Authentication Errors
- Ensure `JWT_SECRET` is set in environment variables
- Check token expiration (currently 60 minutes)
- Verify Authorization header format: `Bearer <token>`

### Port Already in Use
- Backend default: 8080 (change in `bin/www`)
- Frontend default: 3000 (CRA uses this)
- Change ports if conflicts occur


---

## 📞 Support & Contact

For issues, questions, or suggestions:
- Create an Issue on GitHub
- Contact the development team through LinkedIn
- Check existing documentation and troubleshooting guide

---

**Happy career hunting! 🚀**
