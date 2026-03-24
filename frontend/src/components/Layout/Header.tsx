import React from 'react';
import { Bell, Search, User } from 'lucide-react';
import { useLocation } from 'react-router-dom';
import './Header.css';

const Header: React.FC = () => {
  const location = useLocation();
  
  const getPageTitle = () => {
    switch (location.pathname) {
      case '/': return '题目生产台';
      case '/bank': return '题库管理';
      case '/knowledge': return '知识库管理';
      case '/practice': return '刷题系统';
      default: return 'Question Factory';
    }
  };

  return (
    <header className="header glass-effect">
      <div className="header-left">
        <h1 className="page-title">{getPageTitle()}</h1>
      </div>
      
      <div className="header-right">
        <div className="search-bar">
          <Search size={18} className="search-icon" />
          <input type="text" placeholder="搜索题目或知识点..." className="search-input" />
        </div>
        
        <button className="icon-btn">
          <Bell size={20} />
          <span className="notification-dot"></span>
        </button>
        
        <div className="user-profile">
          <div className="avatar">
            <User size={20} />
          </div>
          <div className="user-info">
            <span className="user-name">Admin</span>
            <span className="user-role">系统管理员</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;
