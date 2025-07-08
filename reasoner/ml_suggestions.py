from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from rich.console import Console
from textblob import TextBlob
import textwrap
import random

from reasoner.models import ReasoningChain, ReasoningStep, Relationship, RelationshipType, StepType

class LocalMLSuggestionEngine:
    """Local Machine Learning-based suggestion engine using TextBlob."""
    
    def __init__(self):
        self.improvement_phrases = [
            "Consider rephrasing for clarity: ",
            "This could be more specific: ",
            "To strengthen your reasoning, try: ",
            "A more precise way to phrase this: "
        ]
        
        self.positive_feedback = [
            "Well structured point about ",
            "Good analysis of ",
            "Strong reasoning regarding "
        ]
    
    def get_suggestions(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Generate suggestions for improving the reasoning chain using local ML.
        
        Args:
            chain: The reasoning chain to analyze
            
        Returns:
            List of suggestion dictionaries
        """
        suggestions = []
        
        # Check for very short steps
        for i, step in enumerate(chain.steps):
            if len(step.text.split()) < 3:  # Very short step
                suggestions.append({
                    "type": "step_too_short",
                    "description": f"Step {i+1} is quite brief and could benefit from more detail",
                    "confidence": 0.9,
                    "severity": "low",
                    "suggestions": [
                        "Elaborate on this point with more specific details",
                        "Provide a concrete example to illustrate your point",
                        "Explain how this connects to your overall reasoning"
                    ]
                })
        
        # Analyze sentiment and subjectivity
        for i, step in enumerate(chain.steps):
            text = step.text.lower()
            blob = TextBlob(step.text)
            
            # Check for highly subjective statements
            subjectivity = blob.sentiment.subjectivity
            
            # Indicators of subjectivity
            subjective_indicators = [
                # First person statements
                'i think', 'i believe', 'in my opinion', 'from my perspective',
                'it seems to me', 'i would argue', 'i would suggest',
                
                # Modal verbs indicating uncertainty or opinion
                'might be', 'could be', 'may be', 'seems', 'appears',
                'suggests', 'indicates', 'implies',
                
                # Value judgments
                'good', 'bad', 'better', 'worse', 'best', 'worst',
                'should', 'ought to', 'must', 'have to', 'need to'
            ]
            
            # Check for absolute statements that might indicate strong opinions
            absolute_indicators = [
                'always', 'never', 'every', 'all', 'none', 'no one',
                'everyone', 'nobody', 'everybody', 'everything', 'nothing'
            ]
            
            has_subjective = any(indicator in text for indicator in subjective_indicators)
            has_absolute = any(indicator in text for indicator in absolute_indicators)
            
            # Calculate confidence based on multiple factors
            confidence = subjectivity
            if has_subjective:
                confidence = min(1.0, confidence + 0.2)
            if has_absolute:
                confidence = min(1.0, confidence + 0.1)
                
            # Check if this is a conclusion or claim
            is_conclusion = any(word in text for word in ['therefore', 'thus', 'hence', 'so', 'conclusion'])
            if is_conclusion:
                confidence = min(1.0, confidence + 0.1)
            
            # If confidence is high enough, add a suggestion
            if confidence > 0.7:  # Slightly lowered threshold
                suggestions.append({
                    "type": "high_subjectivity",
                    "description": f"Step {i+1} appears to be opinion-based or subjective",
                    "confidence": min(0.95, confidence),  # Cap confidence
                    "severity": "info",
                    "suggestions": [
                        "Support this with objective evidence or data",
                        "Clarify that this reflects your personal perspective",
                        "Explain the reasoning behind this viewpoint"
                    ]
                })
            
            # Check for strong sentiment (positive or negative)
            polarity = blob.sentiment.polarity
            
            # Check for negative sentiment with different thresholds
            if polarity < -0.3:  # Negative sentiment
                # Check for words that indicate strong negative sentiment
                strong_negative_words = ['fail', 'terrible', 'awful', 'horrible', 'never', 'worst']
                has_strong_negative = any(word in text for word in strong_negative_words)
                
                if has_strong_negative or polarity < -0.5:
                    # Strong negative sentiment
                    suggestions.append({
                        "type": "strong_negative_sentiment",
                        "description": f"Step {i+1} includes strong negative language",
                        "confidence": min(0.95, abs(polarity) + 0.2),
                        "severity": "medium",
                        "suggestions": [
                            "Consider rephrasing to be more neutral or constructive",
                            "Provide evidence or reasoning to support this strong claim"
                        ]
                    })
                else:
                    # Regular negative sentiment
                    suggestions.append({
                        "type": "negative_sentiment",
                        "description": f"Step {i+1} includes negative language",
                        "confidence": min(0.9, abs(polarity)),
                        "severity": "low",
                        "suggestions": [
                            "Consider whether this negative framing is necessary",
                            "Try to maintain a balanced perspective"
                        ]
                    })
            # Check for positive sentiment
            elif polarity > 0.4:  # Positive sentiment
                # Check for intensifiers that might indicate stronger sentiment
                intensifiers = ['very', 'really', 'extremely', 'incredibly', 'absolutely']
                has_intensifier = any(word in text for word in intensifiers)
                
                suggestions.append({
                    "type": "strong_positive_sentiment",
                    "description": f"Step {i+1} includes strong positive language",
                    "confidence": min(0.9, abs(polarity) + (0.15 if has_intensifier else 0)),
                    "severity": "low",
                    "suggestions": [
                        "Consider if the positive language is supported by evidence",
                        "Balance emotional language with factual statements"
                    ]
                })
        
        # Check reasoning flow
        if len(chain.steps) > 1:
            suggestions.extend(self._analyze_flow(chain))
        
        return suggestions
    
    def _analyze_flow(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Analyze the flow between reasoning steps."""
        suggestions = []
        
        # Check for logical connectors between steps
        connectors = ["because", "therefore", "thus", "however", "but", "so", "and", "or"]
        
        for i in range(len(chain.steps) - 1):
            current = chain.steps[i].text.lower()
            next_step = chain.steps[i+1].text.lower()
            
            # Check for abrupt topic changes
            current_topics = set(word for word in current.split() if len(word) > 4)
            next_topics = set(word for word in next_step.split() if len(word) > 4)
            
            if not current_topics.intersection(next_topics) and \
               not any(connector in next_step for connector in connectors):
                suggestions.append({
                    "type": "abrupt_transition",
                    "description": f"The transition between steps {i+1} and {i+2} might need a smoother connection",
                    "confidence": 0.7,
                    "severity": "low",
                    "suggestions": [
                        "Add a transition that connects these ideas",
                        "Explain how these steps relate to each other",
                        "Consider reordering steps for better flow"
                    ]
                })
        
        return suggestions
    
    def display_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Display the suggestions in a user-friendly format."""
        console = Console(width=100)
        
        if not suggestions:
            console.print("\n[green]✓ No specific suggestions. Your reasoning looks solid![/green]")
            return
        
        # Group by severity
        by_severity = {"info": [], "low": [], "medium": [], "high": []}
        for s in suggestions:
            by_severity[s.get("severity", "info")].append(s)
        
        # Display by severity
        for severity, items in by_severity.items():
            if not items:
                continue
                
            if severity == "info":
                console.print("\n[blue]Insights:[/blue]")
            elif severity == "low":
                console.print("\n[yellow]Considerations:[/yellow]")
            else:
                console.print(f"\n[red]Areas for Improvement ({severity}):[/red]")
            
            for item in items:
                # Print description with proper wrapping
                console.print(f"\n  • {item['description']}")
                
                # Print suggestions if they exist
                if "suggestions" in item and item["suggestions"]:
                    console.print("    [dim]Suggestions:[/dim]")
                    for suggestion in item["suggestions"]:
                        # Wrap long suggestions
                        for line in textwrap.wrap(suggestion, width=80):
                            prefix = "      ◦ " if line == suggestion.split('\n')[0] else "        "
                            console.print(f"{prefix}{line}")
