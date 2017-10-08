from django.contrib import admin
from checklist.models import CheckList, CheckListItem

admin.site.register(CheckList)
admin.site.register(CheckListItem)