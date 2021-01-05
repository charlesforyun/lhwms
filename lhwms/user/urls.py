from django.conf.urls import url
from django.contrib import admin
from .views import index, group, user

urlpatterns = [
    url(r'^menu_all$', index.menu_all, name='menu_all'),
    url(r'^menu_per$', index.menu_per, name='menu_per'),

    url(r'^group$', group.group, name='group'),
    url(r'^group/add$', group.add, name='group_add'),
    url(r'^group/del$', group.delete, name='group_del'),
    url(r'^group/edit$', group.edit, name='group_edit'),
    url(r'^group/allow$', group.allow, name='group_allow'),
    url(r'^group/forbid$', group.forbid, name='group_forbid'),
    url(r'^group/search_data$', group.search_data, name='group_search_data'),
    url(r'^group/load_data$', group.load_data, name='group_load_data'),
    url(r'^group/down_excel_template$', group.down_excel_template,
        name='group_down_excel_template'),
    url(r'^group/upload_excel$', group.upload_excel, name='group_upload_excel'),
    url(r'^group/import_data$', group.import_data, name='group_import_data'),
    url(r'^group/export_excel$', group.export_excel, name='group_export_excel'),
    url(r'^group/lists$', group.lists, name='group_lists'),

    url(r'^user$', user.user, name='user'),
    url(r'^user/add$', user.add, name='user_add'),
    url(r'^user/del$', user.delete, name='user_del'),
    url(r'^user/edit$', user.edit, name='user_edit'),
    url(r'^user/allow$', user.allow, name='user_allow'),
    url(r'^user/forbid$', user.forbid, name='user_forbid'),
    url(r'^user/search_data$', user.search_data, name='user_search_data'),
    url(r'^user/load_data$', user.load_data, name='user_load_data'),
    url(r'^user/down_excel_template$', user.down_excel_template,
        name='user_down_excel_template'),
    url(r'^user/upload_excel$', user.upload_excel, name='user_upload_excel'),
    url(r'^user/import_data$', user.import_data, name='user_import_data'),
    url(r'^user/export_excel$', user.export_excel, name='user_export_excel'),
    url(r'^user/set_password$', user.set_password, name='user_set_password'),
    url(r'^user/reset_password$', user.reset_password,
        name='user_reset_password'),
]
