import React from 'react';

export default function RecommendationDisplay({ recommendations }) {
  if (!recommendations) return null;

  const sections = [
    { key: 'description', title: '📝 Description', icon: '📝' },
    { key: 'symptoms', title: '🔍 Symptoms', icon: '🔍' },
    { key: 'treatment', title: '💊 Treatment', icon: '💊' },
    { key: 'prevention', title: '🛡️ Prevention', icon: '🛡️' },
    { key: 'organic_solutions', title: '🌱 Organic Solutions', icon: '🌱' },
    { key: 'chemical_solutions', title: '⚗️ Chemical Solutions', icon: '⚗️' },
    { key: 'care_instructions', title: '🌿 Care Instructions', icon: '🌿' }
  ];

  return (
    <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
      <h3 className="font-bold text-lg text-gray-800 mb-4 flex items-center gap-2">
        <span>💡</span> Recommendations
      </h3>
      
      <div className="space-y-4">
        {sections.map(({ key, title, icon }) => {
          const content = recommendations[key];
          if (!content) return null;

          return (
            <div key={key} className="bg-white rounded-lg p-4 shadow-sm">
              <h4 className="font-semibold text-gray-700 mb-2 flex items-center gap-2">
                <span>{icon}</span>
                {title.replace(/^[^ ]+ /, '')}
              </h4>
              <div className="text-gray-600 text-sm whitespace-pre-line">
                {content}
              </div>
            </div>
          );
        })}

        {recommendations.additional_info && (
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-semibold text-gray-700 mb-2">ℹ️ Additional Information</h4>
            <p className="text-sm text-gray-600">{recommendations.additional_info}</p>
          </div>
        )}

        {recommendations.severity && (
          <div className="flex items-center gap-2 text-sm">
            <span className="font-semibold text-gray-700">Severity:</span>
            <span className={`px-3 py-1 rounded-full font-medium ${
              recommendations.severity === 'high' ? 'bg-red-100 text-red-700' :
              recommendations.severity === 'moderate' ? 'bg-yellow-100 text-yellow-700' :
              'bg-green-100 text-green-700'
            }`}>
              {recommendations.severity}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}
