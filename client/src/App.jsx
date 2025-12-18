import { Routes, Route } from 'react-router-dom';
import AddMusic from './components/AddMusic';
import Library from './components/Library';
import Navigation from './components/Navigation';

function App() {
  return (
    <>
      <Routes>
        <Route path="/" element={<AddMusic />} />
        <Route path="/library" element={<Library />} />
      </Routes>
      <Navigation />
    </>
  );
}

export default App;
