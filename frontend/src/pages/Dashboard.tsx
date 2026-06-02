import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { FileText, CheckCircle, AlertTriangle, Clock, Layers } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [ocrMetrics, setOcrMetrics] = useState<any>(null);
  const [recent, setRecent] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchDashboard = async () => {
      try {
        const [sumRes, ocrRes, recRes] = await Promise.all([
          apiClient.get('/dashboard/summary'),
          apiClient.get('/dashboard/ocr-metrics'),
          apiClient.get('/dashboard/recent-activity')
        ]);
        setSummary(sumRes.data);
        setOcrMetrics(ocrRes.data);
        setRecent(recRes.data);
      } catch (err) {
        console.error("Failed to load dashboard", err);
      } finally {
        setLoading(false);
      }
    };
    fetchDashboard();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Dashboard Overview</h1>
      </div>

      {/* KPI Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '1rem', background: 'var(--color-info)', color: 'white', borderRadius: 'var(--radius-lg)' }}>
            <FileText size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Total Invoices</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{summary?.total_invoices || 0}</div>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '1rem', background: 'var(--color-success)', color: 'white', borderRadius: 'var(--radius-lg)' }}>
            <CheckCircle size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Approved</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{summary?.approved || 0}</div>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '1rem', background: 'var(--color-warning)', color: 'white', borderRadius: 'var(--radius-lg)' }}>
            <Clock size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Pending Approval</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{summary?.pending_approval || 0}</div>
          </div>
        </div>
        
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <div style={{ padding: '1rem', background: 'var(--color-danger)', color: 'white', borderRadius: 'var(--radius-lg)' }}>
            <AlertTriangle size={24} />
          </div>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Validation Failed</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>{summary?.validation_failed || 0}</div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Layers size={20} className="text-primary" />
            OCR Performance
          </h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Average Confidence</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{((ocrMetrics?.avg_ocr_confidence || 0) * 100).toFixed(1)}%</div>
            </div>
            <div>
              <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Validation Success Rate</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{(ocrMetrics?.validation_success_rate || 0).toFixed(1)}%</div>
            </div>
            <div>
              <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.25rem' }}>Total Processed</div>
              <div style={{ fontSize: '1.25rem', fontWeight: 600 }}>{ocrMetrics?.total_processed || 0}</div>
            </div>
          </div>
        </div>

        <div className="card">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1rem' }}>Recent Activity</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem', maxHeight: '300px', overflowY: 'auto' }}>
            {recent.map((log: any, idx) => (
              <div key={idx} style={{ paddingBottom: '1rem', borderBottom: '1px solid var(--color-border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                  <span style={{ fontWeight: 600, fontSize: '0.875rem' }}>{log.action}</span>
                  <span style={{ fontSize: '0.75rem', color: 'var(--color-text-muted)' }}>
                    {new Date(log.timestamp).toLocaleString()}
                  </span>
                </div>
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>{log.actor} - {log.details}</div>
              </div>
            ))}
            {recent.length === 0 && <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>No recent activity.</div>}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
