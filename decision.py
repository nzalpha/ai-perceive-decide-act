# decision.py
from rich.console import Console

console = Console()

async def make_decision(client, prompt, generate_with_timeout):
    """
    Decision Layer:
    Sends the current context (prompt) to the LLM,
    interprets the decision (FUNCTION_CALL, UNCERTAIN, FINAL_ANSWER),
    and returns the parsed command and arguments.
    """
    response = await generate_with_timeout(client, prompt)
    if not response or not response.text:
        console.print("[red]No response from LLM[/red]")
        return None

    result = response.text.strip()
    console.print(f"\n[yellow]Assistant:[/yellow] {result}")

    # Extract the last valid command line
    lines = result.split('\n')
    command_line = None
    for line in reversed(lines):
        line = line.strip()
        if line.startswith("Assistant:"):
            line = line[len("Assistant:"):].strip()
        if line.startswith(("FUNCTION_CALL:", "UNCERTAIN:", "FINAL_ANSWER:")):
            command_line = line
            break

    if not command_line:
        return None

    console.print(f"[dim]Parsed decision: {command_line[:80]}...[/dim]")
    return command_line
