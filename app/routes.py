import os
from dotenv import load_dotenv
from flask import jsonify, request
from flasgger import swag_from
from app import app
from app.git import GitRepo
import traceback

load_dotenv()

repos = {}


def get_repo(project):
    if project not in repos:
        token = os.getenv(f"{project}_TOKEN")
        repo_name = os.getenv(f"{project}_REPO_NAME")
        repos[project] = GitRepo(repo_name, token)

    return repos[project]


@app.route("/")
@swag_from("../swagger.yaml", methods=["GET"])
def list_content():
    project_name = request.args.get("project", default=None)
    repo = get_repo(project_name)
    files = repo.list_files()
    return jsonify(files)


@app.route("/", methods=["PUT"])
@swag_from("../swagger.yaml", methods=["PUT"])
def update_content():
    try:
        data = request.get_json()
        if "body" in data:
            data = data["body"]
        if not data or "branchName" not in data or "files" not in data:
            return (
                jsonify({"error": "Invalid request data", "details": data}),
                400,
            )
        project_name = data["project"]
        repo = get_repo(project_name)
        repo.update_files(data["branchName"], data["files"])
        return jsonify({"message": "Files updated successfully"}), 204
    except Exception as e:
        error_trace = traceback.format_exc()
        return jsonify({"errorXXX": error_trace}), 500
