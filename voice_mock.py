import asyncio
import json
import random
from datetime import datetime
from typing import Dict, List
import time

class VoiceMockGateway:
    def __init__(self):
        self.active_calls = {}
        self.call_transcripts = {}
        self.ai_suggestions = [
            "Mention the ROI statistics from the TechCorp case study",
            "Ask about their current pain points with their existing solution",
            "Highlight our 24/7 support as a key differentiator",
            "Suggest scheduling a technical deep-dive session",
            "Address the pricing concern by mentioning flexible payment plans",
            "Emphasize the implementation timeline - we can go live in 2 weeks",
            "Share success metrics from similar-sized companies"
        ]

        self.mock_conversations = [
            {
                "speaker": "Customer",
                "text": "Hi, I'm interested in learning more about your sales platform.",
                "timestamp": 0
            },
            {
                "speaker": "Sales Rep",
                "text": "Great to hear from you! I'd love to understand your current sales process.",
                "timestamp": 2
            },
            {
                "speaker": "Customer",
                "text": "We're using multiple tools right now and it's quite fragmented.",
                "timestamp": 5
            },
            {
                "speaker": "Sales Rep",
                "text": "That's a common challenge. Our platform integrates everything in one place.",
                "timestamp": 8
            },
            {
                "speaker": "Customer",
                "text": "What about pricing? We have a team of 50 sales reps.",
                "timestamp": 11
            },
            {
                "speaker": "Sales Rep",
                "text": "For a team your size, we have enterprise plans starting at $99 per user per month.",
                "timestamp": 14
            },
            {
                "speaker": "Customer",
                "text": "That seems reasonable. Can we see a demo?",
                "timestamp": 17
            },
            {
                "speaker": "Sales Rep",
                "text": "Absolutely! I can show you a demo right now or schedule one for your team.",
                "timestamp": 20
            }
        ]

    def start_mock_call(self, call_id: str, participant: str) -> Dict:
        """Start a mock voice call"""
        self.active_calls[call_id] = {
            'id': call_id,
            'participant': participant,
            'start_time': datetime.now().isoformat(),
            'status': 'active',
            'duration': 0
        }

        self.call_transcripts[call_id] = []

        return {
            'call_id': call_id,
            'status': 'connected',
            'message': f'Mock call started with {participant}'
        }

    def get_real_time_transcript(self, call_id: str, last_index: int = 0) -> Dict:
        """Get real-time transcript for mock call"""
        if call_id not in self.active_calls:
            return {'error': 'Call not found'}

        # Simulate real-time transcription
        call = self.active_calls[call_id]
        elapsed_time = (datetime.now() - datetime.fromisoformat(call['start_time'])).seconds

        # Add mock conversation based on elapsed time
        new_messages = []
        for conv in self.mock_conversations:
            if conv['timestamp'] <= elapsed_time and conv['timestamp'] > last_index:
                new_messages.append({
                    'speaker': conv['speaker'],
                    'text': conv['text'],
                    'timestamp': conv['timestamp'],
                    'sentiment': self._analyze_sentiment(conv['text'])
                })
                self.call_transcripts[call_id].append(conv)

        # Generate AI suggestions based on conversation
        ai_suggestion = None
        if elapsed_time > 10 and elapsed_time % 10 < 2:  # Every 10 seconds
            ai_suggestion = random.choice(self.ai_suggestions)

        return {
            'call_id': call_id,
            'elapsed_time': elapsed_time,
            'new_messages': new_messages,
            'ai_suggestion': ai_suggestion,
            'sentiment_score': self._calculate_overall_sentiment(call_id)
        }

    def end_call(self, call_id: str) -> Dict:
        """End a mock call and generate analytics"""
        if call_id not in self.active_calls:
            return {'error': 'Call not found'}

        call = self.active_calls[call_id]
        end_time = datetime.now()
        duration = (end_time - datetime.fromisoformat(call['start_time'])).seconds

        # Generate call analytics
        analytics = self._generate_call_analytics(call_id, duration)

        # Update call status
        call['status'] = 'completed'
        call['end_time'] = end_time.isoformat()
        call['duration'] = duration

        return {
            'call_id': call_id,
            'status': 'completed',
            'duration': duration,
            'analytics': analytics
        }

    def _analyze_sentiment(self, text: str) -> str:
        """Simple sentiment analysis"""
        positive_words = ['interested', 'great', 'love', 'reasonable', 'absolutely', 'excited']
        negative_words = ['fragmented', 'challenge', 'concern', 'difficult', 'problem']

        text_lower = text.lower()
        positive_count = sum(1 for word in positive_words if word in text_lower)
        negative_count = sum(1 for word in negative_words if word in text_lower)

        if positive_count > negative_count:
            return 'positive'
        elif negative_count > positive_count:
            return 'negative'
        else:
            return 'neutral'

    def _calculate_overall_sentiment(self, call_id: str) -> float:
        """Calculate overall sentiment score for the call"""
        if call_id not in self.call_transcripts:
            return 0.5

        transcripts = self.call_transcripts[call_id]
        if not transcripts:
            return 0.5

        sentiments = {'positive': 1, 'neutral': 0.5, 'negative': 0}
        scores = [sentiments.get(self._analyze_sentiment(t.get('text', '')), 0.5) 
                 for t in transcripts]

        return sum(scores) / len(scores) if scores else 0.5

    def _generate_call_analytics(self, call_id: str, duration: int) -> Dict:
        """Generate comprehensive call analytics"""
        transcripts = self.call_transcripts.get(call_id, [])

        # Count speaker turns
        speaker_turns = {'Sales Rep': 0, 'Customer': 0}
        for t in transcripts:
            speaker = t.get('speaker', '')
            if speaker in speaker_turns:
                speaker_turns[speaker] += 1

        # Identify key topics discussed
        topics = []
        topic_keywords = {
            'pricing': ['pricing', 'cost', 'price', 'per user'],
            'integration': ['integrate', 'tools', 'platform'],
            'demo': ['demo', 'show', 'see'],
            'team_size': ['team', 'reps', 'users'],
            'pain_points': ['challenge', 'fragmented', 'problem']
        }

        all_text = ' '.join([t.get('text', '') for t in transcripts]).lower()
        for topic, keywords in topic_keywords.items():
            if any(keyword in all_text for keyword in keywords):
                topics.append(topic)

        # Calculate talk ratio
        total_turns = sum(speaker_turns.values())
        talk_ratio = speaker_turns['Sales Rep'] / total_turns if total_turns > 0 else 0

        # Generate recommendations
        recommendations = []
        if talk_ratio > 0.6:
            recommendations.append("Try to ask more open-ended questions")
        if 'pricing' in topics and 'demo' not in topics:
            recommendations.append("Consider offering a demo before discussing pricing")
        if duration < 300:  # Less than 5 minutes
            recommendations.append("Engage in deeper discovery questions")

        return {
            'duration': duration,
            'sentiment_score': self._calculate_overall_sentiment(call_id),
            'speaker_turns': speaker_turns,
            'talk_ratio': talk_ratio,
            'topics_discussed': topics,
            'key_moments': self._identify_key_moments(transcripts),
            'recommendations': recommendations,
            'next_steps': self._suggest_next_steps(topics, transcripts)
        }

    def _identify_key_moments(self, transcripts: List[Dict]) -> List[Dict]:
        """Identify key moments in the conversation"""
        key_moments = []

        for t in transcripts:
            text = t.get('text', '').lower()
            # Identify buying signals
            if any(signal in text for signal in ['interested', 'demo', 'reasonable', 'team of']):
                key_moments.append({
                    'timestamp': t.get('timestamp', 0),
                    'type': 'buying_signal',
                    'text': t.get('text', ''),
                    'speaker': t.get('speaker', '')
                })
            # Identify concerns
            elif any(concern in text for concern in ['pricing', 'fragmented', 'challenge']):
                key_moments.append({
                    'timestamp': t.get('timestamp', 0),
                    'type': 'concern',
                    'text': t.get('text', ''),
                    'speaker': t.get('speaker', '')
                })

        return key_moments

    def _suggest_next_steps(self, topics: List[str], transcripts: List[Dict]) -> List[str]:
        """Suggest next steps based on call analysis"""
        next_steps = []

        if 'demo' in topics:
            next_steps.append("Schedule a detailed product demo")
        if 'pricing' in topics:
            next_steps.append("Send detailed pricing proposal")
        if 'team_size' in topics:
            next_steps.append("Prepare enterprise package options")

        # Check if they expressed high interest
        all_text = ' '.join([t.get('text', '') for t in transcripts]).lower()
        if 'interested' in all_text or 'reasonable' in all_text:
            next_steps.append("Follow up within 24 hours")
            next_steps.append("Connect them with customer success team")

        return next_steps
