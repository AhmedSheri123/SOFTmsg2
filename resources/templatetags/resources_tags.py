from django import template
from django.template.defaultfilters import stringfilter
from resources.models import SectionContentsModel, DocsServicesModel
from django.contrib.auth.models import User

register = template.Library()

@register.simple_tag
@stringfilter
def get_contents_by_section(section_id):
    contents = SectionContentsModel.objects.filter(section__id=section_id).order_by('ordering')
    return contents


@register.simple_tag
@stringfilter
def get_doc_services(section_id):
    doc_services = DocsServicesModel.objects.filter().order_by('ordering')
    return doc_services