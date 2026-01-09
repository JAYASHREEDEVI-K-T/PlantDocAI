// src/components/FeedbackModal.jsx
import React, { useState } from 'react';

export default function FeedbackModal({ isOpen, onClose, onSubmit, disease, recommendationId }) {
  const [rating, setRating] = useState(3);
  const [wasHelpful, setWasHelpful] = useState(true);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async () => {
    setSubmitting(true);
    await onSubmit({ disease, recommendationId, rating, wasHelpful, comment });
    setSubmitting(false);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-xl w-full p-6 relative">
        <h2 className="text-xl font-semibold mb-4">Help us improve</h2>
        <div className="space-y-4">
          <div>
            <label className="block mb-1">Rating (1-5):</label>
            <input
              type="range"
              min={1}
              max={5}
              value={rating}
              onChange={(e) => setRating(Number(e.target.value))}
              className="w-full"
            />
            <div className="text-center text-sm">{rating} star(s)</div>
          </div>
          <div>
            <label className="block mb-1">Helpful?</label>
            <select
              value={wasHelpful ? 'yes' : 'no'}
              onChange={(e) => setWasHelpful(e.target.value === 'yes')}
              className="w-full border p-2 rounded"
            >
              <option value="yes">Yes</option>
              <option value="no">No</option>
            </select>
          </div>
          <div>
            <label className="block mb-1">Comment:</label>
            <textarea
              value={comment}
              onChange={(e) => setComment(e.target.value)}
              className="w-full border p-2 rounded h-20"
              placeholder="Your comments..."
            />
          </div>
        </div>
        <div className="mt-4 flex justify-end gap-2">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-300 rounded hover:bg-gray-400"
            disabled={submitting}
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            className="px-4 py-2 bg-green-600 text-white rounded hover:bg-green-700"
            disabled={submitting}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  );
}
