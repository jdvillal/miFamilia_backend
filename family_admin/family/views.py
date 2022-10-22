from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from ast import Return, Try
from logging import RootLogger
from multiprocessing.sharedctypes import Value
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from .models import UserProfile
from .models import *
from .permisionHandler import validarPermisosUsuario, validarPermisoUsuario, PERMISOS, GRUPOS, checkUserHasPermission
import json
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.core.mail import EmailMessage, BadHeaderError, send_mail, send_mass_mail
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from rest_framework import serializers
from django.db import transaction
import datetime
import re
# Create your views here.


@login_required(login_url='/')
def content(request):
    return render(request, 'views/contenido.html')


@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.GALERIA, [PERMISOS.VER, PERMISOS.EDITAR, PERMISOS.ELIMINAR])
def view_eliminar_galeria(request):
    videos = Videos_galeria.objects.filter(estado=1)
    imagenes = Imagenes_galeria.objects.filter(estado=1)

    if request.method == 'POST':
        try:
            titulo = request.POST['titulo']
            descripcion = request.POST['descripcion']
            id_ = request.POST['id']
            tipo = request.POST['tipo']

            if tipo == 'imagen':
                imagen = Imagenes_galeria.objects.filter(id=id_).first()
                imagen.fecha = datetime.datetime.now()
                if request.FILES.get('imagen'):
                    imagen.image = request.FILES['imagen']
                imagen.save()
                imagen.id_galeria.titulo = titulo
                imagen.id_galeria.descripcion = descripcion
                imagen.id_galeria.save()
            if tipo == "video":
                video = Videos_galeria.objects.filter(id=id_).first()
                video.fecha = datetime.datetime.now()
                if request.FILES.get('video'):
                    video.video = request.FILE['video']
                video.save()
                video.id_galeria.titulo = titulo
                video.id_galeria.descripcion = descripcion
                video.id_galeria.save()

            return render(request, 'views/galeria/eliminar_galeria.html', {'videos': videos, 'imagenes': imagenes, 'modal': True, 'mess': 'actualizado correctamente'})
        except Exception as e:
            print('Error: ', e)
            return render(request, 'views/galeria/eliminar_galeria.html', {'videos': videos, 'imagenes': imagenes, 'modal': True, 'mess': 'Error al actualizar'})

    return render(request, 'views/galeria/eliminar_galeria.html', {'videos': videos, 'imagenes': imagenes})


def view_registrar_nosotros(request):
    if request.method == 'POST':
        try:
            nosotros = Nosotros(
                nombre_completo=request.POST['nombre'], estudios=request.POST['estudio'], image=request.FILES['image'])
            nosotros.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Registrado exitosamente.')
        except Exception as e:
            print(e)
            messages.add_message(request, messages.ERROR,
                                 'Error al registrar.')
            return redirect('registrar_nosotros')
    return render(request, 'views/registros/registrar_nosotros.html')


@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.ROLES, [PERMISOS.VER, PERMISOS.EDITAR])
def view_roles(request):
    roles = Rol.objects.filter(estado=1)
    categorias = Grupo_Permiso.objects.all()
    permisos = Permiso.objects.all()
    rolPermisos = Rol_Permiso.objects.select_related().all()

    rol_permiso = dict()
    for rol in roles:
        rol_permiso[rol.nombre] = dict()
        for categoria in categorias:
            rolesPermisoCategoria = rolPermisos.filter( id_rol=rol, id_grupo_permiso=categoria)
            rol_permiso[rol.nombre][categoria.nombre] = list( map(lambda x: x.id_permiso.nombre, rolesPermisoCategoria))

    return render(request, 'views/roles/index.html', {'permisos': permisos, 'rol_permiso': rol_permiso})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.USUARIOS, PERMISOS.CREAR)
def view_crear_usuario(request):
    if request.method == 'POST':
        try:
            nombre = request.POST['nombre_usuario'].upper()
            apellidos = request.POST['apellidos_usuario'].upper()
            usuario = request.POST['usuario']
            correo = request.POST['correo']
            fecha_nacimiento = request.POST['fecha_nacimiento']
            cedula = request.POST['cedula']
            telefono = request.POST['telefono']
            sexo = request.POST['sexo']

            user = UserProfile(fecha_nacimiento=fecha_nacimiento,
                               telefono=telefono, sexo=sexo, cedula=cedula)
            if request.FILES.get('foto'):
                user.foto = request.FILES['foto']
            user.first_name = nombre
            user.last_name = apellidos
            user.email = correo
            user.username = usuario
            # la contraseña es el mismo usuario al crear la cuenta
            user.set_password(usuario)
            # unique email
            if UserProfile.objects.filter(email=correo).all().__len__() != 0:
                return render(request, 'views/usuarios/crear.html', {'modal': True, 'mess': 'No se pudo crear usario. El correo \"'+correo + "\" no esta disponible"})
            if UserProfile.objects.filter(username=usuario).all().__len__() != 0:
                return render(request, 'views/usuarios/crear.html', {'modal': True, 'mess': 'No se pudo crear usario. El nombre de usuario \"'+usuario + "\" no esta disponible"})
            user.save()
            return render(request, 'views/usuarios/crear.html', {'modal': True, 'mess': 'usuario creado correctamente'})
        except Exception as e:
            print("ERROR-> ", e)
            return render(request, 'views/usuarios/crear.html', {'modal': True, 'mess': 'usuario no se puedo crear'})

    return render(request, 'views/usuarios/crear.html', {'modal': False, 'mess': ''})


