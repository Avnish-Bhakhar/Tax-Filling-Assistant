"""
Chatbot NLP Engine — Conversational AI for Tax Assistance
==========================================================
Implements a comprehensive NLP pipeline:

1. Tokenization: NLTK word tokenization with custom tax tokenizer
2. Embeddings: TF-IDF vectorization with n-gram support
3. Intent Classification: Neural network with attention-inspired mechanism
4. Entity Extraction: Regex + pattern matching for tax-specific entities
5. Context Management: Conversation state tracking
6. Response Generation: Template-based with dynamic content

The chatbot integrates with the A* state-space search
for intelligent conversation navigation.
"""

import re
import json
import pickle
import random
import numpy as np
from typing import Dict, List, Optional, Tuple
from pathlib import Path
from datetime import datetime

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.neural_network import MLPClassifier
    from sklearn.preprocessing import LabelEncoder
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.stem import WordNetLemmatizer
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False


class TaxTokenizer:
    """Custom tokenizer for tax-related text processing."""

    # Tax-specific patterns
    TAX_PATTERNS = {
        'money': r'₹?\s*[\d,]+(?:\.\d{2})?(?:\s*(?:lakhs?|lacs?|crores?|k|L|Cr))?',
        'section': r'(?:section\s+)?(?:80[A-Z]{1,3}(?:\([0-9A-Za-z]+\))?|24\([a-z]\)|194[A-Z]?)',
        'pan': r'[A-Z]{5}[0-9]{4}[A-Z]',
        'percentage': r'\d+(?:\.\d+)?%',
        'date': r'\d{1,2}[/-]\d{1,2}[/-]\d{2,4}',
        'financial_year': r'(?:FY|AY)\s*\d{4}-?\d{2,4}',
    }

    def __init__(self):
        self.lemmatizer = WordNetLemmatizer() if NLTK_AVAILABLE else None
        # Download required NLTK data
        if NLTK_AVAILABLE:
            try:
                nltk.data.find('tokenizers/punkt')
            except LookupError:
                try:
                    nltk.download('punkt', quiet=True)
                    nltk.download('punkt_tab', quiet=True)
                    nltk.download('wordnet', quiet=True)
                    nltk.download('omw-1.4', quiet=True)
                except:
                    pass

    def tokenize(self, text: str) -> List[str]:
        """Tokenize text with tax-specific handling."""
        if NLTK_AVAILABLE:
            try:
                tokens = word_tokenize(text.lower())
            except:
                tokens = text.lower().split()
        else:
            tokens = text.lower().split()

        # Lemmatize
        if self.lemmatizer:
            try:
                tokens = [self.lemmatizer.lemmatize(t) for t in tokens]
            except:
                pass

        return tokens

    def extract_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract tax-specific entities from text."""
        entities = {}
        for entity_type, pattern in self.TAX_PATTERNS.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                entities[entity_type] = matches
        return entities

    def extract_amounts(self, text: str) -> List[float]:
        """Extract monetary amounts from text."""
        amounts = []
        patterns = [
            r'₹\s*([\d,]+(?:\.\d{2})?)',
            r'([\d,]+(?:\.\d{2})?)\s*(?:rupees|rs\.?)',
            r'(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:lakhs?|lacs?)',
            r'(\d+(?:\.\d+)?)\s*(?:lakh|lac)',
        ]
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    clean = match.replace(',', '')
                    if 'lakh' in text.lower() or 'lac' in text.lower():
                        amounts.append(float(clean) * 100000)
                    else:
                        amounts.append(float(clean))
                except ValueError:
                    pass

        # Also try plain numbers
        plain_numbers = re.findall(r'\b(\d{4,})\b', text)
        for num in plain_numbers:
            try:
                amounts.append(float(num))
            except ValueError:
                pass

        return amounts


class AttentionLayer:
    """
    Simple attention mechanism for context-aware intent classification.
    Inspired by transformer self-attention but simplified for CPU inference.

    attention_score = softmax(query · key^T / √d_k) · value
    """

    def __init__(self, feature_dim: int):
        self.feature_dim = feature_dim
        # Initialize random weight matrices
        np.random.seed(42)
        self.W_q = np.random.randn(feature_dim, feature_dim) * 0.01
        self.W_k = np.random.randn(feature_dim, feature_dim) * 0.01
        self.W_v = np.random.randn(feature_dim, feature_dim) * 0.01

    def compute_attention(self, features: np.ndarray, context: np.ndarray = None) -> np.ndarray:
        """Compute attention-weighted features."""
        if context is None:
            context = features

        # Ensure proper shape
        if features.ndim == 1:
            features = features.reshape(1, -1)
        if context.ndim == 1:
            context = context.reshape(1, -1)

        # Handle dimension mismatch
        f_dim = features.shape[1]
        c_dim = context.shape[1]
        dim = min(f_dim, c_dim, self.feature_dim)

        # Truncate/pad to match
        Q = features[:, :dim]
        K = context[:, :dim]
        V = context[:, :dim]

        # Scaled dot-product attention
        d_k = dim
        scores = np.dot(Q, K.T) / np.sqrt(d_k)

        # Softmax
        exp_scores = np.exp(scores - np.max(scores))
        attention_weights = exp_scores / (exp_scores.sum(axis=-1, keepdims=True) + 1e-8)

        # Weighted sum
        attended = np.dot(attention_weights, V)

        # Concatenate with original features
        result = np.concatenate([features[:, :dim], attended], axis=-1)
        return result


class ChatbotEngine:
    """
    NLP-powered chatbot engine for tax filing assistance.

    Pipeline:
    Input → Tokenize → TF-IDF Embed → Attention → Intent Classify → Entity Extract → Response Generate
    """

    def __init__(self, intents_path: str = None):
        self.tokenizer = TaxTokenizer()
        self.vectorizer = TfidfVectorizer(
            max_features=3000, ngram_range=(1, 2),
            stop_words='english', sublinear_tf=True
        ) if SKLEARN_AVAILABLE else None
        self.intent_classifier = None
        self.label_encoder = LabelEncoder() if SKLEARN_AVAILABLE else None
        self.attention = None
        self.is_trained = False
        self.intents_data = {}

        # Conversation state
        self.conversation_history: List[Dict] = []
        self.context = ""
        self.user_data: Dict = {}

        if intents_path:
            self.load_intents(intents_path)

    def load_intents(self, path: str):
        """Load intent definitions from JSON."""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
                self.intents_data = {
                    intent['tag']: intent for intent in data.get('intents', [])
                }
        except Exception as e:
            print(f"Error loading intents: {e}")

    def train(self, intents_path: str = None, save_path: str = None) -> Dict:
        """Train the intent classification model."""
        if not SKLEARN_AVAILABLE:
            return {"error": "scikit-learn not installed"}

        if intents_path:
            self.load_intents(intents_path)

        if not self.intents_data:
            return {"error": "No intents data loaded"}

        # Prepare training data
        texts = []
        labels = []
        for tag, intent in self.intents_data.items():
            for pattern in intent.get('patterns', []):
                texts.append(pattern)
                labels.append(tag)
                # Data augmentation
                tokens = pattern.split()
                if len(tokens) > 3:
                    augmented = tokens[:]
                    random.shuffle(augmented)
                    texts.append(' '.join(augmented))
                    labels.append(tag)

        if not texts:
            return {"error": "No training patterns found"}

        # TF-IDF vectorization
        X = self.vectorizer.fit_transform(texts).toarray()
        y = self.label_encoder.fit_transform(labels)

        # Initialize attention layer
        self.attention = AttentionLayer(X.shape[1])

        # Apply attention
        X_attended = np.array([
            self.attention.compute_attention(x.reshape(1, -1)).flatten()[:X.shape[1] * 2]
            for x in X
        ])

        # Pad to uniform size
        max_dim = max(len(x) for x in X_attended)
        X_padded = np.zeros((len(X_attended), max_dim))
        for i, x in enumerate(X_attended):
            X_padded[i, :len(x)] = x

        # Neural network classifier
        self.intent_classifier = MLPClassifier(
            hidden_layer_sizes=(128, 64, 32),
            activation='relu',
            solver='adam',
            alpha=0.001,
            max_iter=500,
            early_stopping=True,
            validation_fraction=0.15,
            random_state=42
        )

        self.intent_classifier.fit(X_padded, y)

        self.is_trained = True
        self.training_metrics = {
            'n_intents': len(set(labels)),
            'n_patterns': len(texts),
            'architecture': 'MLP(128-64-32) with Attention',
            'vectorizer': 'TF-IDF (3000 features, 1-2 grams)'
        }

        if save_path:
            self.save_model(save_path)

        return self.training_metrics

    def classify_intent(self, text: str) -> Tuple[str, float]:
        """Classify the intent of user input."""
        if not self.is_trained:
            return self._rule_based_intent(text)

        # Vectorize
        X = self.vectorizer.transform([text]).toarray()

        # Apply attention with context
        X_attended = self.attention.compute_attention(X)

        # Pad to match training dimensions
        expected_dim = self.intent_classifier.coefs_[0].shape[0]
        X_padded = np.zeros((1, expected_dim))
        X_padded[0, :min(X_attended.shape[1], expected_dim)] = X_attended[0, :expected_dim]

        # Predict
        prediction = self.intent_classifier.predict(X_padded)[0]
        probabilities = self.intent_classifier.predict_proba(X_padded)[0]

        intent = self.label_encoder.inverse_transform([prediction])[0]
        confidence = float(max(probabilities)) * 100

        # Low confidence → fallback
        if confidence < 40:
            return 'default_fallback', confidence

        return intent, confidence

    def _rule_based_intent(self, text: str) -> Tuple[str, float]:
        """Fallback rule-based intent classification."""
        text_lower = text.lower().strip()

        intent_keywords = {
            'greeting': ['hello', 'hi', 'hey', 'namaste', 'good morning', 'good evening'],
            'goodbye': ['bye', 'goodbye', 'see you', 'quit', 'exit'],
            'thanks': ['thanks', 'thank you', 'appreciate', 'helpful'],
            'tax_regime': ['regime', 'old regime', 'new regime', 'which regime', 'compare regime'],
            'tax_calculation': ['calculate', 'tax amount', 'tax liability', 'compute tax', 'how much tax'],
            'deductions': ['deduction', '80c', '80d', 'save tax', 'investment', 'tax saving'],
            'filing_process': ['file tax', 'filing', 'itr', 'how to file', 'filing process', 'steps'],
            'document_upload': ['upload', 'document', 'form 16', 'salary slip', 'scan'],
            'what_if': ['what if', 'simulator', 'simulate', 'scenario'],
            'hra_query': ['hra', 'house rent', 'rent allowance'],
            'audit_risk': ['audit', 'audit risk', 'audited'],
            'tax_terms': ['what is', 'define', 'meaning', 'explain', 'glossary']
        }

        best_intent = 'default_fallback'
        best_score = 0

        for intent, keywords in intent_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > best_score:
                best_score = score
                best_intent = intent

        confidence = min(85, best_score * 30 + 20) if best_score > 0 else 15

        return best_intent, confidence

    def process_message(self, user_message: str) -> Dict:
        """
        Process a user message and generate a response.

        Full NLP Pipeline:
        1. Tokenize input
        2. Extract entities (amounts, sections, dates)
        3. Classify intent
        4. Generate contextual response
        5. Update conversation state
        """
        # Step 1: Tokenize
        tokens = self.tokenizer.tokenize(user_message)

        # Step 2: Extract entities
        entities = self.tokenizer.extract_entities(user_message)
        amounts = self.tokenizer.extract_amounts(user_message)

        # Update user data from entities
        if amounts:
            self.user_data['last_mentioned_amount'] = amounts[-1]
        if 'section' in entities:
            self.user_data['last_mentioned_section'] = entities['section'][-1]

        # Step 3: Classify intent
        intent, confidence = self.classify_intent(user_message)

        # Step 4: Generate response
        response = self._generate_response(intent, confidence, entities, amounts, user_message)

        # Step 5: Update conversation state
        self.conversation_history.append({
            'role': 'user',
            'message': user_message,
            'timestamp': datetime.now().isoformat(),
            'intent': intent,
            'confidence': confidence,
            'entities': entities
        })

        self.conversation_history.append({
            'role': 'assistant',
            'message': response['response'],
            'timestamp': datetime.now().isoformat(),
            'intent': intent
        })

        # Update context
        if intent in self.intents_data:
            intent_context = self.intents_data[intent].get('context', '')
            if intent_context:
                self.context = intent_context

        return {
            'response': response['response'],
            'intent': intent,
            'confidence': round(confidence, 2),
            'entities': entities,
            'amounts_detected': amounts,
            'context': self.context,
            'suggestions': response.get('suggestions', []),
            'nlp_details': {
                'tokens': tokens[:20],
                'n_tokens': len(tokens),
                'intent_method': 'neural_network' if self.is_trained else 'rule_based'
            }
        }

    def _generate_response(
        self, intent: str, confidence: float,
        entities: Dict, amounts: List[float], user_message: str
    ) -> Dict:
        """Generate a contextual response based on classified intent."""
        # Get template responses
        if intent in self.intents_data:
            responses = self.intents_data[intent].get('responses', [])
            base_response = random.choice(responses) if responses else "I can help you with that!"
        else:
            base_response = "I can help you with tax-related queries. Try asking about tax calculation, deductions, regime comparison, or filing steps."

        # Context-aware response augmentation
        augmented = base_response

        # Add amount-specific context
        if amounts and intent in ['tax_calculation', 'what_if']:
            augmented += f"\n\nI noticed you mentioned ₹{amounts[-1]:,.0f}. I'll use this in my calculations."

        # Add section-specific info
        if 'section' in entities and intent == 'deductions':
            section = entities['section'][0]
            augmented += f"\n\nYou mentioned Section {section}. Let me provide specific details about this deduction."

        # Suggestions based on intent
        suggestions = self._get_suggestions(intent)

        return {
            'response': augmented,
            'suggestions': suggestions
        }

    def _get_suggestions(self, current_intent: str) -> List[str]:
        """Generate follow-up suggestions based on current intent."""
        suggestion_map = {
            'greeting': [
                "Calculate my tax",
                "Compare tax regimes",
                "Help me file taxes",
                "What deductions can I claim?"
            ],
            'tax_regime': [
                "Calculate tax under old regime",
                "Calculate tax under new regime",
                "What deductions are available?",
                "What's my tax liability?"
            ],
            'tax_calculation': [
                "Compare with other regime",
                "Recommend deductions",
                "Check audit risk",
                "Run what-if scenario"
            ],
            'deductions': [
                "How much can I save?",
                "Tell me about 80C options",
                "NPS tax benefit",
                "Calculate my tax"
            ],
            'filing_process': [
                "Let's start filing",
                "Upload my Form 16",
                "Which ITR form do I need?",
                "What documents do I need?"
            ],
            'default_fallback': [
                "Calculate my tax",
                "Help me with deductions",
                "Compare tax regimes",
                "Start filing process"
            ]
        }

        return suggestion_map.get(current_intent, suggestion_map['default_fallback'])

    def reset_conversation(self):
        """Reset the conversation state."""
        self.conversation_history = []
        self.context = ""
        self.user_data = {}

    def get_history(self) -> List[Dict]:
        """Get conversation history."""
        return self.conversation_history

    def save_model(self, path: str):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        model_data = {
            'intent_classifier': self.intent_classifier,
            'vectorizer': self.vectorizer,
            'label_encoder': self.label_encoder,
            'attention_W_q': self.attention.W_q if self.attention else None,
            'attention_W_k': self.attention.W_k if self.attention else None,
            'attention_W_v': self.attention.W_v if self.attention else None,
            'attention_dim': self.attention.feature_dim if self.attention else None,
        }
        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

    def load_model(self, path: str) -> bool:
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            self.intent_classifier = model_data['intent_classifier']
            self.vectorizer = model_data['vectorizer']
            self.label_encoder = model_data['label_encoder']
            if model_data.get('attention_dim'):
                self.attention = AttentionLayer(model_data['attention_dim'])
                self.attention.W_q = model_data['attention_W_q']
                self.attention.W_k = model_data['attention_W_k']
                self.attention.W_v = model_data['attention_W_v']
            self.is_trained = True
            return True
        except Exception as e:
            print(f"Error loading chatbot model: {e}")
            return False


# Module-level instance
chatbot_engine = ChatbotEngine()
