from typing import Optional
import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from loomcast.common.config import LoomcastConfig
from loomcast.common.exceptions import LoomcastError
from loomcast.core.manager import LoomcastManager
from loomcast.domain.entities import RuntimeType

app = typer.Typer(
    name="loomcast",
    help="Loomcast: Multi-runtime Local LLM Manager (Ollama, LM Studio)",
    add_completion=False,
)
console = Console()


def get_manager() -> LoomcastManager:
    try:
        config = LoomcastConfig.load()
        return LoomcastManager(config=config)
    except Exception as e:
        console.print(f"[bold red]Configuration error:[/bold red] {e}")
        raise typer.Exit(code=1)


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
        endpoint = manager.config.ollama_url if rtype == RuntimeType.OLLAMA else manager.config.lmstudio_url
        is_default = "[bold cyan]Yes[/bold cyan]" if rtype == default_backend else "No"
        status_str = "[bold green]Online[/bold green]" if is_online else "[bold red]Offline[/bold red]"
        table.add_row(rtype.value.upper(), endpoint, is_default, status_str)

    console.print(table)


@app.command("list")
def list_cmd(
    backend: Optional[str] = typer.Option(None, "--backend", "-b", help="Runtime backend (ollama | lmstudio)")
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
                        table.add_row(rtype.value.upper(), "[dim]No models installed[/dim]")
                    else:
                        for m in models:
                            table.add_row(rtype.value.upper(), m)
                except LoomcastError as e:
                    table.add_row(rtype.value.upper(), f"[red]Error: {e}[/red]")
            else:
                table.add_row(rtype.value.upper(), "[dim red]Runtime offline[/dim red]")

        console.print(table)
    except ValueError:
        console.print(f"[bold red]Invalid backend:[/bold red] '{backend}'. Choose 'ollama' or 'lmstudio'.")
        raise typer.Exit(code=1)


@app.command("install")
def install_cmd(
    model: str = typer.Argument(..., help="Model identifier to install/pull"),
    backend: Optional[str] = typer.Option(None, "--backend", "-b", help="Runtime backend (ollama | lmstudio)"),
):
    """Install or pull a model into the target runtime."""
    manager = get_manager()
    try:
        console.print(f"Installing model '[bold cyan]{model}[/bold cyan]'...")
        manager.install(model, runtime_type=backend)
        console.print(f"[bold green]Successfully installed model '[cyan]{model}[/cyan]'![/bold green]")
    except LoomcastError as e:
        console.print(f"[bold red]Installation failed:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("chat")
def chat_cmd(
    model: str = typer.Argument(..., help="Model name to chat with"),
    prompt: str = typer.Argument(..., help="User prompt string"),
    backend: Optional[str] = typer.Option(None, "--backend", "-b", help="Runtime backend (ollama | lmstudio)"),
):
    """Send a single prompt to a model and display the response."""
    manager = get_manager()
    try:
        messages = [{"role": "user", "content": prompt}]
        with console.status(f"[bold green]Generating response from {model}...[/bold green]"):
            response = manager.chat(model, messages, runtime_type=backend)
        
        console.print(Panel(response, title=f"Model: {model}", border_style="cyan"))
    except LoomcastError as e:
        console.print(f"[bold red]Chat error:[/bold red] {e}")
        raise typer.Exit(code=1)


@app.command("config")
def config_cmd(
    set_default_backend: Optional[str] = typer.Option(None, "--set-default", help="Set default backend (ollama | lmstudio)"),
    show: bool = typer.Option(True, "--show/--no-show", help="Display current configuration"),
):
    """View or update Loomcast configuration."""
    config = LoomcastConfig.load()
    if set_default_backend:
        try:
            config.default_backend = RuntimeType(set_default_backend.lower())
            config.save()
            console.print(f"[bold green]Default backend updated to:[/bold green] {config.default_backend.value}")
        except ValueError:
            console.print(f"[bold red]Invalid backend:[/bold red] '{set_default_backend}'.")
            raise typer.Exit(code=1)

    if show:
        table = Table(title="Loomcast Configuration")
        table.add_column("Setting", style="cyan")
        table.add_column("Value", style="yellow")
        for k, v in config.model_dump().items():
            table.add_row(k, str(v))
        console.print(table)


if __name__ == "__main__":
    app()
