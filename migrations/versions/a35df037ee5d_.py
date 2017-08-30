"""empty message

Revision ID: a35df037ee5d
Revises: None
Create Date: 2017-08-26 19:41:35.543000

"""

# revision identifiers, used by Alembic.
revision = 'a35df037ee5d'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('questions', sa.Column('attention_counter', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('questions', 'attention_counter')
    ### end Alembic commands ###
