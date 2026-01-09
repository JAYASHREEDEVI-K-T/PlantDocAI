import React, { useState } from 'react';
import Modal from './Modal';
import FeaturesContent from './FeaturesContent';
import AboutContent from './AboutContent';
import FeedbackModal from './FeedbackModal';
import AnalyticsDashboard from './AnalyticsDashboard';
import { submitFeedback, clearCache, saveKnowledgeBase } from '../api';


function HistoryContent({ history, onClose, onDelete }) {
  const formatDate = (timestamp) => {
    if (!timestamp) return 'N/A';
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) return 'N/A';
      
      return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    } catch (error) {
      return 'N/A';
    }
  };

  return (
    <div>
      {history.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No history to display.</p>
      ) : (
        history.map((item, index) => (
          <div
            key={index}
            className="mb-4 border-b border-gray-200 pb-4 last:border-b-0"
          >
            <div className="flex items-start gap-4">
              {/* Conditional rendering based on type */}
              {item.type === 'image' && item.preview && (
                <img
                  src={item.preview}
                  alt={`History ${index}`}
                  className="w-32 h-32 object-cover rounded-lg flex-shrink-0"
                />
              )}
              
              {item.type === 'text' && (
                <div className="w-32 h-32 bg-blue-50 rounded-lg flex-shrink-0 flex items-center justify-center">
                  <svg className="w-12 h-12 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                  </svg>
                </div>
              )}

              {/* If no type is specified, assume it's an old image entry */}
              {!item.type && item.preview && (
                <img
                  src={item.preview}
                  alt={`History ${index}`}
                  className="w-32 h-32 object-cover rounded-lg flex-shrink-0"
                />
              )}

              <div className="flex-1 min-w-0">
                {/* Display type badge */}
                <div className="flex items-center gap-2 mb-2">
                  {item.type === 'image' ? (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      📷 Image Detection
                    </span>
                  ) : item.type === 'text' ? (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                      📝 Text Detection
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                      📷 Image Detection
                    </span>
                  )}
                </div>

                {/* Display text description for text predictions */}
                {item.type === 'text' && item.text && (
                  <p className="text-sm text-gray-600 mb-2 line-clamp-2 italic">
                    "{item.text.length > 100 ? item.text.substring(0, 100) + '...' : item.text}"
                  </p>
                )}

                <p className="mb-1">
                  <span className="font-semibold text-gray-800">Disease:</span>{' '}
                  <span className="text-gray-700">
                    {item.prediction || item.result?.prediction || 'N/A'}
                  </span>
                </p>
                
                <p className="mb-1">
                  <span className="font-semibold text-gray-800">Confidence:</span>{' '}
                  <span className="text-gray-700">
                    {item.confidence 
                      ? `${(item.confidence * 100).toFixed(2)}%`
                      : item.result?.confidence 
                      ? `${(item.result.confidence * 100).toFixed(2)}%`
                      : 'N/A'}
                  </span>
                </p>

                <p className="text-sm text-gray-500 mb-3">
                  {formatDate(item.timestamp || item.date)}
                </p>

                <button
                  onClick={() => onDelete(index)}
                  className="text-red-600 hover:text-red-800 text-sm font-semibold rounded px-3 py-1 border border-red-600 hover:bg-red-50 transition-colors"
                >
                  Delete
                </button>
              </div>
            </div>
          </div>
        ))
      )}
      <button
        onClick={onClose}
        className="mt-4 w-full bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors font-semibold"
      >
        Close
      </button>
    </div>
  );
}


