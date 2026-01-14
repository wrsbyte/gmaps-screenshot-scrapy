import uuid

import scrapy

from gmaps_screenshot_engine.items import ScreenshotItem
from gmaps_screenshot_engine.models import TargetLocationModel
from gmaps_screenshot_engine.services import (
    CompressImageService,
    GMapsUrlService,
    PostgresService,
    S3SaverImageService,
    TargetLocationService,
)


class GmapsScreenshotSpider(scrapy.Spider):
    name = "gmaps-screenshot-spider"
    allowed_domains = [
        "google.com",
    ]
    start_urls = ["https://google.com"]

    async def start(self):
        crawler = self.crawler
        settings = crawler.settings

        job_id = str(uuid.uuid4())

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
                meta={
                    "playwright": True,
                    "playwright_include_page": True,
                    "job_id": job_id,
                    **url.model_dump(),
                },
            )

    async def parse(self, response):
        target_location = TargetLocationModel(**response.meta)

        page = response.meta["playwright_page"]
        job_id = response.meta["job_id"]

        await page.set_viewport_size(
            {
                "width": 1280,
                "height": 720,
            }
        )
        screenshot_bytes = await page.screenshot(
            full_page=True,
            type="png",
        )

        file_name = f"{target_location.id}__{target_location.name.lower().replace(' ', '-')}__{target_location.latitude}_{target_location.longitude}__{target_location.gmaps_zoom}z"

        file_path = f"{target_location.folder}/{job_id}/{file_name}.jpg"

        compress_image, size = CompressImageService.compress(
            image_bytes=screenshot_bytes,
        )

        await page.close()

        S3SaverImageService.save(
            file_path=file_path,
            image=compress_image,
        )

        self.logger.info(f" 🪂 Process {target_location.model_dump()}")

        return ScreenshotItem(
            target_location_id=target_location.id,
            parent_folder=target_location.folder,
            file_path=file_path,
            size=0,
            job_id=job_id,
        )
