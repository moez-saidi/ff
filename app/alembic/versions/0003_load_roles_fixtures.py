"""
load_roles_fixtures

Revision ID: 0003
Revises: 0002
Create Date: 2025-01-29 17:02:13.109486

"""

import json
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

from app.models.roles import Role

# revision identifiers, used by Alembic.
revision: str = "0003"
down_revision: str | None = "0002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

roles_fixtures_file_path = "/code/app/fixtures/roles.json"
with open(roles_fixtures_file_path) as f:
    roles_json = json.load(f)


def upgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.sessionmaker(bind=bind)()

    for role in roles_json:
        if not session.query(Role).filter(Role.id == role["id"]).first():
            session.add(Role(id=role["id"], name=role["name"], description=role["description"]))
    session.commit()


def downgrade() -> None:
    bind = op.get_bind()
    session = sa.orm.sessionmaker(bind=bind)()
    session.query(Role).delete()
    session.commit()
