"""Extended image format support for InvokeAI."""

from datetime import datetime
from pathlib import Path
from typing import Literal
from uuid import uuid4

import pillow_avif  # noqa: F401

from invokeai.invocation_api import (
    BaseInvocation,
    BaseInvocationOutput,
    ImageField,
    InputField,
    InvocationContext,
    OutputField,
    invocation,
    invocation_output,
)

TIFFCompression = Literal["none", "lzw", "jpeg", "zip"]
JPEGSubsampling = Literal["4:4:4", "4:2:2", "4:2:0"]


@invocation_output("path_output")
class PathOutput(BaseInvocationOutput):
    """Path output."""

    path: str = OutputField(description="Path to saved file")


def _get_output_path(context: InvocationContext, extension: str) -> Path:
    output_dir = context.config.get().outputs_path / "invoke_image_export"
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y-%m-%d-%H%M")
    unique_id = str(uuid4())[:8]
    filename = f"{timestamp}-{unique_id}.{extension}"

    return output_dir / filename


@invocation(
    "save_png",
    title="Save Image as PNG",
    tags=["image", "save", "export", "png"],
    category="image",
    version="0.0.2",
    use_cache=False,
)
class SavePNGInvocation(BaseInvocation):
    """Save image as PNG with compression options."""

    image: ImageField = InputField(description="Image to save")
    compression: int = InputField(default=6, ge=0, le=9, description="PNG compression level")
    optimize: bool = InputField(default=True, description="Optimize PNG file size")

    def invoke(self, context: InvocationContext) -> PathOutput:
        image = context.images.get_pil(self.image.image_name)
        output_path = _get_output_path(context, "png")

        image.save(output_path, "PNG", compress_level=self.compression, optimize=self.optimize)

        return PathOutput(path=str(output_path))


@invocation(
    "save_jpeg",
    title="Save Image as JPEG",
    tags=["image", "save", "export", "jpeg", "jpg"],
    category="image",
    version="0.0.2",
    use_cache=False,
)
class SaveJPEGInvocation(BaseInvocation):
    """Save image as JPEG with quality options."""

    image: ImageField = InputField(description="Image to save")
    quality: int = InputField(default=95, ge=1, le=100, description="JPEG quality")
    progressive: bool = InputField(default=False, description="Save as progressive JPEG")
    optimize: bool = InputField(default=True, description="Optimize JPEG file size")
    subsampling: JPEGSubsampling = InputField(default="4:2:0", description="Chroma subsampling")

    def invoke(self, context: InvocationContext) -> PathOutput:
        image = context.images.get_pil(self.image.image_name)

        if image.mode in ("RGBA", "LA", "P"):
            image = image.convert("RGB")

        output_path = _get_output_path(context, "jpg")
        subsampling_map = {"4:4:4": 0, "4:2:2": 1, "4:2:0": 2}

        image.save(
            output_path,
            "JPEG",
            quality=self.quality,
            progressive=self.progressive,
            optimize=self.optimize,
            subsampling=subsampling_map[self.subsampling],
        )

        return PathOutput(path=str(output_path))


@invocation(
    "save_webp",
    title="Save Image as WebP",
    tags=["image", "save", "export", "webp"],
    category="image",
    version="0.0.2",
    use_cache=False,
)
class SaveWebPInvocation(BaseInvocation):
    """Save image as WebP with quality and compression options."""

    image: ImageField = InputField(description="Image to save")
    quality: int = InputField(default=90, ge=1, le=100, description="WebP quality")
    lossless: bool = InputField(default=False, description="Use lossless compression")
    method: int = InputField(default=4, ge=0, le=6, description="Compression method (0=fast, 6=slower/smaller)")

    def invoke(self, context: InvocationContext) -> PathOutput:
        image = context.images.get_pil(self.image.image_name)
        output_path = _get_output_path(context, "webp")

        image.save(
            output_path,
            "WebP",
            quality=self.quality,
            lossless=self.lossless,
            method=self.method,
        )

        return PathOutput(path=str(output_path))


@invocation(
    "save_avif",
    title="Save Image as AVIF",
    tags=["image", "save", "export", "avif"],
    category="image",
    version="0.0.2",
    use_cache=False,
)
class SaveAVIFInvocation(BaseInvocation):
    """Save image as AVIF with quality and speed options."""

    image: ImageField = InputField(description="Image to save")
    quality: int = InputField(default=85, ge=1, le=100, description="AVIF quality")
    speed: int = InputField(default=6, ge=0, le=10, description="Encoding speed (0=slowest/best, 10=fastest)")

    def invoke(self, context: InvocationContext) -> PathOutput:
        image = context.images.get_pil(self.image.image_name)
        output_path = _get_output_path(context, "avif")

        image.save(output_path, "AVIF", quality=self.quality, speed=self.speed)

        return PathOutput(path=str(output_path))


@invocation(
    "save_tiff",
    title="Save Image as TIFF",
    tags=["image", "save", "export", "tiff"],
    category="image",
    version="0.0.2",
    use_cache=False,
)
class SaveTIFFInvocation(BaseInvocation):
    """Save image as TIFF with compression options."""

    image: ImageField = InputField(description="Image to save")
    compression: TIFFCompression = InputField(default="lzw", description="TIFF compression method")

    def invoke(self, context: InvocationContext) -> PathOutput:
        image = context.images.get_pil(self.image.image_name)
        output_path = _get_output_path(context, "tiff")

        image.save(output_path, "TIFF", compression=self.compression)

        return PathOutput(path=str(output_path))
