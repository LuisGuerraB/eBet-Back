from datetime import date
import time

from apscheduler.triggers.cron import CronTrigger
from flask_apscheduler import APScheduler

from database import db
from src.enums import MatchStatus
from src.models import Match, Result


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
        res = []
        for i in jobs:
            res.append(str(i))
        return res

    def schedule_matches(self):
        today = date.today()
        year = today.year
        current_month = today.month
        limit = 500
        for month in range(current_month, 13):
            match_list = self.db_populator.api_scrapper.get_list_match(MatchStatus.NOT_STARTED, year, month,
                                                                       leagueId=None, limit=limit,
                                                                       page=0)
            if match_list is None:
                return
            for match_json in match_list:
                if match_json['awayTeamId'] is None or match_json['homeTeamId'] is None:
                    continue
                self.add_match_to_scheduler(match_json['id'], match_json['numberOfGames'],
                                            match_json['scheduledAt'])

    def schedule_repopulate_matches(self):
        trigger = CronTrigger(hour=0, minute=0)
        self._scheduler.add_job(id='repopulate_matches', func=lambda: self.populate_matches(), trigger=trigger)

    def add_match_to_scheduler(self, match_id, sets, start_date):
        self._scheduler.add_job(func=lambda: self.wake_up_result_scrapping(match_id, sets), trigger='date',
                                run_date=start_date, id=f'generate_{match_id}', replace_existing=True,
                                misfire_grace_time=3600, coalesce=False)

    def wake_up_result_scrapping(self, match_id, sets):
        for set in range(1, sets + 1):
            self._scheduler.add_job(id=f'update_{match_id}_{set}', func=lambda num=set: self.update_result(match_id, num),
                                    trigger='interval', minutes=3)
            time.sleep(1)

    def update_result(self, match_id, set):
        with self._scheduler.app.app_context():
            session = db.session(expire_on_commit=False)
            result_json = self.db_populator.populate_result(match_id, set, session=session)
            match = Match.query.get(match_id)
            Result.update_result_from_match(match, session)
            if (result_json is not None and result_json.get('endAt', None) is not None) or match.get_final_number_of_sets() is not None:
                self._scheduler.remove_job(f'update_{match_id}_{set}')
                self.db_populator.update_data_from_match(match, session=session)
                self.db_populator.resolve_bets(match, session=session)
                session.commit()

    def populate_matches(self):
        with self._scheduler.app.app_context():
            today = date.today()
            year = today.year
            current_month = today.month
            self.db_populator.populate_matches(MatchStatus.NOT_STARTED, year=year, month=current_month)
            if today.day > 20:
                self.db_populator.populate_matches(MatchStatus.NOT_STARTED, year=year, month=current_month + 1)
