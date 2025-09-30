from typing import List, Dict, Any, Optional
from .models import ReasoningChain, ReasoningStep, RelationshipType

class SuggestionEngine:
    def __init__(self):
        self.suggestions = {
            "unsupported_claim": self._suggest_for_unsupported_claim,
            "circular_reasoning": self._suggest_for_circular_reasoning,
            "hasty_generalization": self._suggest_for_hasty_generalization,
            "contradiction": self._suggest_for_contradiction,
            "emotional_reasoning": self._suggest_for_emotional_reasoning,
        }
    
    def generate_suggestions(self, chain: ReasoningChain, issues: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate suggestions for improving the reasoning chain."""
        enhanced_issues = []
        
        for issue in issues:
            issue_type = issue.get("type")
            if issue_type in self.suggestions:
                suggestion = self.suggestions[issue_type](chain, issue)
                enhanced_issue = issue.copy()
                enhanced_issue["suggestions"] = suggestion
                enhanced_issues.append(enhanced_issue)
            else:
                enhanced_issues.append(issue)
        
        return enhanced_issues
    
    def _suggest_for_unsupported_claim(self, chain: ReasoningChain, issue: Dict[str, Any]) -> List[str]:
        """Generate suggestions for unsupported claims."""
        step_id = issue["step_ids"][0]
        step = next(s for s in chain.steps if s.id == step_id)
        
        return [
            f"Add supporting evidence or reasoning for: '{step.text}'",
            "Consider if this is a conclusion that needs backing up with facts or data",
            "Ask yourself: What evidence do I have for this claim?"
        ]
    
    def _suggest_for_circular_reasoning(self, chain: ReasoningChain, issue: Dict[str, Any]) -> List[str]:
        """Generate suggestions for circular reasoning."""
        step1_id, step2_id = issue["step_ids"]
        step1 = next(s for s in chain.steps if s.id == step1_id)
        step2 = next(s for s in chain.steps if s.id == step2_id)
        
        return [
            f"The statements '{step1.text}' and '{step2.text}' appear to be circular.",
            "Try to provide independent evidence or reasoning for each claim.",
            "Ask: What external evidence supports this conclusion?"
        ]
    
    def _suggest_for_hasty_generalization(self, chain: ReasoningChain, issue: Dict[str, Any]) -> List[str]:
        """Generate suggestions for hasty generalizations."""
        step_id = issue["step_ids"][0]
        step = next(s for s in chain.steps if s.id == step_id)
        
        return [
            f"The statement '{step.text}' makes a broad generalization.",
            "Consider if you have enough evidence to support this generalization.",
            "Could you quantify this statement? (e.g., 'some' instead of 'all' or 'every')",
            "What exceptions might there be to this generalization?"
        ]
    
    def _suggest_for_contradiction(self, chain: ReasoningChain, issue: Dict[str, Any]) -> List[str]:
        """Generate suggestions for contradictions."""
        step1_id, step2_id = issue["step_ids"]
        step1 = next(s for s in chain.steps if s.id == step1_id)
        step2 = next(s for s in chain.steps if s.id == step2_id)
        
        return [
            f"The statements '{step1.text}' and '{step2.text}' appear to contradict each other.",
            "Clarify how these statements can both be true.",
            "Consider if you need to revise one or both statements to resolve the contradiction.",
            "Is there additional context that reconciles these statements?"
        ]
    
    def _suggest_for_emotional_reasoning(self, chain: ReasoningChain, issue: Dict[str, Any]) -> List[str]:
        """Generate suggestions for emotional reasoning."""
        step_id = issue["step_ids"][0]
        step = next(s for s in chain.steps if s.id == step_id)
        
        return [
            f"The statement '{step.text}' appears to be based on emotion.",
            "While feelings are valid, consider what objective evidence supports this.",
            "Could you rephrase this to be more neutral and fact-based?",
            "What specific observations or data support how you're feeling?"
        ]
    
    def get_chain_improvement_suggestions(self, chain: ReasoningChain) -> List[str]:
        """Generate detailed, actionable suggestions for improving the reasoning chain."""
        suggestions = []
        all_text = ' '.join([s.text.lower() for s in chain.steps])
        
        # Detect context
        context = self._detect_context(all_text)
        
        # 1. Conclusion Suggestion (only for non-trivial decisions)
        has_conclusion = any(step.step_type == "conclusion" for step in chain.steps)
        if not has_conclusion and len(chain.steps) > 1 and context not in ['health', 'academic']:
            conclusion_suggestions = {
                'relationship': [
                    "🔍 Let's craft a clear conclusion:",
                    "   - Review your main reasons for considering this decision",
                    "   - Consider: 'Based on how I feel and what I need in a relationship...'"
                ],
                'career': [
                    "🔍 Let's craft a clear conclusion:",
                    "   - Review your career goals and current situation",
                    "   - Consider: 'Given my skills and aspirations, I should...'"
                ],
                'financial': [
                    "🔍 Let's craft a clear conclusion:",
                    "   - Review your financial situation and goals",
                    "   - Consider: 'Based on my current finances and future plans...'"
                ],
                'default': [
                    "🔍 Let's craft a clear conclusion:",
                    "   - Summarize your main points",
                    "   - State what action or decision follows from your reasoning"
                ]
            }
            suggestions.extend(conclusion_suggestions.get(context, conclusion_suggestions['default']))
        
        # 2. Context-specific suggestions
        if context == 'relationship':
            suggestions.extend(self._get_relationship_suggestions(all_text))
        elif context == 'career':
            suggestions.extend(self._get_career_suggestions(all_text))
        elif context == 'financial':
            suggestions.extend(self._get_financial_suggestions(all_text))
        elif context == 'health':
            suggestions.extend(self._get_health_suggestions(all_text))
        elif context == 'academic':
            suggestions.extend(self._get_academic_suggestions(all_text))
        
        # 3. General decision-making suggestions
        if any(word in all_text for word in ["should", "decide", "choose", "whether"]):
            suggestions.extend([
                "\n🤔 Decision-Making Framework:",
                "   1. List your options clearly",
                "   2. For each option, consider:",
                "      - Pros and cons",
                "      - How it aligns with your values and goals",
                "      - Potential outcomes and consequences",
                "   3. Give yourself a deadline to decide",
                "   4. Trust your instincts but verify with facts"
            ])
        
        # 4. Emotional well-being check
        if any(word in all_text for word in ["stress", "overwhelm", "anxious", "worried"]):
            suggestions.extend([
                "\n💆‍♀️ Self-Care Suggestions:",
                "   - Take deep breaths and ground yourself in the present",
                "   - Talk to a trusted friend or professional",
                "   - Practice self-compassion - it's okay to have these feelings",
                "   - Consider journaling to process your thoughts"
            ])
        
        return suggestions
    
    def _detect_context(self, text: str) -> str:
        """Determine the main context of the reasoning chain."""
        relationship_terms = ["boyfriend", "girlfriend", "partner", "relationship", "break up", "date"]
        career_terms = ["job", "career", "work", "employ", "promotion", "resume", "interview"]
        financial_terms = ["money", "save", "debt", "income", "broke", "bill", "expense", "budget"]
        health_terms = ["eat", "dinner", "lunch", "breakfast", "food", "exercise", "workout", "sleep", "rest"]
        academic_terms = ["study", "exam", "test", "homework", "assignment", "class", "course", "learn", "review"]
        
        if any(term in text for term in academic_terms):
            return 'academic'
        elif any(term in text for term in relationship_terms):
            return 'relationship'
        elif any(term in text for term in career_terms):
            return 'career'
        elif any(term in text for term in financial_terms):
            return 'financial'
        elif any(term in text for term in health_terms):
            return 'health'
        return 'default'
    
    def _get_relationship_suggestions(self, text: str) -> List[str]:
        """Generate relationship-specific suggestions."""
        suggestions = []
        
        if any(term in text for term in ["break up", "breakup", "end"]):
            suggestions.extend([
                "\n💔 Considering a Breakup?",
                "   1. Have you communicated your concerns to your partner?",
                "   2. Consider couples counseling if you're both willing",
                "   3. Make a list of deal-breakers vs. workable issues",
                "   4. Imagine your life in 1 year with and without this relationship"
            ])
        
        if any(term in text for term in ["happy", "unsatisfied", "unhappy"]):
            suggestions.extend([
                "\n💭 Reflective Questions:",
                "   - What specifically would make you happier in this relationship?",
                "   - Have your needs changed over time?",
                "   - What have you learned about what you need in a partner?"
            ])
        
        return suggestions
    
    def _get_career_suggestions(self, text: str) -> List[str]:
        """Generate career-specific suggestions."""
        return [
            "\n💼 Career Development:",
            "   1. Update your resume and LinkedIn profile",
            "   2. Set specific job search goals (e.g., applications/week)",
            "   3. Network: Reach out to 2-3 contacts weekly",
            "   4. Track your applications and follow-ups"
        ]
    
    def _get_health_suggestions(self, text: str) -> List[str]:
        """Generate health and wellness suggestions."""
        suggestions = []
        
        if any(term in text for term in ["eat", "dinner", "lunch", "breakfast", "snack"]):
            suggestions.extend([
                "\n🍽️ Nutrition Tips:",
                "   - Aim for balanced meals with protein, vegetables, and whole grains",
                "   - Stay hydrated - drink water throughout the day",
                "   - Listen to your body's hunger and fullness cues",
                "   - Plan meals ahead to make healthier choices easier"
            ])
        
        if any(term in text for term in ["sleep", "rest", "tired"]):
            suggestions.extend([
                "\n😴 Sleep Hygiene:",
                "   - Maintain a consistent sleep schedule",
                "   - Create a relaxing bedtime routine",
                "   - Limit screen time before bed",
                "   - Ensure your sleep environment is comfortable and dark"
            ])
            
        return suggestions if suggestions else [
            "\n🌱 Wellness Reminder:",
            "   - Take breaks to stretch and move throughout the day",
            "   - Practice mindful breathing when feeling stressed",
            "   - Small, consistent healthy habits add up over time"
        ]
    
    def _get_academic_suggestions(self, text: str) -> List[str]:
        """Generate academic and study-related suggestions."""
        suggestions = []
        
        if any(term in text for term in ["study", "exam", "test", "review"]) and any(term in text for term in ["struggle", "difficult", "hard"]):
            suggestions.extend([
                "\n📚 Study Strategy for Challenging Topics:",
                "   1. Break the material into smaller, manageable chunks",
                "   2. Use active recall techniques (e.g., self-quizzing)",
                "   3. Try different learning methods (videos, practice problems, study groups)",
                "   4. Schedule regular review sessions to reinforce learning"
            ])
        
        if any(term in text for term in ["exam", "test", "final"]):
            suggestions.extend([
                "\n⏱️ Exam Preparation Tips:",
                "   - Create a study schedule leading up to the exam",
                "   - Practice with past exams or sample questions",
                "   - Teach the material to someone else to test your understanding",
                "   - Get adequate rest before the exam day"
            ])
            
        return suggestions if suggestions else [
            "\n🎓 Academic Success Tips:",
            "   - Attend all classes and take thorough notes",
            "   - Review material shortly after class",
            "   - Don't hesitate to ask for help from professors or TAs",
            "   - Form or join a study group"
        ]
    
    def _get_financial_suggestions(self, text: str) -> List[str]:
        """Generate financial-specific suggestions."""
        return [
            "\n💰 Financial Planning:",
            "   1. Track all income and expenses for one month",
            "   2. Create a realistic budget based on your spending",
            "   3. Set specific savings goals (e.g., emergency fund)",
            "   4. Consider consulting a financial advisor"
        ]
