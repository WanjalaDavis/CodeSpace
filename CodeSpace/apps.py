from django.apps import AppConfig


class CodespaceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'CodeSpace'

    def ready(self):
        import CodeSpace.signals
