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

    def stest_list_files(self):
        files = self.repo.list_files()
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)
        # print(json.dumps(files, indent=4))

    def test_update_files(self):
        test_branch = "test-branch"
        test_file = git_file("test", "test.txt", "This is a test content")
        self.repo.update_files(test_branch, [test_file])

        # Verificar se o branch foi criado
        response = requests.get(
            f"{self.repo.api_url}/branches/{test_branch}", headers=self.repo.headers
        )
        self.assertEqual(response.status_code, 200)

        test_file = git_file("test", "test2.txt", "This is a test content2")
        self.repo.update_files(test_branch, [test_file])
        # Verificar se o arquivo foi atualizado
        files = self.repo.list_files(test_branch)

        # find file test/test2.txt content in files
        for file in files:
            if file["filepath"] == "test" and file["filename"] == "test.txt":
                self.assertEqual(
                    file["content"],
                    "This is a test content",
                )
            if file["filepath"] == "test" and file["filename"] == "test2.txt":
                self.assertEqual(
                    file["content"],
                    "This is a test content2",
                )


if __name__ == "__main__":
    unittest.main()
