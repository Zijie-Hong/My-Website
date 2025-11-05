from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('tasks/', views.task_list, name='task_list'),
    path('projects/', views.project_list, name='project_list'),
    path('projects/<int:project_id>/tasks/', views.task_list, name='project_tasks'),
    path('projects/<int:project_id>/tasks/<int:task_id>/', views.task_detail, name='task_detail'),
    path('projects/<int:project_id>/tasks/<int:task_id>/edit/', views.edit_task, name='edit_task'),
    path('projects/<int:project_id>/tasks/<int:task_id>/delete/', views.delete_task, name='delete_task'),
    path('projects/<int:project_id>/tasks/<int:task_id>/update-process/', views.update_task_process, name='update_task_process'),
    path('projects/<int:project_id>/', views.project_detail, name='project_detail'),
    path('projects/<int:project_id>/add_task/', views.add_task, name='add_task'),
    path('about/', views.about, name='about'),
    path('test-workshop-stats/', views.test_workshop_stats, name='test_workshop_stats'),
    # 图片上传和获取的URL
    path('projects/<int:project_id>/tasks/<int:task_id>/upload-image/', views.upload_task_image, name='upload_task_image'),
    path('projects/<int:project_id>/tasks/<int:task_id>/images/', views.get_task_images, name='get_task_images'),
]