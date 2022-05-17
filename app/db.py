import datetime
from flask import jsonify, make_response, request
import json

from sqlalchemy import ForeignKey, desc
from app import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy(app)


## TODO: 1. Check Unique fields --> constraints in general
##       2. Check Insert logic and O(n) rn you loop thorugh everything O(n)^3 (performance check)
#        3. Check db initialization --> maybe ask Thierry
#   
class CollectionCycle(db.Model):
    CollectionCycleId = db.Column(db.Integer, primary_key=True)
    CollectionCycleName = db.Column(db.String(80), nullable=False)
    StartDate = db.Column(db.String(80), nullable=False)
    EndDate = db.Column(db.String(80), nullable=False)

    def to_dict(self):
        return {
            'CollectionCycleName': self.CollectionCycleName,
            'CollectionCycleStart': self.StartDate,
            'CollectionCycleEnd': self.EndDate
        }


class Host(db.Model):
    HostId = db.Column(db.Integer, primary_key=True)
    HostName = db.Column(db.String(80), unique=True, nullable=False)
    CollectionCycle = db.Column(db.Integer, db.ForeignKey(
        'collection_cycle.CollectionCycleId'))

    def to_dict(self):
        return {
            'HostId': self.HostId,
            'HostName': self.HostName,
            'CollectionCycle': self.CollectionCycle
        }


class Artifact(db.Model):
    ArtifactId = db.Column(db.Integer, primary_key=True)
    ArtifactName = db.Column(db.String(80), nullable=False)
    ArtifactDescription = db.Column(db.String(160), nullable=False)

    ArtifactHost = db.Column(
        db.Integer, db.ForeignKey('host.HostId'), nullable=False)

    def to_dict(self):
        return {
            'ArtifactId': self.ArtifactId,
            'ArtifactName': self.ArtifactName,
            'ArtifactDescription': self.ArtifactDescription, 
            'ArtifactHost': self.ArtifactHost
        }


class ArtifactSource(db.Model):
    ArtifactSoruceId = db.Column(db.Integer, primary_key=True)
    ArtifactSourceName = db.Column(db.String(80), unique=True, nullable=False)

    ArtifactId = db.Column(db.Integer, db.ForeignKey('artifact.ArtifactId'), nullable=False)

    def to_dict(self):
            return {
        'ArtifactSourceId': self.ArtifactSoruceId,
        'ArtifactSourceName': self.ArtifactSourceName,
        'ArtifactId': self.ArtifactId
    }


class ArtifactType(db.Model):
    ArtifactTypeId = db.Column(db.Integer, primary_key=True)
    ArtifactTypeName = db.Column(db.String(80), unique=True, nullable=False)
    ArtifactId = db.Column(db.Integer, db.ForeignKey('artifact.ArtifactId'), nullable=False)

    def to_dict(self):
            return {
        'ArtifactTypeId': self.ArtifactId,
        'ArtifactTypeName': self.ArtifactTypeName,
        'ArtifactId': self.ArtifactId
    }


class ArtifactTypeAttributes(db.Model):
    ArtifactTypeattributeId = db.Column(db.Integer, primary_key=True)
    ArtifactTypeAttributeName = db.Column(db.String(80), unique=True, nullable=False)
    ArtifactTypeAttributeValue = db.Column(db.String(80), unique=True, nullable=False)

    ArtifactTypeId = db.Column(db.Integer, db.ForeignKey(
        'artifact_type.ArtifactTypeId'), nullable=False)

    def to_dict(self):
            return {
        'ArtifactTypeattributeId': self.ArtifactTypeattributeId,
        'ArtifactTypeAttributeName': self.ArtifactTypeAttributeName,
        'ArtifactTypeAttributeValue': self.ArtifactTypeAttributeValue,
        'ArtifactTypeId': self.ArtifactTypeId
    }
    
db.create_all()


## Method to Store one or multiple CollectionCycles to the DB. CollectionCycles are represetned as JSON - Object.
## {"CollectionCycle":[{"Hostname":1, "HostOs": CentOS, "Artifacts":[{"ArtifactName" : 1}, {"ArtifactName" : 2}]}}, {"Hostname":2, "HostOs": RaspbianBuster, "Artifacts":[{"ArtifactName" : 1}, {"ArtifactName" : 2}]}]}
@app.route("/artifacts", methods=['POST'])
def store_artifact():

    if request.is_json:
        # Get Data From json
        artifact_data = request.get_json()

        # extract cycles for esier parsing
        cycles = artifact_data['CollectionCycles']

        # loop through cycles and store them in db
        for i in range(len(cycles)):

            collectionCycle = CollectionCycle(

                CollectionCycleName=cycles[i]['name'],
                StartDate=cycles[i]['dateStart'],
                EndDate=cycles[i]['dateEnd']
            )

            db.session.add(collectionCycle)
            db.session.flush()
            # grab cycle ID so we can use it for hosts
            cycleId = collectionCycle.CollectionCycleId

            # Grab host list for easier parsing
            hosts = cycles[i]['Hosts']

            # cycle through hosts and them to db
            for j in range(len(hosts)):
                host = Host(
                    HostName=hosts[j]['HostName'],
                    CollectionCycle=cycleId
                )
                db.session.add(host)
                db.session.flush()
                # grab HostID for Artifacts
                hostId = host.HostId

                # grab Artifacts ..
                artifacts = hosts[j]['HostArtifacts']

                # loop through artifacts and store them.
                for k in range(len(artifacts)):

                    artifact = Artifact(
                        ArtifactName=artifacts[k]['ArtifactName'],
                        ArtifactDescription=artifacts[k]['ArtifactDescription'],
                        ArtifactHost=hostId

                    )
                    db.session.add(artifact)

            db.session.commit()

        # Response

        response_body = {

            "name": artifact_data.get("CollectionCycleName"),
            "Start": artifact_data.get("CollectionCycleStart"),
            "End": artifact_data.get("CollectionCycleEnd"),
            "message": "JSON received!"
        }
        res = make_response(jsonify(response_body), 300)
        return res

    else:
        return make_response(jsonify({"message": "Reueqst body must be JSOn"}), 400)
