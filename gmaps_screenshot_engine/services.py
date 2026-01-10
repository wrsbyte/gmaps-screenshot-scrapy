from urllib.parse import urlencode

import psycopg2

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
            """)

            targets = cursor.fetchall()
            conn.close()

            return [
                TargetLocationModel(
                    id=target[0],
                    name=target[1],
                    description=target[2],
                    address=target[3],
                    link=target[4],
                    latitude=target[5],
                    longitude=target[6],
                    gmaps_zoom=target[7],
                    gmaps_extra_params=target[8],
                    active=target[9],
                    created_at=target[10],
                    updated_at=target[11],
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
            "zoom": target_location.gmaps_zoom,
            "data": "!5m1!1e1",
            "entry": "ttu",
        }

        if target_location.gmaps_extra_params:
            params.update(target_location.gmaps_extra_params)

        return f"{base_url}/maps/@{target_location.latitude},{target_location.longitude},{target_location.gmaps_zoom}z?{urlencode(params)}"
