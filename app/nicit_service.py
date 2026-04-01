import os
import httpx
from datetime import datetime
from app.config import settings

class NicitService:
    def __init__(self):
        self.base_url = settings.NICIT_BASE_URL
        self.download_dir = settings.NICIT_DOWNLOAD_DIR

    async def download_file(self, date_str: str, slot: str) -> bool:
        # date_str format: YYYYMMDD, slot: 09 or 16
        filename = f"{date_str}{slot}.txt"
        url = f"{self.base_url}/{filename}"
        filepath = os.path.join(self.download_dir, filename)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(url, timeout=30.0)
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
                    return True
        except Exception as e:
            print(f"Error downloading {filename}: {e}")
        return False

    def get_downloaded_files(self):
        files = []
        if os.path.exists(self.download_dir):
            for filename in os.listdir(self.download_dir):
                if filename.endswith(".txt"):
                    filepath = os.path.join(self.download_dir, filename)
                    size = os.path.getsize(filepath)
                    mtime = os.path.getmtime(filepath)
                    files.append({
                        "filename": filename,
                        "size": size,
                        "downloaded_at": datetime.fromtimestamp(mtime)
                    })
        return sorted(files, key=lambda x: x["filename"], reverse=True)
