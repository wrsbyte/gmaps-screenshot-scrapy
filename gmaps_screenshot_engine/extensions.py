import json
from datetime import datetime

import psycopg2
from scrapy import Spider, signals
from scrapy.crawler import Crawler
from scrapy.statscollectors import StatsCollector
from typing_extensions import Self

from gmaps_screenshot_engine.services import PostgresService


def map_json(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()

    return obj


class PostgresStatsExtension:
    def __init__(self, stats: StatsCollector, postgres_service):
        self.postgres_service = postgres_service
        self.conn = None
        self.cursor = None
        self.stats: StatsCollector = stats

    @classmethod
    def from_crawler(cls, crawler: Crawler) -> Self:
        assert crawler.stats

        settings = crawler.settings
        postgres_service = PostgresService(
            host=settings.get("POSTGRES_HOST"),
            port=settings.get("POSTGRES_PORT"),
            user=settings.get("POSTGRES_USER"),
            password=settings.get("POSTGRES_PASSWORD"),
            database=settings.get("POSTGRES_DB"),
        )

        o = cls(crawler.stats, postgres_service)
        crawler.signals.connect(o.spider_closed, signal=signals.spider_closed)
        crawler.signals.connect(o.spider_opened, signal=signals.spider_opened)

        return o

    def spider_opened(self, spider: Spider) -> None:
        try:
            self.conn = self.postgres_service.connect()
            self.cursor = self.conn.cursor()
            spider.logger.info("🟢 [PostgresStatsExtension] connection established")
        except psycopg2.Error as e:
            spider.logger.error(f"🔴 [PostgresStatsExtension] Error on connection: {e}")
            raise

    def spider_closed(self, spider, reason):
        spider.logger.info("👋 spider closed")
        stats = self.stats.get_stats()

        try:
            insert_query = """
            INSERT INTO scrapy_run_stats
            (
                job_id,
                started_at,
                finished_at,
                elapsed_time_seconds,
                item_scraped_count,
                finish_reason,
                responses_per_minute,
                items_per_minute,
                stats
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
            self.cursor.execute(
                insert_query,
                (
                    stats.get("job_id"),
                    stats.get("start_time"),
                    stats.get("finish_time"),
                    stats.get("elapsed_time_seconds"),
                    stats.get("item_scraped_count"),
                    stats.get("finish_reason"),
                    stats.get("responses_per_minute"),
                    stats.get("items_per_minute"),
                    json.dumps(stats, default=map_json),
                ),
            )

            self.conn.commit()
            spider.logger.info(
                f"✅ [PostgresStatsExtension] Stats inserted/updated: {stats.get('job_id')}"
            )
        except psycopg2.Error as e:
            spider.logger.error(
                f"❌ [PostgresStatsExtension] Error on insert stats: {e}"
            )
            self.conn.rollback()
        finally:
            if self.cursor:
                self.cursor.close()
            if self.conn:
                self.conn.close()
                spider.logger.info("🔴 [PostgresStatsExtension] connection closed")
