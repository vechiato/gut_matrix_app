"""Add role column to team_user

Revision ID: cd84c550734c
Revises: 6cf92f9ff225
Create Date: 2024-06-01 19:22:01.008427

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'cd84c550734c'
down_revision = '6cf92f9ff225'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team_user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('role', sa.String(length=50), nullable=False, server_default='regular'))

    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('team_user', schema=None) as batch_op:
        batch_op.drop_column('role')

    # ### end Alembic commands ###
