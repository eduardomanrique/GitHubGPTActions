import base64
import requests
import json
import time


def git_file(filename, content):
    return {"filename": filename, "content": content}


class GitRepo:
    def __init__(self, repo_url, token, main_branch):
        self.repo_url = repo_url
        self.token = token
        # Ajuste a URL do repositório aqui
        repo_name = repo_url.replace("https://github.com/", "").replace(".git", "")
        self.api_url = f"https://api.github.com/repos/{repo_name}"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json",
        }
        self.main_branch = main_branch

    def list_files(self, branch_name=None):
        branch_name = branch_name if branch_name else self.main_branch

        response = requests.get(
            f"{self.api_url}/git/trees/{branch_name}?recursive=1",
            headers=self.headers,
        )
        if response.status_code != 200:
            self.create_branch(branch_name)
            # Get the reference of the new branch
            response = requests.get(
                f"{self.api_url}/git/trees/{branch_name}?recursive=1",
                headers=self.headers,
            )

        tree = response.json()["tree"]
        files = []
        for item in tree:
            if item["type"] == "blob":
                file_content = base64.b64decode(
                    requests.get(item["url"], headers=self.headers).json()["content"]
                ).decode("utf-8")
                path = "/".join(item["path"].split("/")[:-1])
                filename = item["path"].split("/")[-1]
                files.append(git_file(f"{path}/{filename}", file_content))
        return files

    def update_files(self, branch_name, git_files, commit_message):
        # Check if branch exists
        branch_url = f"{self.api_url}/git/ref/heads/{branch_name}"
        response = requests.get(branch_url, headers=self.headers)

        if response.status_code == 200:
            # Branch exists, get the latest commit SHA
            latest_commit_sha = response.json()["object"]["sha"]
        else:
            latest_commit_sha = self.create_branch(branch_name)

        # Create a new blob for each file
        tree = []
        for file in git_files:
            data = json.dumps(
                {
                    "content": base64.b64encode(file["content"].encode("utf-8")).decode(
                        "utf-8"
                    ),
                    "encoding": "base64",
                }
            )
            response = requests.post(
                f"{self.api_url}/git/blobs", headers=self.headers, data=data
            )
            blob_sha = response.json()["sha"]
            print("Create blob response:", response.json())
            print("\n\n")
            path = file["filename"]
            if path.startswith("/"):
                path = path[1:]

            tree.append(
                {
                    "path": path,
                    "mode": "100644",
                    "type": "blob",
                    "sha": blob_sha,
                }
            )

        # Create a new tree with the new blobs
        data = json.dumps({"base_tree": latest_commit_sha, "tree": tree})
        response = requests.post(
            f"{self.api_url}/git/trees", headers=self.headers, data=data
        )
        json_response = response.json()
        if "sha" not in json_response:
            raise Exception(f"Error creating tree for {self.api_url}: {json_response}")

        tree_sha = json_response["sha"]
        print("Create tree response:", json_response)
        print("\n\n")
        # Create a new commit with the new tree
        data = json.dumps(
            {
                "message": commit_message,
                "tree": tree_sha,
                "parents": [latest_commit_sha],
            }
        )
        response = requests.post(
            f"{self.api_url}/git/commits", headers=self.headers, data=data
        )
        commit_sha = response.json()["sha"]
        print("Create commit response:", response.json())
        print("\n\n")
        # Update the branch to point to the new commit
        data = json.dumps({"sha": commit_sha, "force": True})

        response = requests.patch(
            f"{self.api_url}/git/refs/heads/{branch_name}",
            headers=self.headers,
            data=data,
        )
        print("Update branch response:", response.json())
        print("\n\n")

    def create_branch(self, branch_name):
        print("Branch does not exist")
        # Branch does not exist, create the branch
        # Get the latest commit SHA of the default branch
        default_branch_url = f"{self.api_url}/git/ref/heads/{self.main_branch}"
        response = requests.get(default_branch_url, headers=self.headers)
        latest_commit_sha = response.json()["object"]["sha"]

        # Create the new branch
        data = json.dumps(
            {"ref": f"refs/heads/{branch_name}", "sha": latest_commit_sha}
        )
        response = requests.post(
            f"{self.api_url}/git/refs", headers=self.headers, data=data
        )
        print("Create branch response:", response.json())
        print("\n\n")
        time.sleep(5)
        return latest_commit_sha
