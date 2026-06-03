import React, { useEffect, useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import apiClient from '../api/client';
import { Upload, FileText, CheckCircle, AlertTriangle } from 'lucide-react';

const UploadInvoice: React.FC = () => {
  const [vendors, setVendors] = useState<any[]>([]);
  const [vendorId, setVendorId] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    // Load active vendors
    apiClient.get('/vendors?skip=0&limit=100').then(res => {
      setVendors(res.data.items?.filter((v: any) => v.status === 'ACTIVE') || []);
    }).catch(err => console.error(err));
  }, []);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const droppedFile = e.dataTransfer.files[0];
      const ext = droppedFile.name.split('.').pop()?.toLowerCase();
      if (['pdf', 'png', 'jpg', 'jpeg'].includes(ext || '')) {
        setFile(droppedFile);
      } else {
        setError('Unsupported file type. Please upload a PDF, PNG, JPG, or JPEG file.');
      }
    }
  };

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!vendorId || !file) {
      setError('Please select a vendor and a file.');
      return;
    }
    setError('');
    setLoading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('vendor_id', vendorId);
    formData.append('file', file);

    try {
      const res = await apiClient.post('/invoices/upload', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      setResult(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Upload Invoice</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: result ? '1fr 1fr' : '1fr', gap: '2rem' }}>
        <div className="card">
          <form onSubmit={handleUpload}>
            {error && (
              <div style={{ background: 'var(--color-danger)', color: 'white', padding: '0.75rem', borderRadius: 'var(--radius-md)', marginBottom: '1.5rem', fontSize: '0.875rem' }}>
                {error}
              </div>
            )}
            
            <div className="input-group">
              <label className="input-label">Select Vendor</label>
              <select className="input-field" value={vendorId} onChange={e => setVendorId(e.target.value)} required>
                <option value="">-- Choose Vendor --</option>
                {vendors.map(v => (
                  <option key={v.id} value={v.id}>{v.name} ({v.gstin || 'No GSTIN'})</option>
                ))}
              </select>
            </div>

            <div className="input-group" style={{ marginTop: '1.5rem' }}>
              <label className="input-label">Invoice File (PDF/Image)</label>
              <div 
                onClick={() => fileInputRef.current?.click()}
                onDragOver={handleDragOver}
                onDragLeave={handleDragLeave}
                onDrop={handleDrop}
                style={{ 
                  border: `2px dashed ${isDragging ? 'var(--color-primary)' : 'var(--color-border)'}`, 
                  borderRadius: 'var(--radius-md)', 
                  padding: '2rem',
                  textAlign: 'center',
                  background: isDragging ? '#e6f0fa' : 'var(--color-bg-base)',
                  cursor: 'pointer',
                  transition: 'all 0.2s ease-in-out'
                }}
              >
                <Upload size={32} style={{ color: isDragging ? 'var(--color-primary)' : 'var(--color-text-muted)', marginBottom: '1rem' }} />
                <div>
                  {isDragging ? (
                    <div style={{ fontWeight: 600, color: 'var(--color-primary)', fontSize: '1.125rem', marginBottom: '0.5rem' }}>Drop Invoice Here</div>
                  ) : (
                    <>
                      <input 
                        type="file" 
                        id="file" 
                        ref={fileInputRef}
                        onChange={handleFileChange} 
                        accept=".pdf,.png,.jpg,.jpeg" 
                        style={{ display: 'none' }} 
                        onClick={(e) => e.stopPropagation()}
                      />
                      <button 
                        type="button" 
                        className="btn btn-outline" 
                        style={{ display: 'inline-flex' }}
                        onClick={(e) => {
                          e.stopPropagation();
                          fileInputRef.current?.click();
                        }}
                      >
                        Browse Files
                      </button>
                    </>
                  )}
                </div>
                {file && !isDragging && <div style={{ marginTop: '1rem', fontWeight: 500 }}>{file.name}</div>}
              </div>
            </div>

            <button type="submit" className="btn btn-primary" style={{ width: '100%', marginTop: '1.5rem', padding: '1rem' }} disabled={loading}>
              {loading ? 'Uploading & Processing via Gemini OCR...' : 'Upload & Process'}
            </button>
          </form>
        </div>

        {/* Results Panel */}
        {result && (
          <div className="card" style={{ background: result.status === 'VALIDATION_PASSED' ? '#f0fdf4' : '#fef2f2' }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              {result.status === 'VALIDATION_PASSED' ? (
                <><CheckCircle className="text-success" /> Processing Successful</>
              ) : (
                <><AlertTriangle className="text-danger" /> Validation Failed</>
              )}
            </h2>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div>
                <span style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Internal Invoice ID:</span>
                <div style={{ fontWeight: 600 }}>#{result.invoice_id}</div>
              </div>

              {result.ocr_data && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                    <FileText size={18} /> Extracted Data
                  </h3>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.5rem', fontSize: '0.875rem' }}>
                    <div><strong>Inv #:</strong> {result.ocr_data.invoice_number}</div>
                    <div><strong>Date:</strong> {result.ocr_data.invoice_date}</div>
                    <div><strong>Total:</strong> {result.ocr_data.total_amount != null ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(result.ocr_data.total_amount) : 'N/A'}</div>
                    <div><strong>GST:</strong> {result.ocr_data.gst_amount != null ? new Intl.NumberFormat('en-IN', { style: 'currency', currency: 'INR' }).format(result.ocr_data.gst_amount) : 'N/A'}</div>
                  </div>
                </div>
              )}

              {result.validation_errors?.length > 0 && (
                <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid rgba(0,0,0,0.1)' }}>
                  <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: '0.5rem', color: 'var(--color-danger)' }}>
                    Errors Detected
                  </h3>
                  <ul style={{ paddingLeft: '1.5rem', fontSize: '0.875rem', color: 'var(--color-danger)' }}>
                    {result.validation_errors.map((err: string, i: number) => <li key={i}>{err}</li>)}
                  </ul>
                </div>
              )}

              <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
                <button 
                  autoFocus
                  className="btn btn-primary" 
                  onClick={() => {
                    setFile(null);
                    setResult(null);
                    setError('');
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' || e.key === ' ') {
                      e.preventDefault();
                      setFile(null);
                      setResult(null);
                      setError('');
                    }
                  }}
                >
                  Continue Processing
                </button>
                <button className="btn btn-outline" onClick={() => navigate(`/invoices/${result.invoice_id}`)}>
                  View Full Details
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default UploadInvoice;
