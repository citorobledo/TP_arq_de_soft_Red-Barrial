{% extends "base.html" %}
{% block titulo %}Panel · Red barrial{% endblock %}
{% block contenido %}
  <h1>Panel</h1>
  <dl>
    <dt>Usuario</dt><dd>{{ user.username }}</dd>
    <dt>Correo</dt><dd>{{ user.email|default:"—" }}</dd>
    <dt>Roles</dt>
    <dd>
      {% for rol in roles %}<span class="etiqueta">{{ rol }}</span>{% empty %}—{% endfor %}
    </dd>
  </dl>
  {% if not roles %}
    <p class="aviso">Tu usuario no tiene ningún rol asignado. Pedile al coordinador que te asigne uno en Keycloak.</p>
  {% endif %}
{% endblock %}
