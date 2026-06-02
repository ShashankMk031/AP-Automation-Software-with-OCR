import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { Search, Filter } from 'lucide-react';

const InvoiceList: React.FC = () => {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const navigate = useNavigate();

  const fetchInvoices = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.append('search', search);
      if (status) params.append('status', status);
      
      const res = await apiClient.get(`/invoices?${params.toString()}`);
      setInvoices(res.data.data);
    } catch (err) {
      console.error("Failed to load invoices", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, [status]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchInvoices();
  };

  const getStatusBadge = (status: string) => {
    const s = status.toLowerCase();
    if (s === 'approved') return 'badge badge-success';
    if (s === 'rejected' || s === 'validation_failed') return 'badge badge-danger';
    if (s === 'pending_approval') return 'badge badge-warning';
    return 'badge badge-default';
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Invoices</h1>
      </div>

      <div className="card" style={{ marginBottom: '2rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end' }}>
          <div className="input-group" style={{ marginBottom: 0, flex: 1 }}>
            <label className="input-label">Search Invoice Number</label>
            <div style={{ position: 'relative' }}>
              <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
              <input 
                type="text" 
                className="input-field" 
                style={{ width: '100%', paddingLeft: '2.5rem' }}
                placeholder="INV-..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
          </div>
          
          <div className="input-group" style={{ marginBottom: 0, width: '200px' }}>
            <label className="input-label">Filter Status</label>
            <div style={{ position: 'relative' }}>
              <Filter size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--color-text-muted)' }} />
              <select 
                className="input-field" 
                style={{ width: '100%', paddingLeft: '2.5rem', appearance: 'none' }}
                value={status}
                onChange={e => setStatus(e.target.value)}
              >
                <option value="">All Statuses</option>
                <option value="UPLOADED">Uploaded</option>
                <option value="EXTRACTED">Extracted</option>
                <option value="VALIDATION_PASSED">Validation Passed</option>
                <option value="VALIDATION_FAILED">Validation Failed</option>
                <option value="PENDING_APPROVAL">Pending Approval</option>
                <option value="APPROVED">Approved</option>
                <option value="REJECTED">Rejected</option>
              </select>
            </div>
          </div>

          <button type="submit" className="btn btn-primary" style={{ padding: '0.75rem 1.5rem' }}>
            Search
          </button>
        </form>
      </div>

      <div className="table-container">
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>Loading invoices...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>ID</th>
                <th>Invoice Number</th>
                <th>Date</th>
                <th>Amount</th>
                <th>Status</th>
                <th>OCR Confidence</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2rem' }}>No invoices found.</td>
                </tr>
              ) : (
                invoices.map((inv) => (
                  <tr key={inv.id}>
                    <td>#{inv.id}</td>
                    <td style={{ fontWeight: 500 }}>{inv.invoice_number}</td>
                    <td>{inv.invoice_date ? new Date(inv.invoice_date).toLocaleDateString() : 'N/A'}</td>
                    <td>{inv.total_amount ? `$${inv.total_amount.toFixed(2)}` : 'N/A'}</td>
                    <td>
                      <span className={getStatusBadge(inv.status)}>
                        {inv.status.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      {inv.ocr_confidence ? `${(inv.ocr_confidence * 100).toFixed(1)}%` : 'N/A'}
                    </td>
                    <td>
                      <button 
                        className="btn btn-outline" 
                        style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}
                        onClick={() => navigate(`/invoices/${inv.id}`)}
                      >
                        View
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
};

export default InvoiceList;