#  @transaction.atomic
@csrf_exempt
@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.USUARIOS, PERMISOS.ELIMINAR)
def view_eliminar_usuario(request, userId):
    mess = ''
    status = 201
    if request.method == 'POST':
        try:
            user = UserProfile.objects.filter(pk=userId).first()
            user.activo = False
            user.save()
            mess = "Usuario \""+user.username+"\" eliminado con exito"
        except Exception as e:
            print("ERROR-> ",e) 
            status = 400
            mess = "No se pudo eliminar \""+user.username+"\" usuario"
    return JsonResponse({"status":status,"mess":mess})
@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.USUARIOS, [PERMISOS.VER, PERMISOS.EDITAR])
def view_gestionar_usuarios(request):
    roles = Rol.objects.all()
    usuarios = UserProfile.objects.filter(activo=True)
    empleados_rol = Empleado_Rol.objects.select_related().all()
    mess = ''
    t = False

    if request.method == 'POST' and checkUserHasPermission(request.user, GRUPOS.USUARIOS, PERMISOS.EDITAR):

        flag = True
        for rol, value in request.POST.items():
            if rol == 'csrfmiddlewaretoken':
                continue
            rol_aux = Rol.objects.filter(nombre=rol).first()
            usuario = UserProfile.objects.filter(username=value).first()
            if flag:
                Empleado_Rol.objects.filter(usuario=usuario).delete()
                flag = False
            Empleado_Rol(usuario=usuario, rol=rol_aux).save()
        mess = 'Roles asignados exitosamente'
        t = True
        # return render(request,'views/usuarios/gestionar.html',{ 'empleados_rol': empleados_rol_dict})

    empleados_rol_dict = dict()
    
    for usuario in usuarios:
        empleados_rol_dict[usuario] = dict()
        for rol in roles:
            empleados_rol_dict[usuario][rol.nombre] = False

    for empleado_rol in empleados_rol:
        if (empleado_rol.usuario.activo):
            empleados_rol_dict[empleado_rol.usuario][empleado_rol.rol.nombre] = True

    return render(request, 'views/usuarios/gestionar.html', {'empleados_rol': empleados_rol_dict, 'modal': t, 'mess': mess})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.ROLES, PERMISOS.CREAR)
def view_crear_rol(request):
    categorias = Grupo_Permiso.objects.all()
    permisos = Permiso.objects.all()
    if request.method == 'POST':
        try:
            nombre_rol = request.POST['nombre_rol'].upper().replace(" ", "_")
            rol = Rol(nombre=nombre_rol)
            rol.save()
            for key, _ in request.POST.items():
                if key == 'nombre_rol':
                    continue
                if key == 'csrfmiddlewaretoken':
                    continue
                categoria, permiso = key.split("-")
                categoriaAux = Grupo_Permiso.objects.filter(
                    nombre=categoria).first()
                permisoAux = Permiso.objects.filter(nombre=permiso).first()
                Rol_Permiso(id_rol=rol, id_grupo_permiso=categoriaAux,
                            id_permiso=permisoAux).save()
            return render(request, "views/roles/crear.html", {'permisos': permisos, 'categorias': categorias, "modal": True, "mess": "Rol creado con exito"})
        except Exception as e:
            return render(request, "views/roles/crear.html", {'permisos': permisos, 'categorias': categorias, "modal": True, "mess": "No se pudo crear Rol"})

    return render(request, 'views/roles/crear.html', {'permisos': permisos, 'categorias': categorias, "modal": False, "mess": ""})


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.ROLES, PERMISOS.ELIMINAR)
def eliminar_rol(request):
    mess = ''
    status = 201
    if request.method == 'POST':
        reqBody = json.loads(request.body)
        rol = reqBody["rol"]
        try:
            Rol.objects.filter(nombre=rol).delete()
            mess = "Rol \""+rol+"\" eliminado con exito"
        except Exception as e:
            mess = 'No se pudo eliminar rol \"'+rol+"\""
            status = 400

    return JsonResponse({"mensaje": mess, "status": status})


