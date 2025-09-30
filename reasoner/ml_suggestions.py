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
        """Generate focused suggestions for improving the reasoning chain.
        
        Args:
            chain: The reasoning chain to analyze
            
        Returns:
            List of suggestion dictionaries
        """
        suggestions = []
        
        # Check for very short steps
        for i, step in enumerate(chain.steps):
            text = step.text.strip()
            words = text.split()
            
            # Skip empty steps
            if not words:
                continue
                
            # Check for very short steps
            if len(words) < 3:
                suggestions.append({
                    "type": "step_too_short",
                    "description": f"Step {i+1} is quite brief",
                    "confidence": 0.9,
                    "severity": "low",
                    "suggestions": [
                        "Add more details or examples",
                        "Explain the connection to your main point"
                    ]
                })
                continue
                
            # Analyze sentiment and subjectivity
            blob = TextBlob(text.lower())
            
            # Check for emotional language
            emotional_indicators = {
                'positive': ['excellent', 'great', 'amazing', 'love', 'perfect', 'best'],
                'negative': ['terrible', 'awful', 'worst', 'hate', 'never', 'always']
            }
            
            # Check for emotional language
            for sentiment_type, indicators in emotional_indicators.items():
                if any(indicator in text.lower() for indicator in indicators):
                    suggestions.append({
                        "type": f"emotional_language_{sentiment_type}",
                        "description": f"Step {i+1} includes {sentiment_type} language",
                        "confidence": 0.8,
                        "severity": "low",
                        "suggestions": [
                            "Consider if this strong language is necessary",
                            "Balance emotional statements with evidence"
                        ]
                    })
                    break
                    
            # Check for subjective language
            subjective_phrases = [
                'i think', 'i believe', 'in my opinion', 'from my perspective',
                'it seems', 'appears', 'suggests', 'indicates'
            ]
            
            if any(phrase in text.lower() for phrase in subjective_phrases):
                suggestions.append({
                    "type": "subjective_language",
                    "description": f"Step {i+1} includes subjective language",
                    "confidence": 0.7,
                    "severity": "info",
                    "suggestions": [
                        "Consider if this could be stated more objectively",
                        "Support with evidence or data if possible"
                    ]
                })
            
            # Check for strong sentiment (positive or negative)
            polarity = blob.sentiment.polarity
            
            # Only flag strong sentiment that might bias the reasoning
            if abs(polarity) > 0.5:  # Strong sentiment (positive or negative)
                sentiment_type = "positive" if polarity > 0 else "negative"
                suggestions.append({
                    "type": f"strong_{sentiment_type}_sentiment",
                    "description": f"Step {i+1} includes strong {sentiment_type} language",
                    "confidence": min(0.9, abs(polarity) * 1.5),
                    "severity": "low",
                    "suggestions": [
                        "Consider if this strong language is necessary",
                        "Balance with factual statements"
                    ]
                })
        
        # Check reasoning flow
        if len(chain.steps) > 1:
            suggestions.extend(self._analyze_flow(chain))
        
        return suggestions
    
    def _analyze_flow(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Analyze the flow between reasoning steps."""
        if len(chain.steps) < 2:
            return []
            
        flow_suggestions = []
        
        # Check for abrupt transitions between steps
        for i in range(len(chain.steps) - 1):
            current_text = chain.steps[i].text.lower()
            next_text = chain.steps[i + 1].text.lower()
            
            # Simple transition words/phrases to look for
            transition_indicators = [
                'therefore', 'thus', 'hence', 'consequently',
                'additionally', 'furthermore', 'moreover',
                'however', 'on the other hand', 'conversely',
                'for example', 'for instance', 'specifically'
            ]
            
            # Check if transition is needed
            needs_transition = not any(indicator in next_text for indicator in transition_indicators)
            
            # Check for topic continuity
            current_words = set(word for word in current_text.split() if len(word) > 3)
            next_words = set(word for word in next_text.split() if len(word) > 3)
            topic_overlap = len(current_words & next_words) / max(1, min(len(current_words), len(next_words)))
            
            if needs_transition and topic_overlap < 0.4:
                flow_suggestions.append({
                    "type": "smooth_transition_needed",
                    "description": f"The transition to step {i+2} could be smoother",
                    "confidence": 0.8 - (topic_overlap * 1.5),
                    "severity": "low",
                    "suggestions": [
                        "Add a transition to connect these ideas",
                        "Explain how these points relate to each other"
                    ]
                })
                
        return flow_suggestions
    
    def display_suggestions(self, suggestions: List[Dict[str, Any]]):
        """Display the suggestions in a concise, non-repetitive format."""
        if not suggestions:
            return
            
        console = Console()
        
        # Group suggestions by type and step
        suggestions_by_step = {}
        for suggestion in suggestions:
            step = suggestion.get('step', 0)
            if step not in suggestions_by_step:
                suggestions_by_step[step] = []
            suggestions_by_step[step].append(suggestion)
        
        # Display suggestions by step
        for step, step_suggestions in suggestions_by_step.items():
            if step > 0:
                console.print(f"\n[bold]Step {step}:[/bold]")
            
            # Group by issue type
            issues = {}
            for suggestion in step_suggestions:
                issue_type = suggestion['type']
                if issue_type not in issues:
                    issues[issue_type] = []
                issues[issue_type].append(suggestion)
            
            # Display each unique issue type
            for issue_type, items in issues.items():
                # Use the first item's description as representative
                console.print(f"  • {items[0]['description']}")
                
                # Collect all unique suggestions
                all_suggestions = set()
                for item in items:
                    if 'suggestions' in item:
                        all_suggestions.update(item['suggestions'])
                
                # Display up to 2 most relevant suggestions
                if all_suggestions:
                    console.print("    [dim]Suggestions:[/dim]")
                    for i, suggestion in enumerate(list(all_suggestions)[:2]):
                        console.print(f"      ◦ {suggestion}")
                    if len(all_suggestions) > 2:
                        console.print(f"      ◦ ...and {len(all_suggestions) - 2} more")
