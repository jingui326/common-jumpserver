# -*- coding: utf-8 -*-
#
from django.dispatch import receiver
from django.db.models.signals import post_save, m2m_changed

from common.decorator import on_transaction_commit
from common.utils import get_logger
from tickets.models import Ticket

logger = get_logger(__name__)


@receiver(post_save, sender=Ticket)
def on_pre_save_ensure_serial_num(sender, instance: Ticket, created=False, **kwargs):
    if created:
        instance.set_serial_num()


@on_transaction_commit
def after_save_set_rel_snapshot(sender, instance, created=False, update_fields=None, **kwargs):
    if update_fields and list(update_fields)[0] == 'rel_snapshot':
        return
    instance.set_rel_snapshot()


@on_transaction_commit
def on_m2m_change(sender, action, instance, reverse=False, **kwargs):
    if action.startswith('post'):
        instance.set_rel_snapshot()


for ticket_cls in Ticket.__subclasses__():
    post_save.connect(after_save_set_rel_snapshot, sender=ticket_cls)
    m2m_changed.connect(on_m2m_change, sender=ticket_cls)
