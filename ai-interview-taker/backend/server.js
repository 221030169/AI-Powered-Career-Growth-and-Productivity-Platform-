require('dotenv').config();
const express = require('express');
const cors = require('cors');
const multer = require('multer');
const pdfParse = require('pdf-parse');
const Groq = require('groq-sdk');

const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());

// Set up multer for memory storage (we don't need to save the file to disk permanently)
const storage = multer.memoryStorage();
const upload = multer({ storage: storage });

// Initialize Groq API
const groq = new Groq({ apiKey: process.env.GROQ_API_KEY });

// Endpoint to upload resume and initialize interview
app.post('/api/upload-resume', upload.single('resume'), async (req, res) => {
    try {
        if (!req.file) {
            return res.status(400).json({ error: 'No resume file uploaded' });
        }

        // Parse PDF
        const data = await pdfParse(req.file.buffer);
        const resumeText = data.text;

        // Ask Groq to analyze resume and generate the first interview question
        const prompt = `You are an expert technical interviewer. I will provide you with a candidate's resume.
        Analyze the resume and prepare to conduct a technical interview.
        Start by greeting the candidate, briefly summarizing their key strengths as you see them, and then ask the very first interview question based on their experience or skills.

        Resume text:
        ${resumeText}`;

        const chatCompletion = await groq.chat.completions.create({
            messages: [{ role: "user", content: prompt }],
            model: "llama-3.3-70b-versatile",
        });
        const initialMessage = chatCompletion.choices[0].message.content;

        res.json({
            resumeText: resumeText, // Send back so frontend can hold it in state if needed
            initialMessage: initialMessage
        });
    } catch (error) {
        console.error('Error processing resume:', error);
        res.status(500).json({ error: 'Failed to process resume' });
    }
});

// Endpoint for interview chat
app.post('/api/chat', async (req, res) => {
    try {
        const { conversationHistory, resumeText } = req.body;

        if (!conversationHistory || conversationHistory.length === 0) {
            return res.status(400).json({ error: 'Conversation history is required' });
        }

        // Construct the prompt with context
        const prompt = `You are an expert technical interviewer conducting an interview.
        Here is the candidate's resume for context:
        ---
        ${resumeText}
        ---
        Here is the conversation history so far:
        ${conversationHistory.map(m => `${m.role === 'interviewer' ? 'Interviewer' : 'Candidate'}: ${m.text}`).join('\n\n')}

        You are the Interviewer. Respond naturally to the Candidate's last message. 
        Limit your response to 4-5 sentences and ask one clear question or follow-up at the end.
        Do NOT write "Interviewer:" at the start of your response, just provide the spoken text.`;

        const chatCompletion = await groq.chat.completions.create({
            messages: [{ role: "user", content: prompt }],
            model: "llama-3.3-70b-versatile",
        });

        res.json({ reply: chatCompletion.choices[0].message.content });
    } catch (error) {
        console.error('Error in chat:', error);
        res.status(500).json({ error: 'Failed to generate chat response' });
    }
});

// Endpoint to generate final feedback
app.post('/api/feedback', async (req, res) => {
    try {
        const { conversationHistory, resumeText } = req.body;

        const historyText = conversationHistory.map(msg => `${msg.role.toUpperCase()}: ${msg.text}`).join('\n\n');

        const prompt = `You are a senior technical recruiter and hiring manager.
        The candidate has just completed an AI-driven technical interview.
        
        Here is the candidate's resume:
        ---
        ${resumeText}
        ---

        Here is the full transcript of the interview:
        ---
        ${historyText}
        ---

        Please provide a detailed, constructive feedback report for the candidate.
        Format your response in Markdown with the following structure:
        1. **Final Score**: Give a numeric score out of 100 based on their performance, followed by a brief 1-sentence justification.
        2. **Overall Assessment**: A brief summary of their performance.
        3. **Strengths**: What they did well, topics they showed mastery in.
        4. **Areas for Improvement**: Specific topics or skills they struggled with or need to brush up on.
        5. **Recommended Topics to Study**: Actionable suggestions for what they should learn or practice before their next real interview and provide few youtube links to learn from them.
        
        Be objective, professional, and encouraging.`;

        const chatCompletion = await groq.chat.completions.create({
            messages: [{ role: "user", content: prompt }],
            model: "llama-3.3-70b-versatile",
        });

        res.json({ feedback: chatCompletion.choices[0].message.content });
    } catch (error) {
        console.error('Error generating feedback:', error);
        res.status(500).json({ error: 'Failed to generate feedback' });
    }
});

app.listen(port, () => {
    console.log(`Backend server running on http://localhost:${port}`);
});
