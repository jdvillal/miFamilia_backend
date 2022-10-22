from cgitb import reset
from urllib import request
from django.shortcuts import render
# Create your api rest here.
from django.shortcuts import render
from django.http import HttpResponse, JsonResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login as do_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import logout
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib import messages
from .models import *
import json
import datetime
from django.views.decorators.csrf import csrf_exempt
from rest_framework_jwt.views import ObtainJSONWebToken
from django.views.decorators.csrf import ensure_csrf_cookie
from django.utils.decorators import method_decorator
from django.contrib.auth.models import User
from rest_framework_jwt.settings import api_settings
from rest_framework.response import Response
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth import authenticate
from django.core.mail import EmailMessage, BadHeaderError, send_mail, send_mass_mail


def get_politicas(request):
    if request.method=='GET':
        politicas = Politicas.objects.all()[0]
        dict_politics={}
        dict_politics['Descripcion']=politicas.descripcion
        return JsonResponse(dict_politics,safe=False)


def get_tips(request):
    if request.method == 'GET':
        tips = Tips.objects.filter(estado=1).order_by('-fecha')
        return JsonResponse(list(tips.values()),safe=False)

def get_profile(request):
    if request.method == 'GET':
        user= request.GET.get("id")
        #response = json.loads(request.body)
        #profile= UserProfile.objects.get(username=response['user'])
        profile= UserProfile.objects.filter(username=user)
        dic = dict()
        lista = list()
        for i in profile:
            dic['Nombre']=i.first_name
            dic['Apellido']=i.last_name
            dic['Email']=i.email
            dic['Edad']=i.edad
            dic['Username']=i.username
            dic['Sexo']='Masculino'
            if(i.image != ''):
                dic['Image']=i.image.url
            dic['consejeria']=i.consejeria
            dic['estado']=i.estado
            if i.estado==1:
                consejeria=Consejeria.objects.get(consejeria_user=i.username)
                dic['inicio']=consejeria.empieza
                dic['termina']=consejeria.termina
            lista.append(dic)
        return JsonResponse(dic,safe=False)

@csrf_exempt
def update_profile(request):
    print(request)
    print(json.loads(request.body))
    if request.method=="POST":
        response = json.loads(request.body)
        print(response)
        try:
            profile= UserProfile.objects.filter(username=response['user'])[0]
            profile.first_name= response['nombre']
            profile.last_name= response['apellido']
            profile.edad= response['edad']
            print(response['edad'])
            profile.email= response['email']
            profile.save()
        except Exception as e:
            print(e)
        print(response)
        return HttpResponse(status=200)
    return HttpResponse(status=404)

@csrf_exempt
def update_password(request):
    if request.method=="POST":
        response = json.loads(request.body)
        print(response)
        try:
            profile= UserProfile.objects.filter(username=response['user'])[0]
            profile.set_password(response['password'])  # replace with your real password
            print(response['password'])
            profile.save()
        except Exception as e:
            print(e)
        print(response)
        return HttpResponse(status=200)
    return HttpResponse(status=404)

@csrf_exempt
def update_image_profile(request):
    if request.method=="POST":
        print(request.POST['user'])
        print(request.FILES['file'])
        try:
            profile= UserProfile.objects.filter(username=request.POST['user'])[0]
            profile.image= request.FILES['file']
            profile.save()
        except Exception as e:
            print(e)
        return HttpResponse(status=200)
    return HttpResponse(status=404)
   

def get_temasPrincipales(request):
    if request.method=='GET':
        response = dict()
        temas = Tema.objects.all()
        categorias = Categoria_Tema.objects.all()
        print(categorias)
        temas_recientes = list()
        for categoria in categorias:
            print(categoria)
            _tema = temas.filter(tema_categoria=categoria,estado=1).order_by('-fecha').first()
            print(_tema)
            if _tema != None:
                imagen=Imagenes_Tema.objects.filter(id_tema=_tema.id_tema)[0]
                res = dict()
                res['titulo']=_tema.titulo
                res['id']=_tema.id_tema
                res['id_categoria']=_tema.tema_categoria.id_categoria_tema
                res['categoria']=_tema.tema_categoria.nombre_categoria
                res['image']=imagen.image.url
                temas_recientes.append(res)
        print(temas_recientes)
        return JsonResponse(temas_recientes,safe=False)

def get_testimonios(request):
    if request.method=='GET':
        testimonios = Testimonios.objects.filter(estado=1).order_by('-fecha').values()       
        return JsonResponse(list(testimonios),safe=False)

