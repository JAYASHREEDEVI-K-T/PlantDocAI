import React, { useState, useEffect } from 'react';
import Navbar from './components/Navbar';
import ImagePredictor from './components/ImagePredictor';
import TextPredictor from './components/TextPredictor';
import Footer from './components/Footer';


export default function App() {
  const [history, setHistory] = useState(() => {
    const savedHistory = localStorage.getItem('plantifyHistory');
    return savedHistory ? JSON.parse(savedHistory) : [];
  });


  useEffect(() => {
    localStorage.setItem('plantifyHistory', JSON.stringify(history));
  }, [history]);


  const addToHistory = (entry) => {
    setHistory((prev) => [entry, ...prev]);
  };


  // Delete a history item by index
  const deleteFromHistory = (index) => {
    setHistory((prev) => prev.filter((_, i) => i !== index));
  };


  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-white via-soft to-white">
      <Navbar history={history} onDeleteFromHistory={deleteFromHistory} />
      <main className="flex-1 container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-5xl font-bold text-gray-800 mb-4">
            PlantDoc <br/> 
          </h1>
          <h2 className="text-5xl text-gray-600 mb-4">AI-Powered Plant Disease Detection & Recommendation System</h2>


          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Upload or click a leaf image or describe the symptoms. Get instant diagnosis and care recommendations.
          </p>
        </div>


        <div className="grid md:grid-cols-2 gap-8 max-w-6xl mx-auto">
          <ImagePredictor onAddToHistory={addToHistory} />
          <TextPredictor onAddToHistory={addToHistory} />
        </div>
      </main>
      <Footer />
    </div>
  );
}
