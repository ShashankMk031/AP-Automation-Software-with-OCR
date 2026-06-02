import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { Check, X } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const ApprovalQueue: React.FC = () => {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  const fetchPending = async () => {
    setLoading(true);
    try {
      const res = await apiClient.get('/invoices/pending-approval');
      setInvoices(res.data);
    } catch (err) {
      console.error("Failed to load pending approvals", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  const handleAction = async (invoiceId: number, action: 'APPROVE' | 'REJECT') => {
    const comments = prompt(`Enter comments for ${action} (optional):`);
    if (comments === null) return; // cancelled

    try {
      await apiClient.post(`/invoices/${invoiceId}/approve`, {
        action,
        comments
      });
      fetchPending();
    } catch (err: any) {
      alert("Failed to submit approval: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Approval Queue</h1>
      </div>

      <div className="table-container">
        {loading ? (
          <div style={{ padding: '2rem', textAlign: 'center' }}>Loading pending invoices...</div>
        ) : (
          <table>
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Vendor</th>
                <th>Amount</th>
                <th>Submission Date</th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {invoices.length === 0 ? (
                <tr>
                  <td colSpan={5} style={{ textAlign: 'center', padding: '2rem' }}>No invoices pending approval.</td>
                </tr>
              ) : (
                invoices.map((inv) => (
                  <tr key={inv.invoice_id}>
                    <td>
                      <button 
                        className="btn btn-outline" 
                        style={{ border: 'none', color: 'var(--color-primary)', padding: 0 }}
                        onClick={() => navigate(`/invoices/${inv.invoice_id}`)}
                      >
                        {inv.invoice_number}
                      </button>
                    </td>
                    <td>{inv.vendor_name}</td>
                    <td style={{ fontWeight: 600 }}>${inv.total_amount?.toFixed(2)}</td>
                    <td>{new Date(inv.submitted_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem' }}>
                        <button 
                          className="btn" 
                          style={{ background: 'var(--color-success)', color: 'white', padding: '0.25rem 0.75rem' }}
                          onClick={() => handleAction(inv.invoice_id, 'APPROVE')}
                        >
                          <Check size={16} /> Approve
                        </button>
                        <button 
                          className="btn" 
                          style={{ background: 'var(--color-danger)', color: 'white', padding: '0.25rem 0.75rem' }}
                          onClick={() => handleAction(inv.invoice_id, 'REJECT')}
                        >
                          <X size={16} /> Reject
                        </button>
                      </div>
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

export default ApprovalQueue;
