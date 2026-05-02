import React from 'react';
import ReactMarkdown from 'react-markdown';
import { RotateCcw, Award } from 'lucide-react';

const Feedback = ({ feedbackText, onRestart }) => {
  return (
    <div className="glass-card feedback-container">
      <div style={{ textAlign: 'center', marginBottom: '2rem' }}>
        <Award size={64} color="var(--primary)" style={{ margin: '0 auto', marginBottom: '1rem' }} />
        <h2>Interview Complete!</h2>
        <p className="subtitle">Here is your personalized feedback report.</p>
      </div>

      <div style={{ background: 'rgba(0, 0, 0, 0.2)', padding: '2rem', borderRadius: '1rem', border: '1px solid var(--surface-border)' }}>
        <ReactMarkdown>{feedbackText}</ReactMarkdown>
      </div>

      <div style={{ marginTop: '3rem', textAlign: 'center' }}>
        <button className="btn" onClick={onRestart}>
          <RotateCcw size={18} /> Take Another Interview
        </button>
      </div>
    </div>
  );
};

export default Feedback;
