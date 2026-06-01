"""harden_schema_and_add_enums

Revision ID: d50ac960b950
Revises: f9bb395670a5
Create Date: 2026-06-01 19:39:43.315563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd50ac960b950'
down_revision: Union[str, None] = 'f9bb395670a5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create Enums manually in Postgres
    userrole_enum = postgresql.ENUM('ADMIN', 'APPROVER', 'FINANCE', name='userrole')
    userrole_enum.create(op.get_bind(), checkfirst=True)

    vendorstatus_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', name='vendorstatus')
    vendorstatus_enum.create(op.get_bind(), checkfirst=True)

    invoicestatus_enum = postgresql.ENUM('UPLOADED', 'EXTRACTED', 'VALIDATION_PASSED', 'VALIDATION_FAILED', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', name='invoicestatus')
    invoicestatus_enum.create(op.get_bind(), checkfirst=True)

    purchaseorderstatus_enum = postgresql.ENUM('OPEN', 'MATCHED', 'CLOSED', name='purchaseorderstatus')
    purchaseorderstatus_enum.create(op.get_bind(), checkfirst=True)

    # 2. Add columns with defaults that don't depend on enum status casts first
    op.add_column('approval_workflows', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('approval_workflows', 'invoice_id', existing_type=sa.INTEGER(), nullable=False)
    
    op.add_column('audit_logs', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('audit_logs', 'invoice_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('audit_logs', 'timestamp', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=False, existing_server_default=sa.text('now()'))
    
    op.add_column('grns', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('grns', 'grn_number', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('grns', 'po_id', existing_type=sa.INTEGER(), nullable=False)
    
    op.add_column('invoice_line_items', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('invoice_line_items', 'invoice_id', existing_type=sa.INTEGER(), nullable=False)
    
    op.add_column('invoices', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('invoices', 'vendor_id', existing_type=sa.INTEGER(), nullable=False)
    op.alter_column('invoices', 'invoice_number', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('invoices', 'invoice_date', existing_type=postgresql.TIMESTAMP(), type_=sa.DateTime(timezone=True), existing_nullable=True)
    op.alter_column('invoices', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=False, existing_server_default=sa.text('now()'))
    op.create_unique_constraint('uq_invoice_vendor_number', 'invoices', ['vendor_id', 'invoice_number'])
    
    op.add_column('purchase_orders', sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.add_column('purchase_orders', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('purchase_orders', 'po_number', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('purchase_orders', 'vendor_id', existing_type=sa.INTEGER(), nullable=False)
    
    op.alter_column('users', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=False, existing_server_default=sa.text('now()'))
    
    op.add_column('vendors', sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False))
    op.alter_column('vendors', 'gstin', existing_type=sa.VARCHAR(), nullable=False)
    op.alter_column('vendors', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=False, existing_server_default=sa.text('now()'))

    # 3. Map values and Cast status fields to Enums using USING cast
    # Users
    op.execute("UPDATE users SET role = 'ADMIN' WHERE role = 'admin'")
    op.execute("UPDATE users SET role = 'APPROVER' WHERE role IN ('approver', 'user')")
    op.execute("UPDATE users SET role = 'FINANCE' WHERE role = 'finance'")
    op.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")
    op.alter_column('users', 'role', nullable=False)

    # Vendors
    op.execute("UPDATE vendors SET status = 'ACTIVE' WHERE status = 'active'")
    op.execute("UPDATE vendors SET status = 'INACTIVE' WHERE status = 'inactive'")
    op.execute("ALTER TABLE vendors ALTER COLUMN status TYPE vendorstatus USING status::vendorstatus")
    op.alter_column('vendors', 'status', nullable=False)

    # Purchase Orders
    op.execute("UPDATE purchase_orders SET status = 'OPEN' WHERE status = 'active'")
    op.execute("UPDATE purchase_orders SET status = 'CLOSED' WHERE status = 'closed'")
    op.execute("ALTER TABLE purchase_orders ALTER COLUMN status TYPE purchaseorderstatus USING status::purchaseorderstatus")
    op.alter_column('purchase_orders', 'status', nullable=False)

    # Invoices
    op.execute("UPDATE invoices SET status = 'PENDING_APPROVAL' WHERE status = 'pending'")
    op.execute("UPDATE invoices SET status = 'APPROVED' WHERE status = 'approved'")
    op.execute("UPDATE invoices SET status = 'REJECTED' WHERE status = 'rejected'")
    op.execute("ALTER TABLE invoices ALTER COLUMN status TYPE invoicestatus USING status::invoicestatus")
    op.alter_column('invoices', 'status', nullable=False)

    # Approval Workflows
    op.execute("UPDATE approval_workflows SET status = 'PENDING_APPROVAL' WHERE status = 'pending'")
    op.execute("UPDATE approval_workflows SET status = 'APPROVED' WHERE status = 'approved'")
    op.execute("UPDATE approval_workflows SET status = 'REJECTED' WHERE status = 'rejected'")
    op.execute("ALTER TABLE approval_workflows ALTER COLUMN status TYPE invoicestatus USING status::invoicestatus")
    op.alter_column('approval_workflows', 'status', nullable=False)


def downgrade() -> None:
    # Downgrade enum columns back to VARCHAR
    op.alter_column('vendors', 'status', existing_type=sa.Enum('ACTIVE', 'INACTIVE', name='vendorstatus'), type_=sa.VARCHAR(), nullable=True)
    op.alter_column('users', 'role', existing_type=sa.Enum('ADMIN', 'APPROVER', 'FINANCE', name='userrole'), type_=sa.VARCHAR(), nullable=True)
    op.alter_column('purchase_orders', 'status', existing_type=sa.Enum('OPEN', 'MATCHED', 'CLOSED', name='purchaseorderstatus'), type_=sa.VARCHAR(), nullable=True)
    op.alter_column('invoices', 'status', existing_type=sa.Enum('UPLOADED', 'EXTRACTED', 'VALIDATION_PASSED', 'VALIDATION_FAILED', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', name='invoicestatus'), type_=sa.VARCHAR(), nullable=True)
    op.alter_column('approval_workflows', 'status', existing_type=sa.Enum('UPLOADED', 'EXTRACTED', 'VALIDATION_PASSED', 'VALIDATION_FAILED', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', name='invoicestatus'), type_=sa.VARCHAR(), nullable=True)

    # Drop enum types
    userrole_enum = postgresql.ENUM('ADMIN', 'APPROVER', 'FINANCE', name='userrole')
    userrole_enum.drop(op.get_bind(), checkfirst=True)

    vendorstatus_enum = postgresql.ENUM('ACTIVE', 'INACTIVE', name='vendorstatus')
    vendorstatus_enum.drop(op.get_bind(), checkfirst=True)

    invoicestatus_enum = postgresql.ENUM('UPLOADED', 'EXTRACTED', 'VALIDATION_PASSED', 'VALIDATION_FAILED', 'PENDING_APPROVAL', 'APPROVED', 'REJECTED', name='invoicestatus')
    invoicestatus_enum.drop(op.get_bind(), checkfirst=True)

    purchaseorderstatus_enum = postgresql.ENUM('OPEN', 'MATCHED', 'CLOSED', name='purchaseorderstatus')
    purchaseorderstatus_enum.drop(op.get_bind(), checkfirst=True)

    # Revert columns structure
    op.alter_column('vendors', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=True, existing_server_default=sa.text('now()'))
    op.alter_column('vendors', 'gstin', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column('vendors', 'updated_at')
    
    op.alter_column('users', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=True, existing_server_default=sa.text('now()'))
    
    op.alter_column('purchase_orders', 'vendor_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('purchase_orders', 'po_number', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column('purchase_orders', 'updated_at')
    op.drop_column('purchase_orders', 'created_at')
    
    op.drop_constraint('uq_invoice_vendor_number', 'invoices', type_='unique')
    op.alter_column('invoices', 'created_at', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=True, existing_server_default=sa.text('now()'))
    op.alter_column('invoices', 'invoice_date', existing_type=sa.DateTime(timezone=True), type_=postgresql.TIMESTAMP(), existing_nullable=True)
    op.alter_column('invoices', 'invoice_number', existing_type=sa.VARCHAR(), nullable=True)
    op.alter_column('invoices', 'vendor_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_column('invoices', 'updated_at')
    
    op.alter_column('invoice_line_items', 'invoice_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_column('invoice_line_items', 'created_at')
    
    op.alter_column('grns', 'po_id', existing_type=sa.INTEGER(), nullable=True)
    op.alter_column('grns', 'grn_number', existing_type=sa.VARCHAR(), nullable=True)
    op.drop_column('grns', 'created_at')
    
    op.alter_column('audit_logs', 'timestamp', existing_type=postgresql.TIMESTAMP(timezone=True), nullable=True, existing_server_default=sa.text('now()'))
    op.alter_column('audit_logs', 'invoice_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_column('audit_logs', 'created_at')
    
    op.alter_column('approval_workflows', 'invoice_id', existing_type=sa.INTEGER(), nullable=True)
    op.drop_column('approval_workflows', 'created_at')
