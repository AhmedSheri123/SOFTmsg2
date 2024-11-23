from django.contrib import admin
from .models import DocsServiceSectionsModel, DocsServicesModel, SectionContentsModel

# Register your models here.
admin.site.register(DocsServiceSectionsModel)
admin.site.register(DocsServicesModel)
admin.site.register(SectionContentsModel)