"""aggiunta tabella ordine

Revision ID: 9aaa8931772f
Revises: 03913512c212
Create Date: 2025-01-25 17:06:13.761256

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9aaa8931772f'
down_revision = '03913512c212'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ordine',
    sa.Column('id_ordine', sa.Integer(), nullable=False),
    sa.Column('id_utente', sa.Integer(), nullable=False),
    sa.Column('id_proiezione', sa.Integer(), nullable=False),
    sa.Column('data_acquisto', sa.DateTime(), nullable=False),
    sa.Column('totale', sa.Numeric(precision=10, scale=2), nullable=False),
    sa.ForeignKeyConstraint(['id_proiezione'], ['proiezione.id_proiezione'], ),
    sa.ForeignKeyConstraint(['id_utente'], ['utente.id_utente'], ),
    sa.PrimaryKeyConstraint('id_ordine')
    )
    with op.batch_alter_table('ordine', schema=None) as batch_op:
        batch_op.create_index('idx_ordine_proiezione', ['id_proiezione'], unique=False)
        batch_op.create_index('idx_ordine_utente', ['id_utente'], unique=False)

    with op.batch_alter_table('biglietto', schema=None) as batch_op:
        batch_op.add_column(sa.Column('id_ordine', sa.Integer(), nullable=False))
        batch_op.create_index('idx_biglietto_proiezione', ['id_proiezione'], unique=False)
        batch_op.create_index('idx_biglietto_utente', ['id_utente'], unique=False)
        batch_op.create_foreign_key(None, 'ordine', ['id_ordine'], ['id_ordine'])

    with op.batch_alter_table('film', schema=None) as batch_op:
        batch_op.create_index('idx_film_titolo', ['titolo'], unique=False)

    with op.batch_alter_table('posto', schema=None) as batch_op:
        batch_op.create_index('idx_posto_sala', ['id_sala'], unique=False)
        batch_op.create_unique_constraint('uq_sala_fila_numero', ['id_sala', 'fila', 'numero'])

    with op.batch_alter_table('proiezione', schema=None) as batch_op:
        batch_op.alter_column('costo',
               existing_type=sa.INTEGER(),
               type_=sa.Numeric(precision=10, scale=2),
               existing_nullable=False)
        batch_op.create_index('idx_proiezione_data', ['data_ora'], unique=False)
        batch_op.create_index('idx_proiezione_film_sala', ['id_film', 'id_sala'], unique=False)

    with op.batch_alter_table('utente', schema=None) as batch_op:
        batch_op.create_index('idx_user_email', ['email'], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('utente', schema=None) as batch_op:
        batch_op.drop_index('idx_user_email')

    with op.batch_alter_table('proiezione', schema=None) as batch_op:
        batch_op.drop_index('idx_proiezione_film_sala')
        batch_op.drop_index('idx_proiezione_data')
        batch_op.alter_column('costo',
               existing_type=sa.Numeric(precision=10, scale=2),
               type_=sa.INTEGER(),
               existing_nullable=False)

    with op.batch_alter_table('posto', schema=None) as batch_op:
        batch_op.drop_constraint('uq_sala_fila_numero', type_='unique')
        batch_op.drop_index('idx_posto_sala')

    with op.batch_alter_table('film', schema=None) as batch_op:
        batch_op.drop_index('idx_film_titolo')

    with op.batch_alter_table('biglietto', schema=None) as batch_op:
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_index('idx_biglietto_utente')
        batch_op.drop_index('idx_biglietto_proiezione')
        batch_op.drop_column('id_ordine')

    with op.batch_alter_table('ordine', schema=None) as batch_op:
        batch_op.drop_index('idx_ordine_utente')
        batch_op.drop_index('idx_ordine_proiezione')

    op.drop_table('ordine')
    # ### end Alembic commands ###
