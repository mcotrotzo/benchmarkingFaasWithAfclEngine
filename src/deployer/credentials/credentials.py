from dataclasses import dataclass
import json
from abc import ABC, abstractmethod
from typing import Optional
from ...utils.utils import handle_error, load_config

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
        try:
            return load_config(file_path=file_path)  
        except Exception as e:
            handle_error(e)
            raise  

@dataclass
class AWSCredentials(Credentials):
    access_key: str = ""
    secret_key: str = ""
    token: str = ""

    def __init__(self, credentials_path: str, key: str):
        super().__init__(credentials_path, key)

    def from_json(self, file_path: str):
        try:
            data = self.load_json(file_path)
            aws_data = data[self.key]
            self.access_key = aws_data['access_key']
            self.secret_key = aws_data['secret_key']
            self.token = aws_data['token']
            return aws_data
        except KeyError as e:
            handle_error(f'Key not found in {file_path}: {e}')
        
        except Exception as e:
            handle_error(e)
    

@dataclass
class GCPClientCredentials:
    client_id: str = ""
    client_secret: str = ""
    quota_project_id: str = ""
    refresh_token: str = ""
    account: str = ""
    universe_domain: str = ""

    def from_json(self, data):
        try:
            self.client_id = data['client_id']
            self.client_secret = data['client_secret']
            self.quota_project_id = data['quota_project_id']
            self.refresh_token = data['refresh_token']
            self.account = data['account']
            self.universe_domain = data['universe_domain']
            return self
        except KeyError as e:
            handle_error(f'Key not found in GCP client credentials data: {e}')
        except Exception as e:
            handle_error(e)

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
        try:
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
            else:
                handle_error(f'No GCP data found for key: {self.key}')  

            client_data = data.get("gcp_client_credentials")
            if client_data:
                self.client_credentials = GCPClientCredentials().from_json(client_data)
            else:
                handle_error('No GCP client credentials found.') 

            return {**gcp_data, **(client_data or {})}
        except KeyError as e:
            handle_error(f'Key not found in {file_path}: {e}')
        except Exception as e:
            handle_error(e)
