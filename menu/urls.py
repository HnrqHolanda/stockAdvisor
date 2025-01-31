from django.urls import path
from . import views

urlpatterns = [
    path('monitoramento', views.monitoramento, name='monitoramento'),
    path('registros', views.registros, name='registros'), 
    path('opções', views.opções, name='opções'),  
    path('logout/', views.customlogout, name='logout'),
    path('atualizar_dict_ativo/', views.atualizar_dict_ativo, name='atualizar_dict_ativo'),
    path('atualizar_dict_cotacao/', views.atualizar_dict_cotacao, name='atualizar_dict_cotacao'),
    path('get_cotacao/', views.get_cotacao, name='get_cotacao'), 
]