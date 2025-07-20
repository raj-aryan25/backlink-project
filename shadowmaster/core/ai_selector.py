"""
AI-powered selector inference for ShadowMaster Framework
Uses GPT-4o to infer optimal selectors when traditional methods fail.
"""

import json
import hashlib
import logging
from typing import Dict, Any, Optional, List
import asyncio
import os
from dataclasses import dataclass

# Optional imports
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False

try:
    import redis
    HAS_REDIS = True
except ImportError:
    HAS_REDIS = False

logger = logging.getLogger(__name__)


@dataclass
class SelectorRecommendation:
    """Data class for AI selector recommendations."""
    preferred: str
    fallback: str
    confidence: float
    reasoning: str
    selector_type: str  # css, xpath, text, role


class AISelector:
    """AI-powered selector inference and caching."""

    def __init__(self, api_key: Optional[str] = None, redis_url: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.redis_client = None
        self.cache_ttl = 3600  # 1 hour

        # Initialize OpenAI client
        if HAS_OPENAI and self.api_key:
            openai.api_key = self.api_key
            self.openai_enabled = True
            logger.info("OpenAI client initialized")
        else:
            self.openai_enabled = False
            logger.warning("OpenAI not available - AI features disabled")

        # Initialize Redis cache
        if HAS_REDIS and redis_url:
            try:
                self.redis_client = redis.from_url(redis_url)
                self.redis_client.ping()  # Test connection
                logger.info("Redis cache initialized")
            except Exception as e:
                logger.warning(f"Redis cache not available: {e}")
                self.redis_client = None

    async def get_best_locator(self, html_snippet: str, target_description: str,
                              context: Optional[str] = None) -> Optional[SelectorRecommendation]:
        """
        Get AI-powered selector recommendation.

        Args:
            html_snippet: HTML content around the target element
            target_description: Human description of what to find
            context: Additional context about the page/action

        Returns:
            SelectorRecommendation with AI suggestions
        """
        if not self.openai_enabled:
            logger.warning("AI selector inference not available")
            return None

        # Check cache first
        cache_key = self._get_cache_key(html_snippet, target_description)
        cached_result = await self._get_from_cache(cache_key)
        if cached_result:
            logger.info("Using cached AI selector recommendation")
            return cached_result

        try:
            # Prepare prompt
            prompt = self._build_selector_prompt(html_snippet, target_description, context)

            # Call OpenAI API
            response = await self._call_openai_api(prompt)

            if response:
                recommendation = self._parse_ai_response(response)

                # Cache the result
                await self._save_to_cache(cache_key, recommendation)

                logger.info(f"AI selector recommendation: {recommendation.preferred}")
                return recommendation

        except Exception as e:
            logger.error(f"Error getting AI selector recommendation: {e}")

        return None

    async def infer_shadow_selectors(self, page_html: str, 
                                   shadow_description: str) -> List[Dict[str, str]]:
        """
        Infer Shadow DOM selectors using AI.

        Args:
            page_html: Full page HTML content
            shadow_description: Description of shadow elements to find

        Returns:
            List of dictionaries with host and inner selectors
        """
        if not self.openai_enabled:
            return []

        prompt = f"""
        Analyze this HTML and identify Shadow DOM structures that match: {shadow_description}

        HTML:
        {page_html[:5000]}  # Truncate for API limits

        Return JSON with format:
        {{
            "shadow_paths": [
                {{
                    "host_selector": "css-selector-for-host",
                    "inner_selector": "css-selector-inside-shadow",
                    "description": "what this selector finds",
                    "confidence": 0.95
                }}
            ]
        }}

        Focus on elements that likely contain Shadow DOM (web components, custom elements).
        """

        try:
            response = await self._call_openai_api(prompt)
            if response:
                result = json.loads(response)
                return result.get("shadow_paths", [])
        except Exception as e:
            logger.error(f"Error inferring shadow selectors: {e}")

        return []

    def _build_selector_prompt(self, html_snippet: str, target_description: str,
                              context: Optional[str] = None) -> str:
        """Build the prompt for AI selector inference."""
        context_part = f"\nContext: {context}" if context else ""

        return f"""
        You are an expert at creating robust web selectors. Analyze this HTML and suggest the best selectors for the target element.

        Target: {target_description}{context_part}

        HTML:
        {html_snippet}

        Return JSON with this exact format:
        {{
            "preferred": "css-selector-or-xpath",
            "fallback": "alternative-selector",
            "confidence": 0.95,
            "reasoning": "why this selector is reliable",
            "selector_type": "css|xpath|text|role"
        }}

        Guidelines:
        1. Prefer CSS selectors over XPath when possible
        2. Use data attributes, IDs, or semantic roles when available
        3. Avoid fragile selectors based on DOM structure
        4. Consider accessibility attributes (aria-*, role)
        5. Provide fallback for dynamic content
        """

    async def _call_openai_api(self, prompt: str) -> Optional[str]:
        """Call OpenAI API with error handling and retry logic."""
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = await asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model="gpt-4o",
                    messages=[
                        {"role": "system", "content": "You are an expert web automation engineer."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=500,
                    temperature=0.1
                )

                return response.choices[0].message.content.strip()

            except Exception as e:
                logger.warning(f"OpenAI API attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error("All OpenAI API attempts failed")

        return None

    def _parse_ai_response(self, response: str) -> SelectorRecommendation:
        """Parse AI response into SelectorRecommendation object."""
        try:
            data = json.loads(response)
            return SelectorRecommendation(
                preferred=data.get("preferred", ""),
                fallback=data.get("fallback", ""),
                confidence=data.get("confidence", 0.5),
                reasoning=data.get("reasoning", ""),
                selector_type=data.get("selector_type", "css")
            )
        except json.JSONDecodeError:
            logger.error("Failed to parse AI response as JSON")
            return SelectorRecommendation(
                preferred="",
                fallback="",
                confidence=0.0,
                reasoning="Parse error",
                selector_type="css"
            )

    def _get_cache_key(self, html_snippet: str, target_description: str) -> str:
        """Generate cache key for HTML and description."""
        content = f"{html_snippet}|{target_description}"
        return f"ai_selector:{hashlib.md5(content.encode()).hexdigest()}"

    async def _get_from_cache(self, cache_key: str) -> Optional[SelectorRecommendation]:
        """Get selector recommendation from cache."""
        if not self.redis_client:
            return None

        try:
            cached_data = await asyncio.to_thread(self.redis_client.get, cache_key)
            if cached_data:
                data = json.loads(cached_data)
                return SelectorRecommendation(**data)
        except Exception as e:
            logger.warning(f"Cache read error: {e}")

        return None

    async def _save_to_cache(self, cache_key: str, recommendation: SelectorRecommendation):
        """Save selector recommendation to cache."""
        if not self.redis_client:
            return

        try:
            data = {
                "preferred": recommendation.preferred,
                "fallback": recommendation.fallback,
                "confidence": recommendation.confidence,
                "reasoning": recommendation.reasoning,
                "selector_type": recommendation.selector_type
            }

            await asyncio.to_thread(
                self.redis_client.setex,
                cache_key,
                self.cache_ttl,
                json.dumps(data)
            )
        except Exception as e:
            logger.warning(f"Cache write error: {e}")


# Global AI selector instance
_ai_selector_instance = None


def get_ai_selector() -> Optional[AISelector]:
    """Get global AI selector instance."""
    global _ai_selector_instance
    if _ai_selector_instance is None:
        _ai_selector_instance = AISelector()
    return _ai_selector_instance


async def get_smart_selector(html_snippet: str, target_description: str) -> str:
    """Convenience function to get AI-powered selector."""
    ai_selector = get_ai_selector()
    if ai_selector:
        recommendation = await ai_selector.get_best_locator(html_snippet, target_description)
        if recommendation and recommendation.confidence > 0.7:
            return recommendation.preferred

    # Fallback to simple heuristics
    return _fallback_selector_inference(html_snippet, target_description)


def _fallback_selector_inference(html_snippet: str, target_description: str) -> str:
    """Simple fallback selector inference without AI."""
    target_lower = target_description.lower()

    # Simple keyword-based selector suggestions
    if "button" in target_lower:
        return "button, [role='button'], input[type='submit']"
    elif "input" in target_lower or "field" in target_lower:
        return "input, textarea, [contenteditable]"
    elif "link" in target_lower:
        return "a, [role='link']"
    elif "close" in target_lower or "dismiss" in target_lower:
        return "[aria-label*='close'], [aria-label*='dismiss'], .close"
    else:
        return "*"  # Last resort
