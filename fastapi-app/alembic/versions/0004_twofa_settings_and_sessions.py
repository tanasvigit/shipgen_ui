"""2FA: settings and sessions
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0004_twofa"
down_revision: Union[str, None] = "0003_iam_rbac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "twofa_settings",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("subject_type", sa.String(length=50), nullable=False),  # 'system' | 'user' | 'company'
        sa.Column("subject_uuid", sa.String(length=36), nullable=True),
        sa.Column("enabled", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("method", sa.String(length=50), nullable=False, server_default="email"),
        sa.Column("enforced", sa.Boolean, nullable=False, server_default=sa.text("FALSE")),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index(
        "twofa_settings_subject_type_uuid_unique",
        "twofa_settings",
        ["subject_type", "subject_uuid"],
        unique=True,
    )

    op.create_table(
        "twofa_sessions",
        sa.Column("id", sa.Integer, primary_key=True),
        sa.Column("identity", sa.String(length=255), nullable=False),
        sa.Column("session_token", sa.String(length=255), nullable=False, unique=True),
        sa.Column("client_token", sa.String(length=255), nullable=True),
        sa.Column("code", sa.String(length=10), nullable=True),
        sa.Column("expires_at", sa.DateTime, nullable=True),
        sa.Column("validated_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index("twofa_sessions_identity_index", "twofa_sessions", ["identity"])


def downgrade() -> None:
    op.drop_table("twofa_sessions")
    op.drop_table("twofa_settings")



