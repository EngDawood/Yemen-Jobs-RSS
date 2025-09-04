#  RSS to Telegram Bot - Domain Management Commands
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
import json

from .. import db
from ..i18n import i18n
from ..helpers.domain_utils import DomainUtils
from . import inner
from .types import CommandFunc
from .utils import PrivateMessage, get_commands_list


async def cmd_set_domain_settings(event, domain: str = None, **kwargs) -> str:
    """Set domain-specific settings for RSS feeds from a particular domain."""
    user_id = event.sender_id
    user = await db.User.filter(id=user_id).first()

    if not user or user.state < 100:  # Only admins can manage domain settings
        return i18n[user.lang if user else 'en']['domain']['not_authorized']

    if not domain:
        return i18n[user.lang]['domain']['domain_required']

    # Extract domain from URL if full URL provided
    if '://' in domain:
        domain = DomainUtils.extract_domain(domain)

    if not domain:
        return i18n[user.lang]['domain']['invalid_domain']

    # Get existing settings or create new
    domain_settings = await db.DomainSettings.filter(domain=domain).first()
    if not domain_settings:
        domain_settings = db.DomainSettings(domain=domain)

    # For now, return a message asking for settings via callback
    # In a full implementation, this would parse additional parameters
    return i18n[user.lang]['domain']['settings_menu'].format(domain=domain)


async def cmd_list_domain_settings(event, **kwargs) -> str:
    """List all configured domain settings."""
    user_id = event.sender_id
    user = await db.User.filter(id=user_id).first()

    if not user or user.state < 100:  # Only admins can view domain settings
        return i18n[user.lang if user else 'en']['domain']['not_authorized']

    domain_settings = await db.DomainSettings.filter(enabled=True).all()

    if not domain_settings:
        return i18n[user.lang]['domain']['no_settings']

    response = i18n[user.lang]['domain']['settings_list_header'] + "\n\n"

    for setting in domain_settings:
        response += f"🌐 {setting.domain}\n"
        if setting.custom_title_template:
            response += f"  📝 Title: {setting.custom_title_template}\n"
        if setting.hashtag_filter:
            hashtags = ', '.join(setting.hashtag_filter)
            response += f"  #️⃣ Hashtags: {hashtags}\n"
        if setting.send_mode != 0:
            response += f"  📤 Send Mode: {setting.send_mode}\n"
        response += "\n"

    return response


async def cmd_remove_domain_settings(event, domain: str = None, **kwargs) -> str:
    """Remove domain-specific settings."""
    user_id = event.sender_id
    user = await db.User.filter(id=user_id).first()

    if not user or user.state < 100:  # Only admins can manage domain settings
        return i18n[user.lang if user else 'en']['domain']['not_authorized']

    if not domain:
        return i18n[user.lang]['domain']['domain_required']

    # Extract domain from URL if full URL provided
    if '://' in domain:
        domain = DomainUtils.extract_domain(domain)

    domain_settings = await db.DomainSettings.filter(domain=domain).first()
    if not domain_settings:
        return i18n[user.lang]['domain']['settings_not_found'].format(domain=domain)

    await domain_settings.delete()
    return i18n[user.lang]['domain']['settings_removed'].format(domain=domain)


async def cmd_get_domain_info(event, url: str = None, **kwargs) -> str:
    """Get information about a domain and its current settings."""
    user_id = event.sender_id
    user = await db.User.filter(id=user_id).first()

    if not user:
        user = await db.User.get_or_create(id=user_id, defaults={'lang': 'en'})

    if not url:
        return i18n[user.lang]['domain']['url_required']

    domain = DomainUtils.extract_domain(url)
    if not domain:
        return i18n[user.lang]['domain']['invalid_domain']

    # Get domain settings
    domain_settings = await db.DomainSettings.filter(domain=domain, enabled=True).first()

    response = i18n[user.lang]['domain']['domain_info'].format(domain=domain) + "\n\n"

    # Domain type detection
    if DomainUtils.is_job_site_domain(domain):
        response += "🏢 " + i18n[user.lang]['domain']['job_site'] + "\n"
    elif DomainUtils.is_news_site_domain(domain):
        response += "📰 " + i18n[user.lang]['domain']['news_site'] + "\n"
    else:
        response += "📄 " + i18n[user.lang]['domain']['general_site'] + "\n"

    if domain_settings:
        response += "\n" + i18n[user.lang]['domain']['custom_settings'] + ":\n"
        if domain_settings.custom_title_template:
            response += f"📝 {i18n[user.lang]['domain']['title_template']}: {domain_settings.custom_title_template}\n"
        if domain_settings.hashtag_filter:
            hashtags = ', '.join(domain_settings.hashtag_filter)
            response += f"#️⃣ {i18n[user.lang]['domain']['hashtags']}: {hashtags}\n"
        if domain_settings.send_mode != 0:
            response += f"📤 {i18n[user.lang]['domain']['send_mode']}: {domain_settings.send_mode}\n"
        if domain_settings.display_author != 0:
            response += f"👤 {i18n[user.lang]['domain']['author_display']}: {domain_settings.display_author}\n"
    else:
        response += "\n" + i18n[user.lang]['domain']['no_custom_settings']

    # Default settings for this domain type
    default_settings = DomainUtils.get_default_domain_settings(domain)
    if default_settings['hashtags']:
        response += f"\n{i18n[user.lang]['domain']['suggested_hashtags']}: {' '.join(default_settings['hashtags'])}"

    return response


# Command registration
def register_domain_commands():
    """Register domain management commands."""
    return {
        'set_domain': cmd_set_domain_settings,
        'list_domains': cmd_list_domain_settings,
        'remove_domain': cmd_remove_domain_settings,
        'domain_info': cmd_get_domain_info,
    }


# Export commands for main command handler
domain_commands = register_domain_commands()