@csrf_exempt
@transaction.atomic
@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.ROLES, PERMISOS.EDITAR)
def change_permisos_roles(request):
    mess = ''
    status = 201
    if request.method == 'POST':
        permisos_rol = json.loads(request.body)
        rol = Rol.objects.filter(nombre=permisos_rol['rol']).first()
        Rol_Permiso.objects.filter(id_rol=rol).delete()
        permisos = Permiso.objects.all()

        try:
            for categoria, dict_permisos in permisos_rol.items():
                if categoria == "rol":
                    continue
                print(dict_permisos, type(dict_permisos))
                categoriaAux = Grupo_Permiso.objects.filter(
                    nombre=categoria).first()
                for permiso, value in dict_permisos.items():
                    if value:
                        permisoAux = Permiso.objects.filter(
                            nombre=permiso).first()
                        Rol_Permiso(
                            id_rol=rol, id_grupo_permiso=categoriaAux, id_permiso=permisoAux).save()
            mess = 'Permisos actualizados con exito.'
        except Exception as e:
            mess = 'No se pudo actualizar'
            status = 400

    return JsonResponse({"mensaje": mess, "status": status})


@csrf_exempt
@login_required(login_url='/')
def eliminar_galeria(request):
    if request.method == 'POST':
        try:
            reqBody = json.loads(request.body)
            tipo = reqBody['tipo']
            id_ = reqBody['id']
            if tipo == 'imagen':
                imagen = Imagenes_galeria.objects.filter(id=id_).first()
                imagen.estado = 0
                imagen.save()
            if tipo == 'video':
                video = Videos_galeria.objects.filter(id=id_).first()
                video.estado = 0
                video.save()
        except Exception as e:
            print('Error:', e)
            return JsonResponse({"mensaje": "Error al eliminar archivo de la galeria", "status": 400})

    return JsonResponse({"mensaje": "Eliminado correctamente", "status": 200})


@csrf_exempt
@login_required(login_url='/')
def view_politicas(request):
    politicas = Politicas.objects.all()[0]
    print(politicas)
    if request.method == 'POST':
        try:
            politicas = Politicas.objects.all()[0]
            politicas.descripcion = request.POST['descripcion']
            politicas.save()
            messages.add_message(request, messages.SUCCESS, 'Cambio exitoso.')
        except Exception as e:
            print("Error ->", e)
            messages.add_message(request, messages.ERROR,
                                 'No se pudo realizar la modificacion.')
        return redirect('politicas_view')

    return render(request, 'views/modificaciones/modificar_politicas.html', {'politicas': politicas})

   # return render(request, 'views/galeria/eliminar_galeria.html',{'imagenes':imagenes})


@login_required(login_url='/')
def view_modificar_nosotros(request):
    All_nosotros = Nosotros.objects.all()
    return render(request, 'views/modificaciones/modificar_nosotros.html', {'nosotros': All_nosotros})


@csrf_exempt
@login_required(login_url='/')
def modificar_nosotros(request, pk):
    All_nosotros = Nosotros.objects.all()
    try:
        nosotros = Nosotros.objects.get(id=pk)
        if request.method == 'POST':
            nosotros.nombre_completo = request.POST['nombres']
            nosotros.estudios = request.POST['estudios']
        # Verifico si envian imagen, si existe procedo a guardar
            if bool(request.FILES.get('imagen1')) == True:
                print("img1")
                nosotros.image = request.FILES['imagen1']
            nosotros.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Modificacion exitosa.')
        return render(request, 'views/modificaciones/modificar_nosotros.html', {'nosotros': All_nosotros, 'user_nosotros': nosotros})
    except Exception as e:
        print("Error ->", e)
        messages.add_message(request, messages.ERROR,
                             'No se pudo realizar la modificacion.')
    return render(request, 'views/modificaciones/modificar_nosotros.html', {'nosotros': All_nosotros})


@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.TESTIMONIOS, [PERMISOS.VER, PERMISOS.EDITAR, PERMISOS.APROBAR])
def eliminar_testimonios(request):
    testimonios = Testimonios.objects.all()  # solo hay una galeria
    return render(request, 'views/eliminacion/eliminar_testimonios.html', {'testimonios': testimonios})


@login_required(login_url='/')
def view_perfil(request):
    username = request.user.username
    user = UserProfile.objects.filter(username=username).first()
    return render(request, "views/usuario/perfil.html", {"user": user})


