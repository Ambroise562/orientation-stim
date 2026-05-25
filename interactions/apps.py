from django.apps import AppConfig


class InteractionsConfig(AppConfig):
    name = 'interactions'
    
    def ready(self):
        import interactions.views  # Import signals when app is ready
