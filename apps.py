{% load static %}<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block titulo %}Red barrial{% endblock %}</title>
  <link rel="stylesheet" href="{% static 'css/app.css' %}">
</head>
<body>
  <header>
    <a class="marca" href="{% url 'home' %}">Red barrial · Banco de alimentos</a>
    <nav>
      {% if user.is_authenticated %}
        <span>{{ user.get_full_name|default:user.username }}</span>
        <form method="post" action="{% url 'oidc_logout' %}">
          {% csrf_token %}
          <button type="submit" class="secundario">Salir</button>
        </form>
      {% endif %}
    </nav>
  </header>
  <main>{% block contenido %}{% endblock %}</main>
</body>
</html>
