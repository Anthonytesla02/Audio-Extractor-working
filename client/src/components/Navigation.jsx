import { NavLink } from 'react-router-dom';

export default function Navigation() {
  return (
    <nav className="bottom-nav">
      <div className="nav-container">
        <NavLink to="/" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <i className="fas fa-plus-circle"></i>
          <span>Add Music</span>
        </NavLink>
        <NavLink to="/library" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <i className="fas fa-book-open"></i>
          <span>Library</span>
        </NavLink>
      </div>
    </nav>
  );
}
