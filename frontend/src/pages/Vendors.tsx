import React, { useEffect, useState, useRef } from 'react';
import apiClient from '../api/client';
import { Search, Plus, Edit2, Check, X } from 'lucide-react';

const Vendors: React.FC = () => {
  const [vendors, setVendors] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  
  // Create / Edit modal state
  const [showModal, setShowModal] = useState(false);
  const [editingId, setEditingId] = useState<number | null>(null);
  const [formData, setFormData] = useState({ name: '', gstin: '', bank_details: '', status: 'ACTIVE' });
  const [error, setError] = useState<string | null>(null);

  const nameInputRef = useRef<HTMLInputElement>(null);

  const fetchVendors = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get(`/vendors?skip=0&limit=100${search ? `&name=${search}` : ''}`);
      setVendors(res.data.items || []);
    } catch (err) {
      console.error("Failed to load vendors", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVendors();
  }, [search]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && showModal) {
        setShowModal(false);
        setError(null);
        return;
      }
      
      if (e.key === 'Tab' && showModal) {
        const modalContainer = nameInputRef.current?.closest('.card');
        if (!modalContainer) return;
        
        const focusableElements = modalContainer.querySelectorAll(
          'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
        );
        if (focusableElements.length === 0) return;
        
        const firstElement = focusableElements[0] as HTMLElement;
        const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement;
        
        if (e.shiftKey) {
          if (document.activeElement === firstElement) {
            lastElement.focus();
            e.preventDefault();
          }
        } else {
          if (document.activeElement === lastElement) {
            firstElement.focus();
            e.preventDefault();
          }
        }
      }
    };
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [showModal]);

  useEffect(() => {
    if (showModal && nameInputRef.current) {
      setTimeout(() => {
        nameInputRef.current?.focus();
      }, 50);
    }
  }, [showModal]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    try {
      if (editingId) {
        await apiClient.put(`/vendors/${editingId}`, formData);
      } else {
        await apiClient.post('/vendors', formData);
      }
      setShowModal(false);
      fetchVendors();
    } catch (err: any) {
      let errMsg = err.response?.data?.detail || err.message;
      if (Array.isArray(errMsg)) {
        errMsg = errMsg.map((e: any) => e.msg).join(', ');
      }
      setError("Failed to save vendor: " + errMsg);
    }
  };

  const openNew = () => {
    setEditingId(null);
    setFormData({ name: '', gstin: '', bank_details: '', status: 'ACTIVE' });
    setError(null);
    setShowModal(true);
  };

  const openEdit = (v: any) => {
    setEditingId(v.id);
    setFormData({ name: v.name, gstin: v.gstin || '', bank_details: v.bank_details || '', status: v.status });
    setError(null);
    setShowModal(true);
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Vendors</h1>
        <button className="btn btn-primary" onClick={openNew}>
          <Plus size={18} /> Add Vendor
        </button>
      </div>

      <div className="card" style={{ marginBottom: '2rem', padding: '1rem' }}>
        <div className="input-group" style={{ marginBottom: 0 }}>
          <div style={{ position: 'relative', width: '300px' }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
            <input 
              type="text" 
              className="input-field" 
              style={{ width: '100%', paddingLeft: '2.5rem' }}
              placeholder="Search vendors by name..."
              value={search}
              onChange={e => setSearch(e.target.value)}
            />
          </div>
        </div>
      </div>

      <div className="table-container">
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>Loading vendors...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Name</th>
                <th>GSTIN</th>
                <th>Bank Details</th>
                <th>Status</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {vendors.length === 0 ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '2rem' }}>No vendors found.</td>
                </tr>
              ) : (
                vendors.map(v => (
                  <tr key={v.id}>
                    <td>#{v.id}</td>
                    <td style={{ fontWeight: 500 }}>{v.name}</td>
                    <td>{v.gstin || '-'}</td>
                    <td>{v.bank_details || '-'}</td>
                    <td>
                      <span className={v.status === 'ACTIVE' ? 'badge badge-success' : 'badge badge-default'}>
                        {v.status}
                      </span>
                    </td>
                    <td>
                      <button className="btn btn-outline" style={{ padding: '0.25rem' }} onClick={() => openEdit(v)}>
                        <Edit2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>

      {/* Modal */}
      {showModal && (
        <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 100 }}>
          <div className="card" style={{ width: '100%', maxWidth: '500px', maxHeight: '90vh', overflowY: 'auto' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 600 }}>{editingId ? 'Edit Vendor' : 'Add Vendor'}</h2>
              <button onClick={() => setShowModal(false)} style={{ background: 'transparent', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}><X size={24} /></button>
            </div>
            
            <form onSubmit={handleSave}>
              {error && (
                <div style={{ padding: '0.75rem', background: '#fee2e2', color: '#b91c1c', borderRadius: 'var(--radius-md)', marginBottom: '1rem', fontSize: '0.875rem' }}>
                  {error}
                </div>
              )}
              <div className="input-group">
                <label className="input-label">Vendor Name *</label>
                <input ref={nameInputRef} type="text" className="input-field" value={formData.name} onChange={e => setFormData({...formData, name: e.target.value})} required />
              </div>
              <div className="input-group">
                <label className="input-label">GSTIN *</label>
                <input type="text" className="input-field" value={formData.gstin} onChange={e => setFormData({...formData, gstin: e.target.value.toUpperCase()})} placeholder="e.g. 29ABCDE1234F1Z5" required />
              </div>
              <div className="input-group">
                <label className="input-label">Bank Details (Optional)</label>
                <textarea className="input-field" rows={3} value={formData.bank_details} onChange={e => setFormData({...formData, bank_details: e.target.value})} placeholder="Account No, IFSC, etc." />
              </div>
              
              {editingId && (
                <div className="input-group">
                  <label className="input-label">Status</label>
                  <select className="input-field" value={formData.status} onChange={e => setFormData({...formData, status: e.target.value})}>
                    <option value="ACTIVE">ACTIVE</option>
                    <option value="INACTIVE">INACTIVE</option>
                  </select>
                </div>
              )}
              
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '1rem', marginTop: '2rem' }}>
                <button type="button" className="btn btn-outline" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary"><Check size={18} /> Save Vendor</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Vendors;
