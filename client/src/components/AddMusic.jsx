import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { api, formatDuration } from '../services/api';

export default function AddMusic() {
  const [url, setUrl] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [status, setStatus] = useState({ message: '', type: '' });
  const navigate = useNavigate();

  const handleConvert = async () => {
    if (!url.trim()) {
      setStatus({ message: 'Please enter a YouTube URL', type: 'error' });
      return;
    }

    setLoading(true);
    setResult(null);
    setStatus({ message: '', type: '' });

    try {
      const data = await api.convertVideo(url.trim());
      if (data.success) {
        setResult(data);
      } else {
        setStatus({ message: data.error || 'Failed to convert video', type: 'error' });
      }
    } catch (error) {
      setStatus({ message: 'Network error. Please try again.', type: 'error' });
    }

    setLoading(false);
  };

  const handleSaveToLibrary = async () => {
    if (!result) return;

    try {
      const data = await api.saveToLibrary({
        file_id: result.file_id,
        title: result.title,
        artist: result.artist,
        duration: result.duration,
        youtube_url: result.youtube_url
      });

      if (data.success) {
        setStatus({ message: 'Saved to your library!', type: 'success' });
        setTimeout(() => navigate('/library'), 1000);
      } else {
        setStatus({ message: data.error || 'Failed to save', type: 'error' });
      }
    } catch (error) {
      setStatus({ message: 'Network error. Please try again.', type: 'error' });
    }
  };

  const handleDownload = () => {
    if (!result) return;
    window.location.href = api.getDownloadUrl(result.file_id, result.safe_title);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') handleConvert();
  };

  return (
    <div className="app-container" style={{ paddingBottom: '100px' }}>
      <div className="header">
        <h1><i className="fas fa-music"></i> MusicBox</h1>
        <p>Download & play your favorite music</p>
      </div>

      <div className="search-section">
        <div className="input-group">
          <input
            type="text"
            className="url-input"
            placeholder="Paste YouTube URL here..."
            value={url}
            onChange={(e) => setUrl(e.target.value)}
            onKeyPress={handleKeyPress}
          />
          <button
            className="convert-btn"
            onClick={handleConvert}
            disabled={loading}
          >
            <i className="fas fa-download"></i>
            <span>Get Music</span>
          </button>
        </div>
      </div>

      {loading && (
        <div className="loading">
          <div className="spinner"></div>
          <p>Extracting audio...</p>
        </div>
      )}

      {result && (
        <div className="result-section">
          <div className="song-preview">
            <div className="song-icon">
              <i className="fas fa-music"></i>
            </div>
            <div className="song-info">
              <h3>{result.title}</h3>
              <p>{result.artist || 'Unknown Artist'}</p>
              <p style={{ color: '#5a6a8a', fontSize: '12px' }}>
                {formatDuration(result.duration)}
              </p>
            </div>
          </div>
          <div className="action-buttons">
            <button className="action-btn save-btn" onClick={handleSaveToLibrary}>
              <i className="fas fa-plus"></i>
              Save to Library
            </button>
            <button className="action-btn download-btn" onClick={handleDownload}>
              <i className="fas fa-download"></i>
              Download
            </button>
          </div>
          {status.message && (
            <div className={`status-message ${status.type}`}>
              {status.message}
            </div>
          )}
        </div>
      )}

      {!loading && !result && status.message && (
        <div className={`status-message ${status.type}`} style={{ margin: '20px 0' }}>
          {status.message}
        </div>
      )}

      <div className="features">
        <div className="feature">
          <i className="fas fa-bolt"></i>
          <span>Fast Extract</span>
        </div>
        <div className="feature">
          <i className="fas fa-hdd"></i>
          <span>Offline Play</span>
        </div>
        <div className="feature">
          <i className="fas fa-headphones"></i>
          <span>High Quality</span>
        </div>
      </div>
    </div>
  );
}
