import os
import httpx
import subprocess
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

    async def download_and_merge_today(self) -> bool:
        today_str = datetime.now().strftime("%Y%m%d")
        
        # Scarica entrambi i file
        success_09 = await self.download_file(today_str, "09")
        success_16 = await self.download_file(today_str, "16")

        if not success_09 and not success_16:
            return False

        domains = set()
        
        # Leggi e unisci i domini
        for slot in ["09", "16"]:
            filepath = os.path.join(self.download_dir, f"{today_str}{slot}.txt")
            if os.path.exists(filepath):
                with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        d = line.strip()
                        if d:
                            domains.add(d)

        # Ordina per lunghezza crescente, e a parità di lunghezza in ordine alfabetico
        sorted_domains = sorted(list(domains), key=lambda x: (len(x), x))

        # Salva il file unito
        merged_filename = f"{today_str}_merged.txt"
        merged_filepath = os.path.join(self.download_dir, merged_filename)

        with open(merged_filepath, "w", encoding="utf-8") as f:
            for d in sorted_domains:
                f.write(f"{d}\n")

        return True

    def open_download_folder(self):
        try:
            # Comando nativo macOS per aprire una cartella nel Finder
            subprocess.Popen(["open", self.download_dir])
        except Exception as e:
            print(f"Error opening folder: {e}")

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

