from django.contrib import admin
from .models import Historia, Rating, Comentario, Favorito, Reporte, Perfil

admin.site.register(Perfil)
admin.site.register(Historia)
admin.site.register(Rating)
admin.site.register(Comentario)
admin.site.register(Favorito)
admin.site.register(Reporte)