from django.db import models

class TimeZone(models.Model):
    store_id = models.IntegerField(primary_key=True)
    time_zone = models.CharField(max_length=50)

    def __str__(self):
        return f"InputData(id={self.store_id}, time_zone={self.time_zone})"