from pyexpat import model
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from datetime import datetime

# Create your models here.

# class customUser(AbstractUser):
#   rol = models.CharField(max_length=2,default='e')#A: administrador, E:editor, C:consejero


class UserProfile(AbstractUser):
    tipo = models.CharField(max_length=2, null=False, blank=False, default='E',
                            verbose_name='Tipos de usuario')  # A:administrador, E: editor, C: consejero
    # consejeria = models.CharField(max_length=300,null=False,blank=False,default='None')# A:administrador, E: editor, C: consejero
    # A:administrador, E: editor, C: consejero
    sexo = models.CharField(max_length=100, null=False, blank=True)
    # edad = models.CharField(max_length=100,null=False,blank=True )# A:administrador, E: editor, C: consejero
    foto = models.ImageField(upload_to='image/', null=False, blank=True,
                             verbose_name="Imagen del perfil", default="image/profile.png")
    cedula = models.CharField(max_length=10, null=True, blank=False)
    telefono = models.CharField(max_length=10, blank=True, null=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    # consejeria=models.CharField(max_length=150,default=None,null=True,blank=True )
    estado = models.SmallIntegerField(default=0)
    activo = models.BooleanField(default=True)

    def say_hello(self):
        return "Hello, my name is {}".format(self.first_name)

    def __str__(self):
        return self.username

    def getPermissions(self):
        categorias = Grupo_Permiso.objects.all()
        permisos = Permiso.objects.all()
        # construir la lista matriz de permisos
        dictPermisos = dict()
        for c in categorias:
            dictPermisos[c.nombre] = dict()
            dictPermisos[c.nombre]["ANY"] = False
            for p in permisos:
                dictPermisos[c.nombre][p.nombre] = False

        # conslultar los roles que tiene el usuario
        roles = [er.rol for er in Empleado_Rol.objects.filter(usuario=self)]

        # conslultar los permisos para dichos roles
        permisos_roles = Rol_Permiso.objects.filter(id_rol__in=roles)

        # registrar todos los permisos encontrados en la matriz de permisos
        for pr in permisos_roles:
            dictPermisos[pr.id_grupo_permiso.nombre][pr.id_permiso.nombre] = True
        # llenar el campo ANY para cada categoria
        for c in categorias:
            dictPermisos[c.nombre]["ANY"] = any(
                dictPermisos[c.nombre].values())
        return dictPermisos


class Categoria_Tema(models.Model):
    id_categoria_tema = models.AutoField(primary_key=True)
    nombre_categoria = models.CharField(
        max_length=200, null=False, blank=True, verbose_name="Nombre de la categoria")
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.nombre_categoria


class Tema(models.Model):
    # Enum
    class Estado(models.IntegerChoices):
        REVISADO = 1
        PENDIENTE = 2

    id_tema = models.AutoField(primary_key=True)
    tema_categoria = models.ForeignKey(
        Categoria_Tema, on_delete=models.CASCADE, null=True, blank=True)
    estado = models.IntegerField(choices=Estado.choices)
    titulo = models.CharField(
        max_length=100, null=False, blank=False, verbose_name="Titulo del tema")
    descripcion = models.TextField(
        max_length="900", null=False, blank=True, verbose_name="Descripcion del tema")
    fecha = models.DateField(null=False, blank=True, default=datetime.now)
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.titulo


class Imagenes_Tema(models.Model):
    image = models.ImageField(
        upload_to='image/', null=False, blank=True, verbose_name="Imagen del tema")
    id_tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    estado = models.SmallIntegerField(default=1)


class Videos_Tema(models.Model):
    video = models.FileField(
        upload_to="video/", null=False, blank=True, verbose_name="Video del tema")
    id_tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    url = models.CharField(max_length=200, null=False, blank=True)
    estado = models.SmallIntegerField(default=1)


class Audio_Tema(models.Model):
    audio = models.FileField(
        upload_to="audio/", null=False, blank=True, verbose_name="Audio del tema")
    id_tema = models.ForeignKey(Tema, on_delete=models.CASCADE)
    estado = models.SmallIntegerField(default=1)


class Galeria(models.Model):
    id_galeria = models.AutoField(primary_key=True)
    descripcion = models.CharField(max_length=500, null=True, blank=True)
    titulo = models.CharField(max_length=100, null=True, blank=True)
    estado = models.SmallIntegerField(default=1)


class Imagenes_galeria(models.Model):
    image = models.ImageField(
        upload_to='image/', null=False, blank=True, verbose_name="Imagen del tema")
    id_galeria = models.ForeignKey(Galeria, on_delete=models.CASCADE)
    fecha = models.DateField(null=False, blank=True, default=datetime.now)
    estado = models.SmallIntegerField(default=1)


class Videos_galeria(models.Model):
    video = models.FileField(
        upload_to="video/", null=False, blank=True, verbose_name="Video del tema")
    estado = models.SmallIntegerField(default=1)
    id_galeria = models.ForeignKey(Galeria, on_delete=models.CASCADE)
    fecha = models.DateField(null=False, blank=True, default=datetime.now)


class Testimonios(models.Model):
    usuario = models.CharField(max_length=150, null=False, blank=False)
    fecha = models.DateField(null=False, blank=True, default=datetime.now)
    titulo = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(max_length=100, null=False, blank=True)
    image = models.ImageField(upload_to='image/', null=False, blank=True)
    estado = models.SmallIntegerField(default=1)


class Tips(models.Model):
    usuario = models.CharField(max_length=150, null=False, blank=False)
    fecha = models.DateField(null=False, blank=True, default=datetime.now)
    titulo = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(max_length=300, null=False, blank=True)
    image = models.ImageField(upload_to='image/', null=False, blank=True)
    estado = models.SmallIntegerField(default=1)


class Contactanos(models.Model):
    usuario = models.CharField(max_length=150, null=False, blank=False)
    fecha = models.DateField(null=False, blank=True, default=datetime.now)
    titulo = models.CharField(max_length=100, null=False, blank=False)
    descripcion = models.TextField(max_length=300, null=False, blank=True)
    correo = models.CharField(max_length=150, null=False, blank=False)
    estado = models.SmallIntegerField(default=1)

class Temas_Consejeria(models.Model):
    nombre = models.CharField(max_length=150,null=False,blank=False)

class Consejeria(models.Model):
    usuario = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='usuario')
    consejero = models.ForeignKey('UserProfile', on_delete=models.CASCADE, related_name='consejero')
    tema = models.ForeignKey('Temas_Consejeria', on_delete=models.CASCADE)
    modalidad = models.CharField(max_length=150, null=False, blank=False)
    link = models.URLField(max_length=500)
    direccion = models.CharField(max_length=200)
    fecha = models.DateField(null=False, blank=True)
    hora = models.CharField(max_length=5,null=False, blank=False)
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    motivo = models.CharField(max_length=1000, null=False, blank=False)


