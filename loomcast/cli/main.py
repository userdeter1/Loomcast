from __future__ import annotations

import os
from enum import Enum
from typing import Optional

import typer
from rich.console import Console
from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from loomcast.adapters.catalog.dynamic import DynamicCatalog
from loomcast.adapters.catalog.static import StaticCatalog
from loomcast.adapters.downloader.progress import RichProgressReporter
from loomcast.common.config import LoomcastConfig
from loomcast.common.exceptions import CatalogIntegrityError, LoomcastError
from loomcast.common.paths import get_config_file_path
from loomcast.core.manager import LoomcastManager
from loomcast.domain.entities import RuntimeType

app = typer.Typer(
    name="loomcast",
    help="Loomcast: Multi-runtime Local LLM Manager (Ollama, LM Studio, llama.cpp)",
    add_completion=False,
)
console = Console()


def get_manager() -> LoomcastManager:
    try:
        config = LoomcastConfig.load()
        return LoomcastManager(config=config)
    except Exception as e:  # noqa: BLE001
        console.print(f"[bold red]Configuration error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("status")
def status_cmd():
    """Show operational status of all local runtimes."""
    manager = get_manager()
    statuses = manager.list_available_runtimes()

    table = Table(title="Loomcast Local Runtimes Status")
    table.add_column("Runtime", style="cyan", no_wrap=True)
    table.add_column("Endpoint", style="blue")
    table.add_column("Default", style="magenta")
    table.add_column("Status", style="bold")

    default_backend = manager.config.default_backend

    for rtype, is_online in statuses.items():
        if rtype == RuntimeType.OLLAMA:
            endpoint = manager.config.ollama_url
        elif rtype == RuntimeType.LMSTUDIO:
            endpoint = manager.config.lmstudio_url
        elif rtype == RuntimeType.LLAMACPP:
            endpoint = manager.config.llamacpp_url
        else:
            endpoint = "-"
        is_default = "[bold cyan]Yes[/bold cyan]" if rtype == default_backend else "No"
        status_str = (
            "[bold green]Online[/bold green]"
            if is_online
            else "[bold red]Offline[/bold red]"
        )
        table.add_row(rtype.value.upper(), endpoint, is_default, status_str)

    console.print(table)


@app.command("list")
def list_cmd(
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Runtime backend (ollama | lmstudio | llamacpp)"
    ),
):
    """List installed models in local runtimes."""
    manager = get_manager()
    try:
        if backend:
            target_type = RuntimeType(backend.lower())
            runtimes = [target_type]
        else:
            runtimes = list(RuntimeType)

        table = Table(title="Installed Models")
        table.add_column("Runtime", style="cyan")
        table.add_column("Model Name", style="green")

        for rtype in runtimes:
            adapter = manager.get_runtime(rtype)
            if adapter.is_available():
                try:
                    models = adapter.list_installed()
                    if not models:
                        table.add_row(
                            rtype.value.upper(), "[dim]No models installed[/dim]"
                        )
                    else:
                        for m in models:
                            table.add_row(rtype.value.upper(), escape(m))
                except LoomcastError as e:
                    table.add_row(
                        rtype.value.upper(), f"[red]Error: {escape(str(e))}[/red]"
                    )
            else:
                table.add_row(rtype.value.upper(), "[dim red]Runtime offline[/dim red]")

        console.print(table)
    except ValueError:
        console.print(
            f"[bold red]Invalid backend:[/bold red] '{escape(backend)}'. Choose 'ollama', 'lmstudio' or 'llamacpp'."
        )
        raise typer.Exit(code=1) from None


