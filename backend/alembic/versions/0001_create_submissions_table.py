from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '0001'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    op.create_table(
        'submissions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('email', sa.String(255), nullable=False),
        sa.Column('phone_number', sa.String(20), nullable=False),
        sa.Column('age', sa.Integer, nullable=False),
        sa.Column('address', sa.Text),
        sa.Column('preferred_contact', sa.String(20), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.TIMESTAMP, server_default=sa.func.now(), nullable=False),
        sa.CheckConstraint('age >= 18 AND age <= 120', name='age_range'),
        sa.CheckConstraint("preferred_contact IN ('Email', 'Phone', 'Both')", name='preferred_contact_check'),
    )

def downgrade():
    op.drop_table('submissions') 