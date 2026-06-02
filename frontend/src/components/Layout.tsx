import React from 'react';
import { NavLink, Outlet } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  LayoutDashboard, 
  Users, 
  FileText, 
  UploadCloud, 
  CheckSquare, 
  BarChart3, 
  LogOut,
  Receipt
} from 'lucide-react';

const Layout: React.FC = () => {
  const { logout, user } = useAuth();

  const navItems = [
    { to: '/', label: 'Dashboard', icon: <LayoutDashboard size={20} /> },
    { to: '/vendors', label: 'Vendors', icon: <Users size={20} /> },
    { to: '/invoices/upload', label: 'Upload Invoice', icon: <UploadCloud size={20} /> },
    { to: '/invoices', label: 'Invoices', icon: <Receipt size={20} /> },
    { to: '/approval-queue', label: 'Approval Queue', icon: <CheckSquare size={20} /> },
    { to: '/reports', label: 'Reports', icon: <BarChart3 size={20} /> },
  ];

  return (
    <div className="app-container">
      <aside className="sidebar">
        <div className="sidebar-header">
          <FileText size={24} className="text-primary" />
          <span>AP Auto</span>
        </div>
        
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
            >
              {item.icon}
              {item.label}
            </NavLink>
          ))}
        </nav>

        <div style={{ marginTop: 'auto' }}>
          <div style={{ padding: '1rem', borderTop: '1px solid rgba(255,255,255,0.1)', marginBottom: '1rem' }}>
            <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>{user?.email}</div>
            <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>Role: {user?.role}</div>
          </div>
          <button onClick={logout} className="nav-item" style={{ width: '100%', background: 'transparent', border: 'none', cursor: 'pointer', textAlign: 'left' }}>
            <LogOut size={20} />
            Logout
          </button>
        </div>
      </aside>
      
      <main className="main-content">
        <Outlet />
      </main>
    </div>
  );
};

export default Layout;
