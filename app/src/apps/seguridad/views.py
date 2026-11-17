""" from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    return render(request, "seguridad/home.html")


@login_required
def panel(request):
    roles = sorted(request.user.groups.values_list("name", flat=True))
    return render(request, "seguridad/panel.html", {"roles": roles})
 """
 from django.shortcuts import redirect, render

RUTAS_POR_ROL = {
    "coordinador": "coordinador",
    "referente_comedor": "comedor",
    "voluntario_deposito": "deposito",
}


def home(request):
    roles = []
    if request.user.is_authenticated:
        roles = sorted(request.user.groups.values_list("name", flat=True))
        if len(roles) == 1 and roles[0] in RUTAS_POR_ROL:
            return redirect(RUTAS_POR_ROL[roles[0]])

    return render(request, "seguridad/home.html", {"roles": roles})