export default function Navbar({ history = [], onDeleteFromHistory }) {
  const [showFeatures, setShowFeatures] = useState(false);
  const [showAbout, setShowAbout] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [showFeedback, setShowFeedback] = useState(false);
  const [showAnalytics, setShowAnalytics] = useState(false);
  const [feedbackData, setFeedbackData] = useState(null);


  const scrollToTop = (e) => {
    e.preventDefault();
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    });
  };


  const handleFeedbackSubmit = async (data) => {
    try {
      await submitFeedback(data);
      alert('Thank you for your feedback!');
    } catch (err) {
      alert('Failed to submit feedback. Please try again.');
    }
  };


  const handleClearCache = async () => {
    try {
      await clearCache();
      alert('Cache cleared successfully');
    } catch {
      alert('Failed to clear cache');
    }
  };


  const handleSaveKnowledgeBase = async () => {
    try {
      await saveKnowledgeBase();
      alert('Knowledge base saved successfully');
    } catch {
      alert('Failed to save knowledge base');
    }
  };


  return (
    <>
      <nav className="bg-white shadow-md sticky top-0 z-40">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <button
              onClick={scrollToTop}
              className="flex items-center gap-3 hover:opacity-80 transition-opacity"
            >
              <div className="w-10 h-10 bg-green-600 rounded-lg flex items-center justify-center">
                <span className="text-white text-2xl">🌿</span>
              </div>
              <span className="text-2xl font-bold text-gray-800">PlantDoc</span>
            </button>


            <div className="flex items-center gap-6">
              <button
                onClick={() => setShowFeatures(true)}
                className="text-gray-600 hover:text-green-600 font-medium transition-colors"
              >
                Features
              </button>
              <button
                onClick={() => setShowAbout(true)}
                className="text-gray-600 hover:text-green-600 font-medium transition-colors"
              >
                About
              </button>
              <button
                onClick={() => setShowHistory(true)}
                className="text-gray-600 hover:text-green-600 font-medium transition-colors relative"
              >
                History
                {history.length > 0 && (
                  <span className="absolute -top-1 -right-2 bg-green-600 text-white text-xs rounded-full w-5 h-5 flex items-center justify-center">
                    {history.length}
                  </span>
                )}
              </button>


              {/* Dropdown for additional options */}
              <div className="relative inline-block text-left">
                <button
                  type="button"
                  className="inline-flex justify-center w-full rounded-md border border-gray-300 shadow-sm px-4 py-2 bg-white text-sm font-medium text-gray-700 hover:bg-gray-50 focus:outline-none"
                  id="options-menu"
                  aria-haspopup="true"
                  aria-expanded="true"
                  onClick={() => {
                    const dropdown = document.getElementById('extra-options-dropdown');
                    if (dropdown.style.display === 'block') {
                      dropdown.style.display = 'none';
                    } else {
                      dropdown.style.display = 'block';
                    }
                  }}
                >
                  ⋮
                </button>


                <div
                  id="extra-options-dropdown"
                  className="origin-top-right absolute right-0 mt-2 w-56 rounded-md shadow-lg bg-white ring-1 ring-black ring-opacity-5"
                  style={{ display: 'none' }}
                >
                  <div
                    className="py-1"
                    role="menu"
                    aria-orientation="vertical"
                    aria-labelledby="options-menu"
                  >
                    <button
                      onClick={() => { setShowFeedback(true); document.getElementById('extra-options-dropdown').style.display = 'none'; }}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-green-100 w-full text-left"
                      role="menuitem"
                    >
                      Feedback
                    </button>
                    <button
                      onClick={() => { setShowAnalytics(true); document.getElementById('extra-options-dropdown').style.display = 'none'; }}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-green-100 w-full text-left"
                      role="menuitem"
                    >
                      Analytics
                    </button>
                    <button
                      onClick={() => { handleClearCache(); document.getElementById('extra-options-dropdown').style.display = 'none'; }}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-red-100 w-full text-left"
                      role="menuitem"
                    >
                      Clear Cache
                    </button>
                    <button
                      onClick={() => { handleSaveKnowledgeBase(); document.getElementById('extra-options-dropdown').style.display = 'none'; }}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-blue-100 w-full text-left"
                      role="menuitem"
                    >
                      Save Knowledge Base
                    </button>
                  </div>
                </div>
              </div>


              <button
                onClick={scrollToTop}
                className="bg-green-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-green-700 transition-colors"
              >
                Home
              </button>
            </div>
          </div>
        </div>
      </nav>


      {/* Features Modal */}
      <Modal
        isOpen={showFeatures}
        onClose={() => setShowFeatures(false)}
        title="✨ Features"
      >
        <FeaturesContent />
      </Modal>


      {/* About Modal */}
      <Modal
        isOpen={showAbout}
        onClose={() => setShowAbout(false)}
        title="🌿 About PlantDoc"
      >
        <AboutContent />
      </Modal>


      {/* History Modal */}
      <Modal
        isOpen={showHistory}
        onClose={() => setShowHistory(false)}
        title="🕘 History"
      >
        <HistoryContent
          history={history}
          onClose={() => setShowHistory(false)}
          onDelete={onDeleteFromHistory}
        />
      </Modal>


      {/* Feedback Modal */}
      <Modal
        isOpen={showFeedback}
        onClose={() => setShowFeedback(false)}
        title="📝 Submit Feedback"
      >
        <FeedbackModal
          isOpen={showFeedback}
          onClose={() => setShowFeedback(false)}
          onSubmit={handleFeedbackSubmit}
          disease={feedbackData?.disease || ''}
          recommendationId={feedbackData?.recommendationId || ''}
        />
      </Modal>


      {/* Analytics Modal */}
      <Modal
        isOpen={showAnalytics}
        onClose={() => setShowAnalytics(false)}
        title="🧾 Analytics & Reports"
      >
        <AnalyticsDashboard />
      </Modal>
    </>
  );
}
