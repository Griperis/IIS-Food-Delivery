from django import template
import datetime

register = template.Library()

@register.filter
def fac_is_open(facility):
    now = datetime.datetime.now().time()
    return now >= facility.opening_time and facility.closing_time <= now