@login_required(login_url='/')
def view_perfil_configuracion(request):
    username = request.user.username
    user = UserProfile.objects.filter(username=username).first()
    if request.method == "POST":
    #  try:
        nombres = request.POST.get("nombre_usuario").strip(" ")
        apellidos = request.POST.get("nombre_usuario").strip(" ")

        username = request.POST.get("usuario")
        correo = request.POST.get("correo")
        fecha_nacimiento = request.POST.get("fecha_nacimiento")
        cedula = request.POST.get("cedula")
        telefono = request.POST.get("telefono")
        sexo = request.POST.get("sexo")
        newProfilePicture = request.FILES.get("profilePicture",None)

        user.first_name = nombres
        user.last_name = apellidos
        user.username = username
        user.email = correo
        user.fecha_nacimiento = datetime.datetime.strptime(
            fecha_nacimiento, "%Y-%m-%d").date()
        user.cedula = cedula
        user.telefono = telefono
        user.sexo = sexo
        
        if newProfilePicture != None:
            user.foto=newProfilePicture
        
        user.save()
        messages.add_message(request, messages.SUCCESS, "Datos actualizads con exito")
        return redirect(view_perfil_configuracion)
    #  except Exception as e:
        #  print(e)
        #  messages.add_message(request, messages.ERROR, "Algo salio mal")
        #  return render(request, "views/usuario/configuracion.html",{"user":user})
    return render(request, "views/usuario/configuracion.html",{"user":user})
@login_required(login_url='/')
def view_cambiar_contrasena(request):
    if request.method == "POST":
        newPassword = request.POST.get("password")
        newPassword2 = request.POST.get("password2")
        
        if newPassword != newPassword2:
            messages.add_message(request, messages.ERROR, "Las contraseñas no coinciden")
            return redirect(view_perfil_configuracion)
        if len(newPassword)<10:
            messages.add_message(request, messages.ERROR, "La contraseña debe tener almenos 10 caracteres")
            return redirect(view_perfil_configuracion)
        messages.add_message(request, messages.SUCCESS, "Contraseña actualizada con exito")

        request.user.set_password(newPassword)
        request.user.save()
        update_session_auth_hash(request, request.user)
    return render (request,"views/usuario/cambiarContraseña.html")

@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.CONTACTANOS, [PERMISOS.VER, PERMISOS.EDITAR])
def view_informacionContacto(request):
    contactInfo = InformacionContacto.objects.first()
    if contactInfo == None:
        contactInfo = InformacionContacto(telefono="", correo="", direccion="")
        contactInfo.save()

    if request.method == "GET":
        direccion = contactInfo.direccion
        correo = contactInfo.correo
        telefono = contactInfo.telefono
    if request.method == "POST" and checkUserHasPermission(request.user, GRUPOS.CONTACTANOS, PERMISOS.EDITAR):
        nuevaDireccion = request.POST.get("direccion")
        nuevoCorreo = request.POST.get("correo")
        nuevoTelefono = request.POST.get("telefono")

        contactInfo.direccion = nuevaDireccion
        contactInfo.correo = nuevoCorreo
        contactInfo.telefono = nuevoTelefono

        contactInfo.save()

        direccion = contactInfo.direccion
        correo = contactInfo.correo
        telefono = contactInfo.telefono

        messages.add_message(request, messages.SUCCESS,
                             'Modificacion exitosa.')

        return render(request, 'views/informacionContacto.html', {"direccion": direccion, "telefono": telefono, "correo": correo})
    return render(request, 'views/informacionContacto.html', {"direccion": direccion, "telefono": telefono, "correo": correo})


@login_required(login_url='/')
def eliminar_nosotros(request):
    nosotros = Nosotros.objects.all()  # solo hay una galeria
    return render(request, 'views/eliminacion/eliminar_nosotros.html', {'nosotros': nosotros})


@login_required(login_url='/')
def eliminar_nosotros_p(request):
    try:
        nosotros = Nosotros.objects.get(id=request.POST['nosotros'])
        nosotros.delete()
        messages.add_message(request, messages.SUCCESS,
                             'Nosotros user eliminado exitosamente.')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR,
                             'Error al eliminar el nostros user.')
    return redirect('eliminarNosotros')


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.TESTIMONIOS, PERMISOS.ELIMINAR)
def eliminar_testimonio_p(request):
    try:
        testi = Testimonios.objects.get(id=request.POST['testimonio'])
        testi.delete()
        messages.add_message(request, messages.SUCCESS,
                             'Testimonio eliminado exitosamente.')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR,
                             'Error al eliminar el Testimonio.')
    return redirect('eliminarTestimonio')


@login_required(login_url='/')
def vista_buzon_entrada(request):
    buzon = Contactanos.objects.filter(
        estado=1)  # false mostrar, #True ocultar
    return render(request, 'notificaciones/buzon_entrada.html', {'buzon': buzon})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.CONSEJERIAS, PERMISOS.CREAR)
def vista_registrar_consejeria(request):
    if request.method == 'POST':
        username = None
        username = request.user.username
        consejeria = Consejeria(tema=request.POST['tema'], usuario=username, correo=request.POST['link'],
                                empieza=request.POST['inicio'], termina=request.POST['termina'])
        consejeria.save()
    return render(request, 'views/registros/registrar_consejeria.html')


