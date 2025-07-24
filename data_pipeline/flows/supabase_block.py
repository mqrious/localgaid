from prefect.blocks.core import Block
from pydantic import SecretStr 

class SupabaseCredentials(Block):
    url: str
    key: SecretStr


SupabaseCredentials.register_type_and_schema()