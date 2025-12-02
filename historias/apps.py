from django.apps import AppConfig

class HistoriasConfig(AppConfig):
    name = 'historias'

    def ready(self):
        import historias.signals