@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.CONSEJERIAS, [PERMISOS.VER, PERMISOS.EDITAR, PERMISOS.ELIMINAR])
def vista_modificar_consejeria(request):
    consejeria = Consejeria.objects.all()
    return render(request, 'views/modificaciones/modificar_consejeria.html', {'consejerias': consejeria})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.CONSEJERIAS, PERMISOS.EDITAR)
def modificar_consejeria(request):
    consejeria = Consejeria.objects.get(id=request.POST['id'])
    if request.POST['tema'] != '':
        consejeria.tema = request.POST['tema']
    if request.POST['inicio'] != '':
        consejeria.empieza = request.POST['inicio']
    if request.POST['termina'] != '':
        consejeria.termina = request.POST['termina']
    consejeria.save()

    return redirect('modificarConsejeria')


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.CONSEJERIAS, PERMISOS.ELIMINAR)
def eliminar_consejeria(request):
    con = Consejeria.objects.get(id=request.POST['id_consejeria'])
    user = UserProfile.objects.get(username=con.consejeria_user)
    user.consejeria = ""  # renicio la consejeria del usuario
    user.estado = 0
    user.save()
    con.delete()
    return redirect('modificarConsejeria')


@login_required(login_url='/')
def eliminar_mensaje_buzon(request):
    msg = Contactanos.objects.get(id=request.POST['id_mensaje'])
    msg.delete()
    return redirect('buzon_entrada')


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.PUBLICACIONES, PERMISOS.CREAR)
def vista_registrar_tema(request):
    categorias = Categoria_Tema.objects.all()
    if (request.method == 'POST'):
        try:
            # Esteado enum 1:Aprobado, 2:Pendiente
            cate_tema = Categoria_Tema.objects.get(
                nombre_categoria=request.POST['categoria'])
            tema = Tema(
                titulo=request.POST['titulo'],
                tema_categoria=cate_tema,
                descripcion=request.POST['descripcion'],
            )
            if request.POST.get("estado") and checkUserHasPermission(request.user, GRUPOS.PUBLICACIONES, PERMISOS.APROBAR):
                tema.estado = request.POST.get("estado")
            if request.POST['fecha'] != '':
                tema.fecha = request.POST['fecha']
            tema.save()

            # Esta podria ser la imagen que se muestra en el index del portal web
            imagen_tema_1 = Imagenes_Tema(id_tema=tema)
            imagen_tema_1.image = request.FILES['imagen1']
            imagen_tema_1.save()
            # Esta podria ser la imagen que se muestra una vez que le de click en el tema
            imagen_tema_2 = Imagenes_Tema(id_tema=tema)
            imagen_tema_2.image = request.FILES['imagen2']
            imagen_tema_2.save()

            # Video: Este se muestra una vez que entre en el tema
            vide_tema = Videos_Tema(id_tema=tema)
            # if bool(request.FILES.get('video')) == True:
            #     vide_tema.video = request.FILES['video']
            #     #vide_tema.save()
            if request.POST['url_video'] != '':
                vide_tema.url = youtube_url_validation(
                    request.POST['url_video'])
            vide_tema.save()
            # Que suba audio podria ser opcional (Casi a nadie le gusta estar oyendo audio de internet)
            messages.add_message(request, messages.SUCCESS,
                                 'Tema guardado exitosamente.')
        except Exception as e:
            print("Errors -> ", e)
            messages.add_message(request, messages.ERROR,
                                 'Error al guardar el tema.')
        # notificaciones(request.POST['titulo'])
        # registrar_tema es la version corta de views/registros/registrar_tema.html
        return redirect('registrar_tema')

    return render(request, 'views/registros/registrar_tema.html', {'categorias': categorias, "estado": Tema.Estado})


def youtube_url_validation(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    youtube_regex_match = re.findall(youtube_regex, url)
    print(youtube_regex_match[0][-1])
    if youtube_regex_match:
        return youtube_regex_match[0][-1]
    return youtube_regex_match


@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.PUBLICACIONES, [PERMISOS.VER, PERMISOS.EDITAR, PERMISOS.APROBAR])
def view_modificar_tema(request):
    All_temas = Tema.objects.all()
    categorias = Categoria_Tema.objects.all()
    return render(request, 'views/modificaciones/modificar_tema.html', {'temas': All_temas, 'categorias': categorias, "estado": Tema.Estado})


