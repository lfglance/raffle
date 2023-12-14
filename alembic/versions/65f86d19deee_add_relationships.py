"""add relationships

Revision ID: 65f86d19deee
Revises: b85e6aecbfdc
Create Date: 2022-11-21 09:38:13.935964

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '65f86d19deee'
down_revision = 'b85e6aecbfdc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('drawingprizes', sa.Column('confirmed_winner_id', sa.Integer(), nullable=True))
    op.add_column('drawingprizes', sa.Column('selected_entry_id', sa.Integer(), nullable=True))
    op.drop_constraint('drawingprizes_selected_entry_fkey', 'drawingprizes', type_='foreignkey')
    op.drop_constraint('drawingprizes_confirmed_winner_fkey', 'drawingprizes', type_='foreignkey')
    op.create_foreign_key(None, 'drawingprizes', 'entries', ['confirmed_winner_id'], ['id'])
    op.create_foreign_key(None, 'drawingprizes', 'entries', ['selected_entry_id'], ['id'])
    op.drop_column('drawingprizes', 'selected_entry')
    op.drop_column('drawingprizes', 'confirmed_winner')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('drawingprizes', sa.Column('confirmed_winner', sa.INTEGER(), autoincrement=False, nullable=True))
    op.add_column('drawingprizes', sa.Column('selected_entry', sa.INTEGER(), autoincrement=False, nullable=True))
    op.drop_constraint(None, 'drawingprizes', type_='foreignkey')
    op.drop_constraint(None, 'drawingprizes', type_='foreignkey')
    op.create_foreign_key('drawingprizes_confirmed_winner_fkey', 'drawingprizes', 'entries', ['confirmed_winner'], ['id'])
    op.create_foreign_key('drawingprizes_selected_entry_fkey', 'drawingprizes', 'entries', ['selected_entry'], ['id'])
    op.drop_column('drawingprizes', 'selected_entry_id')
    op.drop_column('drawingprizes', 'confirmed_winner_id')
    # ### end Alembic commands ###