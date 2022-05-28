from flask import jsonify, make_response, request

from sqlalchemy import BLOB, ForeignKey, desc
from app import db
from flask_sqlalchemy import SQLAlchemy
import os
import json
import numpy as np
from app import app

db = SQLAlchemy()

class Base(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    date_modified = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())



## TODO: 1. Check Unique fields --> constraints in general
##       2. Check Insert logic and O(n) rn you loop thorugh everything O(n)^3 (performance check)
#        3. Check db initialization --> maybe ask Thierry
#   
class CollectionCycle(Base):
    CollectionCycleName = db.Column(db.String(80), nullable=False)
    StartDate = db.Column(db.String(80), nullable=True)
    EndDate = db.Column(db.String(80), nullable=True)
    CollectionCycleType = db.Column(db.String(80), nullable=True)

    def to_dict(self):
        return {
            'CollectionCycleName': self.CollectionCycleName,
            'CollectionCycleStart': self.StartDate,
            'CollectionCycleEnd': self.EndDate
        }


class Host(Base):
    
    HostName = db.Column(db.String(80), unique=False, nullable=False)
    HostIP = db.Column(db.String(80), unique=False, nullable=True)
    HostOS = db.Column(db.String(80), unique=False, nullable=True)
    CollectionCycle = db.Column(db.Integer, db.ForeignKey(
        'collection_cycle.id'))

    def to_dict(self):
        return {
            'HostId': self.id,
            'HostName': self.HostName,
            'CollectionCycle': self.CollectionCycle
        }


class Artifact(Base):
    ArtifactName = db.Column(db.String(80), nullable=False)
    ArtifactDescription = db.Column(db.String(160), nullable=False)
    ArtifactData = db.Column(BLOB, nullable=True)

    #ArtifactHost = db.Column(
     #   db.Integer, db.ForeignKey('host.id'), nullable=False)

    def to_dict(self):
        return {
            'ArtifactId': self.id,
            'ArtifactName': self.ArtifactName,
            'ArtifactDescription': self.ArtifactDescription, 
        }


class ArtifactSource(Base):
    ArtifactSourceName = db.Column(db.String(80), unique=False, nullable=False)

    ArtifactId = db.Column(db.Integer, db.ForeignKey('artifact.id'), nullable=False)

    def to_dict(self):
            return {
        'ArtifactSourceId': self.id,
        'ArtifactSourceName': self.ArtifactSourceName,
        'ArtifactId': self.ArtifactId
    }


class ArtifactType(Base):
    ArtifactTypeName = db.Column(db.String(80), unique=False, nullable=False)
    ArtifactId = db.Column(db.Integer, db.ForeignKey('artifact.id'), nullable=False)
    ArtifactCollectionTime = db.Column(db.String(80), nullable=True)

    def to_dict(self):
            return {
        'ArtifactTypeId': self.id,
        'ArtifactTypeName': self.ArtifactTypeName,
        'ArtifactId': self.ArtifactId
    }


class ArtifactTypeAttributes(Base):
    ArtifactTypeAttributeName = db.Column(db.String(80), unique=True, nullable=False)
    ArtifactTypeAttributeValue = db.Column(db.String(80), unique=True, nullable=False)

    ArtifactTypeId = db.Column(db.Integer, db.ForeignKey(
        'artifact_type.id'), nullable=False)

    def to_dict(self):
            return {
        'ArtifactTypeattributeId': self.id,
        'ArtifactTypeAttributeName': self.ArtifactTypeAttributeName,
        'ArtifactTypeAttributeValue': self.ArtifactTypeAttributeValue,
        'ArtifactTypeId': self.ArtifactTypeId
    }
    



## Method to Store one or multiple CollectionCycles to the DB. CollectionCycles are represetned as JSON - Object.
## {"CollectionCycle":[{"Hostname":1, "HostOs": CentOS, "Artifacts":[{"ArtifactName" : 1}, {"ArtifactName" : 2}]}}, {"Hostname":2, "HostOs": RaspbianBuster, "Artifacts":[{"ArtifactName" : 1}, {"ArtifactName" : 2}]}]}
