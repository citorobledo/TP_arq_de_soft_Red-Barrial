from django.contrib.auth.decorators import login_required
from django.shortcuts import render


def home(request):
    return render(request, "seguridad/home.html")


@login_required
def panel(request):
    roles = sorted(request.user.groups.values_list("name", flat=True))
    return render(request, "seguridad/panel.html", {"roles": roles})