def get_informacion_contacto(request):
    """
       Devuelve un json con la direccion de las oficinas, emails y telefonos de la compañia 
    """
    if request.method == "GET":
        contactInfo = InformacionContacto.objects.first()

        direccion = contactInfo.direccion
        email = contactInfo.correo
        telefono = contactInfo.telefono


        return JsonResponse({"direccion":direccion,"telefono":telefono,"email":email})


def get_nosotros(request):
    if request.method=='GET':
        nosotros = Nosotros.objects.all().values()       
        return JsonResponse(list(nosotros),safe=False)

def get_categorias(request):
    if request.method=='GET':
        cetegorias = Categoria_Tema.objects.all().values()
        return JsonResponse(list(cetegorias), safe=False)

def get_temaByID(request):
    if request.method=='GET':
        id= request.GET.get("id")
        tema = Tema.objects.filter(id_tema=id).values()

        return JsonResponse(list(tema), safe=False)

def get_temaByCategory(request):
    if request.method=='GET':
        id_categoria= request.GET.get("id")
        temas = Tema.objects.filter(tema_categoria=id_categoria).order_by('-fecha').values()
        temas2= Tema.objects.filter(tema_categoria=id_categoria)
        images = Imagenes_Tema.objects.all()
        return JsonResponse(list(temas), safe=False)

def get_temas_images(request):
    if request.method=='GET':
        id_categoria= request.GET.get("id")
        temas2= Tema.objects.filter(tema_categoria=id_categoria).order_by('-fecha')
        images = Imagenes_Tema.objects.all()
        list_tema=[]
        for i in temas2:
            res = dict()
            res['titulo']=i.titulo
            res['categoria']=i.tema_categoria.id_categoria_tema
            res['id_tema']=i.id_tema
            res['images']=images.filter(id_tema=i.id_tema).first().image.url
            res['descripcion']=i.descripcion
            res['fecha']=i.fecha

            list_tema.append(res)

        return JsonResponse(list_tema, safe=False)

def get_imageTema(request):
    if request.method=='GET':
        _id= request.GET.get("id")
        images = Imagenes_Tema.objects.filter(id_tema=_id).values()
        print(images)
        return JsonResponse(list(images), safe=False)

def get_videoTema(request):
    if request.method=='GET':
        _id= request.GET.get("id")
        videos = Videos_Tema.objects.filter(id_tema=_id).values()
        print(videos)
        return JsonResponse(list(videos), safe=False)

def get_imagesGaleria(request):
    if request.method=='GET':
        img_galeria= Imagenes_galeria.objects.all().values()
        listReturn = []
        for imagen in img_galeria:
            galeria = Galeria.objects.filter(id_galeria=imagen['id_galeria_id']).values().first()
            dictImagen = {
                "id": imagen["id"], 
                "image": imagen["image"],
                "estado": imagen["estado"],
                "id_galeria_id": galeria,
                "fecha": imagen["fecha"]    
            }
            listReturn.append(dictImagen)
        return JsonResponse(listReturn, safe=False)

def get_videosGaleria(request):
    if request.method ==  'GET':
        videos_galeria = Videos_galeria.objects.all().values()
        listReturn = []
        for video in videos_galeria:
            galeria = Galeria.objects.filter(id_galeria=video['id_galeria_id']).values().first()
            dictVideo = {
                "id": video["id"], 
                "video": video["video"],
                "estado": video["estado"],
                "id_galeria_id": galeria,
                "fecha": video["fecha"]    
            }
            listReturn.append(dictVideo)
        return JsonResponse(listReturn,safe=False)

def get_empleados_rol(request):
    if request.method == 'GET':
        empleados_rol = Empleado_Rol.objects.all().values()
        print(empleados_rol)
        response = []
        for empleado_rol in empleados_rol:
            usuario = UserProfile.objects.filter(id=empleado_rol["usuario_id"]).values().first()
            rol = Rol.objects.filter(id=empleado_rol["rol_id"],estado=1).values().first()
            dic = {
                "id" : empleado_rol["id"],
                "usuario" : {
                    "id": usuario["id"],
                    "usuario": usuario["username"],
                    "nombre": usuario["first_name"] + ' ' + usuario["last_name"],
                    "correo": usuario["email"],
                    "telefono": usuario["telefono"],
                    "cedula": usuario["cedula"],
                    "foto": usuario["foto"],
                    "tipo": usuario["tipo"]
                },
                "rol" : {
                    "id_rol" : rol["id"],
                    "nombre" : rol["nombre"],
                }
            }
            response.append(dic)
        return JsonResponse(response,safe=False)
    return HttpResponse(status=404)

def get_tema_consejeria(request):
    if request.method == 'GET' :
        temas_consejerias = Temas_Consejeria.objects.all().values()
        return JsonResponse(list(temas_consejerias), safe=False)   

