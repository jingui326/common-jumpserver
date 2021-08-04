from .services.command import ServiceBaseCommand


class Command(ServiceBaseCommand):
    help = 'Stop services'

    def _handle(self):
        stop_daemon = str(self.Services.all) in self.services_names
        self.services_util.stop(self.services, force=self.force, stop_daemon=stop_daemon)
