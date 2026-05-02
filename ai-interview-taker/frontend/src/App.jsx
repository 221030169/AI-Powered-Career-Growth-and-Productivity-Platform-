import React, { useState } from 'react';
import ResumeUpload from './components/ResumeUpload';
import InterviewChat from './components/InterviewChat';
import Feedback from './components/Feedback';
import { BrainCircuit } from 'lucide-react';

function App() {
  const [step, setStep] = useState('upload'); // 'upload', 'interview', 'feedback'
  const [resumeData, setResumeData] = useState({ text: '', initialMessage: '' });
  const [feedbackText, setFeedbackText] = useState('');

  const handleUploadSuccess = (data) => {
    setResumeData({
      text: data.resumeText,
      initialMessage: data.initialMessage
    });
    setStep('interview');
  };

  const handleInterviewFinish = (feedback) => {
    setFeedbackText(feedback);
    setStep('feedback');
  };

  const handleRestart = () => {
    setResumeData({ text: '', initialMessage: '' });
    setFeedbackText('');
    setStep('upload');
  };

  return (
    <div className="app-container">
      <header>
        <BrainCircuit size={48} color="var(--primary)" style={{ margin: '0 auto 1rem auto' }} />
        <h1>AI Interviewer Dojo</h1>
        <p className="subtitle">
          {step === 'upload' && "Upload your resume to start a realistic AI technical interview."}
          {step === 'interview' && "Answer the questions as if it were a real interview."}
          {step === 'feedback' && "Review your feedback and improve your skills."}
        </p>
      </header>

      <main>
        {step === 'upload' && (
          <ResumeUpload onUploadSuccess={handleUploadSuccess} />
        )}

        {step === 'interview' && (
          <InterviewChat
            resumeText={resumeData.text}
            initialMessage={resumeData.initialMessage}
            onFinish={handleInterviewFinish}
          />
        )}

        {step === 'feedback' && (
          <Feedback
            feedbackText={feedbackText}
            onRestart={handleRestart}
          />
        )}
      </main>
    </div>
  );
}

export default App;
