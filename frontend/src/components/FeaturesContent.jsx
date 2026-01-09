import React from 'react';

export default function FeaturesContent() {
  const features = [
    {
      icon: '📸',
      title: 'Image-Based Detection',
      description: 'Upload or click clear photos of affected plant leaves for instant AI-powered disease identification.',
      color: 'green',
      details: [
        'Supports JPG, PNG, and JPEG formats',
        'CNN-based deep learning model',
        '95%+ accuracy rate',
        'Processes images in under 2 seconds'
      ]
    },
    {
      icon: '🎤',
      title: 'Voice Input Recognition',
      description: 'Describe symptoms using your voice - perfect for field work without typing.',
      color: 'blue',
      details: [
        'Real-time speech-to-text conversion',
        'Supports multiple languages',
        'Hands-free operation',
        'Works offline after initial load'
      ]
    },
    {
      icon: '🤖',
      title: 'AI-Powered Recommendations',
      description: 'Get personalized treatment plans powered by GPT-4 and expert agricultural knowledge.',
      color: 'purple',
      details: [
        'GPT-4o-mini integration',
        'Organic and chemical solutions',
        'Step-by-step care instructions',
        'Severity assessment'
      ]
    },
    {
      icon: '🕘',
      title: 'History Management',
      description: 'Review your past plant analyses with easy access to previous uploads and results.',
      color: 'yellow',
      details: [
        'View all past image and photo analyses',
        'Easy access from the navbar',
        'Delete unwanted entries anytime',
        'Data persists between sessions'
      ]
    }
  
  ];

  const colorClasses = {
    green: 'bg-green-50 border-green-200',
    blue: 'bg-blue-50 border-blue-200',
    purple: 'bg-purple-50 border-purple-200',
    yellow: 'bg-yellow-50 border-yellow-200',
    red: 'bg-red-50 border-red-200',
    indigo: 'bg-indigo-50 border-indigo-200'
  };

  return (
    <div className="space-y-6">
      <p className="text-gray-600 text-lg">
        PlantDoc combines cutting-edge AI technology with agricultural expertise to provide 
        comprehensive plant disease detection and treatment solutions.
      </p>

      <div className="grid md:grid-cols-2 gap-6">
        {features.map((feature, index) => (
          <div 
            key={index}
            className={`${colorClasses[feature.color]} border-2 rounded-xl p-5 hover:shadow-lg transition-shadow`}
          >
            <div className="flex items-start gap-3 mb-3">
              <span className="text-4xl">{feature.icon}</span>
              <div>
                <h3 className="text-xl font-bold text-gray-800 mb-1">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            </div>
            
            <ul className="space-y-2 mt-4">
              {feature.details.map((detail, idx) => (
                <li key={idx} className="flex items-start gap-2 text-sm text-gray-700">
                  <span className="text-green-600 mt-0.5">✓</span>
                  <span>{detail}</span>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
