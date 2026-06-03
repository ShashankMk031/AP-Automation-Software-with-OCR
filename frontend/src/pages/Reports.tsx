import React, { useEffect, useState } from 'react';
import apiClient from '../api/client';
import { BarChart, PieChart, CheckSquare, AlertTriangle } from 'lucide-react';

const Reports: React.FC = () => {
  const [invoiceStatusReport, setInvoiceStatusReport] = useState<any[]>([]);
  const [vendorReport, setVendorReport] = useState<any[]>([]);
  const [approvalReport, setApprovalReport] = useState<any>(null);
  const [apAgingReport, setApAgingReport] = useState<any>(null);
  const [exceptionReport, setExceptionReport] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchReports = async () => {
      try {
        const [statusRes, vendorRes, approvalRes, apAgingRes, exceptionsRes] = await Promise.all([
          apiClient.get('/reports/invoice-status'),
          apiClient.get('/reports/vendor-report'),
          apiClient.get('/reports/approval-report'),
          apiClient.get('/reports/ap-aging'),
          apiClient.get('/reports/exceptions')
        ]);
        
        setInvoiceStatusReport(statusRes.data);
        setVendorReport(vendorRes.data);
        setApprovalReport(approvalRes.data);
        setApAgingReport(apAgingRes.data);
        setExceptionReport(exceptionsRes.data);
      } catch (err) {
        console.error("Failed to load reports", err);
      } finally {
        setLoading(false);
      }
    };
    fetchReports();
  }, []);

  if (loading) return <div style={{ padding: '2rem' }}>Loading reports...</div>;

  return (
    <div>
      <div className="page-header">
        <h1 className="page-title">Reporting & Analytics</h1>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '1.5rem', marginBottom: '2rem' }}>
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', borderLeft: '4px solid var(--color-primary)' }}>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Total Documents</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
              {invoiceStatusReport.reduce((acc, curr) => acc + curr.count, 0)}
            </div>
          </div>
        </div>
        
        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', borderLeft: '4px solid var(--color-info)' }}>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Active Vendors</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700 }}>
              {vendorReport.length}
            </div>
          </div>
        </div>

        <div className="card" style={{ display: 'flex', alignItems: 'center', gap: '1rem', borderLeft: '4px solid var(--color-success)' }}>
          <div>
            <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)' }}>Total Approvals</div>
            <div style={{ fontSize: '1.5rem', fontWeight: 700, color: 'var(--color-success)' }}>
              {approvalReport?.total_approved || 0}
            </div>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
        
        <div className="card">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <PieChart size={20} className="text-primary" />
            Invoice Status Distribution
          </h2>
          <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>Status</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {invoiceStatusReport.map((stat, i) => (
                  <tr key={i}>
                    <td>
                      <span className="badge badge-default">
                        {stat.status}
                      </span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{stat.count}</td>
                  </tr>
                ))}
                {invoiceStatusReport.length === 0 && (
                  <tr><td colSpan={2}>No data available</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="card">
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <CheckSquare size={20} className="text-primary" />
            Approval Summary
          </h2>
          {approvalReport && (
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div style={{ padding: '1.5rem', background: 'var(--color-bg-base)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>Total Approved</div>
                <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-success)' }}>{approvalReport.total_approved}</div>
              </div>
              <div style={{ padding: '1.5rem', background: 'var(--color-bg-base)', borderRadius: 'var(--radius-md)', textAlign: 'center' }}>
                <div style={{ fontSize: '0.875rem', color: 'var(--color-text-muted)', marginBottom: '0.5rem' }}>Total Rejected</div>
                <div style={{ fontSize: '2rem', fontWeight: 700, color: 'var(--color-danger)' }}>{approvalReport.total_rejected}</div>
              </div>
            </div>
          )}
        </div>
      </div>

      {apAgingReport && (
        <div className="card" style={{ marginBottom: '2rem' }}>
          <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <BarChart size={20} className="text-primary" />
            Accounts Payable Aging
          </h2>
          <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
            <table>
              <thead>
                <tr>
                  <th>Aging Bucket</th>
                  <th>Invoice Count</th>
                  <th>Percentage</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>0 - 30 Days</td>
                  <td>{apAgingReport.days_0_30}</td>
                  <td>{apAgingReport.total ? Math.round((apAgingReport.days_0_30 / apAgingReport.total) * 100) : 0}%</td>
                </tr>
                <tr>
                  <td>31 - 60 Days</td>
                  <td>{apAgingReport.days_31_60}</td>
                  <td>{apAgingReport.total ? Math.round((apAgingReport.days_31_60 / apAgingReport.total) * 100) : 0}%</td>
                </tr>
                <tr>
                  <td>61 - 90 Days</td>
                  <td>{apAgingReport.days_61_90}</td>
                  <td>{apAgingReport.total ? Math.round((apAgingReport.days_61_90 / apAgingReport.total) * 100) : 0}%</td>
                </tr>
                <tr>
                  <td>90+ Days</td>
                  <td>{apAgingReport.days_90_plus}</td>
                  <td>{apAgingReport.total ? Math.round((apAgingReport.days_90_plus / apAgingReport.total) * 100) : 0}%</td>
                </tr>
                <tr style={{ fontWeight: 700, background: 'var(--color-bg-base)' }}>
                  <td>Total Open Invoices</td>
                  <td>{apAgingReport.total}</td>
                  <td>100%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      )}

      <div className="card">
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <BarChart size={20} className="text-primary" />
          Vendor Processing Report
        </h2>
        <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
          <table>
            <thead>
              <tr>
                <th>Vendor Name</th>
                <th>Total Invoices</th>
                <th>Approved</th>
                <th>Rejected</th>
              </tr>
            </thead>
            <tbody>
              {vendorReport.map((v, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 500 }}>{v.vendor_name}</td>
                  <td>{v.total_invoices}</td>
                  <td><span className="text-success">{v.approved_count}</span></td>
                  <td><span className="text-danger">{v.rejected_count}</span></td>
                </tr>
              ))}
              {vendorReport.length === 0 && (
                <tr><td colSpan={4}>No vendor data available</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
      <div className="card" style={{ marginTop: '2rem' }}>
        <h2 style={{ fontSize: '1.125rem', fontWeight: 600, marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
          <AlertTriangle size={20} className="text-danger" />
          Exception Report
        </h2>
        <div className="table-container" style={{ border: 'none', boxShadow: 'none' }}>
          <table>
            <thead>
              <tr>
                <th>Invoice #</th>
                <th>Vendor</th>
                <th>Status</th>
                <th>Date</th>
                <th>Reason / Comments</th>
              </tr>
            </thead>
            <tbody>
              {exceptionReport.map((ex, i) => (
                <tr key={i}>
                  <td style={{ fontWeight: 500 }}>{ex.invoice_number}</td>
                  <td>{ex.vendor_name}</td>
                  <td>
                    <span className={`badge ${ex.status === 'REJECTED' ? 'badge-danger' : 'badge-warning'}`}>
                      {ex.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td>{ex.date ? new Date(ex.date).toLocaleDateString() : 'N/A'}</td>
                  <td>
                    {ex.status === 'VALIDATION_FAILED' && ex.failure_reason && (
                      <span className="text-warning">{ex.failure_reason}</span>
                    )}
                    {ex.status === 'REJECTED' && ex.rejection_comments && (
                      <span className="text-danger">Rejected: {ex.rejection_comments}</span>
                    )}
                    {!ex.failure_reason && !ex.rejection_comments && (
                      <span className="text-muted">No details available</span>
                    )}
                  </td>
                </tr>
              ))}
              {exceptionReport.length === 0 && (
                <tr><td colSpan={5}>No exceptions found</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
      
    </div>
  );
};

export default Reports;
