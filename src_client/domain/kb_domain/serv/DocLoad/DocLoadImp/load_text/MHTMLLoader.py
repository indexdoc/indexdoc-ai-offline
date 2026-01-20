import email
from typing import Union

from domain.kb_domain.serv.DocLoad.DocLoadImp.BaseLoader import BaseLoader


class MHTMLLoader(BaseLoader):
    """Parse `MHTML` files with `BeautifulSoup`."""

    def __init__(
            self,
            file_path: str,
            open_encoding: Union[str, None] = None,
            bs_kwargs: Union[dict, None] = None,
    ) -> None:
        super().__init__(file_path)
        try:
            import bs4  # noqa:F401
        except ImportError:
            raise ImportError(
                "beautifulsoup4 package not found, please install it with "
                "`pip install beautifulsoup4`"
            )
        self.file_path = file_path
        self.open_encoding = open_encoding
        if bs_kwargs is None:
            bs_kwargs = {"features": "lxml"}
        self.bs_kwargs = bs_kwargs

    def _load_impl(self):
        from bs4 import BeautifulSoup
        """Load MHTML document into document objects."""
        with open(self.file_path, "r", encoding=self.open_encoding) as f:
            message = email.message_from_string(f.read())
            parts = message.get_payload()

            if not isinstance(parts, list):
                parts = [message]
            file_content = []
            for part in parts:
                if part.get_content_type() == "text/html":
                    html = part.get_payload(decode=True).decode()

                    soup = BeautifulSoup(html, **self.bs_kwargs)
                    text = soup.get_text()
                    file_content.append(text)
            return file_content
