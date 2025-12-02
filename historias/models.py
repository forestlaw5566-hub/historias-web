from django.db import models
from django.contrib.auth.models import User

class Historia(models.Model):
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField()
    contenido = models.TextField()
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    vistas = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.titulo


class Rating(models.Model):
    historia = models.ForeignKey(Historia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    estrellas = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ("historia", "usuario")


class Comentario(models.Model):
    historia = models.ForeignKey(Historia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    texto = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)


class Favorito(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    historia = models.ForeignKey(Historia, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("usuario", "historia")


class Reporte(models.Model):
    historia = models.ForeignKey(Historia, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    motivo = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(
        max_length=20,
        choices=[
            ("lector", "Lector"),
            ("autor", "Autor"),
            ("moderador", "Moderador")
        ],
        default="lector"
    )

    def __str__(self):
        return self.user.username
    
class Notificacion(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    mensaje = models.CharField(max_length=250)
    leido = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.mensaje