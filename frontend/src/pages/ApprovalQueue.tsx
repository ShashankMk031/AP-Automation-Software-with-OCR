import React, { useEffect, useState, useRef } from 'react';
import apiClient from '../api/client';
import { Check, X, ShieldAlert, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const ApprovalQueue: React.FC = () => {
  const [invoices, setInvoices] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [accessDenied, setAccessDenied] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const navigate = useNavigate();
  
  const { user } = useAuth();
  const isApprover = user?.role === 'APPROVER';

  // Modal states
  const [modalOpen, setModalOpen] = useState(false);
  const [modalAction, setModalAction] = useState<'APPROVE' | 'REJECT' | null>(null);
  const [modalInvoiceId, setModalInvoiceId] = useState<number | null>(null);
  const [modalComments, setModalComments] = useState('');
  const [submitting, setSubmitting] = useState(false);
  
  const commentInputRef = useRef<HTMLTextAreaElement>(null);

  const fetchPending = async () => {
    setLoading(true);
    setAccessDenied(false);
    try {
      const res = await apiClient.get('/invoices/pending-approval');
      setInvoices(res.data);
    } catch (err: any) {
      if (err.response?.status === 403) {
        setAccessDenied(true);
      } else {
        console.error("Failed to load pending approvals", err);
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPending();
  }, []);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && modalOpen) {
        closeModal();
        return;
      }

      if (e.key === 'Tab' && modalOpen) {
        const modalContainer = commentInputRef.current?.closest('.card');
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
  }, [modalOpen]);

  useEffect(() => {
    if (modalOpen && commentInputRef.current) {
      commentInputRef.current.focus();
    }
  }, [modalOpen]);

  const openModal = (invoiceId: number, action: 'APPROVE' | 'REJECT') => {
    if (!isApprover) return;
    setModalInvoiceId(invoiceId);
    setModalAction(action);
    setModalComments('');
    setModalOpen(true);
  };

  const closeModal = () => {
    setModalOpen(false);
    setModalAction(null);
    setModalInvoiceId(null);
    setModalComments('');
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!modalInvoiceId || !modalAction || !isApprover) return;

    setError(null);
    setSubmitting(true);
    try {
      await apiClient.post(`/invoices/${modalInvoiceId}/${modalAction.toLowerCase()}`, {
        action: modalAction,
        comments: modalComments
      });
      closeModal();
      fetchPending();
    } catch (err: any) {
      if (err.response?.status === 403) {
        setAccessDenied(true);
        closeModal();
      } else {
        setError("Failed to submit approval: " + (err.response?.data?.detail || err.message));
      }
    } finally {
      setSubmitting(false);
    }
  };

  if (accessDenied) {
    return (
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%' }}>
        <div className="card" style={{ maxWidth: '400px', textAlign: 'center', padding: '3rem 2rem' }}>
          <ShieldAlert size={48} className="text-danger" style={{ margin: '0 auto 1rem' }} />
          <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', color: 'var(--color-danger)' }}>Access Restricted</h2>
          
          <div style={{ background: 'var(--color-bg-base)', padding: '1rem', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem', textAlign: 'left', fontSize: '0.875rem' }}>
            <div style={{ marginBottom: '0.5rem' }}>
              <span style={{ color: 'var(--color-text-muted)', display: 'block', marginBottom: '0.125rem' }}>Current Role:</span>
              <span style={{ fontWeight: 600, fontFamily: 'monospace' }}>{user?.role || 'UNKNOWN'}</span>
            </div>
            <div>
              <span style={{ color: 'var(--color-text-muted)', display: 'block', marginBottom: '0.125rem' }}>Required Role:</span>
              <span style={{ fontWeight: 600, fontFamily: 'monospace' }}>APPROVER</span>
            </div>
          </div>

          <p style={{ color: 'var(--color-text-muted)', lineHeight: 1.5, fontSize: '0.875rem' }}>
            You do not have permission to approve or reject invoices using this account.<br/><br/>
            Please sign in using an account assigned the <strong>APPROVER</strong> role.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Approval Queue</h1>
      </div>

      <div style={{ padding: '0.75rem', background: '#e0f2fe', color: '#0369a1', borderRadius: 'var(--radius-md)', marginBottom: '1rem', fontSize: '0.875rem' }}>
        Only accounts with the <strong>APPROVER</strong> role can execute Approve or Reject actions. 
        Admin and Finance roles are intentionally restricted from this queue.
      </div>

      {error && (
        <div style={{ padding: '1rem', background: '#fee2e2', color: '#b91c1c', borderRadius: 'var(--radius-md)', display: 'flex', gap: '0.5rem', alignItems: 'center', marginBottom: '1rem' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

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
                    <td style={{ fontWeight: 600 }}>{inv.total_amount != null ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(inv.total_amount) : 'N/A'}</td>
                    <td>{new Date(inv.submitted_at).toLocaleDateString()}</td>
                    <td>
                      <div style={{ display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
                        <button 
                          className="btn" 
                          style={{ 
                            background: isApprover ? 'var(--color-success)' : 'var(--color-border)', 
                            color: isApprover ? 'white' : 'var(--color-text-muted)', 
                            padding: '0.25rem 0.75rem',
                            cursor: isApprover ? 'pointer' : 'not-allowed'
                          }}
                          onClick={() => openModal(inv.invoice_id, 'APPROVE')}
                          disabled={!isApprover}
                          title={!isApprover ? "Approval permissions required" : ""}
                        >
                          <Check size={16} style={{ display: 'inline', verticalAlign: 'text-bottom' }} /> Approve
                        </button>
                        <button 
                          className="btn" 
                          style={{ 
                            background: isApprover ? 'var(--color-danger)' : 'var(--color-border)', 
                            color: isApprover ? 'white' : 'var(--color-text-muted)', 
                            padding: '0.25rem 0.75rem',
                            cursor: isApprover ? 'pointer' : 'not-allowed'
                          }}
                          onClick={() => openModal(inv.invoice_id, 'REJECT')}
                          disabled={!isApprover}
                          title={!isApprover ? "Approval permissions required" : ""}
                        >
                          <X size={16} style={{ display: 'inline', verticalAlign: 'text-bottom' }} /> Reject
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

      {modalOpen && (
        <div style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
          background: 'rgba(0,0,0,0.5)', zIndex: 1000,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          backdropFilter: 'blur(4px)'
        }}>
          <div className="card" style={{ width: '400px', maxWidth: '90vw' }}>
            <h2 style={{ 
              fontSize: '1.25rem', fontWeight: 600, marginBottom: '1rem',
              color: modalAction === 'APPROVE' ? 'var(--color-success)' : 'var(--color-danger)'
            }}>
              {modalAction === 'APPROVE' ? 'Approve Invoice' : 'Reject Invoice'}
            </h2>
            <form onSubmit={handleSubmit}>
              <div className="input-group">
                <label className="input-label">Comments (Required)</label>
                <textarea 
                  ref={commentInputRef}
                  className="input-field" 
                  rows={4}
                  value={modalComments}
                  onChange={(e) => setModalComments(e.target.value)}
                  placeholder={`Reason for ${modalAction?.toLowerCase()}...`}
                  required
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault();
                      if (modalComments.trim()) {
                        handleSubmit(e);
                      }
                    }
                  }}
                />
              </div>
              <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '0.5rem', marginTop: '1.5rem' }}>
                <button type="button" className="btn btn-outline" onClick={closeModal} disabled={submitting}>
                  Cancel
                </button>
                <button type="submit" className="btn" style={{ background: modalAction === 'APPROVE' ? 'var(--color-success)' : 'var(--color-danger)', color: 'white' }} disabled={submitting || !modalComments.trim()}>
                  {submitting ? 'Submitting...' : `Confirm ${modalAction}`}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default ApprovalQueue;
