from django.db import models
from datetime import date


## TODO: replace this with something that doesn't hit the db. At this point the traffic should be low and it's not much of a concern. 
## also we're not pushing the stats anywhere... 


class logreport(models.Model):
    date = models.DateField()
    apikey = models.CharField(max_length=63)
    count = models.IntegerField()
    
    

def ApiLogIncrement(apikey):
    """ increment today's calls from an apikey. Assumes that the client api key has already been filtered out. Returns daily calls."""
    today = date.today()
    try:
        report = logreport.objects.get(apikey=apikey, date=today)
        report.count += 1
        report.save()
        return report.count
    except logreport.DoesNotExist:
        newreport = logreport(date=today, apikey=apikey, count=1)
        newreport.save()
        return 1
