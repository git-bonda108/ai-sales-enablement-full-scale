import json
import re
from typing import Dict, List, Tuple

class EmailAnalyzer:
    def __init__(self):
        # Buying signal keywords and patterns
        self.buying_signals = {
            'high_intent': [
                'interested in purchasing',
                'looking to buy',
                'need a quote',
                'pricing information',
                'schedule a demo',
                'trial period',
                'implementation timeline',
                'budget approved',
                'decision maker',
                'ready to move forward'
            ],
            'medium_intent': [
                'exploring options',
                'considering',
                'evaluating',
                'comparison',
                'requirements',
                'capabilities',
                'features',
                'integration',
                'scalability'
            ],
            'questions': [
                'how much',
                'what is the cost',
                'pricing',
                'discount',
                'contract terms',
                'support included',
                'training provided'
            ]
        }

        self.objection_patterns = [
            'too expensive',
            'not the right time',
            'need to think',
            'compare with competitors',
            'concerns about',
            'worried about'
        ]

    def analyze_email(self, email: Dict) -> Dict:
        """Analyze email for buying signals and generate insights"""
        body = email.get('body', '').lower()
        subject = email.get('subject', '').lower()

        # Combine subject and body for analysis
        full_text = f"{subject} {body}"

        # Detect buying signals
        signal_score = self._calculate_signal_score(full_text)
        intent_level = self._determine_intent_level(signal_score)

        # Extract key information
        questions = self._extract_questions(full_text)
        objections = self._detect_objections(full_text)

        # Generate AI response suggestion
        response_suggestion = self._generate_response_suggestion(
            intent_level, questions, objections
        )

        return {
            'email_id': email.get('id'),
            'from': email.get('from'),
            'subject': email.get('subject'),
            'signal_score': signal_score,
            'intent_level': intent_level,
            'questions': questions,
            'objections': objections,
            'response_suggestion': response_suggestion,
            'key_points': self._extract_key_points(full_text),
            'next_steps': self._suggest_next_steps(intent_level, questions)
        }

    def _calculate_signal_score(self, text: str) -> float:
        """Calculate buying signal score from 0-100"""
        score = 0

        # High intent signals (weight: 10)
        for signal in self.buying_signals['high_intent']:
            if signal in text:
                score += 10

        # Medium intent signals (weight: 5)
        for signal in self.buying_signals['medium_intent']:
            if signal in text:
                score += 5

        # Questions (weight: 3)
        for signal in self.buying_signals['questions']:
            if signal in text:
                score += 3

        # Cap at 100
        return min(score, 100)

    def _determine_intent_level(self, score: float) -> str:
        """Determine intent level based on score"""
        if score >= 70:
            return "HIGH"
        elif score >= 40:
            return "MEDIUM"
        elif score >= 20:
            return "LOW"
        else:
            return "MINIMAL"

    def _extract_questions(self, text: str) -> List[str]:
        """Extract questions from email"""
        # Simple question extraction
        sentences = text.split('.')
        questions = []

        for sentence in sentences:
            if '?' in sentence:
                questions.append(sentence.strip())
            elif any(q in sentence for q in ['how', 'what', 'when', 'where', 'why', 'can you']):
                questions.append(sentence.strip())

        return questions[:5]  # Limit to 5 questions

    def _detect_objections(self, text: str) -> List[str]:
        """Detect potential objections"""
        objections = []

        for pattern in self.objection_patterns:
            if pattern in text:
                # Extract the sentence containing the objection
                sentences = text.split('.')
                for sentence in sentences:
                    if pattern in sentence:
                        objections.append(sentence.strip())
                        break

        return objections

    def _generate_response_suggestion(self, intent_level: str, 
                                    questions: List[str], 
                                    objections: List[str]) -> str:
        """Generate AI-powered response suggestion"""

        if intent_level == "HIGH":
            response = "Thank you for your interest! I'm excited to help you move forward. "
            if questions:
                response += "Let me address your questions: "
            response += "I'd love to schedule a quick call to discuss your specific needs and provide a customized solution. Are you available this week?"

        elif intent_level == "MEDIUM":
            response = "Thank you for considering our solution. "
            if questions:
                response += f"I'll be happy to answer your questions about {', '.join(questions[:2])}. "
            response += "I'd like to understand your requirements better. Could we schedule a brief discovery call?"

        else:
            response = "Thank you for reaching out. "
            if objections:
                response += "I understand your concerns and would like to address them. "
            response += "I'm here to help whenever you're ready to explore how we can add value to your business."

        return response

    def _extract_key_points(self, text: str) -> List[str]:
        """Extract key points from email"""
        key_points = []

        # Look for specific patterns
        patterns = [
            r'we need (.*?)[\.,]',
            r'looking for (.*?)[\.,]',
            r'interested in (.*?)[\.,]',
            r'our goal is (.*?)[\.,]',
            r'we want to (.*?)[\.,]'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            key_points.extend(matches)

        return key_points[:5]

    def _suggest_next_steps(self, intent_level: str, questions: List[str]) -> List[str]:
        """Suggest next steps based on analysis"""
        steps = []

        if intent_level == "HIGH":
            steps.extend([
                "Schedule demo immediately",
                "Prepare custom pricing proposal",
                "Identify decision makers",
                "Set up technical deep-dive if needed"
            ])
        elif intent_level == "MEDIUM":
            steps.extend([
                "Send relevant case studies",
                "Schedule discovery call",
                "Share product comparison guide",
                "Connect with technical team if needed"
            ])
        else:
            steps.extend([
                "Add to nurture campaign",
                "Send educational content",
                "Schedule follow-up in 2 weeks",
                "Monitor for increased engagement"
            ])

        return steps

    def generate_email_response(self, analysis: Dict) -> str:
        """Generate a complete email response based on analysis"""
        intent = analysis['intent_level']
        questions = analysis['questions']
        objections = analysis['objections']

        # Start with greeting
        response = f"Hi,\n\n"

        # Add main response based on suggestion
        response += analysis['response_suggestion'] + "\n\n"

        # Address specific questions if any
        if questions:
            response += "To address your specific questions:\n"
            for i, question in enumerate(questions[:3], 1):
                response += f"{i}. Regarding '{question}' - I'll be happy to provide detailed information.\n"
            response += "\n"

        # Handle objections
        if objections:
            response += "I understand you may have some concerns. "
            response += "Many of our successful clients had similar questions initially, and I'd be happy to share how they benefited from our solution.\n\n"

        # Add call to action
        if intent == "HIGH":
            response += "📅 Here's my calendar link: [Schedule a Demo]\n"
            response += "I have slots available tomorrow at 2 PM or Thursday at 10 AM. Which works better for you?\n\n"
        elif intent == "MEDIUM":
            response += "Would you prefer a quick 15-minute call to discuss, or should I send over some relevant materials first?\n\n"
        else:
            response += "I'll follow up with some helpful resources that might interest you. Feel free to reach out if you have any questions!\n\n"

        # Sign off
        response += "Best regards,\n[Your AI Sales Assistant]"

        return response
