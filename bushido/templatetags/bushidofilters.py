from django import template

register = template.Library()


@register.filter
def formatTrait(trait):
    return trait.trait.full.replace("X", trait.X).replace("Y", trait.Y).replace("Descriptor", trait.descriptor).replace("Bonus", trait.descriptor)


@register.filter
def addBrackets(text):
    if len(text) == 0:
        return ""
    return "("+text+")"
