import base64
import requests
import json


def git_file(filepath, filename, content):
    return {"filepath": filepath, "filename": filename, "content": content}


class GitRepo:
    def __init__(self, repo_url, token):
        self.repo_url = repo_url
        self.token = token
        # Ajuste a URL do repositório aqui
        repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
        self.api_url = f"https://api.github.com/repos/{repo_name}"
        self.headers = {"Authorization": f"token {token}"}

    def list_files(self, branch="master"):
        response = requests.get(
            f"{self.api_url}/git/trees/{branch}?recursive=1", headers=self.headers
        )
        response.raise_for_status()
        tree = response.json()["tree"]
        files = []
        for item in tree:
            if item["type"] == "blob":
                file_content = base64.b64decode(
                    requests.get(item["url"], headers=self.headers).json()["content"]
                ).decode("utf-8")
                path = "/".join(item["path"].split("/")[:-1])
                filename = item["path"].split("/")[-1]
                files.append(git_file(path, filename, file_content))
        return files

    def update_files(self, branch_name, git_files, default_branch="master"):
        branch_url = f"{self.api_url}/branches/{branch_name}"
        # Check if the branch already exists
        response = requests.get(branch_url, headers=self.headers)

        if response.status_code == 200:
            # Branch exists, get the latest commit SHA
            latest_commit_sha = response.json()["commit"]["sha"]
        else:
            # Branch does not exist, create the branch
            # Get the latest commit SHA of the default branch
            default_branch_url = f"{self.api_url}/git/ref/heads/{default_branch}"
            response = requests.get(default_branch_url, headers=self.headers)
            latest_commit_sha = response.json()["object"]["sha"]

            # Create the new branch
            data = json.dumps(
                {"ref": f"refs/heads/{branch_name}", "sha": latest_commit_sha}
            )
            requests.post(f"{self.api_url}/git/refs", headers=self.headers, data=data)

        # Get the SHA of the latest commit on master
        base_tree_sha = requests.get(
            f"{self.api_url}/git/commits/{latest_commit_sha}", headers=self.headers
        ).json()["tree"]["sha"]

        # Create blobs for each file
        blobs = []
        for file in git_files:
            blob_data = {
                "content": base64.b64encode(file["content"].encode("utf-8")).decode(
                    "utf-8"
                ),
                "encoding": "base64",
            }
            response = requests.post(
                f"{self.api_url}/git/blobs", headers=self.headers, json=blob_data
            )
            print(response.json())
            blob_sha = response.json()["sha"]
            blobs.append(
                {
                    "path": (file["filepath"] + "/" if file["filepath"] != "" else "")
                    + file["filename"],
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                }
            )

        # Create a new tree
        tree_data = {"base_tree": base_tree_sha, "tree": blobs}
        tree_sha_json = requests.post(
            f"{self.api_url}/git/trees", headers=self.headers, json=tree_data
        ).json()
        tree_sha = tree_sha_json["sha"]

        # Create a new commit
        commit_data = {
            "message": f"Update files in {branch_name}",
            "author": {
                "name": "GitHub Actions",
                "email": "eduardo.manrique@gmail.com",
                "date": "2021-04-11T14:00:00+02:00",
            },
            "parents": [latest_commit_sha],
            "tree": tree_sha,
        }
        commit_sha = requests.post(
            f"{self.api_url}/git/commits", headers=self.headers, json=commit_data
        ).json()["sha"]

        # Update the branch to point to the new commit
        data = json.dumps({"sha": commit_sha, "force": True})
        requests.patch(branch_url, headers=self.headers, data=data)
