import os
from dotenv import load_dotenv
from flask import jsonify, request
from flasgger import swag_from
from app import app
from app.git import GitRepo

load_dotenv()

TOKEN = os.getenv("TOKEN")
REPO_NAME = os.getenv("REPO_NAME")

repo = GitRepo(REPO_NAME, TOKEN)


@app.route("/")
@swag_from("../swagger.yaml", methods=["GET"])
def list_content():
    files = repo.list_files()
    return jsonify([file.to_dict() for file in files])


@app.route("/", methods=["PUT"])
@swag_from("../swagger.yaml", methods=["PUT"])
def update_content():
    data = request.get_json()
    if not data or "branchName" not in data or "files" not in data:
        return jsonify({"error": "Invalid request data"}), 400

    repo.update_files(data["branchName"], data["files"])
    return jsonify({"message": "Files updated successfully"}), 204