# request.POST.get('categoria') retorna none si no contiene ningun elemento para option
# request.POST['categoria']
@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.PUBLICACIONES, [PERMISOS.EDITAR, PERMISOS.APROBAR])
def modificar_tema(request, pk):
    All_temas = Tema.objects.all()
    categorias = Categoria_Tema.objects.all()
    # print("X->",request.POST['categoria'])

    try:
        tema = Tema.objects.get(id_tema=pk)
        if request.method == 'POST':
            tema.titulo = request.POST['titulo']
            tema.descripcion = request.POST['descripcion']
            tema.tema_categoria.id_categoria_tema
            if request.POST.get('categoria') != None:
                tema.tema_categoria = Categoria_Tema.objects.get(
                    nombre_categoria=request.POST.get('categoria'))
                print("cate->", request.POST['categoria'])
            if request.POST['fecha'] != "":
                tema.fecha = request.POST['fecha']
                print("X->", request.POST['fecha'])
            if request.POST.get('estado') != None:
                tema.estado = request.POST['estado']
                print("X->", request.POST.get('estado'))

        # Verifico si envian imagen, si existe procedo a guardar
            if bool(request.FILES.get('imagen1')) == True:
                print("img1")
                imagenes_tema = Imagenes_Tema.objects.filter(id_tema=pk)[0]
                imagenes_tema.image = request.FILES['imagen1']
                imagenes_tema.save()
            if bool(request.FILES.get('imagen2')) == True:
                print("img2")
                imagenes_tema2 = Imagenes_Tema.objects.filter(id_tema=pk)[1]
                imagenes_tema2.image = request.FILES['imagen2']
                imagenes_tema2.save()

            # Video: Este se muestra una vez que entre en el tema
            if request.POST['url_video'] != '':
                vide_tema = Videos_Tema.objects.filter(id_tema=pk)[0]
                vide_tema.url = youtube_url_validation(
                    request.POST['url_video'])
                vide_tema.save()
            tema.save()

            messages.add_message(request, messages.SUCCESS,
                                 'Modificacion exitosa.')
            return render(request, 'views/modificaciones/modificar_tema.html', {'temas': All_temas, 'categorias': categorias, "estado": Tema.Estado, 'tema': tema})
    except Exception as e:
        print("Error ->", e)
        messages.add_message(request, messages.ERROR,
                             'No se pudo realizar la modificacion.')

    return render(request, 'views/modificaciones/modificar_tema.html', {'temas': All_temas, 'categorias': categorias, "estado": Tema.Estado, 'tema': tema})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.PUBLICACIONES, PERMISOS.ELIMINAR)
def view_eliminar_tema(request):
    All_temas = Tema.objects.all()
    categorias = Categoria_Tema.objects.all()
    return render(request, 'views/eliminacion/eliminar_tema.html', {'temas': All_temas, 'categorias': categorias, "estado": Tema.Estado})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.PUBLICACIONES, PERMISOS.ELIMINAR)
def eliminar_tema_p(request):
    try:
        tema = Tema.objects.get(id_tema=request.POST['tema'])
        imagenes = Imagenes_Tema.objects.filter(id_tema=tema.id_tema)
        for imagen in imagenes:
            imagenes.delete()
        videos = Videos_Tema.objects.filter(id_tema=tema)
        videos.delete()
        tema.delete()
        print(imagenes)
        messages.add_message(request, messages.SUCCESS,
                             'Tema eliminado exitosamente.')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR,
                             'Error al eliminar el tema.')

        categorias = Categoria_Tema.objects.all()
    return redirect('eliminar_tema')


@login_required(login_url="/")
@validarPermisoUsuario(GRUPOS.TIPS, PERMISOS.CREAR)
def view_registrar_tips(request):
    if (request.method == 'POST'):
        try:
            recomendacion = Tips(
                usuario=request.user,
                titulo=request.POST['titulo'],
                descripcion=request.POST['descripcion'],
            )
            if (request.POST.get("estado") and user.getPermissions()[GRUPOS.TIPS][PERMISOS.APROBAR]):
                recomendacion.estado = request.POST.get("estado")
            if bool(request.FILES.get('imagen1')) == True:
                print("image tips")
                recomendacion.image = request.FILES['imagen1']
            recomendacion.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Tip guardado exitosamente.')
        except Exception as e:
            print("Errors -> ", e)
            messages.add_message(request, messages.ERROR,
                                 'Error al guardar el tip.')
        return redirect('registrar_tema')
    return render(request, 'views/registros/registrar_tips.html')


@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.TIPS, [PERMISOS.VER, PERMISOS.EDITAR, PERMISOS.APROBAR])
def view_modificar_tips(request):
    All_tips = Tips.objects.all()
    return render(request, 'views/modificaciones/modificar_tips.html', {'tips': All_tips})


