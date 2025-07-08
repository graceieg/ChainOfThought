"""
Comprehensive test suite for the Chain of Thought Debugger.

This module combines all test cases from various test files into a single,
well-organized test suite using Python's unittest framework.
"""
import unittest
import os
import sys
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('..'))

from reasoner.parser import ReasoningParser
from reasoner.analyzer import ReasoningAnalyzer
from reasoner.ml_suggestions import LocalMLSuggestionEngine

console = Console()

class TestReasoningAnalyzer(unittest.TestCase):    
    @classmethod
    def setUpClass(cls):
        """Set up test fixtures before any tests are run."""
        cls.parser = ReasoningParser()
        cls.analyzer = ReasoningAnalyzer()
        cls.ml_engine = LocalMLSuggestionEngine()
    
    def analyze_text(self, text):
        """Helper method to parse and analyze text."""
        chain = self.parser.parse_text(text)
        issues = self.analyzer.analyze_chain(chain)
        suggestions = self.ml_engine.get_suggestions(chain)
        return chain, issues, suggestions
    
    def assertIssueFound(self, issues, issue_type, description_fragment=None):
        """Assert that a specific issue was found."""
        found = False
        for issue in issues:
            if issue['type'] == issue_type:
                if description_fragment is None or description_fragment in issue['description']:
                    found = True
                    break
        self.assertTrue(found, f"Expected issue of type '{issue_type}' not found")
    
    def assertIssueNotPresent(self, issues, issue_type):
        """Assert that a specific issue was not found."""
        for issue in issues:
            self.assertNotEqual(issue['type'], issue_type, 
                              f"Unexpected issue of type '{issue_type}' found")
    
    def assertSuggestionFound(self, suggestions, suggestion_type):
        """Assert that a specific ML suggestion was found."""
        found = any(s['type'] == suggestion_type for s in suggestions)
        self.assertTrue(found, f"Expected ML suggestion of type '{suggestion_type}' not found")

    # Test Cases
    
    def test_valid_deductive_reasoning(self):
        """Test valid deductive reasoning."""
        text = """
        1. All mammals are warm-blooded
        2. Whales are mammals
        3. Therefore, whales are warm-blooded
        """
        _, issues, _ = self.analyze_text(text)
        self.assertIssueNotPresent(issues, "hasty_generalization")
        self.assertIssueNotPresent(issues, "potential_assumption")
    
    def test_casual_conversation(self):
        """Test casual conversation with emotion."""
        text = """
        1. I'm feeling really excited about the concert tonight
        2. I hope the band plays my favorite song
        3. I should remember to bring earplugs
        """
        _, issues, suggestions = self.analyze_text(text)
        self.assertIssueNotPresent(issues, "hasty_generalization")
        self.assertIssueNotPresent(issues, "potential_assumption")
        self.assertSuggestionFound(suggestions, "high_subjectivity")
    
    def test_hasty_generalization(self):
        """Test hasty generalization."""
        text = """
        1. My last Uber driver was rude
        2. All Uber drivers must be rude
        3. I should stop using Uber
        """
        _, issues, suggestions = self.analyze_text(text)
        self.assertIssueFound(issues, "hasty_generalization")
        self.assertSuggestionFound(suggestions, "high_subjectivity")
    
    def test_scientific_reasoning(self):
        """Test scientific reasoning with evidence."""
        text = """
        1. The study shows 95% of participants improved with treatment
        2. The p-value was less than 0.05
        3. Therefore, the treatment is likely effective
        """
        _, issues, _ = self.analyze_text(text)
        self.assertIssueNotPresent(issues, "hasty_generalization")
        self.assertIssueNotPresent(issues, "potential_assumption")
    
    def test_circular_reasoning(self):
        """Test circular reasoning."""
        text = """
        1. The Bible is true because it says so
        2. We know it says so because it's true
        3. Therefore, you should believe it
        """
        _, issues, _ = self.analyze_text(text)
        self.assertIssueFound(issues, "circular_reasoning")
    
    def test_emotional_reasoning_fallacy(self):
        """Test emotional reasoning fallacy."""
        text = """
        1. I feel like I'm going to fail the test
        2. Therefore, I will definitely fail the test
        3. I might as well not even study
        """
        _, issues, suggestions = self.analyze_text(text)
        self.assertIssueFound(issues, "emotional_reasoning")
        self.assertSuggestionFound(suggestions, "strong_negative_sentiment")
    
    def test_common_knowledge(self):
        """Test statements of common knowledge."""
        text = """
        1. The sky is blue
        2. Water is wet
        3. 2+2=4
        """
        _, issues, _ = self.analyze_text(text)
        self.assertIssueNotPresent(issues, "consider_adding_support")
    
    def test_complex_argument_with_assumptions(self):
        """Test complex argument with assumptions."""
        text = """
        1. Remote work increases productivity
        2. Happy employees are more productive
        3. Therefore, companies should allow remote work
        """
        _, issues, _ = self.analyze_text(text)
        self.assertIssueFound(issues, "potential_assumption")


def run_tests():
    """Run all tests with rich console output."""
    console.print(Panel.fit(
        "[bold blue]Running Chain of Thought Debugger Tests[/bold blue]",
        border_style="blue",
        padding=(1, 2)
    ))
    
    # Run the tests
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestReasoningAnalyzer)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    console.print("\n[bold]Test Summary:[/bold]")
    if result.wasSuccessful():
        console.print(f"[green]✓ All {result.testsRun} tests passed![/green]")
    else:
        console.print(f"[red]✗ {len(result.failures)} test(s) failed out of {result.testsRun}[/red]")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    run_tests()
