import unittest
from app.git import GitRepo, GitFile
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
        cls.repo = GitRepo(cls.repo_url, cls.token)

    def test_list_files(self):
        files = self.repo.list_files()
        self.assertIsInstance(files, list)
        self.assertGreater(len(files), 0)
        files_dict = [vars(file) for file in files]
        print(json.dumps(files_dict, indent=4))

    def test_update_files(self):
        test_branch = "test-branch"
        test_file = GitFile("test.txt", "test.txt", "This is a test content")
        self.repo.update_files(test_branch, [test_file])

        # Verificar se o branch foi criado
        response = requests.get(
            f"{self.repo.api_url}/branches/{test_branch}", headers=self.repo.headers
        )
        self.assertEqual(response.status_code, 200)

        # Verificar se o arquivo foi atualizado
        response = requests.get(
            f"{self.repo.api_url}/contents/{test_file.filepath}?ref={test_branch}",
            headers=self.repo.headers,
        )
        self.assertEqual(response.status_code, 200)
        content = response.json()["content"]
        self.assertEqual(
            content.strip(),
            base64.b64encode(test_file.content.encode("utf-8")).decode("utf-8"),
        )
        self.repo.delete_branch(test_branch)


if __name__ == "__main__":
    unittest.main()
