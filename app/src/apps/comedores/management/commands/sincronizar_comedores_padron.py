from django.core.management.base import BaseCommand, CommandError

from apps.comedores.services import sincronizar_comedores_padron


class Command(BaseCommand):
    help = "Sincroniza los comedores publicados por el padrón provincial."

    def handle(self, *args, **options):
        try:
            resultado = sincronizar_comedores_padron()
        except (RuntimeError, ValueError) as error:
            raise CommandError(str(error)) from error
        self.stdout.write(
            self.style.SUCCESS(
                "Sincronización completada: "
                f"{resultado['actualizados']} estados actualizados, "
                f"{resultado['sin_cambios']} sin cambios, "
                f"{resultado['sin_coincidencia']} sin coincidencia local."
            )
        )
