from functools import wraps

from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def rol_requerido(*roles):
    """Exige sesión iniciada y al menos uno de los roles indicados (403 si no)."""

    def decorador(vista):
        @wraps(vista)
        @login_required
        def envoltura(request, *args, **kwargs):
            if not request.user.groups.filter(name__in=roles).exists():
                return render(request, "seguridad/sin_permisos.html", status=403)
            return vista(request, *args, **kwargs)

        return envoltura

    return decorador
