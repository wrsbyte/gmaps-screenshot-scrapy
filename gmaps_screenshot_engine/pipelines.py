import psycopg2
from itemadapter import ItemAdapter

from gmaps_screenshot_engine.services import PostgresService


class GmapsScreenshotsPostgresExportPipeline:
    def __init__(self, postgres_service):
        self.postgres_service = postgres_service
        self.conn = None
        self.cursor = None

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        postgres_service = PostgresService(
            host=settings.get("POSTGRES_HOST"),
            port=settings.get("POSTGRES_PORT"),
            user=settings.get("POSTGRES_USER"),
            password=settings.get("POSTGRES_PASSWORD"),
            database=settings.get("POSTGRES_DB"),
        )

        return cls(
            postgres_service=postgres_service,
        )

    def open_spider(self, spider):
        try:
            self.conn = self.postgres_service.connect()
            self.cursor = self.conn.cursor()
            spider.logger.info(
                "🟢 [GmapsScreenshotsPostgresExportPipeline] connection established"
            )
        except psycopg2.Error as e:
            spider.logger.error(
                f"🔴 [GmapsScreenshotsPostgresExportPipeline] Error on connection: {e}"
            )
            raise

    def process_item(self, item, spider):
        try:
            adapter = ItemAdapter(item)

            insert_query = """
            INSERT INTO gmaps_screenshots (
                target_location_id,
                parent_folder,
                file_path,
                size,
                job_id
            )
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (file_path) DO NOTHING;
            """

            self.cursor.execute(
                insert_query,
                (
                    adapter.get("target_location_id"),
                    adapter.get("parent_folder"),
                    adapter.get("file_path"),
                    adapter.get("size"),
                    adapter.get("job_id"),
                ),
            )

            self.conn.commit()
            spider.logger.info(
                f"✅ [GmapsScreenshotsPostgresExportPipeline] Item inserted/updated: {adapter.get('file_path')}"
            )

        except psycopg2.Error as e:
            spider.logger.error(
                f"❌ [GmapsScreenshotsPostgresExportPipeline] Error on insert item: {e}"
            )
            self.conn.rollback()

        return item

    def close_spider(self, spider):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            spider.logger.info(
                "🔴 [GmapsScreenshotsPostgresExportPipeline] connection closed"
            )
