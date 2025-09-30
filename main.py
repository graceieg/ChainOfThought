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
    """Display the analysis results in a concise, non-repetitive format."""
    console = Console(width=100)
    
    # Display the reasoning chain with proper wrapping
    console.print("\n[bold cyan]Your Reasoning Chain:[/bold cyan]")
    for i, step in enumerate(chain.steps, 1):
        text = f"{i}. {step.text}"
        for line in text.split('\n'):
            for wrapped_line in textwrap.wrap(line, width=90):
                console.print(f"  {wrapped_line}")
    
    # Track displayed suggestions to avoid repetition
    displayed_suggestions = set()
    
    # Process and display issues by severity
    severity_titles = {
        'info': "[bold blue]Key Insights:[/bold blue]",
        'low': "[bold yellow]Considerations:[/bold yellow]",
        'medium': "[bold orange]Areas for Improvement:[/bold orange]",
        'high': "[bold red]Critical Issues:[/bold red]"
    }
    
    # Group and process issues by step
    step_issues = {}
    for issue in issues:
        step_num = issue.get('step', 0)
        if step_num not in step_issues:
            step_issues[step_num] = []
        step_issues[step_num].append(issue)
    
    # Display issues by step for better context
    for step_num, step_issues_list in step_issues.items():
        if not step_issues_list:
            continue
            
        # Group issues by severity within each step
        severity_groups = {}
        for issue in step_issues_list:
            severity = issue.get('severity', 'info')
            if severity not in severity_groups:
                severity_groups[severity] = []
            severity_groups[severity].append(issue)
        
        # Display the step header if there are multiple steps
        if len(step_issues) > 1:
            console.print(f"\n[bold]Step {step_num}:[/bold]")
        
        # Display issues by severity
        for severity, issues_list in severity_groups.items():
            console.print(severity_titles.get(severity, "[bold]Findings:[/bold]"))
            
            for issue in issues_list:
                # Format description
                description = issue['description'].strip()
                if not description.endswith(('.', '!', '?')):
                    description += '.'
                console.print(f"  • {description}")
                
                # Process suggestions
                if 'suggestions' in issue and issue['suggestions']:
                    # Only show unique suggestions
                    unique_suggestions = []
                    for suggestion in issue['suggestions']:
                        suggestion = suggestion.strip()
                        if suggestion and suggestion not in displayed_suggestions:
                            unique_suggestions.append(suggestion)
                            displayed_suggestions.add(suggestion)
                    
                    if unique_suggestions:
                        console.print("    [dim]Suggestions:[/dim]")
                        for suggestion in unique_suggestions[:3]:  # Limit to top 3 suggestions
                            if not suggestion.endswith(('.', '!', '?')):
                                suggestion += '.'
                            console.print(f"      ◦ {suggestion}")
    
    if not any(step_issues.values()):
        console.print("\n[green]✓ Your reasoning looks solid! No major issues found.[/green]")
    
    # Generate and display ML-based suggestions if not already covered
    try:
        ml_engine = LocalMLSuggestionEngine()
        ml_suggestions = ml_engine.get_suggestions(chain)
        
        # Filter out suggestions already shown
        new_suggestions = []
        for suggestion in ml_suggestions:
            if 'suggestions' in suggestion:
                new_suggestions.extend([s for s in suggestion['suggestions'] 
                                     if s.strip() not in displayed_suggestions])
        
        if new_suggestions:
            console.print("\n[bold]Additional Suggestions:[/bold]")
            for suggestion in new_suggestions[:3]:  # Limit to top 3 additional suggestions
                if not suggestion.endswith(('.', '!', '?')):
                    suggestion += '.'
                console.print(f"  • {suggestion}")
                
    except Exception as e:
        console.print(f"\n[red]Note: Some suggestions could not be generated: {str(e)}[/red]")

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
