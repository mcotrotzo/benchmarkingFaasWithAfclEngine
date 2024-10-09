from dataclasses import dataclass
import json
from abc import ABC, abstractmethod


@dataclass
class Credentials(ABC):
    key: str
    credentials: dict = None

    def __init__(self, credentials_path: str, key: str):
        self.key = key
        self.credentials = self.from_json(credentials_path)

    @abstractmethod
    def from_json(self, file_path: str):
        pass

    def load_json(self, file_path: str):
        with open(file_path, 'r') as file:
            data = json.load(file)
        return data


# AWS Credentials class
@dataclass
class AWSCredentials(Credentials):
    access_key: str = ""
    secret_key: str = ""
    token: str = ""

    def __init__(self, credentials_path: str, key: str):
        super().__init__(credentials_path, key)

    def from_json(self, file_path: str):
        data = self.load_json(file_path)
        aws_data = data.get(self.key)
        if aws_data:
            self.access_key = aws_data.get('access_key')
            self.secret_key = aws_data.get('secret_key')
            self.token = aws_data.get('token')
        else:
            raise ValueError(f"Key {self.key} not found in the credentials file.")
        return aws_data



@dataclass
class GCPClientCredentials:
    client_id: str = ""
    client_secret: str = ""
    quota_project_id: str = ""
    refresh_token: str = ""
    account: str = ""
    universe_domain: str = ""

    def from_json(self, data):
        if data:
            self.client_id = data.get('client_id', "")
            self.client_secret = data.get('client_secret', "")
            self.quota_project_id = data.get('quota_project_id', "")
            self.refresh_token = data.get('refresh_token', "")
            self.account = data.get('account', "")
            self.universe_domain = data.get('universe_domain', "")
        return self



@dataclass
class GCPCredentials(Credentials):

    type: str = ""
    project_id: str = ""
    private_key_id: str = ""
    private_key: str = ""
    client_email: str = ""
    client_id: str = ""
    auth_uri: str = ""
    token_uri: str = ""
    auth_provider_x509_cert_url: str = ""
    client_x509_cert_url: str = ""
    universe_domain: str = ""


    client_credentials: GCPClientCredentials = None

    def __init__(self, credentials_path: str, key: str):
        super().__init__(credentials_path, key)

    def from_json(self, file_path: str):
        data = self.load_json(file_path)

        gcp_data = data.get(self.key)
        if gcp_data:
            self.type = gcp_data.get('type', "")
            self.project_id = gcp_data.get('project_id', "")
            self.private_key_id = gcp_data.get('private_key_id', "")
            self.private_key = gcp_data.get('private_key', "")
            self.client_email = gcp_data.get('client_email', "")
            self.client_id = gcp_data.get('client_id', "")
            self.auth_uri = gcp_data.get('auth_uri', "")
            self.token_uri = gcp_data.get('token_uri', "")
            self.auth_provider_x509_cert_url = gcp_data.get('auth_provider_x509_cert_url', "")
            self.client_x509_cert_url = gcp_data.get('client_x509_cert_url', "")
            self.universe_domain = gcp_data.get('universe_domain', "")

        client_data = data.get("gcp_client_credentials")
        if client_data:
            self.client_credentials = GCPClientCredentials().from_json(client_data)
        
        return {**gcp_data, **(client_data or {})}