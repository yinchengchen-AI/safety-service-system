"""
添加通知公告表

Revision ID: 20260330_0001
Revises: 
Create Date: 2026-03-30 22:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '20260330_0001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级数据库"""
    # 创建公告表
    op.create_table(
        'notices',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False, comment='公告标题'),
        sa.Column('content', sa.Text(), nullable=False, comment='公告内容'),
        sa.Column('summary', sa.String(length=500), nullable=True, comment='摘要'),
        sa.Column('type', sa.String(length=20), nullable=False, server_default='normal', comment='公告类型'),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='draft', comment='公告状态'),
        sa.Column('publish_time', sa.DateTime(), nullable=True, comment='发布时间'),
        sa.Column('expire_time', sa.DateTime(), nullable=True, comment='过期时间'),
        sa.Column('is_top', sa.Boolean(), nullable=False, server_default='false', comment='是否置顶'),
        sa.Column('top_expire_time', sa.DateTime(), nullable=True, comment='置顶过期时间'),
        sa.Column('attachment', sa.String(length=500), nullable=True, comment='附件路径'),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0', comment='浏览次数'),
        sa.Column('publisher_id', sa.BigInteger(), nullable=False, comment='发布人ID'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['publisher_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        comment='公告表'
    )
    op.create_index('ix_notices_status', 'notices', ['status'])
    op.create_index('ix_notices_type', 'notices', ['type'])
    op.create_index('ix_notices_is_top', 'notices', ['is_top'])
    
    # 创建公告阅读状态表
    op.create_table(
        'notice_read_status',
        sa.Column('id', sa.BigInteger(), nullable=False),
        sa.Column('notice_id', sa.BigInteger(), nullable=False, comment='公告ID'),
        sa.Column('user_id', sa.BigInteger(), nullable=False, comment='用户ID'),
        sa.Column('is_read', sa.Boolean(), nullable=False, server_default='false', comment='是否已读'),
        sa.Column('read_time', sa.DateTime(), nullable=True, comment='阅读时间'),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.ForeignKeyConstraint(['notice_id'], ['notices.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        comment='公告阅读状态表'
    )
    op.create_index('ix_notice_read_status_notice_id', 'notice_read_status', ['notice_id'])
    op.create_index('ix_notice_read_status_user_id', 'notice_read_status', ['user_id'])


def downgrade() -> None:
    """降级数据库"""
    op.drop_table('notice_read_status')
    op.drop_table('notices')
