import React, { useState, useEffect, useRef } from 'react';
import './VoiceRecognition.css';

const VoiceRecognition = ({ onTranscript, onError }) => {
  const [isListening, setIsListening] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [isSupported, setIsSupported] = useState(false);
  const [error, setError] = useState('');
  const recognitionRef = useRef(null);
  const finalTranscriptRef = useRef('');
  const interimTranscriptRef = useRef('');

  // Check browser support for Web Speech API
  useEffect(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    setIsSupported(!!SpeechRecognition);

    if (SpeechRecognition) {
      const recognition = new SpeechRecognition();
      
      // Configure recognition
      recognition.continuous = true;
      recognition.interimResults = true;
      recognition.lang = 'ja-JP'; // Japanese primary, can be changed
      recognition.maxAlternatives = 1;

      // Event handlers
      recognition.onstart = () => {
        setIsListening(true);
        setError('');
        console.log('Voice recognition started');
      };

      recognition.onresult = (event) => {
        let finalTranscript = '';
        let interimTranscript = '';

        for (let i = 0; i < event.results.length; i++) {
          const transcript = event.results[i][0].transcript;
          
          if (event.results[i].isFinal) {
            finalTranscript += transcript;
          } else {
            interimTranscript += transcript;
          }
        }

        // Update refs
        finalTranscriptRef.current = finalTranscript;
        interimTranscriptRef.current = interimTranscript;

        // Update display transcript
        const fullTranscript = finalTranscript + interimTranscript;
        setTranscript(fullTranscript);

        // Send final transcript to parent
        if (finalTranscript && onTranscript) {
          onTranscript(finalTranscript);
        }
      };

      recognition.onerror = (event) => {
        console.error('Speech recognition error:', event.error);
        let errorMessage = '';
        
        switch (event.error) {
          case 'no-speech':
            errorMessage = '音声が検出されませんでした';
            break;
          case 'audio-capture':
            errorMessage = 'マイクにアクセスできません';
            break;
          case 'not-allowed':
            errorMessage = 'マイクの使用が許可されていません';
            break;
          case 'network':
            errorMessage = 'ネットワークエラーが発生しました';
            break;
          default:
            errorMessage = `音声認識エラー: ${event.error}`;
        }
        
        setError(errorMessage);
        setIsListening(false);
        
        if (onError) {
          onError(errorMessage);
        }
      };

      recognition.onend = () => {
        setIsListening(false);
        console.log('Voice recognition ended');
      };

      recognitionRef.current = recognition;
    }

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, [onTranscript, onError]);

  const startListening = () => {
    if (recognitionRef.current && !isListening) {
      try {
        // Reset transcripts
        finalTranscriptRef.current = '';
        interimTranscriptRef.current = '';
        setTranscript('');
        setError('');
        
        recognitionRef.current.start();
      } catch (error) {
        console.error('Failed to start recognition:', error);
        setError('音声認識の開始に失敗しました');
      }
    }
  };

  const stopListening = () => {
    if (recognitionRef.current && isListening) {
      recognitionRef.current.stop();
    }
  };

  const toggleListening = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  if (!isSupported) {
    return (
      <div className="voice-recognition unsupported">
        <span className="error-text">このブラウザでは音声認識がサポートされていません</span>
      </div>
    );
  }

  return (
    <div className="voice-recognition">
      <button
        className={`voice-button ${isListening ? 'listening' : ''}`}
        onClick={toggleListening}
        title={isListening ? '音声認識を停止' : '音声認識を開始'}
      >
        <div className="microphone-icon">
          {isListening ? (
            <div className="pulse-animation">🎤</div>
          ) : (
            '🎤'
          )}
        </div>
      </button>
      
      {isListening && (
        <div className="listening-indicator">
          <span className="listening-text">音声を聞いています...</span>
          <div className="sound-wave">
            <div className="wave"></div>
            <div className="wave"></div>
            <div className="wave"></div>
          </div>
        </div>
      )}
      
      {transcript && (
        <div className="transcript-preview">
          <span className="transcript-text">{transcript}</span>
        </div>
      )}
      
      {error && (
        <div className="voice-error">
          <span className="error-text">{error}</span>
        </div>
      )}
    </div>
  );
};

export default VoiceRecognition;