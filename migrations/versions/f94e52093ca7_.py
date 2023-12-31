"""empty message

Revision ID: f94e52093ca7
Revises: 
Create Date: 2023-12-31 16:57:52.297557

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f94e52093ca7'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.add_column(sa.Column('birthday', sa.String(length=30), nullable=False))
        batch_op.add_column(sa.Column('gender', sa.String(length=50), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('user', schema=None) as batch_op:
        batch_op.drop_column('gender')
        batch_op.drop_column('birthday')

    # ### end Alembic commands ###
