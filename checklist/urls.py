from checklist import views
from django.conf.urls import url

app_name="checklist"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^all$', views.all, name='all'),
    url(r'ajax/item_check$', views.item_check, name='ajax_item_check'),
    url(r'^complete[d]?$', views.complete, name='complete'),
    url(r'^(?P<checklist_id>[0-9]+)$', views.checklist_view, name="view"),
    url(r'^(?P<checklist_id>[0-9]+)/edit$', views.checklist_edit, name="edit"),
    url(r'^postedit$', views.post_edit, name="post_edit"),
    url(r'^new$', views.new_checklist, name="new"),
]