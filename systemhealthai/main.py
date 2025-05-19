import asyncio
import trio
import typer
import sys
from typing import Optional, List
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich.progress import Progress, SpinnerColumn, TextColumn
from systemhealthai.shai import ShaiAIAgent


# Create console for rich output
console = Console()

# Create the Typer app
app = typer.Typer(
    help="AI SRE CLI tool for system health monitoring and troubleshooting",
    name="shai",
    add_completion=True
)
    
def get_agent(model: str) -> ShaiAIAgent:
    """Get or create the MCPCliManager instance."""
    return ShaiAIAgent(model=model)


@app.command("run")
def run_query(
    nodename: str = typer.Argument("localhost", help="node to query metrics for"),
    start_time: Optional[str] = typer.Option(
        None, "--start-time", "-st", help='Start time in the format "%Y-%m-%dT%H:%M:%S"'),
    end_time: Optional[str] = typer.Option(
        None, "--end-time", "-et", help='End time in the format "%Y-%m-%dT%H:%M:%S"'),
    model: Optional[str] = typer.Option(
        "openai:o4-mini", "--model", "-m", help="Specify the model to use (e.g., openai:o4-mini)"),

):
    """Diagnose system health"""
    if not nodename:
        console.print("[bold red]Error: No nodename provided.[/bold red]")
        raise typer.Exit(code=1)
    
    # Extract the model and provider from the model argument
    if model:
        provider, model_name = model.split(":", 1)
        console.print(f"[bold green]Using provider:[/bold green] {provider}")
        console.print(f"[bold green]Using model:[/bold green] {model_name}")

    if not start_time and not end_time:
        console.print("[bold yellow]No start or end time provided. " \
        "Will check system health for last 10 minutes.[/bold yellow]")
    
    # Form a dictionary from the input parameters
    query_params = {
        "nodename": nodename,
        "start_time": start_time,
        "end_time": end_time,
    }
    
    # Load environment variables
    load_dotenv()
    
    async def _run():
        manager = get_agent(model=model_name)
        
        try:
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Initializing MCP client and agent...[/bold blue]"),
                console=console
            ) as progress:
                progress.add_task("initializing", total=None)
                initialized = await manager.initialize()
            
            if not initialized:
                console.print("[bold red]Failed to initialize MCP client.[/bold red]")
                return 1
            
            # console.print(f"[bold cyan]Executing query:[/bold cyan] {query}")
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]Processing query...[/bold blue]"),
                console=console
            ) as progress:
                progress.add_task("processing", total=None)
                try:
                    # Run the query with a timeout
                    result = await manager.run_query(query_params=query_params)
                        
                except asyncio.TimeoutError:
                    console.print("[bold red]Query execution timed out. Cancelling operation.[/bold red]")
                    return 1
            
            console.print(Panel.fit(
                Markdown(result),
                title="Result",
                border_style="green"
            ))
            
            return 0
            
        except Exception as e:
            console.print(f"[bold red]Error during execution: {str(e)}[/bold red]")
            return 1

    
    # Create and run a new event loop for this command
    try:
        # Run the async function and wait for it to complete
        # TODO: replace with trio
        exit_code = asyncio.get_event_loop().run_until_complete(_run())
        
        # Exit with the appropriate code
        if exit_code != 0:
            raise typer.Exit(code=exit_code)
            
    except KeyboardInterrupt:
        console.print("[bold yellow]Operation cancelled by user.[/bold yellow]")
        # Ensure proper exit code
        raise typer.Exit(code=1)

def main():
    try:
        app()
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)
    

if __name__ == "__main__":
    main()