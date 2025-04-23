from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('create/', views.create_task, name='create_task'),
    path('list/<str:slave_name>/', views.list_tasks_slave, name='list_tasks_slave'),
    path('stop/<str:container_name>/', views.stop_container, name='stop_container'),
    path('start/<str:container_name>/', views.start_container, name='start_container'),
    path('esquema/', views.esquema_dinamico, name='esquema_dinamico'),

    
]

