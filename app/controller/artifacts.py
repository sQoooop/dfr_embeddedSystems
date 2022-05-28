from ctypes import POINTER
from fileinput import filename
import json
import os
from urllib import response

from flask import flash, jsonify, make_response, redirect, render_template, request, Blueprint
from app.db import db, CollectionCycle, Host, Artifact, ArtifactSource, ArtifactType, ArtifactTypeAttributes
from app import config


artifacts_api = Blueprint('artifacts', __name__)

@artifacts_api.route("/")
def index():
    return render_template("index.html")

# Artifact table which accesses artifacts form db (/api/artifactdata)
@artifacts_api.route("/artifact/table")
def render_artifacts():

    return render_template("artifact_table.html", title='Artifact Table')

# ArtifactData for table
@artifacts_api.route("/api/artifactdata")
def return_artifact_from_db():
    return {'data': [a.to_dict() for a in Artifact.query]}

@artifacts_api.route("/api/hostdata")
def return_hosts_from_db():
    return {'hostdata': [h.to_dict() for h in Host.query]}

@artifacts_api.route("/api/collectioncycledata")
def return_ccycle_from_db():
    return {'cycledata': [c.to_dict() for c in CollectionCycle.query]}



# Basic get for artifacts
@artifacts_api.route("/artifact/list")
def return_artifacts():
    return jsonify([a.to_dict() for a in Artifact.query.all()])

# Basic get5 for collectioncycle
@artifacts_api.route("/collectioncycle/list")
def return_collection():
    return jsonify([c.to_dict() for c in CollectionCycle.query.all()])


# Processing a JSON objects File sent to the API
@artifacts_api.route("/upload/artifacts", methods=['GET', 'POST'])
def upload_json_file():
    if request.method == 'POST':

        file = request.files['file']
        filePath = os.path.join(config.UPLOAD_FOLDER, file.filename)
        file.save(filePath)
        cycles = []
        hosts= []
        artifacts= []

        with open(filePath, 'r') as jsonFile:
            json_data = json.load(jsonFile)

            for cycle in json_data['CollectionCycles']:
                print(cycle.get('name'))
                print(cycle.get('dateStart'))
                for host in cycle['Hosts']:
                    print(host.get('HostName'))
                    print(host.get('HostIP'))

                    for artifact in host['HostArtifacts']:
                        print(artifact.get('ArtifactName'))
      

        return "File " + file.filename + " stored succsessfully!"

    else:
        return "Soryy this is not the file we wanted"

@artifacts_api.route('/upload/cycle', methods=['POST'])
def upload_and_store():
 
    data = request.get_json()
    store_collection_cycle(data)
    #file = request.files['file']
    #filePath = os.path.join(config.UPLOAD_FOLDER, file.filename)
    #file.save(filePath)

    return "File  stored succsessfully!"


def store_collection_cycle(artifact_data):

        # extract cycles for esier parsing
        #cycle = artifact_data['CollectionCycle']

        # define collection Cycle object

        collectionCycle = CollectionCycle(

            CollectionCycleName=artifact_data['CycleName'],
            StartDate=artifact_data['CycleStart'],
            EndDate=artifact_data['CycleEnd']
        )

        db.session.add(collectionCycle)
        db.session.flush()
        # grab cycle ID so we can for Artifacts
        cycleId = collectionCycle.id
        artifacts = artifact_data['Artifacts']    
        # loop through artifacts and store them.
        for k in range(len(artifacts)):

            artifact = Artifact(
                ArtifactName=artifacts[k]['ArtifactName'],
                ArtifactDescription=artifacts[k]['ArtifactDescription'],
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

     
@artifacts_api.route("/artifacts", methods=['POST'])
def store_artifact():

    if request.is_json:
        # Get Data From json
        artifact_data = request.get_json()

        # extract cycles for esier parsing
        cycles = artifact_data['CollectionCycle']

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
            cycleId = collectionCycle.id

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
                hostId = host.id

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
        return make_response(jsonify({"message": "Reueqst body must be JSOn" + res}), 400)

@artifacts_api.route('/runtimetest', methods=['POST'])
def test_insertion_time():
    ''' artifact_data = request.get_json()

    name = artifact_data['name']
    tüüp = artifact_data['type']
    source = artifact_data['source']

    collectionCycle = CollectionCycle(
        CollectionCycleName="Lustig hahahaha"
    )
    db.session.add(collectionCycle)
    db.session.flush()

    
    host = Host(HostName= "Der Host", CollectionCycle=collectionCycle.id)
    db.session.add(host)
    db.session.flush()

    artifact = Artifact(
        ArtifactName = name,
        ArtifactDescription = "test",
        ArtifactHost = host.id
    )
        
    db.session.add(artifact)
    db.session.flush()

    tüüüüp = ArtifactType(
        ArtifactTypeName = tüüp,
        ArtifactId = artifact.id,
        ArtifactCollectionTime = artifact.date_created
    )
    db.session.add(tüüüüp)

    source = ArtifactSource(
        ArtifactSourceName = source,
        ArtifactId = artifact.id,

    )
    db.session.add(source)
    db.session.commit() '''

    return "status ok"


@artifacts_api.route('/cycle', methods=['GET', 'POST'])
def store_cycle_file():
    if request.method == 'POST':
    
        file = request.files['file']
        filePath = os.path.join(config.UPLOAD_FOLDER, file.filename)
        file.save(filePath)

        with open (filePath, 'r') as jsonFile:
            json_data = json.load(jsonFile)

            cycleName = json_data['CycleName']
            cycleStart = json_data['CycleStart']
            cycleType = json_data['CycleType']

            artifactName = json_data['Artifacts'][0]['ArtifactName']
            artifactType = json_data['Artifacts'][0]['ArtifactType']
            artifactData = json_data['Artifacts'][0]['ArtifactData']

            artifact = Artifact(
                ArtifactName=artifactName,
                ArtifactDescription=artifactType,
                ArtifactData=artifactData,
                ArtifactHost=1
            )
            db.session.add(artifact)
            db.session.commit()

            
    return "hello myfriend"