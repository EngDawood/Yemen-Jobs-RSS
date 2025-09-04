#  RSS to Telegram Bot - Domain Settings Migration
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

from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "domain_settings" (
            "id" INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
            "created_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "updated_at" TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            "domain" VARCHAR(255) NOT NULL UNIQUE,
            "custom_title_template" VARCHAR(1024),
            "hashtag_filter" JSON,
            "content_filter" JSON,
            "media_handling" VARCHAR(32) NOT NULL DEFAULT 'auto',
            "send_mode" SMALLINT NOT NULL DEFAULT 0,
            "display_author" SMALLINT NOT NULL DEFAULT 0,
            "display_via" SMALLINT NOT NULL DEFAULT 0,
            "style" SMALLINT NOT NULL DEFAULT 0,
            "enabled" INT NOT NULL DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS "idx_domain_settings_domain" ON "domain_settings" ("domain");
        CREATE INDEX IF NOT EXISTS "idx_domain_settings_enabled" ON "domain_settings" ("enabled");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        DROP TABLE IF EXISTS "domain_settings";"""
