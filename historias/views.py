from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg
from .models import Notificacion

from .models import Historia, Rating, Comentario, Favorito

def index(request):
    historias = Historia.objects.all()

    top_historias = (
        Historia.objects
        .annotate(promedio=Avg("rating__estrellas"))
        .order_by("-promedio").first()
    )

    top_vistas = Historia.objects.order_by('-vistas').first()

    return render(request, "historias/index.html", {
        "historias": historias,
        "top_historias": top_historias,
        "top_vistas": top_vistas,
    })

def leer_historia(request, id):
    historia = get_object_or_404(Historia, id=id)
    
    historia.vistas += 1
    historia.save(update_fields=["vistas"])

    ratings = Rating.objects.filter(historia=historia)
    promedio = ratings.aggregate(Avg("estrellas"))["estrellas__avg"]
    promedio = round(promedio, 1) if promedio else None

    comentarios = Comentario.objects.filter(historia=historia).order_by("-fecha")

    voto_usuario = None
    es_favorito = False

    if request.user.is_authenticated:
        voto_usuario = Rating.objects.filter(historia=historia, usuario=request.user).first()
        es_favorito = Favorito.objects.filter(usuario=request.user, historia=historia).exists()

    return render(request, "historias/leer.html", {
        "historia": historia,
        "promedio": promedio,
        "voto_usuario": voto_usuario,
        "es_favorito": es_favorito,
        "comentarios": comentarios,
    })


def publicar(request):
    if request.user.perfil.rol != 'autor':
        return HttpResponseForbidden("Solo los autores pueden publicar.")

    if request.method == "POST":
        Historia.objects.create(
            titulo=request.POST["titulo"],
            autor=request.user,
            descripcion=request.POST["descripcion"],
            contenido=request.POST["contenido"]
        )
        return redirect("index")

    return render(request, "historias/publicar.html")

def borrar_historia(request, id):
    historia = get_object_or_404(Historia, id=id)
    rol = request.user.perfil.rol

    if rol == "lector":
        return HttpResponseForbidden("No puedes borrar historias.")

    if rol == "autor" and historia.autor != request.user:
        return HttpResponseForbidden("No puedes borrar historias de otros autores.")

    historia.delete()
    return redirect("index")

def registro(request):
    if request.method == "POST":
        usuario = request.POST["username"]
        mail = request.POST.get("email", "")
        pass1 = request.POST["password"]
        rol = request.POST["rol"]

        user = User.objects.create_user(username=usuario, email=mail, password=pass1)

        user.perfil.rol = rol
        user.perfil.save()

        return redirect("login")

    return render(request, "registro.html")

@login_required
def perfil(request):
    mis_historias = []
    favoritos = []
    notificaciones = []


    if request.user.perfil.rol in ["autor", "moderador"]:
        mis_historias = Historia.objects.filter(autor=request.user)

    favoritos = Favorito.objects.filter(usuario=request.user)


    notificaciones = Notificacion.objects.filter(usuario=request.user).order_by("-fecha")

    return render(request, "historias/perfil.html", {
        "mis_historias": mis_historias,
        "favoritos": favoritos,
        "notificaciones": notificaciones,
    })

@login_required
def editar_historia(request, id):
    historia = get_object_or_404(Historia, id=id)
    rol = request.user.perfil.rol

    if rol == "lector":
        return HttpResponseForbidden("No puedes editar historias.")

    if rol == "autor" and historia.autor != request.user:
        return HttpResponseForbidden("No puedes editar historias de otros.")

    if request.method == "POST":
        historia.titulo = request.POST["titulo"]
        historia.descripcion = request.POST["descripcion"]
        historia.contenido = request.POST["contenido"]
        historia.save()
        return redirect("perfil")

    return render(request, "historias/editar.html", {"historia": historia})

@login_required
def votar_historia(request, id):
    historia = get_object_or_404(Historia, id=id)

    if request.user.perfil.rol == "autor" and historia.autor == request.user:
        return HttpResponseForbidden("No puedes votar tu propia historia.")

    if request.method == "POST":
        estrellas = int(request.POST["estrellas"])
        Rating.objects.update_or_create(
            historia=historia,
            usuario=request.user,
            defaults={"estrellas": estrellas}
        )

        if historia.autor != request.user:
            Notificacion.objects.create(
                usuario=historia.autor,
                mensaje=f"{request.user.username} votó tu historia '{historia.titulo}'"
            )

        return redirect("leer", id=historia.id)
    
@login_required
def comentar(request, id):
    historia = get_object_or_404(Historia, id=id)

    if request.method == "POST":
        texto = request.POST["comentario"]
        comentario = Comentario.objects.create(
            historia=historia,
            usuario=request.user,
            texto=texto
        )

        # Notificar al autor
        if historia.autor != request.user:
            Notificacion.objects.create(
                usuario=historia.autor,
                mensaje=f"{request.user.username} comentó tu historia '{historia.titulo}'"
            )

        return redirect("leer", id=historia.id)

@login_required
def toggle_favorito(request, id):
    historia = get_object_or_404(Historia, id=id)

    fav, created = Favorito.objects.get_or_create(
        usuario=request.user,
        historia=historia
    )

    if not created:
        fav.delete()

    return redirect("leer", id=historia.id)
from .models import Reporte

@login_required
def panel_moderacion(request):
    if request.user.perfil.rol != "moderador":
        return HttpResponseForbidden("Acceso solo para moderadores.")

    reportes = Reporte.objects.all().order_by("-fecha")
    return render(request, "historias/moderacion.html", {"reportes": reportes})

@login_required
def reportar(request, id):
    historia = get_object_or_404(Historia, id=id)

    if request.method == "POST":
        Reporte.objects.create(
            historia=historia,
            usuario=request.user,
            motivo=request.POST["motivo"]
        )

        moderadores = User.objects.filter(perfil__rol="moderador")

        for mod in moderadores:
            Notificacion.objects.create(
                usuario=mod,
                mensaje=f"{request.user.username} reportó la historia '{historia.titulo}'"
            )

        return redirect("leer", id=historia.id)

@login_required
def borrar_comentario(request, id):
    comentario = get_object_or_404(Comentario, id=id)

    # Si es autor del comentario o moderador → permitido
    if comentario.usuario == request.user or request.user.perfil.rol == "moderador":
        historia_id = comentario.historia.id
        comentario.delete()
        return redirect("leer", id=historia_id)

    return HttpResponseForbidden("No puedes borrar este comentario.")
