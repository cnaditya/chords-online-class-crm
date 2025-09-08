"""Update student model with country codes

Revision ID: 002
Revises: 001
Create Date: 2024-01-01 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add new columns
    op.add_column('students', sa.Column('country_code', sa.String(length=5), nullable=False, server_default='+91'))
    op.add_column('students', sa.Column('parent1_country_code', sa.String(length=5), nullable=True))
    op.add_column('students', sa.Column('parent1_phone', sa.String(length=15), nullable=True))
    op.add_column('students', sa.Column('parent2_country_code', sa.String(length=5), nullable=True))
    op.add_column('students', sa.Column('parent2_phone', sa.String(length=15), nullable=True))
    
    # Drop old columns
    op.drop_column('students', 'whatsapp_number')
    op.drop_column('students', 'emergency_contact')
    op.drop_column('students', 'emergency_phone')


def downgrade() -> None:
    # Add back old columns
    op.add_column('students', sa.Column('whatsapp_number', sa.String(length=15), nullable=True))
    op.add_column('students', sa.Column('emergency_contact', sa.String(length=100), nullable=True))
    op.add_column('students', sa.Column('emergency_phone', sa.String(length=15), nullable=True))
    
    # Drop new columns
    op.drop_column('students', 'parent2_phone')
    op.drop_column('students', 'parent2_country_code')
    op.drop_column('students', 'parent1_phone')
    op.drop_column('students', 'parent1_country_code')
    op.drop_column('students', 'country_code')