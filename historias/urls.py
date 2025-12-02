from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("historia/<int:id>/", views.leer_historia, name="leer"),
    path("publicar/", views.publicar, name="publicar"),
    path("borrar/<int:id>/", views.borrar_historia, name="borrar"),
    path("registro/", views.registro, name="registro"),
    path("perfil/", views.perfil, name="perfil"),
    path("editar/<int:id>/", views.editar_historia, name="editar"),
    path("votar/<int:id>/", views.votar_historia, name="votar"),
    path("comentar/<int:id>/", views.comentar, name="comentar"),
    path("favorito/<int:id>/", views.toggle_favorito, name="favorito"),
    path("moderacion/", views.panel_moderacion, name="moderacion"),
    path("reportar/<int:id>/", views.reportar, name="reportar"),
    path("borrar-comentario/<int:id>/", views.borrar_comentario, name="borrar_comentario"),
]
