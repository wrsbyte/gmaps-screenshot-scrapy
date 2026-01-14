from datetime import datetime

import scrapy


class ScreenshotItem(scrapy.Item):
    target_location_id = scrapy.Field()
    parent_folder = scrapy.Field()
    file_path = scrapy.Field()
    size = scrapy.Field()
    job_id = scrapy.Field()
    captured_at = scrapy.Field(default=datetime.now())
