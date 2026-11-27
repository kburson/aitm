"""Install the CLI without importing unselected route modules."""

from collections.abc import Mapping
from importlib import import_module
from uuid import uuid4

import typer

from .catalog import ROUTES


def _execute(
    ctx: typer.Context, prefix: str, routes: Mapping[tuple[str, ...], str]
) -> None:
    from aitm_core.models.common import CommandResult, LocalOutcome

    arguments = list(ctx.args)
    path = (prefix,)
    if arguments and (prefix, arguments[0]) in routes:
        path = (prefix, arguments.pop(0))

    json_output = ctx.find_root().obj
    if "--json" in arguments:
        arguments.remove("--json")
        json_output = True

    module = routes.get(path)
    handle = None
    if module:
        try:
            handle = getattr(import_module(module), "handle", None)
        except ModuleNotFoundError as error:
            if error.name != module:
                raise

    if handle is None:
        result = CommandResult(
            operation_id=uuid4().hex,
            local=LocalOutcome.UNAVAILABLE,
            evidence=(f"Core route is unavailable: {' '.join(path)}",),
        )
    else:
        result = handle(path, tuple(arguments))

    if json_output:
        typer.echo(result.model_dump_json(by_alias=True))
    elif result.evidence:
        for message in result.evidence:
            typer.echo(message, err=result.exit_code != 0)
    else:
        typer.echo(result.local, err=result.exit_code != 0)
    raise typer.Exit(result.exit_code)


def build_cli(routes: Mapping[tuple[str, ...], str] = ROUTES) -> typer.Typer:
    app = typer.Typer(
        name="aitm",
        help="AITM Core workflow commands.",
        no_args_is_help=True,
        pretty_exceptions_enable=False,
    )

    @app.callback()
    def configure(
        ctx: typer.Context, json_output: bool = typer.Option(False, "--json")
    ) -> None:
        ctx.obj = json_output

    def route_callback(prefix: str):
        def run(ctx: typer.Context) -> None:
            _execute(ctx, prefix, routes)

        return run

    for prefix in sorted({path[0] for path in routes}):
        children = sorted(
            path[1] for path in routes if len(path) == 2 and path[0] == prefix
        )
        help_text = f"Subcommands: {', '.join(children)}." if children else None
        app.command(
            prefix,
            help=help_text,
            context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
        )(route_callback(prefix))
    return app


def main() -> int:
    try:
        build_cli()()
    except SystemExit as error:
        if isinstance(error.code, int):
            return error.code
        raise
    return 0
