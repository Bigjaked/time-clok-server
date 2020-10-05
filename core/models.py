"""This file contains our ORM (Object Relational Mapper) classes for our cloud database
schema. These basically allow us to more easily query and insert into our database
without having to play with sql directly unless we want to. """

from datetime import datetime
from typing import Union

from sqlalchemy import Column, DateTime, Integer, TEXT, UniqueConstraint, desc, String
from sqlalchemy.orm import relationship

from core.database import Model, SurrogatePK, Tracked, reference_col
from core.defines import SECONDS_PER_HOUR
from core.utils import get_date_key, get_month, get_week, parse_date


class SpanQuery:
    id: int


class User(Model, SurrogatePK, Tracked):
    __tablename__ = "time_clok_users"
    name = Column(String(64), unique=True, nullable=False)
    job_id = reference_col("time_clok_jobs", default=None, nullable=True)
    clok_id = reference_col("time_clok", default=None, nullable=True)
    clok = relationship("Clok", lazy="joined")
    job = relationship("Job", lazy="joined")
    last_login = Column(DateTime, onupdate=datetime.now)

    def set_clok(self, clok: "Clok"):
        self.clok = clok
        self.save()

    def set_job(self, job: "Job"):
        self.job = job
        self.save()

    def clear_clok(self):
        self.clok_id = None
        self.save()

    @property
    def to_dict(self):
        return dict(job_id=self.job_id, clok_id=self.clok_id, id=self.id)

    def get_by_month_key(self, key: Union[datetime, int, str] = None, all_jobs=False):
        key = get_month() if key is None else key
        if all_jobs:
            return [
                i
                for i in (
                    Clok.query()
                    .filter(Clok.user_id == self.id)
                    .filter(Clok.month_key == int(key))
                    .all()
                )
            ]
        else:
            return [
                i
                for i in (
                    Clok.query()
                    .filter(Clok.user_id == self.id)
                    .filter(Clok.month_key == int(key))
                    .filter(Clok.job_id == self.job_id)
                    .all()
                )
            ]

    def get_by_week_key(self, key: Union[datetime, int, str] = None, all_jobs=False):
        key = get_week() if key is None else key
        if all_jobs:
            return [
                i
                for i in (
                    Clok.query()
                    .filter(Clok.user_id == self.id)
                    .filter(Clok.week_key == int(key))
                    .all()
                )
            ]
        else:
            return [
                i
                for i in (
                    self.query()
                    .filter(Clok.user_id == self.id)
                    .filter(Clok.week_key == int(key))
                    .filter(Clok.job_id == self.job_id)
                    .all()
                )
            ]

    def get_by_date_key(self, key: Union[datetime, int, str] = None, all_jobs=False):
        key = get_date_key(key)
        if all_jobs:
            return [
                i
                for i in (
                    Clok.query()
                    .filter(Clok.user_id == self.id)
                    .filter(Clok.date_key == key)
                    .all()
                )
            ]
        else:
            return [
                i
                for i in (
                    Clok.query()
                    .filter(Clok.user_id == self.id)
                    .filter(Clok.job_id == self.job_id)
                    .filter(Clok.date_key == key)
                    .all()
                )
            ]

    def get_last_record(self):
        if self.clok is None:
            return (
                Clok.query()
                .filter(Clok.job_id == self.job_id)
                .order_by(desc(Clok.time_in))
                .first()
            )
        else:
            return self.clok

    def get_most_recent_record(cls):
        return cls.query().order_by(desc(cls.id)).first()

    def clock_in(cls, verbose=False):
        cls.clock_in_when(datetime.now(), verbose)

    def clock_in_when(self, when: datetime, verbose=False):

        c = Clok(
            user_id=self.id,
            time_in=when,
            date_key=get_date_key(when),
            month_key=get_month(when),
            week_key=get_week(when),
        )
        c.save()
        self.set_clok(c)
        return c

    def clock_out(cls, verbose=False):
        cls.clock_out_when(datetime.now(), verbose)

    def clock_out_when(cls, when: datetime, verbose=False):
        if verbose:
            print(f"Clocking you out at {when:%Y-%m-%d %H:%M:%S}")
        r = cls.get_last_record()
        r.time_out = when
        r.update_span()
        r.save()

    def get_day_hours(self, key: int = None, all_jobs=False):
        records = self.get_by_date_key(key, all_jobs=all_jobs)
        return sum([i.time_span for i in records])

    def get_week_hours(self, key: int = None, all_jobs=False):
        records = self.get_by_week_key(key, all_jobs=all_jobs)
        return sum([i.time_span for i in records])

    def get_month_hours(self, key: int = None, all_jobs=False):
        records = self.get_by_month_key(key, all_jobs=all_jobs)
        return sum([i.time_span for i in records])

    @classmethod
    def dump(cls):
        return [i.to_dict for i in cls.query().all()]


