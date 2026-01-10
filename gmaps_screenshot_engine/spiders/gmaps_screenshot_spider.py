import scrapy

from gmaps_screenshot_engine.services import (
    GMapsUrlService,
    PostgresService,
    TargetLocationService,
)
from gmaps_screenshot_engine.models import TargetLocationModel


class GmapsScreenshotSpider(scrapy.Spider):
    name = "gmaps-screenshot-spider"
    allowed_domains = [
        "google.com",
        "google.com.mx",
        "google.com.co",
    ]
    start_urls = ["https://google.com"]

    async def start(self):
        crawler = self.crawler
        settings = crawler.settings

        target_location_service = TargetLocationService(
            postgres_service=PostgresService(
                host=settings.get("POSTGRES_HOST"),
                port=settings.get("POSTGRES_PORT"),
                user=settings.get("POSTGRES_USER"),
                password=settings.get("POSTGRES_PASSWORD"),
                database=settings.get("POSTGRES_DB"),
            )
        )

        urls = target_location_service.get_targets()
        for url in urls:
            self.logger.info(
                f" 🪂 Send to process {url.name} [{url.latitude}, {url.longitude}]"
            )
            yield scrapy.Request(
                url=GMapsUrlService.generate(
                    base_url=settings.get("GMAPS_BASE_URL"),
                    target_location=url,
                ),
                callback=self.parse,
                meta=url.model_dump(),
            )

    def parse(self, response):
        target_location = TargetLocationModel(**response.meta)

        self.logger.info(f" 🪂 Process {target_location.model_dump()}")

        return {
            "name": target_location.name,
        }
