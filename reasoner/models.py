from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional, Dict, Any

class StepType(str, Enum):
    PREMISE = "premise"
    CONCLUSION = "conclusion"
    EVIDENCE = "evidence"
    ASSUMPTION = "assumption"

class RelationshipType(str, Enum):
    SUPPORTS = "supports"
    CONTRADICTS = "contradicts"
    QUESTIONS = "questions"
    ELABORATES = "elaborates"

@dataclass
class ReasoningStep:
    id: int
    text: str
    step_type: StepType
    confidence: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class Relationship:
    source_id: int
    target_id: int
    rel_type: RelationshipType
    confidence: float = 1.0

@dataclass
class ReasoningChain:
    steps: List[ReasoningStep] = field(default_factory=list)
    relationships: List[Relationship] = field(default_factory=list)
    
    def add_step(self, text: str, step_type: StepType, **kwargs) -> ReasoningStep:
        step_id = len(self.steps) + 1
        step = ReasoningStep(id=step_id, text=text, step_type=step_type, **kwargs)
        self.steps.append(step)
        return step
    
    def add_relationship(self, source_id: int, target_id: int, rel_type: RelationshipType, **kwargs) -> Relationship:
        rel = Relationship(
            source_id=source_id,
            target_id=target_id,
            rel_type=rel_type,
            **kwargs
        )
        self.relationships.append(rel)
        return rel
    
    def get_step(self, step_id: int) -> Optional[ReasoningStep]:
        for step in self.steps:
            if step.id == step_id:
                return step
        return None
    
    def get_relationships(self, step_id: int) -> List[Relationship]:
        return [r for r in self.relationships 
                if r.source_id == step_id or r.target_id == step_id]
