import React from 'react';

export default function AboutContent() {
  return (
    <div className="space-y-6">
      <div className="text-gray-600 space-y-4">
        <p className="text-lg leading-relaxed">
          PlantDoc is an advanced AI-powered plant disease detection system designed to help 
          <span className="font-semibold text-gray-800"> farmers, gardeners, and agricultural professionals</span> identify 
          and treat plant diseases quickly and accurately.
        </p>
        
        <p className="leading-relaxed">
          Using state-of-the-art machine learning models and GPT-powered recommendations, Plantify 
          analyzes both images and text descriptions to provide comprehensive disease diagnosis and 
          treatment plans. Our system combines computer vision, natural language processing, and 
          expert agricultural knowledge to deliver actionable insights.
        </p>
      </div>

      <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl p-6 border-2 border-green-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">🎯 Our Mission</h3>
        <p className="text-gray-700">
          To empower agricultural communities worldwide with accessible, accurate, and AI-driven 
          plant health solutions that increase crop yields and reduce losses from plant diseases.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-4">
        <div className="bg-blue-50 rounded-lg p-5 border border-blue-200">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">🎯</span>
            <h4 className="font-bold text-gray-800">Accurate Detection</h4>
          </div>
          <p className="text-sm text-gray-600">
            CNN-based image classification with <span className="font-semibold">95%+ accuracy</span> trained 
            on thousands of plant disease images.
          </p>
        </div>

        <div className="bg-purple-50 rounded-lg p-5 border border-purple-200">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">🤖</span>
            <h4 className="font-bold text-gray-800">AI-Powered</h4>
          </div>
          <p className="text-sm text-gray-600">
            GPT-4 integration provides <span className="font-semibold">intelligent recommendations</span> with 
            rule-based fallback for reliability.
          </p>
        </div>

        <div className="bg-green-50 rounded-lg p-5 border border-green-200">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">⚡</span>
            <h4 className="font-bold text-gray-800">Real-time Analysis</h4>
          </div>
          <p className="text-sm text-gray-600">
            Get instant results in <span className="font-semibold">under 2 seconds</span> with comprehensive 
            treatment recommendations.
          </p>
        </div>

        <div className="bg-yellow-50 rounded-lg p-5 border border-yellow-200">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">🌍</span>
            <h4 className="font-bold text-gray-800">Globally Accessible</h4>
          </div>
          <p className="text-sm text-gray-600">
            <span className="font-semibold"></span> voice input make it accessible 
            to farmers worldwide.
          </p>
        </div>
      </div>

      <div className="bg-white rounded-xl border-2 border-gray-200 p-6">
        <h3 className="text-xl font-bold text-gray-800 mb-4">🔬 Technology Stack</h3>
        <div className="grid md:grid-cols-3 gap-4">
          <div>
            <h5 className="font-semibold text-gray-700 mb-2">Backend</h5>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• FastAPI (Python)</li>
              <li>• PyTorch</li>
              <li>• OpenAI GPT-4o-mini</li>
              <li>• Transformers</li>
            </ul>
          </div>
          <div>
            <h5 className="font-semibold text-gray-700 mb-2">Frontend</h5>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• React 18</li>
              <li>• Tailwind CSS</li>
              <li>• Vite</li>
              <li>• Web Speech API</li>
            </ul>
          </div>
          <div>
            <h5 className="font-semibold text-gray-700 mb-2">ML Models</h5>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• CNN (ResNet)</li>
              <li>• BERT-based NLP</li>
              <li>• Custom Disease DB</li>
              <li>• LangChain</li>
            </ul>
          </div>
        </div>
      </div>

      <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-6 border-2 border-blue-200">
        <div className="space-y-2 text-gray-700">
          
          <p>🌐 Website: <a href="https://plantDoc.ai" className="text-blue-600 hover:underline">plantify.ai</a></p>
          <p className="text-sm text-gray-600 mt-3">
            @2025JaiKisan
          </p>
        </div>
      </div>
    </div>
  );
}
