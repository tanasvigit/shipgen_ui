"""Core IAM: roles, permissions, policies
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "0003_iam_rbac"
down_revision: Union[str, None] = "0002_fleetops_core"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "permissions",
        sa.Column("id", sa.String(length=36), primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("guard_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index(
        "permissions_name_guard_name_unique",
        "permissions",
        ["name", "guard_name"],
        unique=True,
    )

    op.create_table(
        "roles",
        sa.Column("id", sa.String(length=36), primary_key=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("guard_name", sa.String(length=255), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )
    op.create_index(
        "roles_name_guard_name_unique",
        "roles",
        ["name", "guard_name"],
        unique=True,
    )

    op.create_table(
        "model_has_permissions",
        sa.Column("permission_id", sa.String(length=36), nullable=False),
        sa.Column("model_type", sa.String(length=255), nullable=False),
        sa.Column("model_uuid", sa.String(length=36), nullable=False),
    )
    op.create_index(
        "model_has_permissions_model_uuid_model_type_index",
        "model_has_permissions",
        ["model_uuid", "model_type"],
    )

    op.create_table(
        "model_has_roles",
        sa.Column("role_id", sa.String(length=36), nullable=False),
        sa.Column("model_type", sa.String(length=255), nullable=False),
        sa.Column("model_uuid", sa.String(length=36), nullable=False),
    )
    op.create_index(
        "model_has_roles_model_uuid_model_type_index",
        "model_has_roles",
        ["model_uuid", "model_type"],
    )

    op.create_table(
        "role_has_permissions",
        sa.Column("permission_id", sa.String(length=36), nullable=False),
        sa.Column("role_id", sa.String(length=36), nullable=False),
    )

    op.create_table(
        "policies",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("_key", sa.String(length=255), nullable=True),
        sa.Column("company_uuid", sa.String(length=36), nullable=True, index=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("guard_name", sa.String(length=255), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("deleted_at", sa.DateTime, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=True),
        sa.Column("updated_at", sa.DateTime, nullable=True),
    )

    op.create_table(
        "model_has_policies",
        sa.Column("policy_id", sa.String(length=36), nullable=False),
        sa.Column("model_type", sa.String(length=255), nullable=False),
        sa.Column("model_uuid", sa.String(length=36), nullable=False),
    )
    op.create_index(
        "model_has_policies_model_uuid_model_type_index",
        "model_has_policies",
        ["model_uuid", "model_type"],
    )


def downgrade() -> None:
    op.drop_table("model_has_policies")
    op.drop_table("policies")
    op.drop_table("role_has_permissions")
    op.drop_table("model_has_roles")
    op.drop_table("model_has_permissions")
    op.drop_table("roles")
    op.drop_table("permissions")



