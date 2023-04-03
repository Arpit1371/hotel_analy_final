from django.db import models

class StoreStatus(models.Model):
    store_id = models.BigIntegerField()
    status = models.CharField(max_length=10)
    timestamp_utc = models.DateTimeField()

    def __str__(self):
        return f"StoreStatus(store_id={self.store_id}, status={self.status}, timestamp_utc={self.timestamp_utc})"
