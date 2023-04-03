from django.db import models

class InputData(models.Model):

    store_id = models.BigIntegerField()
    store_day = models.IntegerField(choices=[(i, i) for i in range(6)])
    start_time_local = models.TimeField(default='00:00:00')
    end_time_local =  models.TimeField(default='23:59:59')

    def __str__(self):
        return f"InputData(id={self.store_id}, store_id={self.store_day}, start_time_local={self.start_time_local})"