import { useRef, useEffect } from 'react';
import { api, formatDuration } from '../services/api';

export default function Player({
  currentSong,
  isPlaying,
  currentTime,
  duration,
  onPlayPause,
  onPrevious,
  onNext,
  onTimeUpdate,
  onEnded,
  onSeek
}) {
  const audioRef = useRef(null);

  useEffect(() => {
    if (currentSong && audioRef.current) {
      audioRef.current.src = api.getAudioUrl(currentSong.id);
      if (isPlaying) {
        audioRef.current.play().catch(console.error);
      }
    }
  }, [currentSong]);

  useEffect(() => {
    if (audioRef.current) {
      if (isPlaying) {
        audioRef.current.play().catch(console.error);
      } else {
        audioRef.current.pause();
      }
    }
  }, [isPlaying]);

  const handleTimeUpdate = () => {
    if (audioRef.current) {
      onTimeUpdate(audioRef.current.currentTime, audioRef.current.duration || 0);
    }
  };

  const handleProgressClick = (e) => {
    if (audioRef.current && duration > 0) {
      const rect = e.currentTarget.getBoundingClientRect();
      const percent = (e.clientX - rect.left) / rect.width;
      const newTime = duration * percent;
      audioRef.current.currentTime = newTime;
      onSeek(newTime);
    }
  };

  if (!currentSong) return null;

  const progressPercent = duration > 0 ? (currentTime / duration) * 100 : 0;

  return (
    <>
      <audio
        ref={audioRef}
        onTimeUpdate={handleTimeUpdate}
        onEnded={onEnded}
      />
      <div className={`player-bar ${currentSong ? 'active' : ''}`}>
        <div className="player-container">
          <div className="player-info">
            <div className="player-thumb">
              <i className="fas fa-music"></i>
            </div>
            <div className="player-details">
              <h4>{currentSong.title}</h4>
              <p>{currentSong.artist}</p>
            </div>
            <div className="player-controls">
              <button className="player-btn small" onClick={onPrevious}>
                <i className="fas fa-backward"></i>
              </button>
              <button className="player-btn" onClick={onPlayPause}>
                <i className={`fas fa-${isPlaying ? 'pause' : 'play'}`}></i>
              </button>
              <button className="player-btn small" onClick={onNext}>
                <i className="fas fa-forward"></i>
              </button>
            </div>
          </div>
          <div className="progress-bar" onClick={handleProgressClick}>
            <div
              className="progress-fill"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
          <div className="time-info">
            <span>{formatDuration(currentTime)}</span>
            <span>{formatDuration(duration)}</span>
          </div>
        </div>
      </div>
    </>
  );
}
