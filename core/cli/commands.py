from typing import Optional
from typer import Typer
from alembic.config import Config
from alembic import command
from core.config import settings
from fastapi_cli.cli import app as fastapi_cli_app

cli_app = Typer(rich_markup_mode="rich")
cli_app.add_typer(fastapi_cli_app, name="run")

alembic_config = Config(settings.BASE_DIR / "alembic.ini")

@cli_app.command()
def makemigration(
    message: str,
    autogenerate: bool = True,
    sql: bool = False,
    head: str = "head",
    splice: bool = False,
    branch_label: str = None,
    version_path: str = None,
    rev_id: str = None,
    depends_on: str = None,):
    command.revision(
        alembic_config,
        message=message,
        autogenerate=autogenerate,
        sql=sql,
        head=head,
        splice=splice,
        branch_label=branch_label,
        version_path=version_path,
        rev_id=rev_id,
        depends_on=depends_on
    )

@cli_app.command()
def migrate(revision: str = "heads", sql: bool = False, tag: str = None):
    command.upgrade(
        alembic_config,
        revision=revision,
        sql=sql,
        tag=tag
    )

@cli_app.command()
def downgrade(revision, sql: bool = False, tag: str = None):
    command.downgrade(
        alembic_config,
        revision=revision,
        sql=sql,
        tag=tag
    )

@cli_app.command()
def alembic_merge(
    revisions: list[str],
    message: Optional[str] = None,
    branch_label: str = None,
    rev_id: str = None,):
    command.merge(
        alembic_config,
        revisions=revisions,
        message=message,
        branch_label=branch_label,
        rev_id=rev_id
    )

