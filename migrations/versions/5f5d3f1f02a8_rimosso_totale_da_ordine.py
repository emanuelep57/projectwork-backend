"""rimosso totale da ordine

Revision ID: 5f5d3f1f02a8
Revises: 9aaa8931772f
Create Date: 2025-01-25 18:17:41.129496

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5f5d3f1f02a8'
down_revision = '9aaa8931772f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ordine', schema=None) as batch_op:
        batch_op.drop_column('totale')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('ordine', schema=None) as batch_op:
        batch_op.add_column(sa.Column('totale', sa.NUMERIC(precision=10, scale=2), autoincrement=False, nullable=False))

    # ### end Alembic commands ###
