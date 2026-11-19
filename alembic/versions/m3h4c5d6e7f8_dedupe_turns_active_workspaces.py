"""dedupe duplicate turns

Revision ID: m3h4c5d6e7f8
Revises: l2g3b4c5d6e7
Create Date: 2026-05-29

Phase P5 of jarvis vision finalization.

Background:
  Repeated re-ingest of the same Claude Code session (different chunk sizes,
  classifier reruns, append v1/v2 policy) created identical (episode_id, role,
  text) rows in `turns`. In the original deployment this removed 5,793
  duplicate rows.

Strategy:
  PARTITION BY (episode_id, role, text), keep the row with the lowest sequence
  (earliest insertion / canonical order). Delete the rest.

  Public copy note: the original revision was scoped to the workspace IDs of
  the author's own database. Here it runs over every workspace, which is a
  no-op on a fresh install.

  Idempotent: re-running it after the dedupe produces a no-op DELETE.
  The downgrade is intentionally a no-op: deleted rows cannot be restored,
  and there is no schema change to revert.
"""

from typing import Sequence, Union

from alembic import op

revision: str = "m3h4c5d6e7f8"
down_revision: Union[str, Sequence[str], None] = "l2g3b4c5d6e7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        """
        WITH ranked AS (
            SELECT id,
                   ROW_NUMBER() OVER (
                       PARTITION BY episode_id, role, text
                       ORDER BY sequence ASC, id ASC
                   ) AS rn
            FROM turns
        )
        DELETE FROM turns
        WHERE id IN (SELECT id FROM ranked WHERE rn > 1);
        """
    )


def downgrade() -> None:
    # Cannot restore deleted rows; no schema changes to revert.
    pass
