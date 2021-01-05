from django.conf.urls import url
from incoming.views import views
from django.conf.urls.static import static
from django.conf import settings

app_name = 'incoming'

urlpatterns = [
    url(r'^apply/creator/$', views.IncomingApplyCreator.as_view(), name='apply_creator'),
    url(r'^apply/delete/$', views.incoming_apply_delete, name='apply_delete'),
    url(r'^apply/update/$', views.incoming_apply_update, name='apply_update'),
    url(r'^apply/search/$', views.incoming_search_data, name='apply_search'),
    url(r'^apply/paginator/$', views.incoming_paginator_data, name='apply_paginator'),
    url(r'^apply/submit/$', views.incoming_apply_submit, name='apply_submit'),
    url(r'^apply/approve/$', views.incoming_apply_approve, name='apply_approve'),
    url(r'^apply/accessory/uploading/$', views.incoming_accessory_uploading,
        name='apply_accessory_uploading'),
    url(r'^apply/accessory/delete/$', views.incoming_accessory_delete,
        name='apply_accessory_delete'),
    url(r'^apply/accessory/download/$', views.incoming_accessory_download,
        name='apply_accessory_download'),

]
#  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
