from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render
from .roles import COORDINADOR, REFERENTE_COMEDOR, VOLUNTARIO_DEPOSITO

def home(request):
    return render(request, "seguridad/home.html")


DESTINO_POR_ROL = [
    (COORDINADOR, "coordinador"),
    (VOLUNTARIO_DEPOSITO, "deposito"),
    (REFERENTE_COMEDOR, "comedor"),
]


@login_required
def panel(request):
    roles = set(request.user.groups.values_list("name", flat=True))
    for rol, nombre_url in DESTINO_POR_ROL:
        if rol in roles:
            return redirect(nombre_url)
    return render(request, "seguridad/sin_permisos.html", status=403)