@login_required(login_url='/')
@validarPermisosUsuario(GRUPOS.TIPS, [PERMISOS.EDITAR, PERMISOS.APROBAR])
def modificar_tips(request, pk):
    All_tips = Tips.objects.all().order_by('-fecha')
    try:
        tip = Tips.objects.get(id=pk)
        if request.method == 'POST':
            tip.titulo = request.POST['titulo']
            tip.usuario = str(request.user)
            tip.descripcion = request.POST['descripcion']
            if request.POST['fecha'] != "":
                tip.fecha = request.POST['fecha']
                print("X->", request.POST['fecha'])
            if request.POST.get('estado') != None and request.user.getPermissions()[GRUPOS.TIPS][PERMISOS.APROBAR]:
                tip.estado = request.POST['estado']
                print("X->", request.POST.get('estado'))
        # Verifico si envian imagen, si existe procedo a guardar
            if bool(request.FILES.get('imagen1')) == True:
                print("img1")
                tip.image = request.FILES['imagen1']
            tip.save()
            messages.add_message(request, messages.SUCCESS,
                                 'Modificacion exitosa.')

        #  return render(request, 'views/modificaciones/modificar_tips.html',{'tips':All_tips,'tip':tip})
        return render(request, 'views/modificaciones/modificar_tips.html', {'tips': All_tips, 'tip': tip})
    except Exception as e:
        print("Error ->", e)
        messages.add_message(request, messages.ERROR,
                             'No se pudo realizar la modificacion.')
    return render(request, 'views/modificaciones/modificar_tips.html', {'tips': All_tips})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.TIPS, PERMISOS.ELIMINAR)
def view_eliminar_tips(request):
    All_tips = Tips.objects.all()
    return render(request, 'views/eliminacion/eliminar_tips.html', {'tips': All_tips})


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.TIPS, PERMISOS.ELIMINAR)
def eliminar_tips_p(request):
    try:
        tip = Tips.objects.get(id=request.POST['tip'])
        tip.delete()
        messages.add_message(request, messages.SUCCESS,
                             'Tip eliminado exitosamente.')
    except Exception as e:
        print(e)
        messages.add_message(request, messages.ERROR,
                             'Error al eliminar el tip.')
    return redirect('eliminar_tips')


@login_required(login_url='/')
@validarPermisoUsuario(GRUPOS.GALERIA, PERMISOS.CREAR)
def view_galeria(request):
    if request.method == 'POST':
        try:
            titulo = request.POST['titulo']
            descripcion = request.POST['descripcion']
            galeria = Galeria(descripcion=descripcion, titulo=titulo)
            galeria.save()
            if request.FILES.get("imagen"):
                Imagenes_galeria(image=request.FILES['imagen'],
                                 id_galeria=galeria).save()
            else:
                Videos_galeria(
                    video=request.FILES['video'], id_galeria=galeria).save()
            return render(request, 'views/galeria/view_galeria.html', {"modal": True, "mess": "Imagen Guardada correctamente."})
        except Exception as e:
            print("EXCEPTION: ", e)
            return render(request, 'views/galeria/view_galeria.html', {"modal": True, "mess": "Error al guardar Imagen."})

    return render(request, 'views/galeria/view_galeria.html', {"modal": False, "mess": ""})


@csrf_exempt
def recuperar_contrasenia_admin(request):
    if request.method == 'POST':
        #response = json.loads(request.body)
        print(request.POST['correo'])
        try:
            usuario = UserProfile.objects.get(email=request.POST['correo'])
            print("validando correo")
        except UserProfile.DoesNotExist:
            usuario = None
            messages.add_message(request, messages.ERROR,
                                 'El correo ingresado no existe.!!')
            return redirect('password')

        new_password = UserProfile.objects.make_random_password()
        usuario.set_password(new_password)
        usuario.save()

        asunto = 'Cambio de contraseña Familias Unidas Ec'
        mail = request.POST['correo']
        mensaje = 'Usted ha solicitado recuperación de contraseña su contraseña nueva es la siguiente: ' + \
            new_password + " asegurese de cambiarla luego."
        nombres = usuario.username

        if nombres != '' and len(mail.split('@')) == 2 and mensaje != '':
            textomensaje = '<br>'
            lista = mensaje.split('\n')
            c = 0
            for i in lista:
                textomensaje += i+'</br>'
                c += 1
                if len(lista) > c:
                    textomensaje += '<br>'
            msj = '<p><strong>Usuario :</strong>'+nombres+'</p><p><strong>Correo: </strong>' + \
                mail+'</p><strong>Mensaje: </strong>'+textomensaje+'</p>'
            msj2 = msj+'<br/><br/><br/><p>Usted esta realizando el proceso de recuperacion de contraseña.</p><p><strong>NO RESPONDER A ESTE MENSAJE</strong>, nosotros nos pondremos en conacto con usted de ser necesario.</p><br/>'
            try:

                send_mail('Contactanos: '+asunto, msj, 'familias.unidasEC@gmail.com', [
                          'familias.unidasEC@gmail.com'], fail_silently=False, html_message='<html><body>'+msj+'</body></html>')
                send_mail('Correo enviado: '+asunto, msj2, 'familias.unidasEC@gmail.com', [
                          mail], fail_silently=False, html_message='<html><body>'+msj2+'</body></html>')
            except BadHeaderError:
                return redirect('password')
            messages.add_message(
                request, messages.SUCCESS, 'Se ha enviado su contraseña temporal, revise su correo.')
            return redirect('password')
    return redirect('password')


