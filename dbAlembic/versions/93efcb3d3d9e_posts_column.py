"""posts column

Revision ID: 93efcb3d3d9e
Revises: 8b775f0603e6
Create Date: 2024-02-26 18:48:40.139524

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '93efcb3d3d9e'
down_revision: Union[str, None] = '8b775f0603e6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("posts", sa.Column('content', sa.String(), nullable=False))
    pass


def downgrade() -> None:
    op.drop_column("posts","content")
    pass
