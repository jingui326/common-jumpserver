from logging import StreamHandler

from django.conf import settings
from celery import current_task
from celery.signals import task_prerun, task_postrun
from kombu import Connection, Exchange, Queue, Producer
from kombu.mixins import ConsumerMixin

from .utils import get_celery_task_log_path

routing_key = 'celery_log'
celery_log_exchange = Exchange('celery_log_exchange', type='direct')
celery_log_queue = [Queue('celery_log', celery_log_exchange, routing_key=routing_key)]


class CeleryLoggerConsumer(ConsumerMixin):
    def __init__(self):
        self.connection = Connection(settings.CELERY_LOG_BROKER_URL)

    def get_consumers(self, Consumer, channel):
        return [Consumer(queues=celery_log_queue,
                         accept=['pickle', 'json'],
                         callbacks=[self.process_task])
                ]

    def handle_task_start(self, task_id, message):
        pass

    def handle_task_end(self, task_id, message):
        pass

    def handle_task_log(self, task_id, msg, message):
        pass

    def process_task(self, body, message):
        action = body.get('action')
        task_id = body.get('task_id')
        msg = body.get('msg')
        if action == CeleryLoggerProducer.ACTION_TASK_LOG:
            self.handle_task_log(task_id, msg, message)
        elif action == CeleryLoggerProducer.ACTION_TASK_START:
            self.handle_task_start(task_id, message)
        elif action == CeleryLoggerProducer.ACTION_TASK_END:
            self.handle_task_end(task_id, message)


class CeleryLoggerProducer:
    ACTION_TASK_START, ACTION_TASK_LOG, ACTION_TASK_END = range(3)

    def __init__(self):
        self.connection = Connection(settings.CELERY_LOG_BROKER_URL)

    @property
    def producer(self):
        return Producer(self.connection)

    def publish(self, payload):
        self.producer.publish(
            payload, serializer='json', exchange=celery_log_exchange,
            declare=[celery_log_exchange], routing_key=routing_key
        )

    def log(self, task_id, msg):
        payload = {'task_id': task_id, 'msg': msg, 'action': self.ACTION_TASK_LOG}
        return self.publish(payload)

    def read(self):
        pass

    def flush(self):
        pass

    def task_end(self, task_id):
        payload = {'task_id': task_id, 'action': self.ACTION_TASK_END}
        return self.publish(payload)

    def task_start(self, task_id):
        payload = {'task_id': task_id, 'action': self.ACTION_TASK_START}
        return self.publish(payload)


class CeleryTaskLoggerHandler(StreamHandler):
    terminator = '\r\n'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        task_prerun.connect(self.on_task_start)
        task_postrun.connect(self.on_start_end)

    @staticmethod
    def get_current_task_id():
        if not current_task:
            return
        task_id = current_task.request.root_id
        return task_id

    def on_task_start(self, sender, task_id, **kwargs):
        return self.handle_task_start(task_id)

    def on_start_end(self, sender, task_id, **kwargs):
        return self.handle_task_end(task_id)

    def emit(self, record):
        task_id = self.get_current_task_id()
        if not task_id:
            return
        try:
            self.write_task_log(task_id, record)
            self.flush()
        except Exception:
            self.handleError(record)

    def write_task_log(self, task_id, msg):
        pass

    def handle_task_start(self, task_id):
        pass

    def handle_task_end(self, task_id):
        pass


class CeleryTaskMQLoggerHandler(CeleryTaskLoggerHandler):
    def __init__(self):
        self.producer = CeleryLoggerProducer()
        super().__init__(stream=None)

    def write_task_log(self, task_id, record):
        msg = self.format(record)
        self.producer.log(task_id, msg)

    def flush(self):
        self.producer.flush()


class CeleryTaskFileHandler(CeleryTaskLoggerHandler):
    def __init__(self):
        self.files = {}
        super().__init__(stream=None)

    def get_file(self, task_id, auto_create=True):
        f = self.files.get(task_id)
        if not f and auto_create:
            f = self.create_task_log_f(task_id)
            self.files[task_id] = f
        return f

    def create_task_log_f(self, task_id):
        log_path = get_celery_task_log_path(task_id)
        f = open(log_path, 'a')
        self.files[task_id] = f
        return f

    def write_task_log(self, task_id, record):
        msg = self.format(record)
        f2 = open('/tmp/abc.log', 'a')
        f2.write(msg)
        f = self.get_file(task_id)
        f.write(msg)
        f.write(self.terminator)
        f.flush()

    def flush(self):
        task_id = self.get_current_task_id()
        f = self.get_file(task_id, auto_create=False)
        if f:
            f.flush()

    def handle_task_start(self, task_id):
        self.create_task_log_f(task_id)

    def handle_task_end(self, task_id):
        f = self.files.pop(task_id, None)
        if f and not f.closed:
            f.close()