@csrf_exempt
def signup(request):

    if request.user.is_authenticated:
        return render(request, "views/index.html")
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        # Con esto crean los tipos de usarios mientras tanto para que vayan probando los diferentes tipos de usuarios
        #new = UserProfile.objects.create_user('john', 'lennon@thebeatles.com', '23198')
        #new.tipo = "A"
        # new.save()
        if user is not None:
            if user.is_active:
                login(request, user)
                # Redirect to a success page.
                # redirect('index')
                try:
                    usuario = UserProfile.objects.get(username=username)
                    print(usuario.username)
                except expression as identifier:
                    pass

                return redirect(signup)
            else:
                # Return a 'disabled account' error message
                messages.add_message(
                    request, messages.ERROR, 'Creedenciales incorrectas, intentelo de nuevo...')
                return render(request, 'views/login.html', {})
        else:
            # Return an 'invalid login' error message.
            messages.add_message(
                request, messages.ERROR, 'Usuario o contraseña incorrectas, intentelo de nuevo...')
            return render(request, 'views/login.html', {})
    else:
        return render(request, 'views/login.html', {})


def logout_view(request):
    logout(request)
    return redirect('/')
    # Redirect to a success page.
    # try:
    #     del request.session['username']
    # except:
    #  pass
    # return render(request, 'app_foldername/login.html', {})


def forgot_password(request):
    return render(request, 'views/forgot-password.html', {})


@csrf_exempt
def recibir_imagenes(request):
    if request.method == "POST":
        galeria = Galeria.objects.get(id_galeria=1)
        for k, v in request.FILES.items():
            imagen = Imagenes_galeria(id_galeria=galeria, image=v)
            imagen.save()

        messages.add_message(request, messages.ERROR,
                             'Creedenciales incorrectas, intentelo de nuevo...')
        return JsonResponse(200, safe=False)
    return JsonResponse(400, safe=False)
    # return redirect('views/galeria/view_galeria.html')


def recibir_video(request):
    if request.method == "POST":
        galeria = Galeria.objects.get(id_galeria=1)
        for k, v in request.FILES.items():
            video = Videos_galeria(id_galeria=galeria, video=v)
            video.save()
        return render(request, 'views/galeria/view_galeria.html')
    return render(request, 'views/galeria/view_galeria.html')


def send_email(request):
    if request.method == "POST":
        correo = request.POST['correo']
        msg = request.POST['msg']
        send_response(msg, correo)
        return redirect('buzon_entrada')
    return redirect('buzon_entrada')


@login_required(login_url="/")
@validarPermisosUsuario(GRUPOS.TESTIMONIOS, [PERMISOS.EDITAR, PERMISOS.APROBAR])
def validarTestimonio(request):
    if request.method == 'POST':
        id_testi = request.POST['id_testimonio']
        testi = Testimonios.objects.get(id=id_testi)
        testi.estado = request.POST['estado']
        testi.save()
    return redirect('eliminarTestimonio')


def notificaciones(informacion):
    usuarios = UserProfile.objects.all()
    asunto = 'Actualizacion de contenido Familias Unidas Ec'
    mensaje = "Se ha actualizado el contenido " + \
        informacion + ", puede revisarlo en el administrador"
    correos = []
    for user in usuarios:
        if user.tipo != "U":
            correos.append(user.email)
    print(correos)
    message1 = (asunto, mensaje, 'familias.unidasEC@gmail.com', correos)
    try:
        send_mass_mail((message1,), fail_silently=False)
        print("mensaje exitoso")
    except BadHeaderError:
        print("error")


def send_response(informacion, correo):
    usuarios = UserProfile.objects.all()
    asunto = 'Familias Unidas Ec'
    print(correo)
    correos = []
    correos.append(correo)
    # message1 = (asunto, mensaje, 'familias.unidasEC@gmail.com',correos)
    try:
        send_mail(asunto, informacion, 'familias.unidasEC@gmail.com',
                  [correo], fail_silently=False)
        send_mail(asunto, informacion, 'familias.unidasEC@gmail.com',
                  ['familias.unidasEC@gmail.com'], fail_silently=False)

        print("mensaje exitoso")
    except BadHeaderError:
        print("error")


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        print(user)
        print(request.data)
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'email': user.email,
            'usuario': user.username,
            'tipo': user.tipo
        })
