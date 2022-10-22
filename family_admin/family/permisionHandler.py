from django.contrib.auth.decorators import  user_passes_test
from .models import *

class PERMISOS:
    VER="VER"
    CREAR="CREAR"
    EDITAR="EDITAR"
    ELIMINAR="ELIMINAR"
    APROBAR="APROBAR"

class GRUPOS:
    GALERIA="GALERIA"
    PUBLICACIONES="PUBLICACIONES"
    USUARIOS="USUARIOS"
    ROLES="ROLES"
    CONSEJERIAS="CONSEJERIAS"
    TIPS="TIPS"
    NOTIFICACIONES="NOTIFICACIONES"
    TESTIMONIOS="TESTIMONIOS"
    CONTACTANOS="CONTACTANOS"
    EVENTOS="EVENTOS"


def checkUserHasPermission(user:UserProfile,category:str,permission:str)->bool:
    categoria = Grupo_Permiso.objects.filter(nombre=category).first()
    permiso = Permiso.objects.filter(nombre=permission).first()
    roles = [er.rol for er in Empleado_Rol.objects.filter(usuario=user)]
    permisos_roles = Rol_Permiso.objects.filter(id_rol__in=roles,id_permiso=permiso,id_grupo_permiso=categoria)
    return permisos_roles.__len__() >= 1

def checkUserHasGroup(user,category:str):
    categoria = Grupo_Permiso.objects.filter(nombre=category).first()
    roles = [er.rol for er in Empleado_Rol.objects.filter(usuario=user)]
    permisos_roles = Rol_Permiso.objects.filter(id_rol__in=roles,id_grupo_permiso=categoria)
    return permisos_roles.__len__() >= 1

def validarPermisoUsuario (category:str,permission:str):
    def checkPermision(user):
        return checkUserHasPermission(user,category,permission)
    return user_passes_test(checkPermision)

def validarPermisosUsuario (category:str,permissions):
    def checkPermisions(user):
        for permiso in permissions:
            if checkUserHasPermission(user, category, permiso): return True
        return False
    return user_passes_test(checkPermisions)
