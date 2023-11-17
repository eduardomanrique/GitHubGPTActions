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
        main_branch = os.getenv(f"{project}_MAIN_BRANCH")
        repos[project] = GitRepo(
            repo_name, token, main_branch if main_branch else "main"
        )

    return repos[project]


@app.route("/", methods=["POST"])
@swag_from("../swagger.yaml", methods=["POST"])
def list_content():
    data = request.get_json()
    if "body" in data:
        data = data["body"]
    project_name = data["projectName"]
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
        if not data or "files" not in data:
            return (
                jsonify({"error": "Invalid request data", "details": data}),
                400,
            )
        if "branchName" not in data:
            return (
                jsonify({"error": "Branch name is mandatory"}),
                400,
            )
        if "projectName" not in data:
            return (
                jsonify({"error": "Project name is mandatory"}),
                400,
            )
        project_name = data["projectName"]
        repo = get_repo(project_name)
        repo.update_files(
            data["branchName"],
            data["files"],
            "Update files" if "commitMessage" not in data else data["commitMessage"],
        )
        return jsonify({"message": "Files updated successfully"}), 204
    except Exception as e:
        error_trace = traceback.format_exc()
        return jsonify({"errorXXX": error_trace}), 500


@app.route("/privacy-policy", methods=["GET"])
def privacy_policy():
    # Your code here...
    return """
            Privacy Policy of [Your Application Name]

            Last updated: [Date]

            Introduction
            Welcome to [Your Application Name]. We are committed to protecting your personal information and your right to privacy. If you have any questions or concerns about this privacy policy, or our practices with regards to your personal information, please contact us at [Contact Information].

            Data Collection
            We collect personal information that you voluntarily provide to us when you [register on the Application, express an interest in obtaining information about us or our products and services, etc.]. The personal information that we collect depends on the context of your interactions with us and the Application, the choices you make, and the products and features you use.

            Data Usage
            We use personal information collected via our Application for a variety of business purposes described below. We process your personal information for these purposes in reliance on our legitimate business interests, in order to enter into or perform a contract with you, with your consent, and/or for compliance with our legal obligations.

            Data Sharing and Disclosure
            We may share your information with third-party service providers, to protect our rights and fulfill our legal obligations, to comply with legal requirements, and to fulfill business transactions.

            User Rights
            You have the right to request access to the personal information we collect from you, change that information, or delete it. To request to review, update, or delete your personal information, please submit a request to [Contact Information].

            Data Security
            We have implemented appropriate technical and organizational security measures designed to protect the security of any personal information we process.

            Children’s Privacy
            Our Application does not address anyone under the age of 13. We do not knowingly collect personal information from anyone under the age of 13.

            International Data Transfers
            We may transfer, store, and process your information in countries other than your own.

            Compliance with Laws and Regulations
            We will update this policy as necessary to stay compliant with relevant laws.

            Changes to the Privacy Policy
            We may update this privacy policy from time to time. The updated version will be indicated by an updated "Revised" date and the updated version will be effective as soon as it is accessible.

            Contact Information
            If you have questions or comments about this policy, you may contact us at [Email Address], [Phone Number], or by mail at [Physical Address].
"""
