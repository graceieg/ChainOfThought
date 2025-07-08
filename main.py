#!/usr/bin/env python3
"""
Chain of Thought - A Debugger for Human Reasoning

This tool helps analyze and improve reasoning chains by identifying logical fallacies,
unsupported claims, and other issues in thought processes.
"""

import sys
import json
from typing import List, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.prompt import Prompt

from reasoner.analyzer import ReasoningAnalyzer
from reasoner.parser import ReasoningParser
from reasoner.ml_suggestions import LocalMLSuggestionEngine
from reasoner.models import ReasoningChain, ReasoningStep, Relationship, RelationshipType

import textwrap

def display_analysis(chain: ReasoningChain, issues: List[Dict[str, Any]], suggestions: List[Dict[str, Any]]):
    """Display the analysis results in a user-friendly format."""
    console = Console(width=100)  # Consistent width with main console
    
    # Display the reasoning chain with proper wrapping
    console.print("\n[bold cyan]Your Reasoning Chain:[/bold cyan]")
    for i, step in enumerate(chain.steps, 1):
        # Split long lines into multiple lines if needed
        text = f"{i}. {step.text}"
        for line in text.split('\n'):
            # Use textwrap for consistent wrapping
            for wrapped_line in textwrap.wrap(line, width=90):
                console.print(f"  {wrapped_line}")
    
    # Group issues by severity
    issues_by_severity = {
        'info': [],
        'low': [],
        'medium': [],
        'high': []
    }
    
    for issue in issues:
        severity = issue.get('severity', 'info')
        issues_by_severity[severity].append(issue)
    
    # Track if we have any issues to show
    has_issues = any(issues_by_severity.values())
    
    # Display issues by severity
    for severity, issues_list in issues_by_severity.items():
        if not issues_list:
            continue
            
        if severity == 'info':
            console.print("\n[bold blue]Insights:[/bold blue]")
        elif severity == 'low':
            console.print("\n[bold yellow]Considerations:[/bold yellow]")
        else:
            console.print(f"\n[bold red]Areas Needing Attention ({severity} severity):[/bold red]")
        
        for item in issues_list:
            # Format description with proper wrapping
            description = item['description'].strip()
            if not description.endswith(('!', '.', '?')):
                description += '.'
            
            # Print bullet point with wrapped description
            wrapped_desc = textwrap.wrap(description, width=85)  # 85 to account for bullet point
            for i, line in enumerate(wrapped_desc):
                prefix = "  • " if i == 0 else "    "
                console.print(prefix + line)
            
            # Print suggestions with proper wrapping
            if 'suggestions' in item and item['suggestions']:
                console.print("\n    [dim]Suggestions:[/dim]")
                for suggestion in item['suggestions']:
                    suggestion = suggestion.strip()
                    if not suggestion.endswith(('.', '!', '?')):
                        suggestion += '.'
                    
                    # Wrap long suggestion lines
                    wrapped_suggestion = textwrap.wrap(suggestion, width=80)  # 80 to account for bullet point and indentation
                    for i, line in enumerate(wrapped_suggestion):
                        prefix = "      ◦ " if i == 0 else "        "
                        console.print(prefix + line)
    
    if not has_issues:
        console.print("\n[green]✓ Your reasoning looks solid! No major issues found.[/green]")

    # Generate and display ML-based suggestions
    console.print("\n[bold]Analysis:[/bold]")
    try:
        ml_engine = LocalMLSuggestionEngine()
        suggestions = ml_engine.get_suggestions(chain)
        ml_engine.display_suggestions(suggestions)
    except Exception as e:
        console.print(f"An error occurred during analysis: {str(e)}", style="red")

def main():
    """Main entry point for the Chain of Thought debugger."""
    console = Console(width=100)  # Set a fixed width for consistent wrapping
    
    # Create a panel with proper width
    title = "Chain of Thought - A Debugger for Human Reasoning"
    instructions = "\n".join([
        "Enter your thoughts one at a time. Press Enter twice when finished.",
        "",
        "Example:",
        "  1. I need to complete three tasks",
        "  2. I work best in the morning",
        "  3. Therefore, I'll start early"
    ])
    
    console.print(Panel.fit(
        f"[bold blue]{title}[/bold blue]\n\n{instructions}",
        border_style="blue",
        padding=(1, 2),
        title_align="left"
    ))
    
    console.print("\nEnter your reasoning below:")
    lines = []
    while True:
        try:
            line = input("> ").strip()
            if not line and lines:
                break
            if line:
                lines.append(line)
        except EOFError:
            break
    
    if not lines:
        console.print("[yellow]No input provided. Exiting.[/yellow]")
        return
    
    # Process the input
    try:
        # Join lines and parse
        input_text = "\n".join(lines)
        parser = ReasoningParser()
        chain = parser.parse_text(input_text)
        
        # Analyze the chain
        analyzer = ReasoningAnalyzer()
        issues = analyzer.analyze_chain(chain)
        
        # Generate and display suggestions using local ML
        ml_engine = LocalMLSuggestionEngine()
        
        # Display basic analysis
        display_analysis(chain, issues, [])
        
        # Get and display ML-powered suggestions
        console.print("\n[bold]Analysis:[/bold]")
        suggestions = ml_engine.get_suggestions(chain)
        ml_engine.display_suggestions(suggestions)
        
    except Exception as e:
        console.print(f"[red]An error occurred: {str(e)}[/red]")
        if __debug__:
            import traceback
            console.print(traceback.format_exc())

if __name__ == "__main__":
    main()
