from pathlib import Path

import docx2txt
import fitz  # PyMuPDF

from server.utils.logger import log


class DocumentParser:
    @staticmethod
    def parse(file_path: str) -> str:
        path = Path(file_path)
        suffix = path.suffix.lower()

        if suffix == ".pdf":
            return DocumentParser._parse_pdf(file_path)
        elif suffix in [".docx", ".doc"]:
            return DocumentParser._parse_word(file_path)
        elif suffix in [".txt", ".md"]:
            return DocumentParser._parse_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {suffix}")

    @staticmethod
    def _parse_pdf(file_path: str) -> str:
        text = ""
        try:
            with fitz.open(file_path) as doc:
                for page in doc:
                    texts = page.get_text("text")
                    if isinstance(texts, list):
                        text += "\n".join(texts) + "\n"
                    elif isinstance(texts, str):
                        text += texts + "\n"
                    elif isinstance(texts, dict):
                        log("parser").warning(
                            f"Unexpected text format in PDF {file_path}: {type(texts)}"
                        )
        except Exception as e:
            log("parser").error(f"Error parsing PDF {file_path}: {e}")
            raise
        return text

    @staticmethod
    def _parse_word(file_path: str) -> str:
        try:
            return docx2txt.process(file_path)
        except Exception as e:
            log("parser").error(f"Error parsing Word {file_path}: {e}")
            raise

    @staticmethod
    def _parse_txt(file_path: str) -> str:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="gbk") as f:
                return f.read()
        except Exception as e:
            log("parser").error(f"Error parsing TXT {file_path}: {e}")
            raise
