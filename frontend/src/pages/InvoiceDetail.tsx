import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import apiClient from '../api/client';
import { FileText, Building, CheckCircle, Activity, Box, Database, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';

const InvoiceDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [poMatchResult, setPoMatchResult] = useState<any>(null);
  const [poId, setPoId] = useState('');
  const [matching, setMatching] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  
  const { user } = useAuth();
  const canSubmit = user?.role === 'ADMIN' || user?.role === 'FINANCE';

  useEffect(() => {
    const fetchDetail = async () => {
      try {
        const res = await apiClient.get(`/invoices/${id}`);
        setData(res.data);
      } catch (err) {
        console.error("Failed to load invoice detail", err);
        setError("Failed to load invoice details.");
      } finally {
        setLoading(false);
      }
    };
    fetchDetail();
  }, [id]);

  const handlePoMatch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!poId) return;
    setError(null);
    setMatching(true);
    try {
      const res = await apiClient.post(`/invoices/${id}/po-match`, { po_id: parseInt(poId) });
      setPoMatchResult(res.data);
    } catch (err: any) {
      setError("PO Match failed: " + (err.response?.data?.detail || err.message));
    } finally {
      setMatching(false);
    }
  };

  const handleSubmitForApproval = async () => {
    if (!canSubmit) return;
    setError(null);
    setSubmitting(true);
    try {
      await apiClient.post(`/invoices/${id}/submit`);
      // Refresh detail
      const res = await apiClient.get(`/invoices/${id}`);
      setData(res.data);
    } catch (err: any) {
      setError("Failed to submit for approval: " + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) return <div style={{ padding: '2rem' }}>Loading invoice details...</div>;
  if (!data) return <div style={{ padding: '2rem' }}>Invoice not found.</div>;

  const { invoice, vendor_name, line_items, approval_history, audit_logs } = data;

  const formatINR = (amount: number | null | undefined) => {
    if (amount == null) return 'N/A';
    return new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(amount);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
      
      <div style={{ padding: '0.75rem', background: '#e0f2fe', color: '#0369a1', borderRadius: 'var(--radius-md)', marginBottom: '-1rem', fontSize: '0.875rem' }}>
        Submitting invoices to the queue requires the <strong>ADMIN</strong> or <strong>FINANCE</strong> role. 
        Final approval actions in the queue require the <strong>APPROVER</strong> role.
      </div>

      <div className="page-header" style={{ marginBottom: 0 }}>
        <div>
          <h1 className="page-title">
            Invoice {invoice.invoice_number?.startsWith('PENDING_') ? <span style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>Not Extracted</span> : invoice.invoice_number}
          </h1>
          <div style={{ marginTop: '0.5rem', color: 'var(--color-text-muted)', display: 'flex', gap: '1rem' }}>
            <span><Building size={16} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '4px' }}/> {vendor_name}</span>
            <span>Date: {invoice.invoice_date ? new Date(invoice.invoice_date).toLocaleDateString() : 'N/A'}</span>
          </div>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.5rem' }}>
          <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-primary)' }}>
            {formatINR(invoice.total_amount)}
          </div>
          {invoice.status === 'VALIDATION_PASSED' && (
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end' }}>
              <button 
                className="btn btn-primary" 
                onClick={handleSubmitForApproval} 
                disabled={submitting || !canSubmit}
                title={!canSubmit ? "Admin or Finance role required to submit." : ""}
              >
                {submitting ? 'Submitting...' : 'Submit For Approval'}
              </button>
              {!canSubmit && (
                <span style={{ fontSize: '0.75rem', color: 'var(--color-warning)', marginTop: '0.25rem' }}>
                  Submission permissions required
                </span>
              )}
            </div>
          )}
        </div>
      </div>

      {error && (
        <div style={{ padding: '1rem', background: '#fee2e2', color: '#b91c1c', borderRadius: 'var(--radius-md)', display: 'flex', gap: '0.5rem', alignItems: 'center' }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        
        {/* Left Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div className="card">
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <FileText size={20} className="text-primary" />
              Extracted Line Items
            </h2>
            <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
              <table>
                <thead>
                  <tr>
                    <th>Description</th>
                    <th>Qty</th>
                    <th>Price</th>
                    <th>Total</th>
                  </tr>
                </thead>
                <tbody>
                  {line_items.length === 0 ? (
                    <tr><td colSpan={4}>No line items extracted.</td></tr>
                  ) : (
                    line_items.map((item: any, idx: number) => (
                      <tr key={idx}>
                        <td>{item.description}</td>
                        <td>{item.quantity}</td>
                        <td>{formatINR(item.unit_price)}</td>
                        <td>{formatINR(item.line_total)}</td>
                      </tr>
                    ))
                  )}
                </tbody>
              </table>
            </div>
          </div>

          <div className="card">
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Box size={20} className="text-primary" />
              Purchase Order Matching
            </h2>
            
            <form onSubmit={handlePoMatch} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-end', marginBottom: '1.5rem' }}>
              <div className="input-group" style={{ marginBottom: 0, flex: 1 }}>
                <label className="input-label">Enter PO ID to Match</label>
                <input 
                  type="number" 
                  className="input-field" 
                  value={poId}
                  onChange={(e) => {
                    setPoId(e.target.value);
                    setPoMatchResult(null); // Clear previous result
                  }}
                  placeholder="e.g. 1001"
                  required
                />
              </div>
              <button type="submit" className="btn btn-primary" disabled={matching}>
                {matching ? 'Matching...' : 'Run Match'}
              </button>
            </form>

            {poMatchResult && (
              <div style={{ padding: '1rem', borderRadius: 'var(--radius-md)', background: poMatchResult.result === 'MATCHED' ? 'var(--color-success)' : (poMatchResult.result === 'PARTIAL_MATCH' ? 'var(--color-warning)' : 'var(--color-danger)'), color: 'white' }}>
                <div style={{ fontWeight: 700, marginBottom: '0.5rem', fontSize: '1.125rem' }}>{poMatchResult.result} ({poMatchResult.match_type})</div>
                <div style={{ fontSize: '0.875rem', opacity: 0.9 }}>
                  <div>PO Amount: {formatINR(poMatchResult.po_amount)}</div>
                  <div>GRN Amount: {formatINR(poMatchResult.grn_amount)}</div>
                  <div>Invoice Amount: {formatINR(poMatchResult.invoice_amount)}</div>
                </div>
                {poMatchResult.details?.length > 0 && (
                  <ul style={{ marginTop: '0.5rem', paddingLeft: '1.5rem', fontSize: '0.875rem' }}>
                    {poMatchResult.details.map((d: string, i: number) => <li key={i}>{d}</li>)}
                  </ul>
                )}
              </div>
            )}
          </div>

          <div className="card">
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <CheckCircle size={20} className="text-primary" />
              Approval History
            </h2>
            {approval_history.length === 0 ? (
              <p style={{ color: 'var(--color-text-muted)' }}>No approval workflows initiated.</p>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                {approval_history.map((hist: any, i: number) => (
                  <div key={i} style={{ padding: '1rem', background: 'var(--color-bg-base)', borderRadius: 'var(--radius-md)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                      <span className="badge badge-default" style={{ background: 'var(--color-primary)', color: 'white' }}>{hist.status}</span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>{hist.actioned_at ? new Date(hist.actioned_at).toLocaleString() : 'Pending'}</span>
                    </div>
                    <div style={{ fontSize: '0.875rem' }}><strong>Approver:</strong> {hist.approver_email || 'Unassigned'}</div>
                    {hist.comments && <div style={{ fontSize: '0.875rem', marginTop: '0.5rem', fontStyle: 'italic' }}>"{hist.comments}"</div>}
                  </div>
                ))}
              </div>
            )}
          </div>

        </div>

        {/* Right Column */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '2rem' }}>
          
          <div className="card">
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Database size={20} className="text-primary" />
              Metadata
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.875rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Status</span>
                <span style={{ fontWeight: 600 }}>{invoice.status}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>OCR Confidence</span>
                <span style={{ fontWeight: 600 }}>{invoice.ocr_confidence ? `${(invoice.ocr_confidence * 100).toFixed(1)}%` : 'N/A'}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Subtotal</span>
                <span style={{ fontWeight: 600 }}>{formatINR(invoice.subtotal)}</span>
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                <span style={{ color: 'var(--color-text-muted)' }}>Tax (GST)</span>
                <span style={{ fontWeight: 600 }}>{formatINR(invoice.gst_amount)}</span>
              </div>
              {invoice.file_path && (
                <div style={{ marginTop: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--color-border)' }}>
                  <span style={{ color: 'var(--color-text-muted)' }}>File</span>
                  <div style={{ fontFamily: 'monospace', wordBreak: 'break-all', fontSize: '0.75rem', marginTop: '0.25rem' }}>
                    {invoice.file_path}
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="card">
            <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity size={20} className="text-primary" />
              Recent Audit Log
            </h2>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '400px', overflowY: 'auto' }}>
              {audit_logs.length === 0 ? (
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>No audit logs found.</div>
              ) : (
                audit_logs.map((log: any) => (
                  <div key={log.id} style={{ position: 'relative', paddingLeft: '1.5rem' }}>
                    <div style={{ position: 'absolute', left: 0, top: '0.25rem', width: '8px', height: '8px', borderRadius: '50%', background: 'var(--color-primary)' }} />
                    <div style={{ fontSize: '0.875rem', fontWeight: 600, marginBottom: '0.125rem' }}>{log.action}</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>
                      {new Date(log.timestamp).toLocaleString()} by {log.actor_email}
                    </div>
                    <div style={{ fontSize: '0.875rem' }}>{log.details}</div>
                  </div>
                ))
              )}
            </div>
          </div>

        </div>

      </div>
    </div>
  );
};

export default InvoiceDetail;
