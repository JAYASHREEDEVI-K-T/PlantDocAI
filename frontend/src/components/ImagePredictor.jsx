import React, { useState, useRef } from 'react';
import RecommendationDisplay from './RecommendationDisplay';

export default function ImagePredictor({ onAddToHistory }) {
  const [selectedFile, setSelectedFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  // Camera states and refs
  const [cameraActive, setCameraActive] = useState(false);
  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setError('File size must be less than 10MB');
      return;
    }

    setSelectedFile(file);
    setError(null);
    setResult(null);

    // Create preview
    const objectUrl = URL.createObjectURL(file);
    setPreview(objectUrl);

    // Cleanup
    return () => URL.revokeObjectURL(objectUrl);
  };

  const startCamera = () => {
    setCameraActive(true);
    navigator.mediaDevices.getUserMedia({ video: true })
      .then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.play();
        }
      })
      .catch(() => setError('Unable to access camera'));
  };

  const capturePhoto = () => {
    if (!canvasRef.current || !videoRef.current) return;
    const context = canvasRef.current.getContext('2d');
    context.drawImage(videoRef.current, 0, 0, canvasRef.current.width, canvasRef.current.height);
    canvasRef.current.toBlob((blob) => {
      if (!blob) return;
      const file = new File([blob], 'photo.jpg', { type: 'image/jpeg' });
      setSelectedFile(file);
      setPreview(URL.createObjectURL(file));
      // Stop camera
      if (videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
      setCameraActive(false);
    }, 'image/jpeg');
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
    setCameraActive(false);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setError('Please select an image first');
      return;
    }

    setIsLoading(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedFile);

    try {
      const response = await fetch('http://localhost:8000/predict/image?include_recommendations=true&language=en', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      setResult(data);

      // Add analysis to history
      if (onAddToHistory) {
        onAddToHistory({
          file: selectedFile,
          preview,
          result: data,
          date: new Date().toISOString(),
        });
      }
    } catch (err) {
      setError(err.message || 'Failed to analyze image. Please try again.');
      console.error('Error:', err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleReset = () => {
    setSelectedFile(null);
    setPreview(null);
    setResult(null);
    setError(null);
    if (preview) {
      URL.revokeObjectURL(preview);
    }
    stopCamera();
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center">
          <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
          </svg>
        </div>
        <h2 className="text-2xl font-bold text-gray-800">Image Analysis</h2>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">

        {/* Click Photo Button and Camera Preview */}
        <div className="mb-4">
          {!cameraActive ? (
            <button
              type="button"
              onClick={startCamera}
              className="bg-green-600 text-white px-4 py-2 rounded-lg mr-4"
              disabled={isLoading}
            >
              Click Photo
            </button>
          ) : (
            <>
              <video ref={videoRef} width="100%" height="240" className="rounded-lg border-2 border-gray-200 mb-2" />
              <canvas ref={canvasRef} width="640" height="480" style={{ display: 'none' }} />
              <div>
                <button type="button" onClick={capturePhoto} className="bg-green-600 text-white px-4 py-2 rounded-lg mr-2">Capture</button>
                <button type="button" onClick={stopCamera} className="px-4 py-2 border rounded-lg">Cancel</button>
              </div>
            </>
          )}
        </div>

        <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center hover:border-green-400 transition-colors">
          <input
            type="file"
            accept="image/*"
            onChange={handleFileChange}
            className="hidden"
            id="image-upload"
            disabled={isLoading}
          />
          <label
            htmlFor="image-upload"
            className="cursor-pointer flex flex-col items-center gap-2"
          >
            <svg className="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
            </svg>
            <span className="text-sm text-gray-600">
              {selectedFile ? selectedFile.name : 'Click to upload or drag and drop'}
            </span>
            <span className="text-xs text-gray-400">PNG, JPG, JPEG up to 10MB</span>
          </label>
        </div>

        {preview && (
          <div className="mt-4">
            <p className="text-sm font-semibold text-gray-700 mb-2">Preview:</p>
            <img
              src={preview}
              alt="Preview"
              className="w-full h-64 object-cover rounded-lg border-2 border-gray-200"
            />
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg">
            <p className="text-sm">{error}</p>
          </div>
        )}

        <div className="flex gap-3">
          <button
            type="submit"
            disabled={!selectedFile || isLoading}
            className="flex-1 bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
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
              'Analyze Image'
            )}
          </button>

          {(selectedFile || result) && (
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
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
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