def get_Consejerias(request):
    if request.method=='GET':
        consejerias = Consejeria.objects.all()
        conj = []
        for consejeria in consejerias.values():
            usuario = UserProfile.objects.filter(id=consejeria['usuario_id']).values().first()
            consejero = UserProfile.objects.filter(id=consejeria['consejero_id']).values().first()
            tema = Temas_Consejeria.objects.filter(id=consejeria['tema_id']).values().first()
            dictionariConsejeria = {
                "id": consejeria['id'],
                "usuario" : {
                    "id": usuario["id"],
                    "usuario": usuario["username"],
                    "nombre": usuario["first_name"] + ' ' + usuario["last_name"],
                    "correo": usuario["email"],
                    "telefono": usuario["telefono"],
                    "cedula": usuario["cedula"],
                    "foto": usuario["foto"],
                    "tipo": usuario["tipo"]
                },
                "consejero" : {
                    "id": consejero["id"],
                    "usuario": consejero["username"],
                    "nombre": consejero["first_name"] + ' ' + consejero["last_name"],
                    "correo": consejero["email"],
                    "telefono": consejero["telefono"],
                    "cedula": consejero["cedula"],
                    "foto": consejero["foto"],
                    "tipo": consejero["tipo"]
                },
                "tema" : {
                    "id": tema["id"],
                    "nombre": tema["nombre"]
                },
                "modalidad" : consejeria["modalidad"],
                "link" : consejeria["link"],
                "direccion" : consejeria["direccion"],
                "fecha" : consejeria["fecha"],
                "hora" : consejeria["hora"],
                "precio" : consejeria["precio"],
                "motivo" : consejeria["motivo"]
            }
            conj.append(dictionariConsejeria)
        return JsonResponse(conj, safe=False)



@csrf_exempt
def post_contactanos(request):
    if request.method=="POST":
        response = json.loads(request.body)
        try:
            contacanos= Contactanos(estado=False,titulo=response['title'],descripcion=response['description'],
            correo=response['email'],usuario=response['name'])
            contacanos.save()
        except Exception as e:
            print(e)
        print(response)
        return HttpResponse(status=200)
    return HttpResponse(status=404)

@csrf_exempt
def post_solicitar_consejeria(request):
    if request.method=="POST":
        response = json.loads(request.body)
        try:
            usuario = UserProfile.objects.filter(id=response['usuario']).first()
            consejero = UserProfile.objects.filter(id=response['consejero']).first()
            tema = Temas_Consejeria.objects.filter(id=response['tema']).first()
            modalidad = response['modalidad']
            link = response['link']
            direccion = response['direccion']
            fecha = response['fecha']
            hora = response['hora']
            precio = response['precio']
            motivo = response['motivo']
            consejeria = Consejeria(usuario=usuario, consejero=consejero, tema=tema, modalidad=modalidad, link=link, direccion=direccion, fecha=fecha, hora=hora, precio=precio, motivo=motivo)
            consejeria.save()
            usuario = UserProfile.objects.filter(id=response['usuario']).values().first()
            consejero = UserProfile.objects.filter(id=response['consejero']).values().first()
            tema = Temas_Consejeria.objects.filter(id=response['tema']).values().first()
            dictionariConsejeria = {
                "id": consejeria.id,
                "usuario" : {
                    "id": usuario["id"],
                    "usuario": usuario["username"],
                    "nombre": usuario["first_name"] + ' ' + usuario["last_name"],
                    "correo": usuario["email"],
                    "telefono": usuario["telefono"],
                    "cedula": usuario["cedula"],
                    "foto": usuario["foto"],
                    "tipo": usuario["tipo"]
                },
                "consejero" : {
                    "id": consejero["id"],
                    "usuario": consejero["username"],
                    "nombre": consejero["first_name"] + ' ' + consejero["last_name"],
                    "correo": consejero["email"],
                    "telefono": consejero["telefono"],
                    "cedula": consejero["cedula"],
                    "foto": consejero["foto"],
                    "tipo": consejero["tipo"]
                },
                "tema" : {
                    "id": tema["id"],
                    "nombre": tema["nombre"]
                },
                "modalidad" : modalidad,
                "link" : link,
                "direccion" : direccion,
                "fecha" : fecha,
                "hora" : hora,
                "precio" : precio,
                "motivo" : motivo
            }
            return HttpResponse(json.dumps(dictionariConsejeria), content_type = "application/json")
        except Exception as e:
            print(e)
            return HttpResponse(status=400)
    return HttpResponse(status=404)


@csrf_exempt
def post_testimonios(request):
    if request.method=="POST":
        response = json.loads(request.body)
        try:
            testimonio= Testimonios(usuario=response['name'],titulo=response['title'],
            descripcion=response['description'],estado=0)
            testimonio.save()
        except Exception as e:
            print(e)
        print(response)
        return HttpResponse(status=200)
    return HttpResponse(status=404)

