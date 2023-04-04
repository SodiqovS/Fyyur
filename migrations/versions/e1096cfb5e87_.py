"""empty message

Revision ID: e1096cfb5e87
Revises: 8bff516a3d7e
Create Date: 2023-04-01 19:10:38.082630

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'e1096cfb5e87'
down_revision = '8bff516a3d7e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('artist_genre',
    sa.Column('artist_id', sa.Integer(), nullable=False),
    sa.Column('genre_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['artist_id'], ['artists.id'], ),
    sa.ForeignKeyConstraint(['genre_id'], ['genres.id'], ),
    sa.PrimaryKeyConstraint('artist_id', 'genre_id')
    )
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('state_id', sa.Integer(), nullable=False))
        batch_op.add_column(sa.Column('website_link', sa.String(length=120), nullable=True))
        batch_op.add_column(sa.Column('seeking_venue', sa.Boolean(), nullable=True))
        batch_op.add_column(sa.Column('seeking_description', sa.Text(), nullable=True))
        batch_op.create_foreign_key(None, 'states', ['state_id'], ['id'])
        batch_op.drop_column('state')
        batch_op.drop_column('genres')

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('artists', schema=None) as batch_op:
        batch_op.add_column(sa.Column('genres', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column('state', sa.VARCHAR(length=120), autoincrement=False, nullable=True))
        batch_op.drop_constraint(None, type_='foreignkey')
        batch_op.drop_column('seeking_description')
        batch_op.drop_column('seeking_venue')
        batch_op.drop_column('website_link')
        batch_op.drop_column('state_id')

    op.drop_table('artist_genre')
    # ### end Alembic commands ###
