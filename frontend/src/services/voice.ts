export const startListening = (lang: string = 'en-IN'): Promise<string> => {
  return new Promise((resolve) => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Voice recognition not supported in this browser');
      resolve('');
      return;
    }
    
    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.lang = lang;
    recognition.continuous = false;
    recognition.interimResults = false;
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      resolve(transcript);
    };
    
    recognition.onerror = () => {
      resolve('');
    };
    
    recognition.start();
  });
};

export const speak = (text: string) => {
  if (!('speechSynthesis' in window)) return;
  
  const utterance = new SpeechSynthesisUtterance(text);
  utterance.lang = /[\u0C80-\u0CFF]/.test(text) ? 'kn-IN' : 'en-IN';
  utterance.rate = 0.9;
  utterance.pitch = 1;
  window.speechSynthesis.cancel();
  window.speechSynthesis.speak(utterance);
};
