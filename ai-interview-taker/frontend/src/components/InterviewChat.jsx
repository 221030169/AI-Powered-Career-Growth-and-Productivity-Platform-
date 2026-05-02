import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Send, User, Bot, CheckCircle, Mic, Camera, Clock } from 'lucide-react';
import axios from 'axios';
import ReactMarkdown from 'react-markdown';

const InterviewChat = ({ resumeText, initialMessage, onFinish }) => {
  const [messages, setMessages] = useState([
    { role: 'interviewer', text: initialMessage }
  ]);
  const [inputValue, setInputValue] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [isEnding, setIsEnding] = useState(false);
  
  // Timers and states
  const [timeLeft, setTimeLeft] = useState(900); // 15 minutes overall
  const [answerTimeLeft, setAnswerTimeLeft] = useState(120); // 2 minutes per answer
  const [isListening, setIsListening] = useState(false);
  const [cameraActive, setCameraActive] = useState(false);
  const [isInterviewerSpeaking, setIsInterviewerSpeaking] = useState(false);

  const chatHistoryRef = useRef(null);
  const videoRef = useRef(null);
  const recognitionRef = useRef(null);
  const hasSpokenInitialRef = useRef(false);
  const prevInputRef = useRef('');

  // Setup Speech Recognition
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      recognition.continuous = true;
      recognition.interimResults = true;
      
      recognition.onresult = (event) => {
        let currentTranscript = '';
        for (let i = 0; i < event.results.length; i++) {
          currentTranscript += event.results[i][0].transcript;
        }
        setInputValue(prevInputRef.current + currentTranscript);
      };
      
      recognition.onerror = (event) => {
        console.error("Speech recognition error", event.error);
        setIsListening(false);
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognitionRef.current = recognition;
    } else {
      console.warn("Speech Recognition API is not supported in this browser.");
    }
  }, []);

  // Main Interview Timer
  useEffect(() => {
    if (timeLeft <= 0) {
      if (!isEnding) handleEndInterview();
      return;
    }
    const timer = setInterval(() => setTimeLeft(prev => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [timeLeft, isEnding]);

  // Answer Timer
  useEffect(() => {
    if (isInterviewerSpeaking || isTyping || isEnding) return;

    if (answerTimeLeft <= 0) {
      // Auto-submit when answer time runs out
      handleSendMessage(true);
      return;
    }
    const timer = setInterval(() => setAnswerTimeLeft(prev => prev - 1), 1000);
    return () => clearInterval(timer);
  }, [answerTimeLeft, isInterviewerSpeaking, isTyping, isEnding]);

  // Camera logic
  useEffect(() => {
    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
        if (videoRef.current) videoRef.current.srcObject = stream;
        setCameraActive(true);
      } catch (err) {
        console.error("Error accessing camera:", err);
      }
    };
    startCamera();
    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  // Scroll to bottom
  useEffect(() => {
    if (chatHistoryRef.current) {
      chatHistoryRef.current.scrollTop = chatHistoryRef.current.scrollHeight;
    }
  }, [messages, isTyping]);

  // Speech Synthesis
  const speakText = useCallback((text) => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsInterviewerSpeaking(true);
      
      const cleanText = text.replace(/[*#_`~]/g, '');
      const utterance = new SpeechSynthesisUtterance(cleanText);
      
      utterance.onend = () => {
        setIsInterviewerSpeaking(false);
        setAnswerTimeLeft(120); // Reset answer timer to 2 minutes when they finish speaking
      };
      
      utterance.onerror = () => {
        setIsInterviewerSpeaking(false);
        setAnswerTimeLeft(120);
      };

      window.speechSynthesis.speak(utterance);
    }
  }, []);

  // Speak initial message
  useEffect(() => {
    if (!hasSpokenInitialRef.current) {
      speakText(initialMessage);
      hasSpokenInitialRef.current = true;
    }
  }, [initialMessage, speakText]);

  const toggleListening = () => {
    if (isListening) {
      recognitionRef.current?.stop();
    } else {
      prevInputRef.current = inputValue ? inputValue + ' ' : '';
      try {
        recognitionRef.current?.start();
        setIsListening(true);
      } catch (e) {
        console.error(e);
      }
    }
  };

  const handleSendMessage = async (isAutoSubmit = false) => {
    // If not auto submit and empty, do nothing
    if (!isAutoSubmit && !inputValue.trim()) return;

    let finalInput = inputValue;
    // If auto submit and empty, inject default message
    if (isAutoSubmit && !finalInput.trim()) {
      finalInput = "[Candidate did not respond in time]";
    }

    if (isListening) {
      recognitionRef.current?.stop();
    }

    const userMessage = { role: 'user', text: finalInput };
    const newMessages = [...messages, userMessage];
    
    setMessages(newMessages);
    setInputValue('');
    setIsTyping(true);
    setAnswerTimeLeft(120); // pause visual timer

    try {
      const response = await axios.post('http://localhost:5000/api/chat', {
        conversationHistory: newMessages,
        resumeText: resumeText
      });

      const replyText = response.data.reply;
      setMessages([...newMessages, { role: 'interviewer', text: replyText }]);
      speakText(replyText);
    } catch (err) {
      console.error(err);
      const errorMsg = "I'm sorry, I'm having trouble connecting to my network. Could you repeat that?";
      setMessages([...newMessages, { role: 'interviewer', text: errorMsg }]);
      speakText(errorMsg);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage(false);
    }
  };

  const handleEndInterview = async () => {
    setIsEnding(true);
    if (isListening) recognitionRef.current?.stop();
    window.speechSynthesis.cancel();

    try {
      const response = await axios.post('http://localhost:5000/api/feedback', {
        conversationHistory: messages,
        resumeText: resumeText
      });
      onFinish(response.data.feedback);
    } catch (err) {
      console.error(err);
      alert('Failed to generate feedback. Please try again.');
      setIsEnding(false);
    }
  };

  const formatTime = (seconds) => {
    const m = Math.floor(seconds / 60);
    const s = seconds % 60;
    return `${m}:${s < 10 ? '0' : ''}${s}`;
  };

  return (
    <div className="interview-layout">
      <div className="interview-sidebar glass-card">
        <div className="camera-container">
          <video ref={videoRef} autoPlay playsInline muted className="camera-feed" />
          {!cameraActive && (
            <div className="camera-off-overlay">
              <Camera size={32} />
              <p>Requesting Camera...</p>
            </div>
          )}
          {cameraActive && (
             <div className="recording-indicator">
              <span className="dot animate-pulse"></span>
              Monitoring
            </div>
          )}
        </div>
        
        <div className="timer-container" style={{ marginBottom: 0 }}>
          <h3>Total Exam Time</h3>
          <div className={`timer-display ${timeLeft < 300 ? 'text-red-500' : ''}`}>
            {formatTime(timeLeft)}
          </div>
          <p className="timer-subtext">Exam auto-submits when time is up.</p>
        </div>

        <div className="timer-container" style={{ background: 'rgba(59, 130, 246, 0.05)', borderColor: 'rgba(59, 130, 246, 0.2)' }}>
          <h3 style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}>
            <Clock size={16} /> Answer Time
          </h3>
          <div className={`timer-display ${answerTimeLeft <= 30 ? 'text-red-500' : ''}`} style={{ fontSize: '2rem' }}>
            {isInterviewerSpeaking ? "Waiting..." : formatTime(answerTimeLeft)}
          </div>
          <p className="timer-subtext">Auto-submits your current answer.</p>
        </div>

        <button 
          className="btn btn-secondary w-full" 
          onClick={handleEndInterview}
          disabled={isEnding || messages.length < 3}
          style={{ marginTop: 'auto' }}
        >
          {isEnding ? (
            <><div className="spinner" style={{ width: '16px', height: '16px' }}></div> Finishing...</>
          ) : (
            <><CheckCircle size={18} /> Finish Interview</>
          )}
        </button>
      </div>

      <div className="glass-card chat-container" style={{ margin: 0, height: '100%' }}>
        {/* Chat History */}
        <div className="chat-history" ref={chatHistoryRef}>
          {messages.map((msg, idx) => (
            <div key={idx} className={`message ${msg.role}`}>
              <div className={`avatar ${msg.role}`}>
                {msg.role === 'interviewer' ? <Bot size={20} color="white" /> : <User size={20} color="white" />}
              </div>
              <div className="message-content">
                {msg.role === 'interviewer' ? (
                   <ReactMarkdown>{msg.text}</ReactMarkdown>
                ) : (
                  msg.text
                )}
              </div>
            </div>
          ))}
          {isTyping && (
            <div className="message interviewer">
              <div className="avatar interviewer">
                <Bot size={20} color="white" />
              </div>
              <div className="message-content loading-dots">
                <span></span><span></span><span></span>
              </div>
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="chat-input-area">
          <button 
            className={`mic-btn ${isListening ? 'active' : ''}`}
            onClick={toggleListening}
            title={isListening ? "Stop listening" : "Use microphone"}
            disabled={isTyping || isEnding || isInterviewerSpeaking}
          >
            <Mic size={20} />
          </button>
          <textarea
            className="chat-input"
            placeholder={
              isInterviewerSpeaking ? "Please listen to the question..." :
              isListening ? "Listening... (Speak now)" : 
              "Type your answer here... (Press Enter to send)"
            }
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isTyping || isEnding || isListening || isInterviewerSpeaking}
          />
          <button 
            className="btn" 
            onClick={() => handleSendMessage(false)} 
            disabled={!inputValue.trim() || isTyping || isEnding || isInterviewerSpeaking}
            style={{ padding: '0.75rem' }}
          >
            <Send size={20} />
          </button>
        </div>
      </div>
    </div>
  );
};

export default InterviewChat;
