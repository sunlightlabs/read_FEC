from django.db import models

# Create your models here.

class HouseRace(models.Model):
    state = models.CharField(max_length=2)
    district = models.IntegerField(help_text="they use integers for districts; at-large = 1")
    rating_id = models.IntegerField()
    rating_label = models.CharField(max_length=63)
    incumbent = models.CharField(max_length=127)
    update_time = models.DateTimeField(auto_now=True)
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    
    
    class Meta:
        unique_together = ("state", "district", "cycle")
    
class SenateRace(models.Model):
    state = models.CharField(max_length=2)
    seat_class = models.CharField(max_length=4, help_text="they use roman numerals for 1-3")
    rating_id = models.IntegerField()
    rating_segment = models.CharField(max_length=63, help_text="they use roman numerals for 1-3")
    rating_label = models.CharField(max_length=63)
    incumbent = models.CharField(max_length=127)
    update_time = models.DateTimeField(auto_now=True)
    cycle = models.CharField(max_length=4, blank=True, null=True, help_text="text cycle; even number.")
    
    
    class Meta:
        unique_together = ("state", "seat_class", "cycle")