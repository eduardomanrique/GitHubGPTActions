from flask import jsonify, request
from flasgger import swag_from
from app import app

# Mock data for GET /endpoint1
files = [
    {
        "filepath": "/path/to/file1",
        "content": "File 1 content",
        "filename": "file1.txt",
    },
    {
        "filepath": "/path/to/file2",
        "content": "File 2 content",
        "filename": "file2.txt",
    },
]


@app.route("/")
@swag_from("../swagger.yaml", methods=["GET"])
def home():
    return jsonify({"message": "Welcome to the API!"})


@app.route("/content")
@swag_from("../swagger.yaml", methods=["GET"])
def list_content():
    # Return the mock data
    return jsonify(files)


@app.route("/content", methods=["PUT"])
@swag_from("../swagger.yaml", methods=["PUT"])
def update_content():
    # Extract the request data
    data = request.get_json()

    # Validate the data (this is a very basic validation, you might want to do something more robust)
    if not data or "branchName" not in data or "files" not in data:
        return jsonify({"error": "Invalid request data"}), 400

    # Here you would typically do something with the data, like updating files in a repository
    # For now, let's just return a success message
    return jsonify({"message": "Files updated successfully"}), 204
