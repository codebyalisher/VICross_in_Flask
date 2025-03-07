"""new filed_id added

Revision ID: 9cfb347a946e
Revises: f29ed64cfbcb
Create Date: 2025-03-07 09:39:15.774305

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9cfb347a946e'
down_revision = 'f29ed64cfbcb'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_file_id', sa.String(length=100), nullable=True))
        batch_op.add_column(sa.Column('background_image_file_id', sa.String(length=100), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.drop_column('background_image_file_id')
        batch_op.drop_column('image_file_id')

    # ### end Alembic commands ###
