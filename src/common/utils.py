import sys
import requests
from io import BytesIO
from uuid import uuid4

from PIL import Image
from django.conf import settings
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.core.exceptions import ValidationError

EXTRA_SMALL_THUMBNAIL_SIZE = settings.EXTRA_SMALL_THUMBNAIL_SIZE
SMALL_THUMBNAIL_SIZE = settings.SMALL_THUMBNAIL_SIZE
MEDIUM_THUMBNAIL_SIZE = settings.MEDIUM_THUMBNAIL_SIZE
BIG_THUMBNAIL_SIZE = settings.BIG_THUMBNAIL_SIZE


def compress_image(
        uploaded_image: InMemoryUploadedFile,
        is_small_thumbnail=False,
        is_medium_thumbnail=False,
        is_big_thumbnail=False,
        is_extra_small=False,
        quality=50,
        is_url=False,
):
    image_format = uploaded_image.name.split('.')[-1].upper()
    image_format = 'JPEG' if image_format == 'JPG' else image_format.upper()
    if image_format == "SVG":
        return uploaded_image
    image_type = "RGBA" if image_format == "PNG" else "RGB"
    thumbnail_type = (
        MEDIUM_THUMBNAIL_SIZE
        if is_medium_thumbnail
        else SMALL_THUMBNAIL_SIZE
        if is_small_thumbnail
        else BIG_THUMBNAIL_SIZE
        if is_big_thumbnail
        else EXTRA_SMALL_THUMBNAIL_SIZE
        if is_extra_small
        else MEDIUM_THUMBNAIL_SIZE
    )

    tmp_image = (
        Image.open(requests.get(uploaded_image, stream=True).raw)
        if is_url
        else Image.open(uploaded_image)
    )
    tmp_image = tmp_image.convert(image_type)
    output_io_stream = BytesIO()
    tmp_image.thumbnail(thumbnail_type)
    tmp_image.save(output_io_stream, format=image_format, quality=quality)
    output_io_stream.seek(0)
    uploaded_image = InMemoryUploadedFile(
        output_io_stream,
        "ImageField",
        f"{uuid4()}.{image_format.lower()}",
        f"image/{image_format.lower()}",
        sys.getsizeof(output_io_stream),
        None,
    )
    tmp_image.close()
    return uploaded_image


def validate_only_one_instance(obj):
    model = obj.__class__
    if (model.objects.count() > 0 and
            obj.id != model.objects.get().id):
        raise ValidationError("Можно создать только 1 обьект %s" % model._meta.verbose_name)