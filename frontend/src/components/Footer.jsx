import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-gray-800 text-white py-8 mt-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-3 gap-8">
          <div>
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <span>🌿</span> PlantDoc
            </h3>
            <p className="text-gray-400">
              AI-powered plant disease detection to help farmers and gardeners maintain healthy crops.
            </p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Features</h4>
            <ul className="space-y-2 text-gray-400">
              <li>• Image-based Detection</li>
              <li>• Text Symptom Analysis</li>
              <li>• AI Recommendations</li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">By: </h4>
            <p className="text-gray-400">
              https://github.com/JAYASHREEDEVI-K-T
            </p>
          </div>
        </div>
        
        <div className="border-t border-gray-700 mt-8 pt-6 text-center text-gray-400 text-sm">
          © 2025 PlantDoc. JaiKisan.
        </div>
      </div>
    </footer>
  );
}
