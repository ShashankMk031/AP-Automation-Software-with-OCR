# Known Limitations & Roadmap

This document outlines the verified limitations of the current Accounts Payable Automation system and defines the future feature roadmap.

## Current Limitations

The following limitations have been verified against the current MVP implementation:

* **Email Ingestion:** The system does not currently monitor an IMAP inbox to automatically ingest invoices. Invoices must be manually uploaded via the web UI.
* **Bulk Upload:** The `UploadInvoice` frontend component and the underlying API only support single-file processing. Batch processing of ZIP files or multiple PDFs is not supported.
* **Approval Matrix Configuration:** The system employs a linear, single-tier approval queue. Complex multi-tier routing (e.g., routing to the IT department for hardware invoices and the Marketing department for ad-spend invoices) does not exist.
* **Escalation Workflows:** Invoices sitting in the `PENDING_APPROVAL` queue indefinitely will not automatically escalate to a higher-level manager.
* **Reminder Notifications:** The system does not currently send email or push notifications alerting approvers of pending invoices.
* **Parallel Approvals:** Approvals cannot be executed concurrently by multiple departments; it relies on a single `APPROVER` role action.
* **External GST Verification:** While GSTIN formats are validated using regular expressions, the system does not ping external government tax APIs to verify the GSTIN is active and corresponds to the vendor name.
* **Payment Processing:** There is no `payments` table or payment request logic.
* **Banking Integration:** The system cannot automatically disburse funds via Stripe Treasury, RazorpayX, or generate ISO 20022 / NACHA batch files. The invoice lifecycle natively ends at `APPROVED`.
* **Vendor-wise Analytics:** The dashboard lacks granular UI visualizations (charts/graphs) detailing the total spend volume per vendor.
* **Single Approval Role:** The workflow currently supports a single APPROVER role. Department-specific approvers (Procurement, Finance Manager, CFO, etc.) are not implemented.
* **Enterprise Security Features:** Features such as Single Sign-On (SSO), Multi-Factor Authentication (MFA), audit retention policies, and secrets management integrations are not currently implemented.
* **PO Matching UI State:** The underlying PO Matching engine functions correctly and produces accurate matching results.A known frontend issue exists where the previously displayed matching result may remain visible after changing the selected Purchase Order until a new match operation is executed or the page is refreshed. This issue affects presentation only and does not impact matching calculations, audit logs, or workflow decisions.

## Verified Implemented Features

The following capabilities are fully operational in the current release:

- Invoice Upload (PDF, PNG, JPG, JPEG)
- AI-Based OCR Extraction
- Multi-page Invoice Processing
- Invoice Validation Engine
- Duplicate Detection
- GST Validation
- Vendor Validation
- 2-Way PO Matching
- 3-Way PO Matching
- Role-Based Access Control (RBAC)
- Approval / Rejection Workflow
- Audit Logging
- Dashboard Metrics
- Invoice Status Reporting
- Vendor Management

## Technical Constraints

* **OCR Provider Rate Limits:** The system supports Gemini as the primary OCR provider and Mistral OCR as a fallback provider. API quotas, rate limits, or service outages may temporarily affect extraction throughput. for data extraction. Heavy concurrent usage may result in `429 Too Many Requests` errors depending on the configured API quota. 
* **External API Dependencies:** The extraction pipeline depends on external AI providers. Extended outages affecting all configured OCR providers would temporarily prevent new document processing.
* **OCR Confidence Tracking:** The AI integration currently hardcodes the `ocr_confidence` metric to `0.95`. This results in the Dashboard artificially displaying a 95% AI accuracy rate, masking true LLM hallucinations.
* **Reporting Performance:** Dashboard KPIs and AP Aging reports dynamically calculate metrics via `GROUP BY` SQL aggregations on the live transactional ledger. At scale, this will induce database locking and severe application latency.
* **Demo Data Assumptions:** The `seed_demo_data.py` script makes structural assumptions about Date formats and Vendor names that may not perfectly align with complex real-world edge cases.
* **Reporting Scenario:** Reporting functionality is currently designed for demonstration and educational workloads. Additional testing and optimization would be required before deployment against large production datasets.

## Future Roadmap

* **Payment Processing Module:** Introduce a `payments` database schema, add `PROCESSING_PAYMENT` and `PAID` statuses to the `InvoiceStatus` enum, and build a feature to generate ERP-compatible batch payment files.
* **Tax Reporting Extract:** Build a dedicated `/reports/gst` endpoint that groups `gst_amount` by `vendor.gstin` for a specific calendar month, allowing the finance team to easily file their Input Tax Credit (ITC) returns.
* **True OCR Confidence Scoring:** Implement a probabilistic scoring mechanism inside the AI extraction layer to accurately report extraction confidence to the Dashboard.

* **Read-Replica Database Routing:** Refactor the SQLAlchemy session injection for all `/reports` and `/dashboard` endpoints to target a read-only database replica or a materialized view.
* **Email & Notification Engine:** Implement Celery background tasks combined with SendGrid to send daily "Pending Approval" reminder digests to managers.
* **Dynamic Approval Matrix:** Build an admin UI allowing the Finance team to configure threshold-based routing (e.g., invoices > ₹10,000 require CFO approval).

* **Direct Banking API Integrations:** Connect the system directly to a corporate banking API (like Stripe Treasury) to disburse funds automatically upon approval, and trigger a PDF "Payment Advice" receipt to the vendor.
* **Automated Inbox Ingestion:** Implement an IMAP listener that scrapes a dedicated `invoices@company.com` inbox and pipes the attachments directly into the OCR engine.
