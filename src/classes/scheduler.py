from datetime import datetime

from apscheduler.triggers.cron import CronTrigger
from flask_apscheduler import APScheduler

from database import db
from src.enums import MatchStatus


class Scheduler:
    _instance = None
    _scheduler = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super().__new__(cls)
        if not cls._scheduler:
            cls._scheduler = APScheduler()
        return cls._instance

    def __init__(self, db_populator):
        self.db_populator = db_populator

    def start(self):
        self._scheduler.start()

    def remove_all_jobs(self):
        self._scheduler.remove_all_jobs()

    def shutdown(self, wait):
        self._scheduler.shutdown(wait=wait)

    def init_app(self, app):
        self._scheduler.init_app(app)

    def get_jobs(self):
        jobs = self._scheduler.get_jobs()
        for i in jobs:
            print(i)

    def schedule_repopulate_matches(self):
        trigger = CronTrigger(day_of_week='sun', hour=0, minute=0)
        self._scheduler.add_job(id='repopulate_matches', func=lambda: self.populate_matches(), trigger=trigger)

    def add_match_to_scheduler(self, match_id, sets, start_date):
        self._scheduler.add_job(func=lambda: self.wake_up_result_scrapping(match_id, sets), trigger='date',
                                run_date=start_date, id=f'generate_{match_id}', replace_existing=True)

    def wake_up_result_scrapping(self, match_id, sets):
        for set in range(1, sets):
            self._scheduler.add_job(id=f'update_{match_id}_{set}', func=lambda: self.update_result(match_id, set),
                                    trigger='interval', seconds=15)
        self._scheduler.add_job(id=f'update_{match_id}_{sets}', func=lambda: self.update_result_last(match_id, sets),
                                trigger='interval', seconds=15)

    def update_result(self, match_id, set):
        with self._scheduler.app.app_context():
            saved = self.db_populator.populate_result(match_id, set, session=db.session())
            if saved:
                self._scheduler.remove_job(f'update_{match_id}_{set}')

    def update_result_last(self, match_id, last_set):
        with self._scheduler.app.app_context():
            saved = self.db_populator.populate_result(match_id, last_set, session=db.session())
            if saved:
                self._scheduler.remove_job(f'update_{match_id}_{last_set}')
                self.db_populator.update_data_from_match(match_id, session=db.session())

    def populate_matches(self):
        with self._scheduler.app.app_context():
            today = datetime.today()
            year = today.year
            actual_month = today.month
            self.db_populator.populate_matches(MatchStatus.NOT_STARTED, year=year, month=actual_month)
            if today.day > 20:
                self.db_populator.populate_matches(MatchStatus.NOT_STARTED, year=year, month=actual_month + 1)
