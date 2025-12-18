const API_BASE_URL = import.meta.env.VITE_API_URL || '';

export const api = {
  async getSongs() {
    const response = await fetch(`${API_BASE_URL}/api/songs`);
    if (!response.ok) throw new Error('Failed to fetch songs');
    return response.json();
  },

  async getSong(id) {
    const response = await fetch(`${API_BASE_URL}/api/songs/${id}`);
    if (!response.ok) throw new Error('Failed to fetch song');
    return response.json();
  },

  async deleteSong(id) {
    const response = await fetch(`${API_BASE_URL}/api/songs/${id}`, {
      method: 'DELETE'
    });
    if (!response.ok) throw new Error('Failed to delete song');
    return response.json();
  },

  async convertVideo(url) {
    const response = await fetch(`${API_BASE_URL}/convert`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ url })
    });
    if (!response.ok) throw new Error('Failed to convert video');
    return response.json();
  },

  async saveToLibrary(data) {
    const response = await fetch(`${API_BASE_URL}/save-to-library`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
    if (!response.ok) throw new Error('Failed to save to library');
    return response.json();
  },

  getAudioUrl(songId) {
    return `${API_BASE_URL}/api/songs/${songId}/audio`;
  },

  getDownloadUrl(fileId, title) {
    return `${API_BASE_URL}/download/${fileId}?title=${encodeURIComponent(title)}`;
  }
};

export function formatDuration(seconds) {
  if (!seconds) return '0:00';
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}
