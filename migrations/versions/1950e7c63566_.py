"""empty message

Revision ID: 1950e7c63566
Revises: 
Create Date: 2025-06-26 20:22:07.951201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1950e7c63566'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('subjects',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.Column('school_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teachers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.Column('school_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id'], ['users.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['school_id'], ['schools.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('subject_teacher',
    sa.Column('teacher_id', sa.Integer(), nullable=False),
    sa.Column('subject_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['subject_id'], ['subjects.id'], ),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], ),
    sa.PrimaryKeyConstraint('teacher_id', 'subject_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('subject_teacher')
    op.drop_table('teachers')
    op.drop_table('subjects')
    # ### end Alembic commands ###
