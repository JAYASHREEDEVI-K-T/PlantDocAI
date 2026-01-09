import React, { useState, useEffect } from 'react';
import RecommendationDisplay from './RecommendationDisplay';


export default function TextPredictor({ onAddToHistory }) {
  const [text, setText] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [recognition, setRecognition] = useState(null);
  const [browserSupported, setBrowserSupported] = useState(true);


  // Initialize Speech Recognition
  useEffect(() => {
    // Check browser support
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    
    if (!SpeechRecognition) {
      setBrowserSupported(false);
      return;
    }


    const recognitionInstance = new SpeechRecognition();
    recognitionInstance.continuous = true;
    recognitionInstance.interimResults = true;
    recognitionInstance.lang = 'en-US';


    recognitionInstance.onstart = () => {
      setIsListening(true);
      setError(null);
    };


    recognitionInstance.onresult = (event) => {
      let interimTranscript = '';
      let finalTranscript = '';


      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript;
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' ';
        } else {
          interimTranscript += transcript;
        }
      }


      setText(prev => {
        const newText = prev + finalTranscript;
        return newText.length <= 500 ? newText : newText.slice(0, 500);
      });
    };


    recognitionInstance.onerror = (event) => {
      console.error('Speech recognition error:', event.error);
      setIsListening(false);
      
      if (event.error === 'not-allowed') {
        setError('Microphone access denied. Please allow microphone access in your browser settings.');
      } else if (event.error === 'no-speech') {
        setError('No speech detected. Please try again.');
      } else {
        setError(`Speech recognition error: ${event.error}`);
      }
    };


    recognitionInstance.onend = () => {
      setIsListening(false);
    };


    setRecognition(recognitionInstance);


    return () => {
      if (recognitionInstance) {
        recognitionInstance.stop();
      }
    };
  }, []);


  const toggleListening = () => {
    if (!recognition) return;


    if (isListening) {
      recognition.stop();
    } else {
      recognition.start();
    }
  };


  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Stop listening if active
    if (isListening && recognition) {
      recognition.stop();
    }


    if (!text.trim()) {
      setError('Please enter or speak a description');
      return;
    }


    setIsLoading(true);
    setError(null);


    const formData = new FormData();
    formData.append('text', text);


    try {
      const response = await fetch('http://localhost:8000/predict/text?include_recommendations=true&language=en', {
        method: 'POST',
        body: formData,
      });


      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }


      const data = await response.json();
      setResult(data);

      // Add to history after successful prediction
      if (onAddToHistory) {
        onAddToHistory({
          type: 'text',
          text: text,
          prediction: data.prediction,
          confidence: data.confidence,
          recommendations: data.recommendations,
          timestamp: new Date().toISOString(),
        });
      }
    } catch (err) {
      setError(err.message || 'Failed to analyze text. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };


  const handleReset = () => {
    if (isListening && recognition) {
      recognition.stop();
    }
    setText('');
    setResult(null);
    setError(null);
  };


  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Text Description</h2>
      </div>


      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label htmlFor="symptom-text" className="block text-sm font-semibold text-gray-700 mb-2">
            Describe the symptoms:
          </label>
          <div className="relative">
            <textarea
              id="symptom-text"
              value={text}
              onChange={(e) => setText(e.target.value.slice(0, 500))}
              placeholder="Example: Yellow spots on leaves with brown edges, wilting stems..."
              rows={6}
              disabled={isLoading}
              className="w-full px-4 py-3 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:outline-none resize-none pr-14"
            />
            
            {/* Voice Input Button */}
            {browserSupported && (
              <button
                type="button"
                onClick={toggleListening}
                disabled={isLoading}
                className={`absolute right-3 bottom-3 p-3 rounded-full transition-all ${
                  isListening 
                    ? 'bg-red-500 hover:bg-red-600 animate-pulse' 
                    : 'bg-blue-500 hover:bg-blue-600'
                } text-white disabled:bg-gray-300 disabled:cursor-not-allowed shadow-lg`}
                title={isListening ? 'Stop recording' : 'Start voice input'}
              >
                {isListening ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                    <rect x="6" y="6" width="12" height="12" rx="2" />
                  </svg>
                ) : (
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z" />
                  </svg>
                )}
              </button>
            )}
          </div>
          
          <div className="flex items-center justify-between mt-1">
            <p className="text-xs text-gray-500">
              {text.length} / 500 characters
            </p>
            {isListening && (
              <p className="text-xs text-red-600 font-semibold flex items-center gap-1">
                <span className="inline-block w-2 h-2 bg-red-600 rounded-full animate-pulse"></span>
                Listening...
              </p>
            )}
          </div>


          {!browserSupported && (
            <div className="mt-2 bg-yellow-50 border border-yellow-200 text-yellow-800 px-3 py-2 rounded-lg text-xs">
              <p>⚠️ Voice input is not supported in your browser. Please type manually or use Chrome/Safari.</p>
            </div>
          )}
        </div>


        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p className="text-sm">{error}</p>
          </div>
        )}


        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!text.trim() || isLoading}
            className="flex-1 bg-blue-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? (
              <span className="flex items-center justify-center gap-2">
                <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                </svg>
                Analyzing...
              </span>
            ) : (
              'Analyze Symptoms'
            )}
          </button>
          
          {(text || result) && (
            <button
              type="button"
              onClick={handleReset}
              className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-lg font-semibold hover:bg-gray-50 transition-colors"
            >
              Reset
            </button>
          )}
        </div>
      </form>


      {result && (
        <div className="mt-6 space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-bold text-lg text-gray-800 mb-2">Detection Result</h3>
            <p className="text-gray-700">
              <span className="font-semibold">Disease:</span> {result.prediction}
            </p>
            <p className="text-gray-700">
              <span className="font-semibold">Confidence:</span> {(result.confidence * 100).toFixed(2)}%
            </p>
            {result.recommendations?.engine_used && (
              <p className="text-xs text-gray-500 mt-2">
                Engine: {result.recommendations.engine_used === 'gpt' ? '🤖 AI-Powered' : '📋 Rule-Based'}
              </p>
            )}
          </div>


          {result.recommendations && (
            <RecommendationDisplay recommendations={result.recommendations} />
          )}
        </div>
      )}
    </div>
  );
}
