from django import template
import django

register = template.Library()


@register.filter
def addBrackets(text):
    if len(text) == 0:
        return ""
    return "("+text+")"


@register.filter
def className(model):
    classNames = {
        "Unit": "Model",
        "KiFeat": "Feat"
    }
    return classNames.get(model.__class__.__name__, model.__class__.__name__)
