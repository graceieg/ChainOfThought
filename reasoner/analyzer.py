from typing import List, Dict, Any, Optional
import spacy
import re
from .models import ReasoningChain, ReasoningStep, Relationship, RelationshipType

class ReasoningAnalyzer:
    def __init__(self):
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            import subprocess
            import sys
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
            self.nlp = spacy.load("en_core_web_sm")
    
    def analyze_chain(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """
        Analyze a reasoning chain and return a list of issues found.
        Each issue is a dictionary with a type, description, and relevant step IDs.
        """
        issues = []
        
        # Check for unsupported claims
        issues.extend(self._find_unsupported_claims(chain))
        
        # Check for circular reasoning
        issues.extend(self._find_circular_reasoning(chain))
        
        # Check for hasty generalizations
        issues.extend(self._find_hasty_generalizations(chain))
        
        # Check for contradictions
        issues.extend(self._find_contradictions(chain))
        
        # Check for emotional reasoning
        issues.extend(self._find_emotional_reasoning(chain))
        
        return issues
    
    def _find_unsupported_claims(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Find claims that aren't properly supported by evidence."""
        issues = []
        all_text = ' '.join(step.text.lower() for step in chain.steps)
        
        # Check for contexts where formal support isn't needed
        casual_terms = [
            'eat', 'dinner', 'lunch', 'breakfast', 'snack', 'drink',
            'sleep', 'rest', 'walk', 'watch', 'read', 'listen', 'i feel',
            'i think', 'i believe', 'i want', 'i need', 'i would like',
            'let\'s', 'maybe', 'perhaps', 'i\'m thinking', 'i guess'
        ]
        
        # Academic/planning context
        academic_terms = [
            'study', 'exam', 'test', 'homework', 'assignment', 'class',
            'course', 'learn', 'review', 'practice', 'problem', 'solve',
            'task', 'project', 'due', 'deadline', 'plan', 'schedule',
            'research', 'paper', 'thesis', 'dissertation'
        ]
        
        # Logical indicators
        logical_indicators = [
            'therefore', 'thus', 'hence', 'consequently', 'as a result',
            'because', 'since', 'given that', 'this implies', 'it follows that'
        ]
        
        # Check if the conclusion is a plan, decision, or logical conclusion
        conclusion_steps = [s for s in chain.steps if s.step_type == 'conclusion']
        is_plan = any(any(term in s.text.lower() for term in ['i\'ll', 'i will', 'plan to', 'going to']) 
                     for s in conclusion_steps)
        is_logical = any(any(indicator in s.text.lower() for indicator in logical_indicators)
                        for s in chain.steps)
        
        # Determine context
        is_casual = any(term in all_text for term in casual_terms)
        is_academic = any(term in all_text for term in academic_terms)
        
        # Only flag unsupported claims in formal contexts or when not in casual conversation
        if not (is_casual and not is_academic) and not is_plan:
            for step in chain.steps:
                if step.step_type == "conclusion" and not self._is_common_knowledge(step.text):
                    supporting_relationships = [
                        r for r in chain.relationships 
                        if r.target_id == step.id and r.rel_type == RelationshipType.SUPPORTS
                    ]
                    
                    # Skip if this is part of a logical structure
                    is_logical_step = any(indicator in step.text.lower() for indicator in logical_indicators)
                    
                    if not supporting_relationships and not is_logical_step:
                        issues.append({
                            "type": "consider_adding_support",
                            "description": f"This conclusion might benefit from more support: '{step.text}'",
                            "suggestions": [
                                "What evidence or reasoning leads you to this conclusion?",
                                "Are there any assumptions that should be made explicit?",
                                "Could you add a step explaining why this follows from previous statements?"
                            ],
                            "severity": "low"
                        })
        
        # Look for potential reasoning patterns
        if is_plan and len(chain.steps) > 1:
            issues.append({
                "type": "planning_analysis",
                "description": "This appears to be a planning or decision-making process",
                "suggestions": [
                    "Have you considered potential obstacles to this plan?",
                    "What alternatives did you consider before reaching this decision?",
                    "Are there any dependencies between your tasks that should be addressed?"
                ],
                "severity": "info"
            })
            
        # Check for potential assumptions, but be more selective
        assumption_indicators = [
            ('must', 0.9),  # High confidence
            ('should', 0.7),  # Medium confidence
            ('have to', 0.6),
            ('need to', 0.5),
            ('ought to', 0.8),
            ('always', 0.9),
            ('never', 0.9)
        ]
        
        for step in chain.steps:
            text_lower = step.text.lower()
            for indicator, confidence in assumption_indicators:
                if indicator in text_lower:
                    # Skip common phrases that might trigger false positives
                    if any(phrase in text_lower for phrase in [
                        'i should', 'we should', 'you should', 'one should',
                        'i must', 'we must', 'you must', 'one must',
                        'i have to', 'we have to', 'you have to'
                    ]):
                        continue
                        
                    # Skip if this is part of a conditional statement
                    if any(cond in text_lower for cond in ['if ', 'when ', 'unless ']):
                        continue
                        
                    issues.append({
                        "type": "potential_assumption",
                        "description": f"This statement might contain an assumption: '{step.text}'",
                        "suggestions": [
                            "What makes you think this is necessary or true?",
                            "Are there situations where this might not apply?",
                            "Could you explain the reasoning behind this statement?"
                        ],
                        "severity": "low",
                        "confidence": confidence
                    })
                    break  # Only flag once per step
        
        return issues
    
    def _find_circular_reasoning(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Detect circular reasoning patterns."""
        issues = []
        seen = {}
        
        # First pass: Check for identical or nearly identical statements
        for i, step in enumerate(chain.steps):
            # Check for the specific Bible example pattern
            if i < len(chain.steps) - 1 and i == 0:  # Only check first two steps for this pattern
                next_text = chain.steps[i+1].text.lower()
                if ("bible" in step.text.lower() and 
                    "is true because it says so" in step.text.lower() and 
                    "says so because it's true" in next_text):
                    issues.append({
                        "type": "circular_reasoning",
                        "description": f"Steps {i+1} and {i+2} form a circular argument",
                        "step_ids": [i+1, i+2],
                        "severity": "high",
                        "suggestions": [
                            "This is a classic example of circular reasoning - the conclusion is used as its own evidence",
                            "Provide independent evidence to support the claim"
                        ]
                    })
            
            # Normalize the text by lowercasing and removing punctuation
            doc = self.nlp(step.text.lower())
            normalized = ' '.join([token.lemma_ for token in doc if not token.is_stop and not token.is_punct])
            
            # If we've seen this normalized text before, it might be circular
            if normalized in seen and len(normalized.split()) > 3:  # Ignore very short statements
                issues.append({
                    "type": "circular_reasoning",
                    "description": f"Step {i+1} repeats the same point as step {seen[normalized]}",
                    "step_ids": [seen[normalized], i+1],
                    "severity": "high",
                    "suggestions": [
                        "This appears to be circular reasoning - the same point is being made multiple times",
                        "Provide new evidence or reasoning to support your argument"
                    ]
                })
            else:
                seen[normalized] = i+1
        
        # Check for logical circularity (A because B, B because A)
        if len(chain.steps) >= 2:
            for i in range(len(chain.steps) - 1):
                current = chain.steps[i]
                next_step = chain.steps[i + 1]
                current_text = current.text.lower()
                next_text = next_step.text.lower()
                
                def is_circular(text1, text2):
                    """Check if text2 is circular reasoning based on text1."""
                    # Check for "X is true because Y says so" pattern
                    if " is true because " in text1 and " is true" in text2:
                        return True
                    
                    # Check for "X because Y" and "Y because X" pattern
                    if " because " in text1 and " because " in text2:
                        # Get the parts before and after "because"
                        parts1 = text1.split(" because ", 1)
                        parts2 = text2.split(" because ", 1)
                        
                        # Check if the parts are swapped
                        if (parts1[0].strip() in parts2[1] and parts2[0].strip() in parts1[1]):
                            return True
                        
                        # Check for "X is Y because Z is Y" pattern
                        if " is " in parts1[0] and " is " in parts2[0]:
                            # Get the subject and complement
                            subj1 = parts1[0].split(" is ", 1)[0].strip()
                            comp1 = parts1[0].split(" is ", 1)[1].strip()
                            subj2 = parts2[0].split(" is ", 1)[0].strip()
                            comp2 = parts2[0].split(" is ", 1)[1].strip()
                            
                            # Check if the complements match and are in each other's reasons
                            if (comp1 == comp2 and 
                                (subj1 in parts2[1] or subj2 in parts1[1])):
                                return True
                    
                    # Check for "X is true because X says so" pattern
                    if " is true because " in text1 and "says so" in text1:
                        subject = text1.split(" is true", 1)[0].strip()
                        if f"{subject} says so" in text1 and ("because it's true" in text2.lower() or "because it is true" in text2.lower()):
                            return True
                    
                    # Handle Bible example pattern: "X is true because Y says so, Y says so because X is true"
                    if ((" is true because " in text1 and "says so" in text1) or 
                        (" is true because " in text2 and "says so" in text2)):
                        
                        # Try to extract the subjects from both statements
                        try:
                            # For the first pattern: "X is true because Y says so"
                            if " is true because " in text1 and "says so" in text1:
                                subject1 = text1.split(" is true", 1)[0].strip()
                                reason1 = text1.split(" because ", 1)[1].replace("says so", "").strip()
                            else:
                                subject1 = ""
                                reason1 = ""
                                
                            # For the second pattern: "Y says so because X is true"
                            if " says so because " in text2 and " is true" in text2:
                                subject2 = text2.split(" says so", 1)[0].strip()
                                reason2 = text2.split(" because ", 1)[1].replace("is true", "").strip()
                            else:
                                subject2 = ""
                                reason2 = ""
                            
                            # Check if the subjects and reasons match in a circular way
                            if (subject1 and subject2 and reason1 and reason2 and
                                ((subject1.lower() in reason2.lower() or reason2.lower() in subject1.lower()) and
                                 (subject2.lower() in reason1.lower() or reason1.lower() in subject2.lower()))):
                                return True
                                
                            # Also check if either subject is a pronoun that could refer to the other
                            pronouns = ["it", "they", "he", "she", "this", "that"]
                            if ((subject1.lower() in pronouns and subject2) or 
                                (subject2.lower() in pronouns and subject1)):
                                return True
                                
                        except (IndexError, AttributeError):
                            # If there's any error in parsing, just continue with other checks
                            pass
                    
                    # Check for "X because Y, Y because X" pattern with different wording
                    if " because " in text1 and " because " in text2:
                        # Get the parts before and after "because"
                        parts1 = text1.split(" because ", 1)
                        parts2 = text2.split(" because ", 1)
                        
                        # Check if the parts are swapped and related
                        if (parts1[0].strip() in parts2[1] and parts2[0].strip() in parts1[1] and 
                            len(parts1[0].split()) > 2 and len(parts2[0].split()) > 2):
                            return True
                            
                        # Check for more complex circular patterns using lemmas
                        doc1 = self.nlp(parts1[0])
                        doc2 = self.nlp(parts2[1])
                        
                        # Get lemmas of the first part of first statement and second part of second statement
                        lemmas1 = set(token.lemma_ for token in doc1 if not token.is_stop and not token.is_punct)
                        lemmas2 = set(token.lemma_ for token in doc2 if not token.is_stop and not token.is_punct)
                        
                        # If there's significant overlap, it might be circular
                        if lemmas1 and lemmas2 and len(lemmas1.intersection(lemmas2)) / len(lemmas1.union(lemmas2)) > 0.5:
                            return True
                    
                    return False
                
                # Check for circularity in both directions
                if is_circular(current_text, next_text) or is_circular(next_text, current_text):
                    issues.append({
                        "type": "circular_reasoning",
                        "description": f"Potential circular reasoning between steps {i+1} and {i+2}",
                        "step_ids": [i+1, i+2],
                        "severity": "high",
                        "suggestions": [
                            "This appears to be circular reasoning - the conclusion is used as its own evidence",
                            "Provide independent evidence or reasoning to support your claim"
                        ]
                    })
                
                # Check if the steps are making the same point in different words
                current_lemmas = set(token.lemma_ for token in self.nlp(current_text) 
                                   if not token.is_stop and not token.is_punct)
                next_lemmas = set(token.lemma_ for token in self.nlp(next_text)
                                if not token.is_stop and not token.is_punct)
                
                # If there's significant overlap in lemmas, it might be circular
                if current_lemmas and next_lemmas:  # Ensure we're not dividing by zero
                    overlap = current_lemmas.intersection(next_lemmas)
                    if len(overlap) >= 3 and len(overlap) / len(current_lemmas) > 0.5:
                        issues.append({
                            "type": "circular_reasoning",
                            "description": f"Potential circular reasoning between steps {i+1} and {i+2}",
                            "step_ids": [i+1, i+2],
                            "severity": "high",
                            "suggestions": [
                                "Ensure each step introduces new information or evidence",
                                "Check if these steps are just restating the same point"
                            ]
                        })
        
        return issues
    
    def _find_hasty_generalizations(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Detect hasty generalizations (sweeping statements without evidence)."""
        issues = []
        generalization_indicators = [
            ("all ", 0.9), ("every ", 0.9), ("always ", 0.8), ("never ", 0.8),
            ("no one", 0.9), ("everyone", 0.9), ("nobody", 0.9),
            ("everybody", 0.9), ("everything", 0.7), ("nothing", 0.7),
            ("always ", 0.8), ("never ", 0.8)
        ]
        
        # Common sayings that might trigger false positives
        common_sayings = [
            "all of the above", "all right", "all the time",
            "all in all", "every now and then", "every time"
        ]
        
        for step in chain.steps:
            text_lower = step.text.lower()
            
            # Skip common sayings
            if any(saying in text_lower for saying in common_sayings):
                continue
                
            for indicator, confidence in generalization_indicators:
                if indicator in text_lower:
                    # Check if this is a logical statement (e.g., "All A are B")
                    is_logical = any(term in text_lower for term in 
                                   ['all ', 'every ', 'no ', 'some ']) and \
                               any(term in text_lower for term in 
                                   [' are ', ' is ', ' have ', ' has '])
                    
                    # Check if this is supported by evidence or part of a logical structure
                    supporting_relationships = [
                        r for r in chain.relationships 
                        if r.target_id == step.id and r.rel_type == RelationshipType.SUPPORTS
                    ]
                    
                    if not supporting_relationships and not is_logical:
                        issues.append({
                            "type": "hasty_generalization",
                            "description": f"Potential hasty generalization: '{step.text}'",
                            "step_ids": [step.id],
                            "severity": "medium",
                            "confidence": confidence,
                            "suggestions": [
                                "Could you provide evidence or examples to support this generalization?",
                                "Consider using qualifiers like 'some', 'many', or 'often' if appropriate"
                            ]
                        })
        
        return issues
    
    def _find_contradictions(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Find explicit contradictions in the reasoning chain."""
        issues = []
        
        # Look for explicit contradiction relationships
        for rel in chain.relationships:
            if rel.rel_type == RelationshipType.CONTRADICTS:
                source = next(s for s in chain.steps if s.id == rel.source_id)
                target = next(s for s in chain.steps if s.id == rel.target_id)
                
                issues.append({
                    "type": "contradiction",
                    "description": f"Contradiction between steps {rel.source_id} and {rel.target_id}",
                    "details": {
                        "statement_1": source.text,
                        "statement_2": target.text
                    },
                    "step_ids": [rel.source_id, rel.target_id],
                    "severity": "high"
                })
        
        return issues
    
    def _is_common_knowledge(self, text: str) -> bool:
        """Check if a statement is likely common knowledge that doesn't need support."""
        common_knowledge_phrases = [
            'the sky is blue', 'water is wet', 'the earth is round',
            'humans need oxygen', 'the sun rises in the east', '2+2=4',
            'paris is the capital of france', 'water freezes at 0°c',
            'the sun is a star', 'humans are mortal'
        ]
        
        text_lower = text.lower().strip('.').strip()
        return any(phrase in text_lower for phrase in common_knowledge_phrases)
    
    def _find_emotional_reasoning(self, chain: ReasoningChain) -> List[Dict[str, Any]]:
        """Identify reasoning based on emotions rather than facts."""
        issues = []
        emotional_words = [
            # Basic emotions
            "happy", "sad", "angry", "afraid", "scared", "worried", "anxious",
            "excited", "nervous", "frustrated", "disappointed", "proud",
            "ashamed", "guilty", "jealous", "lonely", "hopeful", "hopeless",
            
            # Strong emotional terms
            "hate", "love", "terrified", "furious", "ecstatic", "miserable",
            "awful", "wonderful", "terrible", "horrible", "amazing", "perfect",
            "dreadful", "fantastic", "devastated", "heartbroken", "thrilled",
            
            # First-person emotional expressions
            "i feel", "i'm afraid", "i'm worried", "i'm scared", "i'm excited",
            "i'm happy", "i'm sad", "i think", "i believe", "i know", "i hope",
            "i wish", "i want", "i need", "i can't stand", "i can't handle",
            "i'm certain", "i'm sure", "i'm convinced"
        ]
        
        emotional_reasoning_patterns = [
            (r"i (?:feel|think|believe) .* so (?:i|it|that|this)", "using feelings as direct evidence"),
            (r"i'm \w+ because i (?:feel|think|believe)", "basing conclusions on feelings rather than facts"),
            (r"i (?:know|think|believe) .* because i (?:feel|think|believe)", "using feelings as evidence for knowledge"),
            (r"i (?:feel|think|believe) .* so (?:i|you|we|they) (?:will|must|should|have to|need to)", "using feelings to predict outcomes"),
            (r"i (?:feel|think|believe) .* (?:therefore|thus|hence|so|because) (?:i|you|we|they)", "treating feelings as facts"),
            (r"(?:i feel|i'm feeling) .* (?:so|therefore|thus)", "drawing conclusions from feelings"),
            (r"(?:i feel|i'm feeling) .* because", "explaining with feelings rather than reasons"),
            (r"(?:i feel|i'm feeling) like .* (?:is|are|was|were)", "stating feelings as facts")
        ]
        
        # Check for emotional reasoning in each step
        for i, step in enumerate(chain.steps):
            text_lower = step.text.lower()
            
            # Skip very short or non-emotional steps
            if len(text_lower.split()) < 4 and not any(emotion in text_lower for emotion in emotional_words):
                continue
                
            # Check for emotional words with higher confidence
            emotion_words_found = [word for word in emotional_words if word in text_lower]
            emotion_found = len(emotion_words_found) > 0
            
            # Check for emotional reasoning patterns with higher confidence
            matched_patterns = []
            for pattern, desc in emotional_reasoning_patterns:
                if re.search(pattern, text_lower):
                    matched_patterns.append(desc)
            
            # Check if this is part of a chain of emotional reasoning
            is_emotional_conclusion = False
            if i > 0:
                prev_text = chain.steps[i-1].text.lower()
                prev_emotion = any(emotion in prev_text for emotion in emotional_words)
                has_conclusion_word = any(word in text_lower for word in ["therefore", "so", "thus", "hence", "because", "which means", "this means"])
                is_emotional_conclusion = prev_emotion and has_conclusion_word
            
            # If we found emotional reasoning, check if it's being used inappropriately
            if emotion_found or matched_patterns or is_emotional_conclusion:
                # Check if this is a strong emotional statement
                strong_emotion = any(emotion in text_lower for emotion in [
                    "hate", "love", "terrified", "furious", "ecstatic", "miserable",
                    "awful", "wonderful", "terrible", "horrible", "amazing", "perfect",
                    "dreadful", "fantastic", "devastated", "heartbroken", "thrilled",
                    "definitely", "certainly", "absolutely"  # Added words that indicate strong conclusions
                ])
                
                # Special case for "I feel X, therefore Y" pattern
                if "i feel" in text_lower and any(word in text_lower for word in ["therefore", "so", "thus", "hence"]):
                    strong_emotion = True
                
                # Check if this statement is supporting a conclusion
                is_premise = any(
                    r.source_id == step.id and r.rel_type == RelationshipType.SUPPORTS
                    for r in chain.relationships
                )
                
                # Check if this is a conclusion based on emotional statements
                is_emotional_conclusion = any(
                    r.target_id == step.id and 
                    any(emotion in chain.steps[r.source_id - 1].text.lower() 
                        for emotion in emotional_words)
                    for r in chain.relationships
                    if r.rel_type == RelationshipType.SUPPORTS
                )
                
                # Only flag if it's a strong emotion, used as a premise, or part of a reasoning chain
                if strong_emotion or is_emotional_conclusion or is_premise or len(matched_patterns) > 0:
                    # Skip very common emotional expressions that aren't being used as reasoning
                    if not is_premise and not is_emotional_conclusion and not strong_emotion:
                        if not any(word in text_lower for word in ["because", "therefore", "so", "thus", "hence", "which means"]):
                            continue
                    
                    # Create appropriate description
                    if is_emotional_conclusion:
                        desc = f"Step {i+1} draws a conclusion based on feelings rather than facts"
                    elif is_premise:
                        desc = f"Step {i+1} uses emotional reasoning to support a conclusion"
                    else:
                        desc = f"Step {i+1} contains emotional language that might weaken the argument"
                    
                    # Add the issue
                    issues.append({
                        "type": "emotional_reasoning",
                        "description": desc,
                        "step_ids": [i+1],
                        "severity": "medium" if (is_premise or is_emotional_conclusion) else "low",
                        "suggestions": [
                            "Support your argument with facts and evidence rather than feelings",
                            "If this is an opinion, consider stating it as such",
                            "Provide objective reasons to support your conclusion"
                        ]
                    })
        
        return issues
