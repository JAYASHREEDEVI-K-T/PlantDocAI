// src/components/AnalyticsDashboard.jsx
import React, { useEffect, useState } from 'react';
import { getAnalytics, getPopularDiseases } from '../api';

export default function AnalyticsDashboard() {
  const [analytics, setAnalytics] = useState(null);
  const [popular, setPopular] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchData() {
      try {
        const [analyticsData, popularData] = await Promise.all([
          getAnalytics(),
          getPopularDiseases()
        ]);
        setAnalytics(analyticsData);
        setPopular(popularData.popular_diseases || []);
      } catch (err) {
        console.error('Error fetching analytics:', err);
      } finally {
        setLoading(false);
      }
    }
    fetchData();
  }, []);

  if (loading) return <p>Loading analytics...</p>;

  return (
    <div className="p-4 space-y-4 bg-white rounded-lg shadow-lg max-h-[80vh] overflow-y-auto">
      <h2 className="text-xl font-semibold mb-2">Analytics Report</h2>
      {analytics ? (
        <pre className="bg-gray-100 p-4 rounded overflow-auto max-h-64">
          {JSON.stringify(analytics, null, 2)}
        </pre>
      ) : (
        <p>No analytics data available.</p>
      )}

      <h3 className="text-lg font-semibold mb-2">Popular Diseases</h3>
      <ul className="list-disc pl-5 space-y-1">
        {popular.length > 0 ? (
          popular.map(({ disease, count }, i) => (
            <li key={i}>
              {disease} — {count} occurrences
            </li>
          ))
        ) : (
          <li>No popular diseases data.</li>
        )}
      </ul>
    </div>
  );
}