@app.command("install")
def install_cmd(
    model: str = typer.Argument(..., help="Model identifier to install/pull"),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Runtime backend (ollama | lmstudio | llamacpp)"
    ),
):
    """Install or pull a model into the target runtime."""
    manager = get_manager()
    try:
        console.print(f"Installing model '[bold cyan]{escape(model)}[/bold cyan]'...")
        with RichProgressReporter(console=console) as progress:
            manager.install(model, runtime_type=backend, progress=progress)
        console.print(
            f"[bold green]Successfully installed model '[cyan]{escape(model)}[/cyan]'![/bold green]"
        )
    except LoomcastError as e:
        console.print(f"[bold red]Installation failed:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("update")
def update_cmd(
    model: str = typer.Argument(..., help="Model identifier to update"),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Runtime backend (ollama | lmstudio | llamacpp)"
    ),
):
    """Update an installed model in the target runtime."""
    manager = get_manager()
    try:
        console.print(f"Updating model '[bold cyan]{escape(model)}[/bold cyan]'...")
        with RichProgressReporter(console=console) as progress:
            updated = manager.update(model, runtime_type=backend, progress=progress)
        if updated:
            console.print(
                f"[bold green]Successfully updated model '[cyan]{escape(model)}[/cyan]'![/bold green]"
            )
        else:
            console.print(
                f"[yellow]Already up to date, nothing to do for '[cyan]{escape(model)}[/cyan]'.[/yellow]"
            )
    except LoomcastError as e:
        console.print(f"[bold red]Update failed:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("remove")
def remove_cmd(
    model: str = typer.Argument(..., help="Model identifier to remove/delete"),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Runtime backend (ollama | lmstudio | llamacpp)"
    ),
    yes: bool = typer.Option(False, "--yes", "-y", help="Skip confirmation prompt"),
):
    """Remove an installed model from the target runtime."""
    # typer.confirm writes plain text, not rich markup, so no escaping here.
    if not yes and not typer.confirm(f"Remove {model}? This action cannot be undone."):
        raise typer.Abort()
    manager = get_manager()
    try:
        manager.remove(model, runtime_type=backend)
        console.print(
            f"[bold green]Successfully removed model '[cyan]{escape(model)}[/cyan]'![/bold green]"
        )
    except LoomcastError as e:
        console.print(f"[bold red]Removal failed:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("chat")
def chat_cmd(
    model: str = typer.Argument(..., help="Model name to chat with"),
    prompt: str = typer.Argument(..., help="User prompt string"),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Runtime backend (ollama | lmstudio | llamacpp)"
    ),
):
    """Send a single prompt to a model and display the response."""
    manager = get_manager()
    try:
        messages = [{"role": "user", "content": prompt}]
        with console.status(
            f"[bold green]Generating response from {escape(model)}...[/bold green]"
        ):
            response = manager.chat(model, messages, runtime_type=backend)

        console.print(
            Panel(
                Text(response),
                title=f"Model: {escape(model)}",
                border_style="cyan",
            )
        )
    except LoomcastError as e:
        console.print(f"[bold red]Chat error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("config")
def config_cmd(
    set_default_backend: Optional[str] = typer.Option(
        None, "--set-default", help="Set default backend (ollama | lmstudio | llamacpp)"
    ),
    show: bool = typer.Option(
        True, "--show/--no-show", help="Display current configuration"
    ),
):
    """View or update Loomcast configuration."""
    config = LoomcastConfig.load()
    if set_default_backend:
        try:
            config.default_backend = RuntimeType(set_default_backend.lower())
            config.save()
            console.print(
                f"[bold green]Default backend updated to:[/bold green] {config.default_backend.value}"
            )
        except ValueError:
            console.print(
                f"[bold red]Invalid backend:[/bold red] '{escape(set_default_backend)}'."
            )
            raise typer.Exit(code=1) from None

    if show:
        table = Table(title="Loomcast Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="yellow")
        for k, v in config.model_dump().items():
            # Render enums as their value ("ollama"), not their repr
            # ("RuntimeType.OLLAMA"), which is what users type back into --set.
            table.add_row(k, escape(v.value if isinstance(v, Enum) else str(v)))
        console.print(table)


@app.command("search")
def search_cmd(
    query: str = typer.Argument(..., help="Query string to search model catalog"),
):
    """Search for models in the catalog."""
    manager = get_manager()
    try:
        entries = manager.search(query)
        if not entries:
            console.print(
                f"[yellow]No models found matching query:[/yellow] '{escape(query)}'"
            )
            return

        table = Table(title=f"Catalog Search Results for '{escape(query)}'")
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Publisher", style="blue")
        table.add_column("Backend", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Tags", style="cyan")

        for e in entries:
            tags_str = ", ".join(e.tags) if e.tags else "-"
            backend_str = e.default_runtime.value if e.default_runtime else "-"
            table.add_row(
                escape(e.name),
                escape(e.publisher or "-"),
                backend_str,
                escape(e.description or "-"),
                escape(tags_str),
            )

        console.print(table)
    except LoomcastError as e:
        console.print(f"[bold red]Search error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("recommend")
def recommend_cmd(
    task: str = typer.Argument(
        ..., help="Task or category tag to filter recommendations"
    ),
):
    """Recommend models for a specific task or category tag."""
    manager = get_manager()
    try:
        entries = manager.recommend(task)
        if not entries:
            console.print(
                f"[yellow]No recommendations found for task:[/yellow] '{escape(task)}'"
            )
            return

        table = Table(title=f"Recommended Models for Task '{escape(task)}'")
        table.add_column("Name", style="green", no_wrap=True)
        table.add_column("Publisher", style="blue")
        table.add_column("Backend", style="magenta")
        table.add_column("Description", style="white")
        table.add_column("Tags", style="cyan")

        for e in entries:
            tags_str = ", ".join(e.tags) if e.tags else "-"
            backend_str = e.default_runtime.value if e.default_runtime else "-"
            table.add_row(
                escape(e.name),
                escape(e.publisher or "-"),
                backend_str,
                escape(e.description or "-"),
                escape(tags_str),
            )

        console.print(table)
    except LoomcastError as e:
        console.print(f"[bold red]Recommendation error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("install-category")
def install_category_cmd(
    category: str = typer.Argument(..., help="Category tag to batch install"),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Runtime backend (ollama | lmstudio | llamacpp)"
    ),
    max_concurrent: int = typer.Option(
        3, "--max-concurrent", "-c", help="Maximum concurrent model downloads"
    ),
    sequential: bool = typer.Option(
        False,
        "--sequential",
        "-s",
        help="Run model installations sequentially (max_concurrent=1)",
    ),
):
    """Batch install all models in a specific category."""
    manager = get_manager()
    effective_concurrent = 1 if sequential else max_concurrent
    try:
        console.print(
            f"Batch installing category '[bold cyan]{escape(category)}[/bold cyan]' (max concurrent: {effective_concurrent})..."
        )
        with RichProgressReporter(console=console) as progress:
            installed, failed = manager.install_category(
                category,
                runtime_type=backend,
                max_concurrent=effective_concurrent,
                progress=progress,
            )

        console.print("[bold green]Category installation complete![/bold green]")
        console.print(
            f"Successfully installed: [cyan]{len(installed)}[/cyan] model(s) ({escape(', '.join(installed)) if installed else 'None'})"
        )
        if failed:
            console.print(
                f"Failed installations: [bold red]{len(failed)}[/bold red] model(s) ({escape(', '.join(failed))})"
            )
    except LoomcastError as e:
        console.print(
            f"[bold red]Category installation error:[/bold red] {escape(str(e))}"
        )
        raise typer.Exit(code=1) from None


@app.command("verify")
def verify_cmd(
    model: str = typer.Argument(..., help="Model name to verify"),
    backend: Optional[str] = typer.Option(
        None, "--backend", "-b", help="Runtime backend (ollama | lmstudio | llamacpp)"
    ),
):
    """Verify integrity of an installed model."""
    manager = get_manager()
    try:
        res = manager.verify(model, runtime_type=backend)
        status_str = (
            "[bold green]Verified[/bold green]"
            if res.verified
            else "[bold red]Not Verified[/bold red]"
        )

        table = Table(title=f"Verification Result: {escape(model)}")
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="yellow")

        table.add_row("Model", escape(res.model))
        table.add_row("Runtime", res.runtime_type.value)
        table.add_row("Status", status_str)
        table.add_row("Digest", escape(res.digest) if res.digest else "[dim]N/A[/dim]")
        table.add_row("Message", escape(res.message))

        console.print(table)
    except LoomcastError as e:
        console.print(f"[bold red]Verification error:[/bold red] {escape(str(e))}")
        raise typer.Exit(code=1) from None


@app.command("doctor")
def doctor_cmd():
    """Run system diagnostics across configuration, runtimes, catalog, and integrity."""
    problems = 0
    warnings = 0

    console.print("[bold cyan]Loomcast System Diagnostics[/bold cyan]\n")

    # 1. Configuration loading
    config_path = get_config_file_path()
    try:
        LoomcastConfig.load()
        console.print(
            f"[bold green]✓[/bold green] Configuration: loaded successfully from [cyan]{escape(str(config_path))}[/cyan]"
        )
    except Exception as e:  # noqa: BLE001
        problems += 1
        console.print(
            f"[bold red]✗[/bold red] Configuration: failed to load ({escape(str(e))})"
        )

    # 2. Environment variables
    env_keys = [
        "LOOMCAST_DEFAULT_BACKEND",
        "LOOMCAST_OLLAMA_URL",
        "LOOMCAST_LMSTUDIO_URL",
        "LOOMCAST_LLAMACPP_URL",
        "LOOMCAST_CATALOG_SOURCE",
    ]
    active_env = [f"{k}={os.environ[k]}" for k in env_keys if k in os.environ]
    if active_env:
        console.print(
            f"[bold green]✓[/bold green] Environment variables set: {escape(', '.join(active_env))}"
        )
    else:
        console.print(
            "[bold green]✓[/bold green] Environment variables: none set, using defaults"
        )

    # 3. Runtime availability
    manager = get_manager()
    default_backend = manager.config.default_backend
    statuses = manager.list_available_runtimes()

    for rtype, is_online in statuses.items():
        name = rtype.value.upper()
        if is_online:
            console.print(f"[bold green]✓[/bold green] Runtime {name}: available")
        else:
            if rtype == default_backend:
                problems += 1
                console.print(
                    f"[bold red]✗[/bold red] Runtime {name} (default backend): unavailable. "
                    "Start the service or change the default backend in the config."
                )
            else:
                warnings += 1
                console.print(
                    f"[bold yellow]⚠[/bold yellow] Runtime {name}: unavailable (not the default backend)"
                )

    # 4. Catalog accessibility
    catalog = manager.catalog
    if isinstance(catalog, DynamicCatalog):
        _entries, is_fallback = catalog._get_entries()
        if is_fallback:
            try:
                fb_entries = catalog.fallback_catalog.search("")
                if fb_entries:
                    warnings += 1
                    console.print(
                        "[bold yellow]⚠[/bold yellow] Catalog: dynamic catalog unavailable (fell back to the static catalog)"
                    )
                else:
                    problems += 1
                    console.print(
                        "[bold red]✗[/bold red] Catalog: both the dynamic catalog and the static fallback are unavailable"
                    )
            except Exception as e:  # noqa: BLE001
                problems += 1
                console.print(
                    f"[bold red]✗[/bold red] Catalog: static fallback catalog failed ({escape(str(e))})"
                )
        else:
            console.print(
                "[bold green]✓[/bold green] Catalog: dynamic catalog reachable"
            )
    else:
        try:
            catalog.search("")
            console.print("[bold green]✓[/bold green] Catalog: reachable")
        except Exception as e:  # noqa: BLE001
            problems += 1
            console.print(
                f"[bold red]✗[/bold red] Catalog: access failed ({escape(str(e))})"
            )

    # 5. Embedded static catalog file integrity
    try:
        StaticCatalog()
        console.print(
            "[bold green]✓[/bold green] Static catalog integrity: SHA-256 check passed"
        )
    except CatalogIntegrityError as e:
        problems += 1
        console.print(
            f"[bold red]✗[/bold red] Static catalog integrity: SHA-256 checksum mismatch ({escape(str(e))})"
        )
    except Exception as e:  # noqa: BLE001
        problems += 1
        console.print(
            f"[bold red]✗[/bold red] Static catalog integrity: error ({escape(str(e))})"
        )

    # Summary
    console.print(f"\n[bold]{problems} problem(s) found, {warnings} warning(s)[/bold]")

    if problems > 0:
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
