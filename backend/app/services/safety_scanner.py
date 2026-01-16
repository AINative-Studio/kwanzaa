"""
Safety Scanner Service

Implements PII detection and content moderation for uploaded documents.
Required by Issue #38 - Safety Integration
"""

from typing import List, Dict, Any
from pydantic import BaseModel
from enum import Enum
import re


class PIIType(str, Enum):
    EMAIL = "email"
    PHONE = "phone"
    SSN = "ssn"
    CREDIT_CARD = "credit_card"
    ADDRESS = "address"
    NAME = "name"


class PIIMatch(BaseModel):
    type: PIIType
    value: str
    start: int
    end: int
    confidence: float


class ModerationCategory(str, Enum):
    HATE_SPEECH = "hate_speech"
    VIOLENCE = "violence"
    SEXUAL = "sexual"
    HARASSMENT = "harassment"
    SELF_HARM = "self_harm"
    SPAM = "spam"


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ModerationResult(BaseModel):
    category: ModerationCategory
    detected: bool
    confidence: float
    severity: Severity
    details: str = None


class SafetyScanResult(BaseModel):
    pii_matches: List[PIIMatch]
    moderation_results: List[ModerationResult]
    passed: bool


class SafetyScanner:
    """
    Safety scanner for PII detection and content moderation.
    """

    # PII detection patterns
    PII_PATTERNS = {
        PIIType.EMAIL: re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        PIIType.PHONE: re.compile(r'\b(\+?1?[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
        PIIType.SSN: re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
        PIIType.CREDIT_CARD: re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'),
    }

    # Content moderation keywords (in production, use ML model)
    MODERATION_KEYWORDS = {
        ModerationCategory.HATE_SPEECH: ['hate', 'racist', 'bigot', 'slur'],
        ModerationCategory.VIOLENCE: ['kill', 'murder', 'attack', 'assault'],
        ModerationCategory.SEXUAL: ['explicit', 'pornographic', 'sexual'],
        ModerationCategory.HARASSMENT: ['bully', 'threaten', 'harass', 'stalk'],
        ModerationCategory.SELF_HARM: ['suicide', 'self-harm', 'cutting'],
        ModerationCategory.SPAM: ['buy now', 'click here', 'limited offer', 'act now'],
    }

    async def scan(self, text: str) -> SafetyScanResult:
        """
        Perform comprehensive safety scan on text.

        Args:
            text: Document text to scan

        Returns:
            SafetyScanResult with PII and moderation findings
        """
        pii_matches = self._detect_pii(text)
        moderation_results = self._moderate_content(text)

        # Determine if document passed
        critical_issues = any(
            r.detected and r.severity == Severity.CRITICAL
            for r in moderation_results
        )
        passed = not critical_issues

        return SafetyScanResult(
            pii_matches=pii_matches,
            moderation_results=moderation_results,
            passed=passed,
        )

    def _detect_pii(self, text: str) -> List[PIIMatch]:
        """Detect PII in text using regex patterns."""
        matches = []

        for pii_type, pattern in self.PII_PATTERNS.items():
            for match in pattern.finditer(text):
                matches.append(PIIMatch(
                    type=pii_type,
                    value=match.group(0),
                    start=match.start(),
                    end=match.end(),
                    confidence=0.9,  # Could be improved with ML
                ))

        return sorted(matches, key=lambda m: m.start)

    def _moderate_content(self, text: str) -> List[ModerationResult]:
        """
        Perform content moderation.

        In production, this should use a trained ML model.
        This implementation uses keyword matching for demonstration.
        """
        text_lower = text.lower()
        results = []

        for category, keywords in self.MODERATION_KEYWORDS.items():
            matches = [kw for kw in keywords if kw.lower() in text_lower]
            detected = len(matches) > 0
            confidence = min(0.5 + len(matches) * 0.2, 0.95) if detected else 0.1

            # Determine severity based on confidence
            if confidence > 0.8:
                severity = Severity.CRITICAL
            elif confidence > 0.6:
                severity = Severity.HIGH
            elif confidence > 0.4:
                severity = Severity.MEDIUM
            else:
                severity = Severity.LOW

            results.append(ModerationResult(
                category=category,
                detected=detected,
                confidence=confidence,
                severity=severity,
                details=f"Found keywords: {', '.join(matches)}" if detected else None,
            ))

        return results

    async def redact_pii(self, text: str, pii_matches: List[PIIMatch]) -> str:
        """
        Redact PII from text.

        Args:
            text: Original text
            pii_matches: List of PII matches to redact

        Returns:
            Redacted text
        """
        if not pii_matches:
            return text

        result = list(text)
        for match in sorted(pii_matches, key=lambda m: m.start, reverse=True):
            # Replace with redacted placeholder
            redaction = f"[{match.type.upper()}_REDACTED]"
            result[match.start:match.end] = list(redaction)

        return ''.join(result)
