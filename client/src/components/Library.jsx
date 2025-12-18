import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { api, formatDuration } from '../services/api';
import Player from './Player';

export default function Library() {
  const [songs, setSongs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [currentSongIndex, setCurrentSongIndex] = useState(-1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [duration, setDuration] = useState(0);

  useEffect(() => {
    loadSongs();
  }, []);

  const loadSongs = async () => {
    try {
      const data = await api.getSongs();
      setSongs(data);
    } catch (error) {
      console.error('Failed to load songs:', error);
    }
    setLoading(false);
  };

  const playSong = (index) => {
    if (currentSongIndex === index && isPlaying) {
      setIsPlaying(false);
      return;
    }
    setCurrentSongIndex(index);
    setIsPlaying(true);
    setCurrentTime(0);
    setDuration(songs[index]?.duration || 0);
  };

  const handlePlayPause = () => {
    setIsPlaying(!isPlaying);
  };

  const handlePrevious = () => {
    if (songs.length === 0) return;
    const newIndex = currentSongIndex <= 0 ? songs.length - 1 : currentSongIndex - 1;
    playSong(newIndex);
  };

  const handleNext = () => {
    if (songs.length === 0) return;
    const newIndex = currentSongIndex >= songs.length - 1 ? 0 : currentSongIndex + 1;
    playSong(newIndex);
  };

  const handleTimeUpdate = (time, dur) => {
    setCurrentTime(time);
    if (dur > 0) setDuration(dur);
  };

  const handleSeek = (time) => {
    setCurrentTime(time);
  };

  const handleEnded = () => {
    handleNext();
  };

  const deleteSong = async (id, e) => {
    e.stopPropagation();
    if (!window.confirm('Delete this song from your library?')) return;

    try {
      const data = await api.deleteSong(id);
      if (data.success) {
        if (currentSongIndex >= 0 && songs[currentSongIndex]?.id === id) {
          setIsPlaying(false);
          setCurrentSongIndex(-1);
        }
        loadSongs();
      }
    } catch (error) {
      console.error('Failed to delete:', error);
    }
  };

  const currentSong = currentSongIndex >= 0 ? songs[currentSongIndex] : null;

  return (
    <>
      <div className="app-container">
        <div className="header">
          <h1><i className="fas fa-book-open"></i> My Library</h1>
          <p>Your saved music collection</p>
          <span className="song-count">
            {songs.length} song{songs.length !== 1 ? 's' : ''}
          </span>
        </div>

        {loading && (
          <div className="loading">
            <div className="spinner"></div>
          </div>
        )}

        {!loading && songs.length === 0 && (
          <div className="empty-state">
            <i className="fas fa-music"></i>
            <h3>No songs yet</h3>
            <p>Add music from YouTube to your library</p>
            <Link to="/"><i className="fas fa-plus"></i> Add Music</Link>
          </div>
        )}

        {!loading && songs.length > 0 && (
          <div className="songs-list">
            {songs.map((song, index) => (
              <div
                key={song.id}
                className={`song-item ${currentSongIndex === index ? 'playing' : ''}`}
              >
                <div className="song-thumb">
                  <i className={`fas ${currentSongIndex === index && isPlaying ? 'fa-pause' : 'fa-music'}`}></i>
                </div>
                <div className="song-details" onClick={() => playSong(index)}>
                  <h3>{song.title}</h3>
                  <p>{song.artist} - {formatDuration(song.duration)}</p>
                </div>
                <div className="song-actions">
                  <button
                    className="song-action-btn play-btn"
                    onClick={() => playSong(index)}
                  >
                    <i className={`fas ${currentSongIndex === index && isPlaying ? 'fa-pause' : 'fa-play'}`}></i>
                  </button>
                  <button
                    className="song-action-btn delete-btn"
                    onClick={(e) => deleteSong(song.id, e)}
                  >
                    <i className="fas fa-trash"></i>
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <Player
        currentSong={currentSong}
        isPlaying={isPlaying}
        currentTime={currentTime}
        duration={duration}
        onPlayPause={handlePlayPause}
        onPrevious={handlePrevious}
        onNext={handleNext}
        onTimeUpdate={handleTimeUpdate}
        onEnded={handleEnded}
        onSeek={handleSeek}
      />
    </>
  );
}
