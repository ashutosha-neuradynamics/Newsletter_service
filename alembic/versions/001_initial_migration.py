"""Initial migration: create topics, subscribers, subscriptions, and content tables

Revision ID: 001_initial
Revises:
Create Date: 2024-01-01 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "001_initial"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "topics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_topics_id"), "topics", ["id"], unique=False)
    op.create_index(op.f("ix_topics_name"), "topics", ["name"], unique=True)

    op.create_table(
        "subscribers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subscribers_id"), "subscribers", ["id"], unique=False)
    op.create_index(op.f("ix_subscribers_email"), "subscribers", ["email"], unique=True)

    op.create_table(
        "subscriptions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("subscriber_id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["subscriber_id"],
            ["subscribers.id"],
        ),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topics.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_subscriptions_id"), "subscriptions", ["id"], unique=False)

    content_status_enum = postgresql.ENUM(
        "pending", "sent", "failed", "cancelled", name="contentstatus"
    )
    # content_status_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "content",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("topic_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("scheduled_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("status", content_status_enum, nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["topic_id"],
            ["topics.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_content_id"), "content", ["id"], unique=False)
    op.create_index(op.f("ix_content_topic_id"), "content", ["topic_id"], unique=False)
    op.create_index(
        op.f("ix_content_scheduled_at"), "content", ["scheduled_at"], unique=False
    )
    op.create_index(op.f("ix_content_status"), "content", ["status"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_content_status"), table_name="content")
    op.drop_index(op.f("ix_content_scheduled_at"), table_name="content")
    op.drop_index(op.f("ix_content_topic_id"), table_name="content")
    op.drop_index(op.f("ix_content_id"), table_name="content")
    op.drop_table("content")

    op.drop_index(op.f("ix_subscriptions_id"), table_name="subscriptions")
    op.drop_table("subscriptions")

    op.drop_index(op.f("ix_subscribers_email"), table_name="subscribers")
    op.drop_index(op.f("ix_subscribers_id"), table_name="subscribers")
    op.drop_table("subscribers")

    op.drop_index(op.f("ix_topics_name"), table_name="topics")
    op.drop_index(op.f("ix_topics_id"), table_name="topics")
    op.drop_table("topics")

    op.execute("DROP TYPE IF EXISTS contentstatus")
