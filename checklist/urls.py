from checklist import views
from django.conf.urls import url

app_name="checklist"

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^all$', views.all, name='all'),
    url(r'ajax/item_check$', views.item_check, name='ajax_item_check'),
    url(r'ajax/emailvalidate$', views.emailvalidate, name="ajax_emailvalidate"),
    url(r'^complete[d]?$', views.complete, name='complete'),
    url(r'^(?P<checklist_id>[0-9]+)$', views.checklist_view, name="view"),
    url(r'^(?P<checklist_id>[0-9]+)/edit$', views.checklist_edit, name="edit"),
    url(r'^postedit$', views.post_edit, name="post_edit"),
    url(r'^new$', views.new_checklist, name="new"),
    url(r'^register$', views.register, name='register'),
    url(r'^registrationresult$', views.register_result, name='register_result'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^login(?P<errors>_err)$', views.login_view, name='login_error'),
    url(r'^loginresult$', views.login_result, name='login_result'),
]