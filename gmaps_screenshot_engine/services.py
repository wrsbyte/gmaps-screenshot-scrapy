import io
import os
from urllib.parse import urlencode

import boto3
import psycopg2
from PIL import Image

from gmaps_screenshot_engine.models import TargetLocationModel


class PostgresService:
    def __init__(self, host, port, user, password, database):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        return psycopg2.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )


class TargetLocationService:
    def __init__(self, postgres_service: PostgresService):
        self.postgres_service = postgres_service

    def get_targets(self) -> list[TargetLocationModel]:
        """Get all target locations from the database.

        Returns:
            list[TargetLocationModel]: List of target locations.
        """

        try:
            conn = self.postgres_service.connect()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    id,
                    name,
                    description,
                    folder,
                    address,
                    link,
                    latitude,
                    longitude,
                    gmaps_zoom,
                    gmaps_extra_params,
                    active,
                    created_at,
                    updated_at
                FROM target_locations
                WHERE active = true
            """)

            targets = cursor.fetchall()
            conn.close()

            return [
                TargetLocationModel(
                    id=target[0],
                    name=target[1],
                    description=target[2],
                    folder=target[3],
                    address=target[4],
                    link=target[5],
                    latitude=target[6],
                    longitude=target[7],
                    gmaps_zoom=target[8],
                    gmaps_extra_params=target[9],
                    active=target[10],
                    created_at=target[11],
                    updated_at=target[12],
                )
                for target in targets
            ]
        except Exception as e:
            print("❌ Error getting targets", e)
            raise RuntimeError("Error getting targets") from e
        finally:
            if conn:
                conn.close()


class GMapsUrlService:
    @classmethod
    def generate(cls, base_url: str, target_location: TargetLocationModel):
        """Generate a Google Maps URL for a target location.

        Args:
            base_url (str): The base URL of the Google Maps website.
            target_location (TargetLocationModel): The target location.

        Returns:
            str: The Google Maps URL for the target location.

        Example:
            A result of this function will be https://www.google.com.mx/maps/@20.6852493,-103.4423015,21z/data=!5m1!1e1?entry=ttu
        """

        params = {
            "entry": "ttu",
        }

        if target_location.gmaps_extra_params:
            params.update(target_location.gmaps_extra_params)

        return f"{base_url}/maps/@{target_location.latitude},{target_location.longitude},{target_location.gmaps_zoom}z/data=!5m1!1e1?{urlencode(params)}"


class LocalSaverImageService:
    @classmethod
    def save(cls, file_path: str, image: Image.Image):
        """Save an image to a local file path, creating directories if they don't exist."""
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        image.save(
            file_path,
            format="JPEG",
            quality=70,
            optimize=True,
            progressive=True,
            subsampling=0,
        )


class S3SaverImageService:
    @classmethod
    def save(cls, file_path: str, image: Image.Image):
        """Save an image to a S3 bucket."""
        buffer = io.BytesIO()
        image.save(
            buffer,
            format="JPEG",
            quality=70,
            optimize=True,
            progressive=True,
            subsampling=0,
        )

        buffer.seek(0)

        s3_client = boto3.client(
            "s3",
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
            region_name=os.getenv("AWS_REGION"),
        )

        s3_client.upload_fileobj(
            Fileobj=buffer,
            Bucket=os.getenv("AWS_BUCKET_NAME"),
            Key=file_path,
        )


class CompressImageService:
    @classmethod
    def compress(cls, image_bytes: bytes):
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")

        image = image.resize((854, 480), Image.Resampling.LANCZOS)

        image = image.quantize(
            colors=128,
            method=Image.Quantize.FASTOCTREE,
            dither=Image.Dither.NONE,
        )
        image = image.convert("RGB")

        new_disk_size = image.size

        return image, new_disk_size
