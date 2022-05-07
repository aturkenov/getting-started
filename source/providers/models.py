from uuid import uuid4
from enum import IntEnum
from datetime import date, datetime
from sqlalchemy import *
from sqlalchemy.orm import relationship, validates, declarative_base
from sqlalchemy.sql import func
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from geoalchemy2 import Geometry
from settings import settings
import domain


ORMBaseModel = declarative_base()


class AbstractORMBaseModel(ORMBaseModel):
    __abstract__ = True

    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid4, unique=True, nullable=False)


class Customer(AbstractORMBaseModel):
    __tablename__ = 'ami_customer'

    class TYPES(IntEnum):
        INDIVIDUAL = 0
        ENTITY = 1

    class TEAMS(IntEnum):
        DEALER = 0
        MOUNTER = 1
        WATCHER = 2

    name = Column(String(255), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=False, index=True) # TODO validation
    description = Column(String(255))
    type = Column(SmallInteger(), nullable=False, default=TYPES.INDIVIDUAL.value)
    team = Column(SmallInteger(), nullable=False, default=TEAMS.WATCHER.value)
    first_name = Column(String(150))
    last_name = Column(String(150))
    password = Column(String(128), nullable=False) # TODO validation

    is_active = Column(Boolean, nullable=False, default=True)
    is_superuser = Column(Boolean, nullable=False, default=False)

    last_activity = Column(DateTime(timezone=settings.USE_TIMEZONE), onupdate=func.now())
    date_joined = Column(DateTime(timezone=settings.USE_TIMEZONE), server_default=func.now(), nullable=False)

    parent_id = Column(BigInteger, ForeignKey(f'{__tablename__}.id'))
    children = relationship('Customer')

    devices = relationship('CustomerDevices', back_populates='customer', uselist=False)
    meter_types = relationship('CustomerMeterTypes', back_populates='customer', uselist=False)
    directories = relationship('CustomerDirectories', back_populates='customer', uselist=False)
    meter_inlines = relationship('CustomerMeterInline', back_populates='customer')
    connectors = relationship('CustomerConnectorsAssociation', back_populates='customer')

    __table_args__ = (
        UniqueConstraint('email', 'team', name='unique_email_and_team'),
        CheckConstraint(id != parent_id, name='id not equal to parent_id')
    )

    @validates('type')
    def validate_type(self, key, type):
        if type:
            type_enum_values = tuple(map(lambda item: item.value, self.TYPES))
            if type not in type_enum_values:
                raise InvalidRequestError(f'Customer type must be in {type_enum_values}')
            return type

        return self.TYPES.INDIVIDUAL.value

    @validates('team')
    def validate_type(self, key, team):
        if team:
            team_enum_values = tuple(map(lambda item: item.value, self.TEAMS))
            if team not in team_enum_values:
                raise InvalidRequestError(f'Customer team must be in {team_enum_values}')
            return team

        return self.TEAMS.WATCHER.value

