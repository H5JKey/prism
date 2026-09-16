from pydantic import BaseModel


class MinioBucketConfig(BaseModel):
    glb_sources: str = "input"
    renders: str = "output"


class MinioConfig(BaseModel):
    host: str = "minio"
    port: int = 9000
    username: str = "adminadmin"
    password: str = "adminadmin"

    bucket: MinioBucketConfig = MinioBucketConfig()
    presigned_url_ttl_seconds: int = 10 * 60

    @property
    def url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def config(self) -> dict[str, str | int]:
        return {
            "endpoint_url": self.url,
            "aws_access_key_id": self.username,
            "aws_secret_access_key": self.password,
        }
