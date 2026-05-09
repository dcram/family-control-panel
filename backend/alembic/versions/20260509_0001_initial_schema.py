"""Schéma initial — toutes les tables + seed

Revision ID: 0001
Revises:
Create Date: 2026-05-09

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "parents",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("login", sa.String(100), nullable=False),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("login"),
    )
    op.create_table(
        "children",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("first_name", sa.String(100), nullable=False),
        sa.Column("date_of_birth", sa.Date, nullable=False),
        sa.Column("color", sa.String(20), nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False, server_default=sa.text("0")),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "kiosk_pins",
        sa.Column("pin", sa.CHAR(4), nullable=False),
        sa.Column("holder_type", sa.String(10), nullable=False),
        sa.Column("holder_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("pin"),
        sa.UniqueConstraint("holder_type", "holder_id", name="uq_kiosk_pins_holder"),
        sa.CheckConstraint("holder_type IN ('parent', 'child')", name="ck_kiosk_pins_holder_type"),
    )
    op.create_table(
        "moments",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("label", sa.String(20), nullable=False),
        sa.Column("start_time", sa.Time, nullable=False),
        sa.Column("end_time", sa.Time, nullable=False),
        sa.Column("sort_order", sa.Integer, nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "tasks",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("emoji", sa.String(10), nullable=True),
        sa.Column("min_age", sa.Integer, nullable=False, server_default=sa.text("4")),
        sa.Column("duration_minutes", sa.Integer, nullable=False),
        sa.Column("archived_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "assignments",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("task_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("child_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("moment_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("day_of_week", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["task_id"], ["tasks.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["child_id"], ["children.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["moment_id"], ["moments.id"], ondelete="RESTRICT"),
    )
    op.create_table(
        "task_instances",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("assignment_id", sa.Uuid(as_uuid=True), nullable=True),
        sa.Column("week_start", sa.Date, nullable=False),
        sa.Column("instance_date", sa.Date, nullable=False),
        sa.Column("state", sa.String(20), nullable=False, server_default=sa.text("'assigned'")),
        sa.Column("declared_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("state_changed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("task_label", sa.String(200), nullable=False),
        sa.Column("task_emoji", sa.String(10), nullable=True),
        sa.Column("task_duration_minutes", sa.Integer, nullable=False),
        sa.Column("child_first_name", sa.String(100), nullable=False),
        sa.Column("child_color", sa.String(20), nullable=False),
        sa.Column("moment_label", sa.String(20), nullable=False),
        sa.Column("day_of_week", sa.Integer, nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["assignment_id"], ["assignments.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("assignment_id", "week_start", name="uq_task_instances_assignment_week"),
    )
    op.create_table(
        "validations",
        sa.Column("id", sa.Uuid(as_uuid=True), nullable=False, server_default=sa.text("gen_random_uuid()")),
        sa.Column("instance_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("parent_id", sa.Uuid(as_uuid=True), nullable=False),
        sa.Column("target_state", sa.String(20), nullable=False),
        sa.Column("reason", sa.String(20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("instance_id"),
        sa.ForeignKeyConstraint(["instance_id"], ["task_instances.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["parents.id"]),
    )
    op.create_table(
        "kiosk_config",
        sa.Column("id", sa.Integer, nullable=False, server_default=sa.text("1")),
        sa.Column("weather_city", sa.String(100), server_default=sa.text("'Paris'")),
        sa.Column("quote_text", sa.Text, nullable=True),
        sa.Column("quote_author", sa.String(200), nullable=True),
        sa.Column("quote_work", sa.String(200), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint("id = 1", name="single_row"),
    )

    # Seed : moments par défaut + config kiosque vide
    op.execute(
        sa.text(
            "INSERT INTO moments (label, start_time, end_time, sort_order) VALUES"
            " ('matin', '07:00', '12:00', 0),"
            " ('midi',  '12:00', '14:00', 1),"
            " ('soir',  '18:00', '21:00', 2)"
        )
    )
    op.execute(sa.text("INSERT INTO kiosk_config (id) VALUES (1)"))


def downgrade() -> None:
    op.drop_table("kiosk_config")
    op.drop_table("validations")
    op.drop_table("task_instances")
    op.drop_table("assignments")
    op.drop_table("tasks")
    op.drop_table("moments")
    op.drop_table("kiosk_pins")
    op.drop_table("children")
    op.drop_table("parents")
