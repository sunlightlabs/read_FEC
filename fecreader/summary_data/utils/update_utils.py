from summary_data.models import Update_Time


def set_update(key):
    this_key, created = Update_Time.objects.get_or_create(key=key)
    this_key.save()

def get_update_time(key):
    this_key = Update_Time.objects.get(key=key)
    return this_key.update_time
