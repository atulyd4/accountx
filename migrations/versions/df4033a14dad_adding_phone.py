"""adding phone.

Revision ID: df4033a14dad
Revises: 
Create Date: 2021-11-07 13:48:39.941640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'df4033a14dad'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('accounts', sa.Column('phone', sa.String(length=20), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('accounts', 'phone')
    # ### end Alembic commands ###
