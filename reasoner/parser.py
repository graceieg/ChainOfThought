import re
from typing import List, Dict, Any, Optional, Tuple
import spacy
from .models import ReasoningStep, StepType, RelationshipType, ReasoningChain

class ReasoningParser:
    def __init__(self):
        # Load English language model
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            # If the model is not downloaded, download it
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    def parse_text(self, text: str) -> ReasoningChain:
        """Parse a block of text containing reasoning steps.
        
        Handles both numbered and unnumbered input:
        
        Numbered input:
            1. First step
            2. Second step
            
        Unnumbered input:
            First step
            Second step
        """
        chain = ReasoningChain()
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        for line in lines:
            # Remove any leading numbers and punctuation
            content = re.sub(r'^\s*\d+[.)]\s*', '', line).strip()
            if content:  # Only add non-empty lines
                step_type = self._determine_step_type(content)
                chain.add_step(text=content, step_type=step_type)
        
        # Analyze relationships between steps
        self._analyze_relationships(chain)
        return chain
    
    def _determine_step_type(self, text: str) -> StepType:
        """Determine the type of reasoning step based on text content."""
        text_lower = text.lower()
        doc = self.nlp(text_lower)
        
        # Check for conclusion indicators
        conclusion_indicators = ["therefore", "so", "thus", "hence", "as a result"]
        if any(indicator in text_lower for indicator in conclusion_indicators):
            return StepType.CONCLUSION
            
        # Check for evidence indicators
        evidence_indicators = ["because", "since", "as", "due to"]
        if any(indicator in text_lower for indicator in evidence_indicators):
            return StepType.EVIDENCE
            
        # Default to premise if no clear indicators
        return StepType.PREMISE
    
    def _analyze_relationships(self, chain: ReasoningChain):
        """Analyze and establish relationships between steps."""
        # Simple implementation - look for contradictions and support
        for i, step1 in enumerate(chain.steps):
            for j, step2 in enumerate(chain.steps[i+1:], i+1):
                if self._are_contradictory(step1.text, step2.text):
                    chain.add_relationship(
                        source_id=step1.id,
                        target_id=step2.id,
                        rel_type=RelationshipType.CONTRADICTS
                    )
    
    def _are_contradictory(self, text1: str, text2: str) -> bool:
        """Check if two statements are contradictory."""
        # This is a simple implementation - could be enhanced with more sophisticated NLP
        doc1 = self.nlp(text1.lower())
        doc2 = self.nlp(text2.lower())
        
        # Simple negation check
        negations = {"no", "not", "never", "none", "nobody", "nothing", "nowhere", "neither", "nor"}
        
        # Check if the same subject but with opposite sentiment/negation
        # This is a very basic implementation
        words1 = set(token.text for token in doc1 if not token.is_stop and not token.is_punct)
        words2 = set(token.text for token in doc2 if not token.is_stop and not token.is_punct)
        
        # If one contains a negation and the other doesn't, they might be contradictory
        has_neg1 = any(neg in words1 for neg in negations)
        has_neg2 = any(neg in words2 for neg in negations)
        
        if has_neg1 != has_neg2:
            # Check if they share enough content to be about the same thing
            common_words = words1.intersection(words2)
            if len(common_words) >= 2:  # At least two meaningful words in common
                return True
                
        return False
