import aiohttp
import os
from dotenv import load_dotenv

class YaDisk:
    def __init__(self) -> None:
        load_dotenv()
        self.basic_url = f"https://cloud-api.yandex.net/v1/disk"
        self.token = os.getenv("YA_TOKEN")
        self.headers = {
            "Authorization": f"OAuth {self.token}",
        }
        self.session = aiohttp.ClientSession()
    
    async def get_info(self,
                 path: str,
                 fields: list[str] = None,
                 limit: int = 20,
                 offset: int = 0,
                 preview_crop: bool = False,
                 preview_size: str = None,
                 sort: str = "name" ) -> dict:
        params = {
            "path": path,
            "limit": limit,
            "preview_crop": str(preview_crop),
            "sort": sort
        }
        if fields:
            params["fields"] = ",".join(fields)
        if offset:
            params["offset"] = offset
        if preview_size:
            params["preview_size"] = preview_size
        
        url = f"{self.basic_url}/resources"
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return data
                else:
                    return {"error": response.status}
    
    async def __get_upload_href(self, file_name: str, folder_path: str, overwrite: bool = False, fields: list[str] = None):
        url = f"{self.basic_url}/resources/upload"
        params = {
            "path": f"/{folder_path}/{file_name}",
            "overwrite": str(overwrite)
        }
        if fields:
            params["fields"] = ",".join(fields)
        async with self.session.get(url, headers=self.headers, params=params) as response:
            if response.status != 200:
                return None
            data = await response.json()
            return data["href"]
    
    async def upload_file(self, file_bytes: bytes, file_name: str, to_folder: str, overwrite: bool = False) -> None:
        upload_href = await self.__get_upload_href(file_name=file_name, folder_path=to_folder, overwrite=overwrite)
        if not upload_href:
            return None
        try:
            async with aiohttp.ClientSession() as session:
                async with session.put(upload_href, data=file_bytes) as resp:
                    if resp.status == 201:
                        return resp.status
                    else:
                        return None
        except Exception as e:
            print(e)
    
    async def do_publish(self, path: str) -> dict:
        url = f"{self.basic_url}/resources/publish"
        params = {
            "path": path
        }
        async with self.session.put(url, headers=self.headers, params=params) as response:
            if response.status == 200:
                return await response.json()
            else:
                return str({"error": response.status})