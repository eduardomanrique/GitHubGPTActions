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


from git import Repo


class GitRepo:
    def __init__(self, repo_path):
        self.repo = Repo(repo_path)

    def list_files(self):
        # Checkout the develop branch
        self.repo.git.checkout("develop")

        # Get the current commit
        commit = self.repo.commit("HEAD")

        # Get the list of files in the current commit
        files = commit.tree.traverse()

        # Convert the list of files to a list of GitFile objects
        return [
            GitFile(f.path, f.data_stream.read().decode("utf-8"), f.name)
            for f in files
            if f.type == "blob"
        ]

    def update_files(self, branch_name, files):
        # Checkout the specified branch
        self.repo.git.checkout(branch_name)

        # Update the files
        for file in files:
            with open(file.filepath, "w") as f:
                f.write(file.content)

        # Commit the changes
        self.repo.git.add("--all")
        self.repo.git.commit("-m", "Update files")

        return True
