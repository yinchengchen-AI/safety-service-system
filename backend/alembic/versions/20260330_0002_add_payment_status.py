"""
添加收款状态字段

Revision ID: 20260330_0002
Revises: 20260330_0001
Create Date: 2026-03-30 23:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = '20260330_0002'
down_revision: Union[str, None] = '20260330_0001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库"""
    op.add_column(
        'payments',
        sa.Column('status', sa.String(length=20), nullable=False, server_default='confirmed', comment='收款状态')
    )


def downgrade() -> None:
    """降级数据库"""
    op.drop_column('payments', 'status')
