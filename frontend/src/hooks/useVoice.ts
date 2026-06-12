import { useState } from 'react';

export const useVoice = () => {
  const [isListening, setIsListening] = useState(false);
  const [isSpeaking, setIsSpeaking] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [error, setError] = useState('');

  const startListening = (lang: string = 'en-IN'): Promise<string> => {
    return new Promise((resolve) => {
      if (!('webkitSpeechRecognition' in window)) {
        setError('Voice recognition not supported in this browser');
        resolve('');
        return;
      }
      
      const recognition = new (window as any).webkitSpeechRecognition();
      recognition.lang = lang;
      recognition.continuous = false;
      recognition.interimResults = false;
      
      setIsListening(true);
      
      recognition.onresult = (event: any) => {
        const result = event.results[0][0].transcript;
        setTranscript(result);
        resolve(result);
      };
      
      recognition.onerror = (e: any) => {
        setError(e.error);
        setIsListening(false);
        resolve('');
      };
      
      recognition.onend = () => {
        setIsListening(false);
      };
      
      recognition.start();
    });
  };

  const stopListening = () => {
    setIsListening(false);
    // Logic to actually stop recognition if needed, typically handles by onend
  };

  const speak = (text: string) => {
    if (!('speechSynthesis' in window)) return;
    
    const utterance = new SpeechSynthesisUtterance(text);
    // Detect Kannada characters roughly
    utterance.lang = /[\u0C80-\u0CFF]/.test(text) ? 'kn-IN' : 'en-IN';
    utterance.rate = 0.9;
    utterance.pitch = 1;
    
    utterance.onstart = () => setIsSpeaking(true);
    utterance.onend = () => setIsSpeaking(false);
    
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utterance);
  };

  const stopSpeech = () => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    }
  };

  return {
    isListening,
    isSpeaking,
    transcript,
    error,
    startListening,
    stopListening,
    speak,
    stopSpeech
  };
};
