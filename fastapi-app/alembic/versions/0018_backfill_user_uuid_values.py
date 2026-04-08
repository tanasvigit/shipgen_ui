"""Backfill missing user uuid/public_id values"""

from typing import Sequence, Union
import uuid as uuidlib

from alembic import op
import sqlalchemy as sa


revision: str = "0018_backfill_user_uuid_values"
down_revision: Union[str, None] = "0017_user_role_rbac"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    users = sa.table(
        "users",
        sa.column("id", sa.Integer),
        sa.column("uuid", sa.String),
        sa.column("public_id", sa.String),
    )

    rows = bind.execute(sa.select(users.c.id, users.c.uuid, users.c.public_id)).fetchall()
    for row in rows:
        updates: dict[str, str] = {}
        if not row.uuid:
            updates["uuid"] = str(uuidlib.uuid4())
        if not row.public_id:
            updates["public_id"] = f"user_{uuidlib.uuid4().hex[:12]}"
        if updates:
            bind.execute(users.update().where(users.c.id == row.id).values(**updates))


def downgrade() -> None:
    # Data backfill is not safely reversible.
    pass
