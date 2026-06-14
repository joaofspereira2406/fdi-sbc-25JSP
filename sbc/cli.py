import click
from pathlib import Path
from rich.console import Console
from rich.table import Table
from sbc.parser import parse_kb, parse_triple
from sbc.engine import query, forward_chain, backward_chain, apply_bindings
from sbc.models import Triple

console = Console()


def has_variables(triple):
    """Check if a triple contains any variables (uppercase tokens)."""
    return any(t[0].isupper() for t in (triple.subject, triple.predicate, triple.obj))


def format_bindings_table(results, goal):
    """Format a list of (bindings, degree) as a Rich table."""
    vars_ = [t for t in (goal.subject, goal.predicate, goal.obj) if t[0].isupper()]

    seen = []
    rows = []
    for b, degree in results:
        key = tuple(sorted(b.items()))
        if key not in seen:
            seen.append(key)
            rows.append((b, degree))

    if not rows:
        return None

    table = Table(show_header=True, header_style="bold cyan")
    for v in vars_:
        table.add_column(v)
    table.add_column("Grado", justify="right")

    for b, degree in rows:
        row_vals = [b.get(v, "?") for v in vars_]
        row_vals.append(f"{degree:.2f}")
        table.add_row(*row_vals)

    return table


def format_facts_table(facts):
    """Format a list of triples (new facts) as a table."""
    table = Table(show_header=True, header_style="bold cyan")
    table.add_column("Sujeto")
    table.add_column("Predicado")
    table.add_column("Objeto")

    for f in sorted(facts, key=lambda t: (t.subject, t.predicate, t.obj)):
        table.add_row(f.subject, f.predicate, f.obj)

    return table


@click.command()
@click.option("--kb", default="kb/automocion.kb", help="Path to knowledge base")
def main(kb):
    kb_path = Path(kb)
    knowledge_base = parse_kb(kb_path)
    forward_chain(knowledge_base)  # pre-populate derived facts
    console.print(f"[green]KB cargada:[/green] {kb_path}")

    while True:
        try:
            line = input("> ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if line in ("salir", "exit", "quit"):
            break

        elif line == "cargar!":
            knowledge_base = parse_kb(kb_path)
            console.print("[green]Base de conocimiento recargada.[/green]")

        elif line == "descubrir!":
            new_facts = forward_chain(knowledge_base)
            if new_facts:
                console.print(
                    f"[cyan]Nuevos hechos descubiertos ({len(new_facts)}):[/cyan]"
                )
                console.print(format_facts_table(new_facts))
            else:
                console.print("[yellow]No se han descubierto nuevos hechos.[/yellow]")

        elif line.startswith("no ") and line.endswith("."):
            triple_str = line[3:-1].strip()
            t = parse_triple(triple_str.split())
            knowledge_base.facts.discard(t)
            console.print(
                f"[yellow]Hecho revocado:[/yellow] {t.subject} {t.predicate} {t.obj}"
            )

        elif line.endswith("."):
            t = parse_triple(line[:-1].strip().split())
            knowledge_base.facts.add(t)
            console.print(
                f"[green]Hecho añadido:[/green] {t.subject} {t.predicate} {t.obj}"
            )

        elif line.startswith("razona si ") and line.endswith("?"):
            triple_str = line[len("razona si ") : -1].strip()
            goal = parse_triple(triple_str.split())
            results = backward_chain(knowledge_base, goal)

            if has_variables(goal):
                table = format_bindings_table(results, goal)
                if table:
                    console.print(table)
                else:
                    console.print("[red]No se puede derivar.[/red]")
            else:
                if results:
                    _, degree = results[0]
                    console.print(f"[green]Sí[/green] [dim](grado: {degree:.2f})[/dim]")
                else:
                    console.print("[red]No.[/red]")

        elif line.endswith("?"):
            goal = parse_triple(line[:-1].strip().split())
            results = query(knowledge_base, goal)

            if has_variables(goal):
                table = format_bindings_table(results, goal)
                if table:
                    console.print(table)
                else:
                    console.print("[red]No encontrado.[/red]")
            else:
                if results:
                    _, degree = results[0]
                    console.print(f"[green]Sí[/green] [dim](grado: {degree:.2f})[/dim]")
                else:
                    console.print("[red]No.[/red]")


if __name__ == "__main__":
    main()
