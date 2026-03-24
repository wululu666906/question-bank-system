import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Database, BookOpen, PenTool, Settings } from 'lucide-react';
import './Sidebar.css';

const Sidebar: React.FC = () => {
  const navItems = [
    { name: '题目生产台', path: '/', icon: <LayoutDashboard size={20} /> },
    { name: '题库管理', path: '/bank', icon: <Database size={20} /> },
    { name: '知识库管理', path: '/knowledge', icon: <BookOpen size={20} /> },
    { name: '刷题系统', path: '/practice', icon: <PenTool size={20} /> },
  ];

  return (
    <div className="sidebar">
      <div className="sidebar-header">
        <div className="logo-container">
          <div className="logo-icon">Q</div>
          <span className="logo-text">Question Factory</span>
        </div>
      </div>
      
      <nav className="sidebar-nav">
        {navItems.map((item) => (
          <NavLink 
            key={item.path} 
            to={item.path} 
            className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            <span className="nav-label">{item.name}</span>
          </NavLink>
        ))}
      </nav>

      <div className="sidebar-footer">
        <NavLink to="/settings" className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}>
          <span className="nav-icon"><Settings size={20} /></span>
          <span className="nav-label">系统设置</span>
        </NavLink>
      </div>
    </div>
  );
};

export default Sidebar;
