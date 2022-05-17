import enum
from fileinput import filename
import json
import os
from app import app, db
from flask import jsonify, make_response, render_template, request
from sqlalchemy.orm import session

UPLOAD_FOLDER = r'C:\Users\spooky\Desktop\app\app\data'
ALLOWED_EXTENSIONS = {'json', 'txt'}



# Artifact table which accesses artifacts form db (/api/artifactdata)
@app.route("/artifact/table")
def render_artifacts():

    return render_template("artifact_table.html", title='Artifact Table')

# Data for json table
@app.route("/api/artifactdata")
def return_artifact_from_db():
    return {'data': [a.to_dict() for a in db.Artifact.query]}


# Basic get for artifacts
@app.route("/artifact/list")
def return_artifacts():
    return jsonify([a.to_dict() for a in db.Artifact.query.all()])

# Basic get5 for collectioncycle
@app.route("/collectioncycle/list")
def return_collection():
    return jsonify([c.to_dict() for c in db.CollectionCycle.query.all()])


@app.route("/upload/artifacts", methods=['GET', 'POST'])
def upload_json_file():
    if request.method == 'POST':

        file = request.files['file']
        filePath = os.path.join(UPLOAD_FOLDER, file.filename)
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
