import datetime
from django.db import models


# There are many different data sets that are updated. Keep track of them here. 
# options are "scrape_electronic_filings", "scrape_new_committees",... 
class Update_Time(models.Model):
    key = models.SlugField()
    update_time = models.DateTimeField()

    def save(self, *args, **kwargs):
        ''' On save, update timestamps '''
        self.update_time = datetime.datetime.today()
        super(Update_Time, self).save(*args, **kwargs)
        
