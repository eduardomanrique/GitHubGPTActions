import unittest
from app.git import GitRepo, git_file
import requests
import base64
import dotenv
import os
import json

dotenv.load_dotenv()


class TestGitRepo(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Substitua com seu token de acesso pessoal e URL do repositório de teste
        cls.token = os.getenv("GITHUB_TEST_TOKEN")
        cls.repo_url = "https://github.com/eduardomanrique/tests.git"
        cls.repo = GitRepo(cls.repo_url, cls.token, "master")

    def test_list_files(self):
        files = self.repo.list_files("test-branch")
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)
        # print(json.dumps(files, indent=4))

    def test_update_files2(self):
        test_branch = "test-branch2"
        test_file = git_file("test/testx.txt", "This is a test content")
        self.repo.update_files(test_branch, [test_file], "test1")

    def test_update_files(self):
        test_branch = "test-branch"
        self.repo.list_files(test_branch)
        test_file = git_file("test/test.txt", "This is a test content")
        self.repo.update_files(test_branch, [test_file], "test1")

        # Verificar se o branch foi criado
        response = requests.get(
            f"{self.repo.api_url}/branches/{test_branch}", headers=self.repo.headers
        )
        self.assertEqual(response.status_code, 200)

        test_file = git_file("test/test2.txt", "This is a test content2")
        self.repo.update_files(test_branch, [test_file], "test2")
        # Verificar se o arquivo foi atualizado
        files = self.repo.list_files(test_branch)

        print(json.dumps(files, indent=4))
        count = 0
        # find file test/test2.txt content in files
        for file in files:
            print(file["filename"])
            if file["filename"] == "test/test.txt":
                count += 1
                self.assertEqual(
                    file["content"],
                    "This is a test content",
                )
            if file["filename"] == "test/test2.txt":
                count += 1
                self.assertEqual(
                    file["content"],
                    "This is a test content2",
                )
        self.assertEqual(count, 2)


if __name__ == "__main__":
    unittest.main()
