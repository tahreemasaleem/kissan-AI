import { useState, useEffect } from 'react';
import { Search, Sprout, Calendar, ShieldAlert, Droplets, BookOpen, AlertCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import axios from 'axios';

export default function CropGuide() {
  const [crops, setCrops] = useState([]);
  const [search, setSearch] = useState('');
  const [selectedCrop, setSelectedCrop] = useState(null);
  const [cropInfo, setCropInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCrops = async () => {
      try {
        const response = await axios.get('http://localhost:8000/crops');
        setCrops(response.data.crops);
        setIsLoading(false);
      } catch {
        setError('Failed to load crop list. Ensure backend is running.');
        setIsLoading(false);
      }
    };
    fetchCrops();
  }, []);

  useEffect(() => {
    if (!selectedCrop) return;

    const fetchCropDetails = async () => {
      setIsLoading(true);
      try {
        const response = await axios.get(`http://localhost:8000/crop/${selectedCrop}`);
        if (response.data.error) {
          setError(response.data.error);
        } else {
          setCropInfo(response.data);
        }
      } catch {
        setError('Failed to fetch crop details.');
      } finally {
        setIsLoading(false);
      }
    };
    
    fetchCropDetails();
  }, [selectedCrop]);

  const filteredCrops = crops.filter(c => c.toLowerCase().includes(search.toLowerCase()));

  if (error) {
    return (
      <div className="error-message">
        <AlertCircle size={20} />
        <p>{error}</p>
      </div>
    );
  }

  return (
    <div className="crop-guide-container">
      {!selectedCrop ? (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="crop-list-view">
          <div className="search-bar-container">
            <Search size={20} className="search-icon" />
            <input 
              type="text" 
              placeholder="Search for a crop (e.g., Rice, Wheat, Tomato)..." 
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              className="crop-search-input"
            />
          </div>

          <div className="crops-grid">
            {isLoading ? (
              <p>Loading crops...</p>
            ) : filteredCrops.length > 0 ? (
              filteredCrops.map((crop, idx) => (
                <motion.div 
                  key={idx}
                  whileHover={{ scale: 1.02 }}
                  className="crop-card"
                  onClick={() => setSelectedCrop(crop)}
                >
                  <Sprout size={24} className="crop-card-icon" />
                  <h4>{crop}</h4>
                </motion.div>
              ))
            ) : (
              <p>No crops found matching "{search}"</p>
            )}
          </div>
        </motion.div>
      ) : (
        <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="crop-details-view">
          <div className="details-header">
            <button className="btn-secondary" onClick={() => setSelectedCrop(null)}>Back to List</button>
            <h3 className="crop-title">{cropInfo?.Crop_Name || selectedCrop}</h3>
          </div>

          {isLoading || !cropInfo ? (
            <p className="mt-2">Loading details...</p>
          ) : (
            <div className="crop-info-grid mt-2">
              <div className="info-card">
                <h5><Calendar size={18} /> Season & Duration</h5>
                <p><strong>Season:</strong> {cropInfo.Season}</p>
                <p><strong>Duration:</strong> {cropInfo.Growing_Duration}</p>
              </div>

              <div className="info-card">
                <h5><Droplets size={18} /> Fertilizer Application</h5>
                <p>{cropInfo.Fertilizer_Application}</p>
              </div>

              <div className="info-card">
                <h5><ShieldAlert size={18} /> Pesticides & Protection</h5>
                <p>{cropInfo.Pesticides_Used}</p>
              </div>

              <div className="info-card" style={{ gridColumn: '1 / -1' }}>
                <h5><BookOpen size={18} /> Cultivation Guide</h5>
                <p>{cropInfo.Cultivation_Guide}</p>
              </div>
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}