class Job(Model, SurrogatePK):
    __tablename__ = "time_clok_jobs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), unique=True)

    def __init__(self, name: str, id: int = None):
        if id is not None:
            self.id = id
        self.name = name.lower()

    @staticmethod
    def print_header():
        return f"{'ID':<6} {'Job Name':}"

    def __repr__(self):
        return f"{self.id:<6} {self.name:}"

    @property
    def to_dict(self):
        return dict(id=self.id, name=self.name)

    @classmethod
    def dump(cls):
        return [i.to_dict for i in cls.query().all()]


class Clok(Model, SurrogatePK, SpanQuery):
    __tablename__ = "time_clok"
    __table_args__ = (
        UniqueConstraint("job_id", "user_id", "time_in", "time_out", name="natural"),
    )
    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = reference_col("time_clok_jobs")
    user_id = reference_col("time_clok_users")
    date_key = Column(Integer, default=get_date_key)
    week_key = Column(Integer, default=get_week)
    month_key = Column(Integer, default=get_month)
    time_in = Column(DateTime, default=datetime.now)
    time_out = Column(DateTime, default=None)
    time_span = Column(Integer, default=0)

    journal_entries = relationship("Journal", lazy="joined")
    job = relationship("Job", lazy="joined")

    def __init__(
        self,
        id: int = None,
        job_id: int = None,
        date_key: int = None,
        week_key: int = None,
        month_key: int = None,
        time_in: datetime = None,
        time_out: datetime = None,
        time_span: int = None,
        journal_msg: str = None,
        **kwargs,
    ):
        self.id = id
        self.date_key = date_key
        self.week_key = week_key
        self.month_key = month_key
        self.time_in = parse_date(time_in)
        self.time_out = parse_date(time_out)
        if time_span is not None:
            self.time_span = time_span
        if journal_msg is not None:
            self.add_journal(journal_msg)
        if job_id is not None:
            self.job_id = job_id
        else:
            self.job_id = State.get().job.id

    @property
    def to_dict(self):
        return dict(
            id=self.id,
            job_id=self.job_id,
            date_key=self.date_key,
            week_key=self.week_key,
            month_key=self.month_key,
            time_in=self.time_in,
            time_out=self.time_out,
            time_span=self.time_span,
            journals=self.get_journals,
        )

    def update_span(self):
        if self.time_in and self.time_out:
            self.time_span = (self.time_out - self.time_in).total_seconds()
            self.save()

    @property
    def span(self):
        return round(self.time_span / SECONDS_PER_HOUR, 2)

    def __repr__(self):
        span = 0
        if self.time_out is None:
            to = datetime.now()
            span = round((to - self.time_in).total_seconds() / SECONDS_PER_HOUR, 2)
            time_out = f"(~{to:%H:%M:%S})"
        else:
            time_out = self.time_out.strftime("%H:%M:%S")

        return _clock_format_row(
            self.id,
            self.job.name,
            self.time_in.strftime("%Y-%m-%d"),
            self.month_key,
            self.week_key,
            self.time_in.strftime("%H:%M:%S"),
            time_out,
            self.span + span,
        )

    def __str__(self):
        return self.__repr__()

    def print(self, journal=False):
        h = 0
        clok_info = self.__repr__()
        if self.time_out is None:
            to = datetime.now()
            h = (to - self.time_in).total_seconds() / SECONDS_PER_HOUR
        if journal:
            journals = [i for i in self.journal_entries]
            if journals:
                j_info = "|".join([str(i) for i in journals])
                clok_info += f"{j_info}"
        return clok_info, h

    def add_journal(self, msg: str):
        j = Journal(clock=self, entry=msg)
        j.save()

    @property
    def get_journals(self):
        journals = self.journal_entries
        if journals is not None:
            return [j.entry for j in journals]
        else:
            return None


class Journal(Model, SurrogatePK, Tracked, SpanQuery):
    __tablename__ = "time_clok_journal"

    __table_args__ = (UniqueConstraint("id", "time", name="natural"),)
    clok_id = reference_col("time_clok")
    time = Column(DateTime, default=datetime.now)
    entry = Column(TEXT)

    def __init__(
        self,
        clock: Clok = None,
        clok_id: int = None,
        time: datetime = None,
        entry: str = None,
        id: int = None,
    ):
        self.id = id
        if clok_id is not None:
            self.clok_id = clok_id
        elif clock is not None:
            self.clok_id = clock.id

        self.time = parse_date(time)
        self.entry = entry

    @property
    def to_dict(self):
        return dict(time=self.time, entry=self.entry, id=self.id)

    def __repr__(self):
        return _journal_format_row(self.id, self.entry)

    def __str__(self):
        return self.__repr__()


def _journal_format_row(journal_id, journal_entry) -> str:
    return f"    - ID: {journal_id:<6} {journal_entry:<64}"  # 80 - ( 6 + 10)


def clock_row_header():
    return _clock_format_row(
        "ID", "Job", "Date Key", "Month", "Week", "Clock In", "Clock Out", "Hours "
    )


def _clock_format_row(
    clok_id, job, date, month, week, time_in, time_out, time_span
) -> str:
    return (
        f"{clok_id:<6} "
        f"{job:<10} "
        f"{month:<6} "
        f"{week:<6} "
        f"{date:<11} "
        f"{time_in:<12} "
        f"{time_out:<12} "
        f"{time_span:<6}"
    )