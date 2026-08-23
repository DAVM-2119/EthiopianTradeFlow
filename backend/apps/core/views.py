from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db import connection
from django.core.cache import cache

class HealthCheckView(APIView):
    """
    Health Check API verifying Django backend, PostgreSQL/PostGIS, and Redis connections.
    """
    permission_classes = []

    def get(self, request, *args, **kwargs):
        health_details = {
            "status": "healthy",
            "services": {
                "django": "healthy",
                "database": "unknown",
                "postgis": "unknown",
                "redis": "unknown",
            }
        }
        overall_healthy = True

        # 1. Check PostgreSQL & PostGIS
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1;")
                cursor.fetchone()
                health_details["services"]["database"] = "healthy"

                # Check PostGIS extension
                try:
                    cursor.execute("SELECT PostGIS_Version();")
                    postgis_version = cursor.fetchone()
                    if postgis_version:
                        health_details["services"]["postgis"] = f"healthy ({postgis_version[0]})"
                    else:
                        health_details["services"]["postgis"] = "unhealthy (version check empty)"
                        overall_healthy = False
                except Exception as pg_err:
                    health_details["services"]["postgis"] = f"unhealthy ({str(pg_err)})"
                    overall_healthy = False
        except Exception as db_err:
            health_details["services"]["database"] = f"unhealthy ({str(db_err)})"
            health_details["services"]["postgis"] = "unhealthy (db connection failed)"
            overall_healthy = False

        # 2. Check Redis
        try:
            cache.set("health_check_key", "ok", timeout=10)
            val = cache.get("health_check_key")
            if val == "ok":
                health_details["services"]["redis"] = "healthy"
            else:
                health_details["services"]["redis"] = "unhealthy (cache get mismatch)"
                overall_healthy = False
        except Exception as redis_err:
            health_details["services"]["redis"] = f"unhealthy ({str(redis_err)})"
            overall_healthy = False

        if not overall_healthy:
            health_details["status"] = "unhealthy"
            return Response(health_details, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        return Response(health_details, status=status.HTTP_200_OK)
