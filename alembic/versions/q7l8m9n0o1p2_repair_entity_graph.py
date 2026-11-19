"""repair entity graph (data-only revision)

Revision ID: q7l8m9n0o1p2
Revises: p6k7l8m9n0o1
Create Date: 2026-05-29

Phase P6 part 2 of jarvis vision finalization — "위키 그래프 정상화".

What the original revision did:
  1) Promoted entities whose names were session labels (contain '>', '+' or
     'YYYY-MM-DD') to entity_type='episode_topic' (added in p6k7l8m9n0o1), so
     they stop bloating the wiki index.
  2) Restored missing parent_id links by case-insensitive name prefix.
  3) Added Korean / lowercase aliases to a canonical project entity.

Public copy note: every step targeted hard-coded workspace and entity IDs of
the author's own database. Those IDs are removed here, so this revision is a
no-op that only keeps the Alembic chain intact.
"""

from typing import Sequence, Union

revision: str = "q7l8m9n0o1p2"
down_revision: Union[str, Sequence[str], None] = "p6k7l8m9n0o1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
