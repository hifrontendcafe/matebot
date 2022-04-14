# -*- coding: utf-8 -*-

from datetime import date, datetime, timezone
import logging
import sys
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from discord import User
from libs.database import Database as DB

log = logging.getLogger(__name__)

class ReminderCore:
    """ Clase ReminderBase

    Se encarga de almacenar los eventos y crear recordatorios.
    """

    def __init__(self, db: DB):
        # Accedo a la base de datos
        self.db = db

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


    # Funciones privadas

    def _remove_by_id(self, id_: str):
        try:
            doc = self.db.delete(self.collection, id_)
            self.sched.remove_job(doc['data']['job'])
            return doc
        except:
            return []


    def _remove_by_id_and_author(self, id_: str, author: str):
        try:
            doc = self.db.delete_by_id_and_author(self.collection, self.indexes['by_id_and_author'], id_, author)
            self.sched.remove_job(doc['data']['job'])
            return doc
        except:
            return None


    async def _remove_old_event(self):
        self.db.delete_by_expired_time(self.indexes['by_time'])


    def _create_job(self, event):
        if event['type'] == 'cron':
            cron = event['cron']
            job = self.sched.add_job(
                self.action,
                'cron',
                year=cron.get('year'),
                month=cron.get('month'),
                day=cron.get('day'),
                day_of_week=cron.get('day_of_week'),
                week=cron.get('week'),
                hour=cron.get('hour'),
                minute=cron.get('minute'),
                start_date=cron.get('start_date'),
                end_date=cron.get('end_date'),
                timezone=cron.get('timezone'),
                args=[event['message'], event['content'], event['channel']] # message, embed, channel
            )
            return job.id
        elif event['type'] == 'date':
            job = self.sched.add_job(
                self.action,
                'date',
                run_date=event['time'],
                args=[event['message'], event['content'], event['channel']] # message, embed, channel
            )
            return job.id
        else:
            log.warn("Event type has to be 'cron' or 'date': %s", event)


    def _generate_event(self, trigger, trigger_data, author, channel, message, content):
        if trigger == 'cron':
            return {
                'author':    str(author),
                'author_id': str(author.id),
                'channel':   str(channel),
                'message':   message,
                'content':   content,
                'cron':      trigger_data,
                'type':      'cron'
            }
        elif trigger == 'date':
            return {
                'author':    str(author),
                'author_id': str(author.id),
                'channel':   str(channel),
                'message':   message,
                'content':   content,
                'time':      trigger_data,
                'type':      'date'
            }
        else:
            return {}


    # Funciones publicas
    async def add_cron(self, author: User, channel: str, content: str, message: str, cron: dict):
        """Agrega un nuevo recordatio de tipo cron"""

        date_time_now = datetime.utcnow().replace(tzinfo=timezone.utc)

        event = self._generate_event('cron', cron, author, channel, message, content)
        job_id = self._create_job(event)

        # Guardo el evento en la base de datos
        data = {
            'author':     event['author'],
            'author_id':  event['author_id'],
            'channel':    event['channel'],
            'content':    event['content'],
            'message':       event['message'],
            'created_at': date_time_now.strftime("%Y-%m-%d | %H:%M | %z"),
            'cron':       event['cron'],
            'job':        job_id,
            'type':       'cron'
        }

        # Genero un registro local
        return self.db.create(self.collection, data)


    async def add_date(self, author: User, channel: str, message: str, content, time: datetime) -> dict:
        """Agrega un nuevo recordatio de tipo date"""

        try:
            date_time = time
            date_time_now = datetime.utcnow().replace(tzinfo=timezone.utc)

            log.info(f'Actual: {date_time_now}')
            log.info(f'Elegida: {date_time}')

            # Si la fecha del evento es anterior a la actual salgo
            if date_time < date_time_now:
                # Si el formato de la fecha es
                log.error(f'Error... Current time: {date_time_now} | Selected time: {date_time}')
                return {}

            event = self._generate_event('date', date_time, author, channel, message, content)
            job_id = self._create_job(event)

            # Guardo el evento en la base de datos
            data = {
                'author':     event['author'],
                'author_id':  event['author_id'],
                'channel':    event['channel'],
                'message':       event['message'],
                'content':    event['content'],
                'created_at': date_time_now.strftime("%Y-%m-%d | %H:%M | %z"),
                'job':        job_id,
                'str_time':   event['time'].strftime("%Y-%m-%d | %H:%M | %z"),
                'time':       self.db.q.time(event['time'].isoformat()),
                'type':       'date'
            }

            log.info(f'DATOS: {data}')
            # Genero un registro local
            return self.db.create(self.collection, data)
        except:
            # Si el formato de la fecha es incorrecto
            log.error(f'Error... {sys.exc_info()[0]}')
            return {}


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
            event = {}
            event_type = doc['data']['type']
            if event_type == 'cron':
                event = {
                    'channel': doc['data']['channel'],
                    'content': doc['data']['content'],
                    'message': doc['data']['message'],
                    'cron':    doc['data']['cron'],
                    'type':    'cron'
                }
            elif event_type == 'date':
                event = {
                    'channel': doc['data']['channel'],
                    'content': doc['data']['content'],
                    'message': doc['data']['message'],
                    'time':    datetime.fromisoformat(f"{doc['data']['time'].value[:-1]}+00:00"),
                    'type':    'date'
                }
            else:
                continue

            # Creo el job
            job_id = self._create_job(event)
            new_docs.append((doc['ref'].id(), {"job": job_id}))

        # Actulizo la base de datos con los nuevos jobs_id
        return self.db.update_all_jobs(self.collection, new_docs)


    async def list(self):
        """Lista todos los eventos programados"""

        events = self.db.get_all(self.indexes['all'])
        return events['data']


    async def remove(self, id_, author) -> dict:
        """Borro un evento programado"""

        return self._remove_by_id_and_author(id_, author)
