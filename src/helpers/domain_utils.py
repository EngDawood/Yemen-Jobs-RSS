#  RSS to Telegram Bot - Domain Utilities
#  Copyright (C) 2025  Eng. Dawood
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as
#  published by the Free Software Foundation, either version 3 of the
#  License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <https://www.gnu.org/licenses/>.

from __future__ import annotations
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse
import re
from functools import lru_cache

from ..db import DomainSettings


class DomainUtils:
    """Utility class for handling domain-specific operations."""

    @staticmethod
    @lru_cache(maxsize=512)
    def extract_domain(url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc.lower()
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except Exception:
            return ""

    @staticmethod
    async def get_domain_settings(domain: str) -> Optional[DomainSettings]:
        """Get domain settings for a specific domain."""
        try:
            settings = await DomainSettings.filter(domain=domain, enabled=True).first()
            return settings
        except Exception:
            return None

    @staticmethod
    def merge_domain_settings(base_settings: Dict[str, Any],
                            domain_settings: Optional[DomainSettings]) -> Dict[str, Any]:
        """Merge domain-specific settings with base settings."""
        if not domain_settings:
            return base_settings

        merged = base_settings.copy()

        # Override settings with domain-specific values
        if domain_settings.send_mode != 0:  # 0 is default/auto
            merged['send_mode'] = domain_settings.send_mode
        if domain_settings.display_author != 0:
            merged['display_author'] = domain_settings.display_author
        if domain_settings.display_via != 0:
            merged['display_via'] = domain_settings.display_via
        if domain_settings.style != 0:
            merged['style'] = domain_settings.style
        if domain_settings.media_handling != 'auto':
            merged['display_media'] = DomainUtils._media_handling_to_int(domain_settings.media_handling)

        return merged

    @staticmethod
    def _media_handling_to_int(media_handling: str) -> int:
        """Convert media handling string to integer value."""
        mapping = {
            'auto': 0,
            'include': 0,
            'exclude': -1,
            'only_media': 1
        }
        return mapping.get(media_handling, 0)

    @staticmethod
    def apply_content_filters(content: str, filters: Optional[Dict[str, Any]]) -> str:
        """Apply content filtering rules to post content."""
        if not filters:
            return content

        filtered_content = content

        # Remove patterns
        if 'remove_patterns' in filters:
            for pattern in filters['remove_patterns']:
                try:
                    filtered_content = re.sub(pattern, '', filtered_content, flags=re.IGNORECASE | re.MULTILINE)
                except re.error:
                    continue  # Skip invalid regex patterns

        # Replace patterns
        if 'replace_patterns' in filters:
            for replacement in filters['replace_patterns']:
                if isinstance(replacement, dict) and 'pattern' in replacement and 'replacement' in replacement:
                    try:
                        filtered_content = re.sub(
                            replacement['pattern'],
                            replacement['replacement'],
                            filtered_content,
                            flags=re.IGNORECASE | re.MULTILINE
                        )
                    except re.error:
                        continue

        # Clean up extra whitespace
        filtered_content = re.sub(r'\n\s*\n\s*\n', '\n\n', filtered_content)
        filtered_content = filtered_content.strip()

        return filtered_content

    @staticmethod
    def apply_title_template(title: str, template: Optional[str], feed_title: str = "") -> str:
        """Apply custom title template if available."""
        if not template:
            return title

        try:
            # Replace placeholders in template
            formatted_title = template.replace('{title}', title)
            formatted_title = formatted_title.replace('{feed_title}', feed_title)
            return formatted_title
        except Exception:
            return title

    @staticmethod
    def get_domain_hashtags(domain: str, base_hashtags: List[str],
                          domain_hashtags: Optional[List[str]]) -> List[str]:
        """Merge domain-specific hashtags with base hashtags."""
        if not domain_hashtags:
            return base_hashtags

        # Combine and deduplicate
        all_hashtags = base_hashtags + domain_hashtags
        return list(set(all_hashtags))  # Remove duplicates while preserving order

    @staticmethod
    def is_job_site_domain(domain: str) -> bool:
        """Check if domain is a job-related website."""
        job_keywords = ['job', 'career', 'employment', 'recruit', 'hr', 'hiring', 'vacancy']
        domain_lower = domain.lower()

        return any(keyword in domain_lower for keyword in job_keywords)

    @staticmethod
    def is_news_site_domain(domain: str) -> bool:
        """Check if domain is a news website."""
        news_keywords = ['news', 'times', 'post', 'journal', 'gazette', 'herald']
        domain_lower = domain.lower()

        return any(keyword in domain_lower for keyword in news_keywords)

    @staticmethod
    def get_default_domain_settings(domain: str) -> Dict[str, Any]:
        """Get default settings for common domain types."""
        if DomainUtils.is_job_site_domain(domain):
            return {
                'send_mode': 0,  # Auto
                'display_author': 1,  # Force display author (company name)
                'display_via': 0,  # Auto
                'style': 0,  # RSStT style
                'display_media': 0,  # Enable media
                'hashtags': ['#Jobs', '#Employment']
            }
        elif DomainUtils.is_news_site_domain(domain):
            return {
                'send_mode': 0,  # Auto
                'display_author': 0,  # Auto
                'display_via': 1,  # Force display via
                'style': 0,  # RSStT style
                'display_media': 0,  # Enable media
                'hashtags': ['#News']
            }

        # Default settings
        return {
            'send_mode': 0,
            'display_author': 0,
            'display_via': 0,
            'style': 0,
            'display_media': 0,
            'hashtags': []
        }
