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

class CollectionCycle(Base):
    CollectionCycleName = db.Column(db.String(80), nullable=False)
    StartDate = db.Column(db.String(80), nullable=True)
    EndDate = db.Column(db.String(80), nullable=True)
    InvestigationId = db.Column(db.String(80), nullable=True)
    ArtifactCount = db.Column(db.Integer, nullable=True)
    CollectionCycleType = db.Column(db.String(80), nullable=True)

    def to_dict(self):
        return {
            'CollectionCycleName': self.CollectionCycleName,
            'CollectionCycleStart': self.StartDate,
            'CollectionCycleEnd': self.EndDate,
            'ArtifactCount': self.ArtifactCount
        }

class Artifact(Base):
    ArtifactName = db.Column(db.String(80), nullable=False)
    ArtifactDescription = db.Column(db.String(160), nullable=False)
    ArtifactCycle = db.Column(db.Integer, db.ForeignKey(
        'collection_cycle.id'), nullable=False)
    ArtifactIntegrityHash = db.Column(db.String(80), nullable=True)
    ArtifactHost = db.Column(db.String(80), nullable=True) 
    ArtifactData = db.Column(db.String(80), nullable=True)

    def to_dict(self):
        return {
            'ArtifactName': self.ArtifactName,
            'ArtifactDescription': self.ArtifactDescription,
            'ArtifactData': self.ArtifactData,
            'ArtifactHost': self.ArtifactHost,
            'ArtifactIntegrityHash': self.ArtifactIntegrityHash,
            'ArtifactDbModifiedTime': str(self.date_modified)
        }

class ArtifactType(Base):
    ArtifactTypeName = db.Column(db.String(80), unique=False, nullable=False)
    ArtifactId = db.Column(db.Integer, db.ForeignKey('artifact.id'), nullable=False)
    ArtifactCollectionTime = db.Column(db.String(80), nullable=True)

    def to_dict(self):
            return {
        'ArtifactTypeName': self.ArtifactTypeName,
    }

class ArtifactTypeAttributes(Base):
    ArtifactTypeAttributeName = db.Column(db.String(80), unique=False, nullable=False)
    ArtifactTypeAttributeValue = db.Column(db.String(80), unique=False, nullable=False)

    ArtifactTypeId = db.Column(db.Integer, db.ForeignKey(
        'artifact_type.id'), nullable=False)

    def to_dict(self):
            return {
        'ArtifactTypeAttributeName': self.ArtifactTypeAttributeName,
        'ArtifactTypeAttributeValue': self.ArtifactTypeAttributeValue
    }
    

