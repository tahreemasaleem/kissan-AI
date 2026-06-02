import { useState, useRef } from 'react';
import { UploadCloud, Leaf, AlertTriangle, CheckCircle, Sun, Scan, Info, ShieldAlert, Syringe, Sprout, Bot } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import axios from 'axios';
import Chatbot from './Chatbot';
import CropGuide from './CropGuide';
import './index.css';

function App() {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [activeMenu, setActiveMenu] = useState('scan');
  const fileInputRef = useRef(null);

  const handleImageChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      setActiveTab('overview');
    }
  };

  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      setSelectedImage(file);
      setImagePreview(URL.createObjectURL(file));
      setResult(null);
      setError(null);
      setActiveTab('overview');
    }
  };

  const analyzeImage = async () => {
    if (!selectedImage) return;

    setIsAnalyzing(true);
    setError(null);

    const formData = new FormData();
    formData.append('file', selectedImage);

    try {
      const response = await axios.post('http://localhost:8000/predict-disease', formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
      });
      setResult(response.data);
    } catch (err) {
      console.error(err);
      setError('Failed to analyze image. Please ensure the backend server is running.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  return (
    <div className="app-container">
      {/* Header */}
      <header className="app-header">
        <div className="logo-container">
          <div className="logo-icon">
            <Leaf size={24} color="#10b981" />
          </div>
          <h1>Kissan <span>AI</span></h1>
        </div>
        <div className="user-profile">
          <div className="avatar"></div>
        </div>
      </header>

      <main className="main-content">
        {/* Welcome Section */}
        <section className="welcome-section">
          <h2>Hello, Farmer 🌾</h2>
          <p>Upload a photo of a crop leaf to detect diseases and get instant treatment recommendations.</p>
          <p>اب آپ اپنی فصل کے پتے کی تصویر اپلوڈ کر کے بیماریوں کی تشخیص کر سکتے ہیں اور فوری طور پر علاج کے لیے مشورے حاصل کر سکتے ہیں۔

            آپ تصویر یہاں اپلوڈ کریں، اور میں اسے دیکھ کر آپ کو بتا سکوں گا کہ پودے کو کیا مسئلہ ہے اور اس کا حل کیا ہے۔ </p>
        </section>

        {/* Action Cards */}
        <div className="quick-actions">
          <div 
            className={`action-card ${activeMenu === 'scan' ? 'active' : ''}`}
            onClick={() => setActiveMenu('scan')}
          >
            <Scan size={24} />
            <span>Disease Scan</span>
          </div>
          <div 
            className={`action-card ${activeMenu === 'botanist' ? 'active' : ''}`}
            onClick={() => setActiveMenu('botanist')}
          >
            <Bot size={24} />
            <span>Virtual Botanist</span>
          </div>
          <div 
            className={`action-card ${activeMenu === 'weather' ? 'active' : ''}`}
            onClick={() => setActiveMenu('weather')}
          >
            <Sun size={24} />
            <span>Weather</span>
          </div>
          <div 
            className={`action-card ${activeMenu === 'cropguide' ? 'active' : ''}`}
            onClick={() => setActiveMenu('cropguide')}
          >
            <Sprout size={24} />
            <span>Crop Guide</span>
          </div>
        </div>

        {/* Dynamic Content */}
        {activeMenu === 'scan' && (
          <>
            {/* Upload Section */}
            <div className="upload-container">
          <AnimatePresence mode="wait">
            {!imagePreview ? (
              <motion.div
                key="upload"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, scale: 0.95 }}
                className="upload-dropzone"
                onClick={() => fileInputRef.current.click()}
                onDragOver={handleDragOver}
                onDrop={handleDrop}
              >
                <div className="upload-icon-wrapper">
                  <UploadCloud size={48} color="#10b981" />
                </div>
                <h3>Tap to Upload or Take Photo</h3>
                <p>Supported formats: JPG, PNG</p>
                <input
                  type="file"
                  ref={fileInputRef}
                  onChange={handleImageChange}
                  accept="image/*"
                  style={{ display: 'none' }}
                />
              </motion.div>
            ) : (
              <motion.div
                key="preview"
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="image-preview-container"
              >
                <div className="preview-header">
                  <button className="btn-secondary" onClick={() => { setImagePreview(null); setSelectedImage(null); setResult(null); setActiveTab('overview'); }}>
                    Back
                  </button>
                  <button
                    className="btn-primary"
                    onClick={analyzeImage}
                    disabled={isAnalyzing}
                  >
                    {isAnalyzing ? (
                      <span className="loading-spinner"></span>
                    ) : 'Analyze Crop'}
                  </button>
                </div>
                <div className="image-wrapper">
                  <img src={imagePreview} alt="Crop preview" />
                  {isAnalyzing && (
                    <div className="scanning-overlay">
                      <div className="scan-line"></div>
                      <p>Analyzing with Kissan AI...</p>
                    </div>
                  )}
                </div>
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="error-message"
          >
            <AlertTriangle size={20} />
            <p>{error}</p>
          </motion.div>
        )}

        {/* Results Section */}
        <AnimatePresence>
          {result && !isAnalyzing && (
            <motion.div
              initial={{ opacity: 0, y: 30 }}
              animate={{ opacity: 1, y: 0 }}
              className="results-container"
            >
              <div className="result-header">
                <div className={`result-status ${result.prediction.toLowerCase().includes('healthy') ? 'success' : 'warning'}`}>
                  {result.prediction.toLowerCase().includes('healthy') ? <CheckCircle size={24} /> : <AlertTriangle size={24} />}
                  <h3>{result.prediction.toLowerCase().includes('healthy') ? 'Plant Healthy' : 'Disease Detected'}</h3>
                </div>
                <div className="confidence-badge">
                  {Math.round(result.confidence * 100)}% Confidence
                </div>
              </div>

              <div className="disease-info">
                <h4>{result.prediction}</h4>
                <div className="tags">
                  {!result.prediction.toLowerCase().includes('healthy') && <span className="tag urgent">Treatment Required</span>}
                  <span className="tag crop">AI Scanned</span>
                </div>
              </div>

              {/* Tabs */}
              <div className="tabs-container">
                <button
                  className={`tab-btn ${activeTab === 'overview' ? 'active' : ''}`}
                  onClick={() => setActiveTab('overview')}
                >
                  <Info size={16} /> Overview
                </button>
                <button
                  className={`tab-btn ${activeTab === 'treatment' ? 'active' : ''}`}
                  onClick={() => setActiveTab('treatment')}
                >
                  <Syringe size={16} /> Treatment
                </button>
                <button
                  className={`tab-btn ${activeTab === 'prevention' ? 'active' : ''}`}
                  onClick={() => setActiveTab('prevention')}
                >
                  <ShieldAlert size={16} /> Prevention
                </button>
              </div>

              {/* Tab Content */}
              <div className="tab-content">
                <AnimatePresence mode="wait">
                  {activeTab === 'overview' && (
                    <motion.div
                      key="overview"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      transition={{ duration: 0.2 }}
                      className="tab-pane"
                    >
                      <div className="info-card">
                        <h5>Description</h5>
                        <p>{result.disease_info?.description || 'No description available.'}</p>
                      </div>
                      {result.disease_info?.symptoms && (
                        <div className="info-card mt-2">
                          <h5>Key Symptoms</h5>
                          <ul className="symptoms-list">
                            {result.disease_info.symptoms.map((sym, idx) => (
                              <li key={idx}><AlertTriangle size={14} className="list-icon" /> {sym}</li>
                            ))}
                          </ul>
                        </div>
                      )}
                    </motion.div>
                  )}

                  {activeTab === 'treatment' && (
                    <motion.div
                      key="treatment"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      transition={{ duration: 0.2 }}
                      className="tab-pane"
                    >
                      <div className="treatment-grid">
                        <div className="rec-card chemical">
                          <h5><Syringe size={16} /> Chemical Control</h5>
                          <p>{result.disease_info?.treatment_chemical || 'No chemical treatment specified.'}</p>
                        </div>
                        <div className="rec-card organic">
                          <h5><Sprout size={16} /> Organic Control</h5>
                          <p>{result.disease_info?.treatment_organic || 'No organic treatment specified.'}</p>
                        </div>
                      </div>
                      <div className="rec-card urdu mt-2">
                        <h5>علاج کی سفارش (Urdu)</h5>
                        <p>{result.recommendation_ur}</p>
                      </div>
                    </motion.div>
                  )}

                  {activeTab === 'prevention' && (
                    <motion.div
                      key="prevention"
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: 10 }}
                      transition={{ duration: 0.2 }}
                      className="tab-pane"
                    >
                      <div className="info-card prevention-card">
                        <h5><ShieldAlert size={16} /> Preventive Measures</h5>
                        <p>{result.disease_info?.prevention || 'No prevention measures specified.'}</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
          </>
        )}

        {activeMenu === 'botanist' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2"
          >
            <h3 className="mb-4" style={{ marginBottom: '1rem' }}>Chat with AI Botanist</h3>
            <Chatbot scanContext={result} />
          </motion.div>
        )}

        {activeMenu === 'weather' && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="info-card mt-2 text-center">
            <Sun size={48} color="#f59e0b" style={{ margin: '0 auto 1rem' }} />
            <h3>Weather Forecast</h3>
            <p>Coming soon: Real-time weather integration to plan your farming activities.</p>
          </motion.div>
        )}

        {activeMenu === 'cropguide' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-2"
          >
            <h3 className="mb-4" style={{ marginBottom: '1rem' }}>Crop Cultivation Guide</h3>
            <CropGuide />
          </motion.div>
        )}
      </main>
    </div>
  );
}

export default App;
