# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timezone

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import User

from libs.database import Database as DB

log = logging.getLogger(__name__)

# def my_decorator_name(name):
#     def my_custome_decorator(function): bb
#         def wrapper(*args, **kwargs):
#
#             print('Name:', name)
#             return function(*args, **kwargs)
#
#         return wrapper
#
#     return my_custome_decorator


class Reminder:
    """ Clase Reminder

    Se encarga de almacenar los eventos y crear recordatorios.
    """

    def __init__(self, secret):
        # Accedo a la base de datos
        self.db = DB(secret)

        # Arranco en Async Scheduler
        self.sched = AsyncIOScheduler()
        self.sched.start()


    @property
    def collection(self):
        return self._collection


    @collection.setter
    def collection(self, value):
        if not isinstance(value, str):
            raise ValueError("The value must be a string")
        self._collection = value


    @property
    def indexes(self):
        return self._indexes


    @indexes.setter
    def indexes(self, value):
        if not isinstance(value, dict):
            raise ValueError("The value must be a dictionary")
        self._indexes = value


    @property
    def action(self):
        return self._action


    @action.setter
    def action(self, value):
        if not callable(value):
            raise ValueError("The value must be a function")
        self._action = value


    @property
    def reminders(self):
        return self._reminders


    @reminders.setter
    def reminders(self, value):
        if not isinstance(value, list):
            raise ValueError("The value must be a list")
        self._reminders = value


    # Funciones privadas

    def _remove_by_id(self, id_: str):
        try:
            doc = self.db.delete(self.collection, id_)
            log.info("hola: %s", doc)
            for job in doc['data']['jobs']:
                self.sched.remove_job(job)
            return doc
        except:
            return []


    def _remove_by_id_and_author(self, id_: str, author: str):
        try:
            doc = self.db.delete_by_id_and_author(self.collection, self.indexes['by_id_and_author'], id_, author)
            for job in doc['data']['jobs']:
                self.sched.remove_job(job)
            return doc
        except:
            return []


    async def _remove_old_event(self):
        self.db.delete_by_expired_time(self.indexes['by_time'])


    def _create_jobs(self, event):
        dt_event = event['time']
        dt_now = datetime.utcnow().replace(tzinfo=timezone.utc)

        jobs_id = []
        for reminder in event['reminders']:
            if dt_event > dt_now + reminder['delta']:
                log.info("Added event")
                job = self.sched.add_job(
                    self.action,
                    'date',
                    run_date=(dt_event - reminder['delta']),
                    args=[reminder['message'], event['content'], event['channel']]
                )
                jobs_id.append(job.id)

        # Job para eliminar el registro de la base de datos
        job = self.sched.add_job(
            self._remove_old_event,
            'date',
            run_date=(dt_event),
            args=[]
        )
        jobs_id.append(job.id)

        return jobs_id


    def _generate_event(self, author, date_time, channel, content):
        return {
            "author": str(author),
            "author_id": str(author.id),
            "time": date_time,
            "channel": str(channel),
            "content": content,
            "reminders": self.reminders,
        }

    # Funciones publicas

    async def add(self, author: User, date: datetime, channel: str, content):
        """Agrega un nuevo evento y crea los recordatorios"""

        try:
            # date_time = datetime.fromisoformat(f"{date}T{time}{time_zone}")
            date_time = date
            date_time_now = datetime.utcnow().replace(tzinfo=timezone.utc)

            # Si la fecha del evento es anterior a la actual salgo
            if date_time < date_time_now:
                return []

            event = self._generate_event(author, date_time, channel, content)
            jobs_id = self._create_jobs(event)

            # Guardo el evento en la base de datos
            data = {
                "author": event['author'],
                "author_id": event['author_id'],
                "time": self.db.q.time(event['time'].isoformat()),
                "str_time": event['time'].strftime("%Y-%m-%d | %H:%M | %z"),
                "content": event['content'],
                "channel": event['channel'],
                "jobs": jobs_id
            }

            # Genero un registro local
            return self.db.create(self.collection, data)
        except:
            # Si el formato de la fecha es incorrecto
            return None


    async def load(self):
        """ Carga los eventos de la base de datos

        Se utiliza para cargar los eventos que están guardados en la base de
        datos al momento de inciar el programa.

        Lee los eventos de la base de datos, los carga en el scheduler y
        actuliza la base de datos con los nuevos jobs_id
        """

        docs = self.db.get_all(self.indexes['all'])
        new_docs = []
        for doc in docs['data']:
            event = {
                "content":   doc['data']['content'],
                "time":      datetime.fromisoformat(f"{doc['data']['time'].value[:-1]}+00:00"),
                "channel":   doc['data']['channel'],
                "reminders": self.reminders
            }

            # Creo los jobs
            jobs_id = self._create_jobs(event)
            new_docs.append((doc['ref'].id(), {"jobs": jobs_id}))

        # Actulizo la base de datos con los nuevos jobs_id
        return self.db.update_all_jobs(self.collection, new_docs)


    async def list(self):
        """Lista todos los eventos programados"""

        events = self.db.get_all_by_time(self.indexes['by_time'])
        return events['data']


    async def remove(self, id_, author):
        """Borro un evento programado"""

        return self._remove_by_id_and_author(id_, author)
