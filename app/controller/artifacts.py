from ctypes import POINTER
from fileinput import filename
import json
import os
from urllib import response

from flask import flash, jsonify, make_response, redirect, render_template, request, Blueprint, session
from app.db import db, CollectionCycle, Artifact, ArtifactType, ArtifactTypeAttributes
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
    return {'data': [a.to_dict() for a in Artifact.query.all()]}
# 

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

@artifacts_api.route("/atype/list")
def return_artifact_Types():
    return 

@artifacts_api.route("/atypeattribute/list")
def return_artifact_Type_Attributes():
    completeData = {}
    artifacts = Artifact.query.order_by(Artifact.id.asc()).all()
    for a in artifacts:
        types = ArtifactType.query.filter_by(ArtifactId = a.id).all()
        for t in types:
            attributes = ArtifactTypeAttributes.query.filter_by(ArtifactTypeId = t.id).all()
            attrHelper = {}
            for at in attributes:
                attributeId = "attributeid" + str(at.id)
                attrHelper[attributeId] = at.to_dict()

    
        data = {"artifact": a.to_dict(), "types": t.to_dict()}
        data["types"]["attributes"] = attrHelper

        artId = "artifact" + str(a.id)
     
        completeData[artId] = data 

    
    return jsonify(completeData)


# Processing a JSON objects File sent to the API
@artifacts_api.route("/upload/artifacts", methods=['GET', 'POST'])
def upload_json_file():
    if request.method == 'POST':

        file = request.files['file']
        filePath = os.path.join(config.UPLOAD_FOLDER, file.filename)
        file.save(filePath)


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
    print("sali")
 
    data = request.get_json()
    print(data)
    store_collection_cycle(data)
    #file = request.files['file']
    #filePath = os.path.join(config.UPLOAD_FOLDER, file.filename)
    #file.save(filePath)

    return "File  stored succsessfully!"

def store_collection_cycle(artifact_data):

        # extract cycles for esier parsing
        # define collection Cycle object

        collectionCycle = CollectionCycle(

            CollectionCycleName=artifact_data['CycleName'],
            StartDate=artifact_data['CycleStart'],
            EndDate=artifact_data['CycleEnd'],
            CollectionCycleType=artifact_data['CycleType']
        )

        db.session.add(collectionCycle)
        db.session.flush()
        # grab cycle ID so we can for Artifacts
        cycleId = collectionCycle.id

        # Grab Artifacts
        artifacts = artifact_data['Artifacts']    
        # loop through artifacts and store them.
        for k in range(len(artifacts)):

            artifact = Artifact(
                ArtifactName=artifacts[k]['ArtifactName'],
                ArtifactDescription=artifacts[k]['ArtifactDescription'],
                ArtifactCycle=cycleId
            )
            db.session.add(artifact)
            db.session.flush()

            artifactId = artifact.id

            # Store Artifact Type
            artifactType = ArtifactType(
                ArtifactTypeName = artifacts[k]['ArtifactType'],
                ArtifactId = artifactId
            )
            db.session.add(artifactType)
            db.session.flush()
            artifactTypeid = artifactType.id

            # get attribute object
            artifactAttributes = artifacts[k]['ArtifactTypeAttributes']
            
            # Store attribute Names and values
            for t in artifactAttributes:
                attribute = ArtifactTypeAttributes(
                    ArtifactTypeId = artifactTypeid,
                    ArtifactTypeAttributeName = t,                  
                    ArtifactTypeAttributeValue = artifactAttributes[t]
                )
                db.session.add(attribute)

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
    artifact_data = request.get_json()

    name = artifact_data['name']
    artifactType = artifact_data['type']
    source = artifact_data['source']
    artifactHash = artifact_data['hash']

    collectionCycle = CollectionCycle(
        CollectionCycleName="TestCycle"
    )
    db.session.add(collectionCycle)
    db.session.flush()
    cycleId = collectionCycle.id

    artifact = Artifact(
        ArtifactName = name,
        ArtifactDescription = "test",
        ArtifactCycle=cycleId,
        ArtifactIntegrityHash= artifactHash
    )
        
    db.session.add(artifact)
    db.session.flush()

    artType = ArtifactType(
        ArtifactTypeName = artifactType,
        ArtifactId = artifact.id,
        ArtifactCollectionTime = artifact.date_created
    )
    db.session.add(artType)

    db.session.commit() 

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