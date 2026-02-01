from core.extractors.extractor import Extractor
from pathlib import Path
import zipfile

class Zip(Extractor):
    def extract(self, input: Path, output: Path) -> None:
        target_dir = output.resolve()

        target_dir.mkdir(parents=True, exist_ok=True)

        with zipfile.ZipFile(input, "r") as z:
            for member in z.infolist():
                member_path = (target_dir / member.filename).resolve()

                if not str(member_path).startswith(str(target_dir)):
                    raise RuntimeError(f"Insecure zip path: {member.filename}")

                z.extract(member, target_dir)

zipInstance = Zip()