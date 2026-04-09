import base64
import io
from PIL import Image


def prepare_image(uploaded_file, max_size: int = 1024) -> str:
    """Resize image if needed and return base64-encoded JPEG string."""
    image = Image.open(uploaded_file).convert("RGB")

    if max(image.size) > max_size:
        image.thumbnail((max_size, max_size), Image.LANCZOS)

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=85)
    buffer.seek(0)

    return base64.b64encode(buffer.read()).decode("utf-8")