#API de Servicios de sugerencias
@csrf_exempt
def postCreateTipoSugerencia(request):
    if request.method=='POST':
        response = json.loads(request.body)
        #Aqui creo el elemento de tipo sugerencia
        tipo = Tipo_sugerencia(sugerencia=response["nuevaSugerencia"])
        tipo.save()
        return HttpResponse(status=200)
    return HttpResponse(status=404)

#API de Servicios de registrar ususario
@csrf_exempt
def register(request):
    if request.method=='POST':
        response = json.loads(request.body)
        #Aqui creo el usuario
        print(response["password"])
        user = UserProfile(username=response["username"],first_name=response["nombre"],last_name=response["apellido"],email=response["correo"],tipo="U")
        user.set_password(response["password"])
        user.save()
        return HttpResponse(status=200)
    return HttpResponse(status=404)

@csrf_exempt
def login(request):
    if request.method == "POST":
        response = json.loads(request.body)
        username = response["username"]
        password = response["password"]
        if(username!=None and password!=None):
            usuario = authenticate(username=username, password=password)
            if(usuario):
                return JsonResponse({"status":"true","usuario":usuario.first_name+" "+usuario.last_name,"username":usuario.username}, safe=False)
            else:
                return JsonResponse({"status":"false"}, safe=False)
            return HttpResponse(status=404)
        return HttpResponse(status=404)
    return HttpResponse(status=404)

@csrf_exempt
def get_scrollGaleria(request):
    if request.method=='GET':
        page = int(request.GET.get("_page"))
        limit = int(request.GET.get("_limit"))
        img_galeria= Imagenes_galeria.objects.all().values('image')[page:limit]
        return JsonResponse(list(img_galeria), safe=False)

@csrf_exempt
def recuperar_contrasenia(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        correo = response["correo"]
        try:
            usuario = UserProfile.objects.get(email=correo)
            print(usuario)
        except UserProfile.DoesNotExist:
            usuario = None
            messages.add_message(request,messages.ERROR,'El correo ingresado no existe.!!')
            return JsonResponse({"status":"false"}, safe=False)
        
        new_password = UserProfile.objects.make_random_password()
        usuario.set_password(new_password)
        usuario.save()

        asunto = 'Cambio de contraseña Familias Unidas Ec'
        mensaje = 'Usted ha solicitado recuperación de contraseña su contraseña nueva es la siguiente: '+ new_password +" asegurese de cambiarla luego."
        nombres = usuario.username

        if nombres != '' and len(correo.split('@')) == 2 and mensaje != '':
            textomensaje = '<br>'
            lista = mensaje.split('\n')
            c = 0
            for i in lista:
                textomensaje += i+'</br>'
                c+=1
                if len(lista)  > c :
                    textomensaje += '<br>'
            msj = '<p><strong>IPSP :</strong>'+nombres+'</p><p><strong>Correo: </strong>'+correo+'</p><strong>Mensaje: </strong>'+textomensaje+'</p>'
            msj2 = msj+'<br/><br/><br/><p>Usted esta realizando el proceso de recuperacion de contraseña.</p><p><strong>NO RESPONDER A ESTE MENSAJE</strong>, nosotros nos pondremos en conacto con usted de ser necesario.</p><br/>'
            try:
                
                send_mail('Contactanos: '+asunto, msj,'familias.unidasEC@gmail.com', ['familias.unidasEC@gmail.com'], fail_silently=False, html_message = '<html><body>'+msj+'</body></html>')
                send_mail('Correo enviado: '+asunto, msj2, 'familias.unidasEC@gmail.com', [correo], fail_silently=False, html_message= '<html><body>'+msj2+'</body></html>')
            except BadHeaderError:
                return JsonResponse({"status":"false"}, safe=False)
            return JsonResponse({"status":"true"}, safe=False)

    return JsonResponse({"status":"false"}, safe=False)

@csrf_exempt
def registro(request):
    if request.method == 'POST':
        response = json.loads(request.body)
        #verificar ususario
        if UserProfile.objects.filter(username=response["usuario"]).exists() or UserProfile.objects.filter(email=response["correo"]).exists():
            return JsonResponse({"status":"false"}, safe=False)
        else:
            user = UserProfile(username=response["usuario"],email=response["correo"],tipo="U", fecha_nacimiento=response["nacimiento"],first_name=response["nombre"],last_name=response["apellido"],sexo=response["genero"])
            user.set_password(response["contraseña"])
            user.save()
            print(response)
        return JsonResponse({"status":"true"}, safe=False)
    return JsonResponse({"status":"false"}, safe=False)
