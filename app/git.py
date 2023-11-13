import os
import base64
import requests
from git import Repo


class GitFile:
    def __init__(self, filepath, filename, content):
        self.filepath = filepath
        self.filefilename = filename
        self.content = content

    def __repr__(self):
        return f"GitFile(filepath={self.filepath}, filename={self.filename})"

    def __str__(self):
        return f"{self.filepath}/{self.filename}"

    def __eq__(self, other):
        return self.filepath == other.filepath and self.filename == other.filename

    def __hash__(self):
        return hash((self.filepath, self.filename))

    def __lt__(self, other):
        return str(self) < str(other)

    def __le__(self, other):
        return str(self) <= str(other)

    def __gt__(self, other):
        return str(self) > str(other)

    def __ge__(self, other):
        return str(self) >= str(other)

    def __ne__(self, other):
        return not self.__eq__(other)


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
                files.append(
                    GitFile(item["path"], item["path"].split("/")[-1], file_content)
                )
        return files

    def update_files(self, branch_name, git_files):
        # Check if the branch already exists
        response = requests.get(
            f"{self.api_url}/branches/{branch_name}", headers=self.headers
        )
        if response.status_code == 200:
            raise Exception(f"Branch '{branch_name}' already exists.")

        # Get the SHA of the latest commit on master
        master_sha = requests.get(
            f"{self.api_url}/git/ref/heads/master", headers=self.headers
        ).json()["object"]["sha"]
        base_tree_sha = requests.get(
            f"{self.api_url}/git/commits/{master_sha}", headers=self.headers
        ).json()["tree"]["sha"]

        # Create blobs for each file
        blobs = []
        for file in git_files:
            blob_data = {
                "content": base64.b64encode(file.content.encode("utf-8")).decode(
                    "utf-8"
                ),
                "encoding": "base64",
            }
            blob_sha = requests.post(
                f"{self.api_url}/git/blobs", headers=self.headers, json=blob_data
            ).json()["sha"]
            blobs.append(
                {
                    "path": file.filepath,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                }
            )

        # Create a new tree
        tree_data = {"base_tree": base_tree_sha, "tree": blobs}
        tree_sha = requests.post(
            f"{self.api_url}/git/trees", headers=self.headers, json=tree_data
        ).json()["sha"]

        # Create a new commit
        commit_data = {
            "message": f"Update files in {branch_name}",
            "author": {
                "name": "GitHub Actions",
                "email": "eduardo.manrique@gmail.com",
                "date": "2021-04-11T14:00:00+02:00",
            },
            "parents": [master_sha],
            "tree": tree_sha,
        }
        commit_sha = requests.post(
            f"{self.api_url}/git/commits", headers=self.headers, json=commit_data
        ).json()["sha"]

        # Create a new branch
        branch_data = {"ref": f"refs/heads/{branch_name}", "sha": commit_sha}
        requests.post(
            f"{self.api_url}/git/refs", headers=self.headers, json=branch_data
        )

    def delete_branch(self, branch_name):
        # Check if the branch exists in the remote repository
        if f"origin/{branch_name}" in self.repo.git.branch("-r"):
            # Delete the branch from the remote repository
            self.repo.git.push("origin", "--delete", branch_name)
            return True
        else:
            return False
