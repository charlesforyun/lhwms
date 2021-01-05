from django.conf.urls import url
from django.contrib import admin
from .views import loginlog, syslog, errlog


urlpatterns = [
    url(r'^loginlog$', loginlog.loginlog, name='loginlog'), 
    url(r'^loginlog/search_data$', loginlog.search_data, name='loginlog_search_data'), 
    url(r'^loginlog/load_data$', loginlog.load_data, name='loginlog_load_data'), 
    url(r'^loginlog/export_excel$', loginlog.export_excel, name='loginlog_export_excel'), 

    url(r'^syslog/search_data$', syslog.search_data, name='syslog_search_data'), 
    url(r'^syslog/load_data$', syslog.load_data, name='syslog_load_data'), 
    url(r'^syslog/export_excel$', syslog.export_excel, name='syslog_export_excel'), 

    url(r'^errlog/search_data$', errlog.search_data, name='errlog_search_data'), 
    url(r'^errlog/load_data$', errlog.load_data, name='errlog_load_data'), 
    url(r'^errlog/export_excel$', errlog.export_excel, name='errlog_export_excel'), 
]