class Nosotros(models.Model):
    nombre_completo = models.CharField(max_length=350, null=False, blank=False)
    estudios = models.CharField(max_length=250, null=False, blank=False)
    image = models.ImageField(upload_to='image/', null=False, blank=True)
    estado = models.SmallIntegerField(default=1)


class Politicas(models.Model):
    descripcion = models.TextField(
        max_length=800, null=False, blank=True, default="Politicas de privacidad.")
    estado = models.SmallIntegerField(default=1)


class InformacionContacto(models.Model):
    """
        modelo: 'InformacionContacto' Informacion de como contactar a la compañia

        **Atributes**
            direccion (CharField): direccion de las oficinas
    """
    informationId = models.AutoField(primary_key=True)
    direccion = models.CharField(null=False, blank=False, max_length=100)
    correo = models.CharField(null=False, blank=False, max_length=50)
    telefono = models.CharField(null=False, blank=False, max_length=50)


class Rol(models.Model):
    nombre = models.CharField(max_length=20, null=False, blank=False)
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.nombre


class Permiso(models.Model):
    nombre = models.CharField(max_length=12, null=False, blank=False)
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.nombre


class Grupo_Permiso(models.Model):
    nombre = models.CharField(max_length=20, null=False, blank=False)
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return self.nombre


class Rol_Permiso(models.Model):
    id_rol = models.ForeignKey(Rol, on_delete=models.CASCADE)
    id_grupo_permiso = models.ForeignKey(
        Grupo_Permiso, on_delete=models.CASCADE)
    id_permiso = models.ForeignKey(Permiso, on_delete=models.CASCADE)
    estado = models.SmallIntegerField(default=1)

    def __str__(self):
        return str(self.id_rol) + " - " + str(self.id_grupo_permiso) + " - " + str(self.id_permiso)


class Empleado_Rol(models.Model):
    usuario = models.ForeignKey('UserProfile', on_delete=models.CASCADE)
    rol = models.ForeignKey('Rol', on_delete=models.CASCADE)
    estado = models.SmallIntegerField(default=1)
