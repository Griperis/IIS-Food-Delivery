from django import template
import datetime

register = template.Library()

@register.filter
def fac_is_open(facility):
    if facility.opening_time == facility.closing_time:
        return True
    now = datetime.datetime.now().time()
    print(now, facility.opening_time, facility.closing_time)
    if facility.opening_time < now:
        return facility.opening_time <= now < facility.closing_time
    else:
        return facility.opening_time <= now or now <= facility.closing_time

@register.filter
def print_opening_hours(facility):
    if facility.opening_time == facility.closing_time:
        return 'Nonstop'
    else:
        return facility.opening_time.strftime('%H:%M') + ' - ' + facility.closing_time.strftime('%H:%M')