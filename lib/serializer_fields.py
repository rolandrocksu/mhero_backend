import base64
import binascii
import imghdr
import io
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers
from rest_framework.fields import ImageField


class CustomChoiceField(serializers.ChoiceField):
    def to_representation(self, obj):
        if obj == '' and self.allow_blank:
            return ''
        if obj is None and self.allow_null:
            return None
        return self._choices[obj]

    def to_internal_value(self, data):
        if data == '' and self.allow_blank:
            return ''
        if data is None and self.allow_null:
            return None
        for key, val in self._choices.items():
            if val == data:
                return key
        self.fail('invalid_choice', input=data)

    class Meta:
        swagger_schema_fields = {'type': 'string'}


class Base64FieldMixin:
    EMPTY_VALUES = (None, '', [], (), {})

    @property
    def ALLOWED_TYPES(self):
        raise NotImplementedError

    @property
    def INVALID_FILE_MESSAGE(self):
        raise NotImplementedError

    @property
    def INVALID_TYPE_MESSAGE(self):
        raise NotImplementedError

    def __init__(self, *args, **kwargs):
        self.trust_provided_content_type = kwargs.pop('trust_provided_content_type', False)
        self.represent_in_base64 = kwargs.pop('represent_in_base64', False)
        super().__init__(*args, **kwargs)

    def to_internal_value(self, base64_data):
        # Check if this is a base64 string
        if base64_data in self.EMPTY_VALUES:
            return None

        if isinstance(base64_data, str):
            file_mime_type = None

            # Strip base64 header, get mime_type from base64 header.
            if ';base64,' in base64_data:
                header, base64_data = base64_data.split(';base64,')
                if self.trust_provided_content_type:
                    file_mime_type = header.replace('data:', '')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(base64_data)
            except (TypeError, binascii.Error, ValueError):
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            # Generate file name:
            file_name = str(uuid.uuid4())

            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            if file_extension not in self.ALLOWED_TYPES:
                raise ValidationError(self.INVALID_TYPE_MESSAGE)

            complete_file_name = file_name + '.' + file_extension
            data = SimpleUploadedFile(
                name=complete_file_name,
                content=decoded_file,
                content_type=file_mime_type
            )

            return super().to_internal_value(data)

        raise ValidationError(
            f"Invalid type. This is not an base64 string: {type(base64_data)}")

    def to_representation(self, file):
        if self.represent_in_base64:
            # If the underlying ImageField is blank, a ValueError would be
            # raised on `open`. When representing as base64, simply return an
            # empty base64 str rather than let the exception propagate unhandled
            # up into serializers.
            if not file:
                return ""

            try:
                with open(file.path, 'rb') as f:
                    return base64.b64encode(f.read()).decode()
            except Exception:
                raise OSError("Error encoding file")
        else:
            return super().to_representation(file)

    def get_file_extension(self, filename, decoded_file):
        raise NotImplementedError


class Base64ImageField(Base64FieldMixin, ImageField):
    """A django-rest-framework field for handling image-uploads through raw post data.
    It uses base64 for en-/decoding the contents of the file."""

    ALLOWED_TYPES = ('jpeg', 'jpg', 'png', 'gif', 'webp')
    INVALID_FILE_MESSAGE = "Please upload a valid image."
    INVALID_TYPE_MESSAGE = "The type of the image couldn't be determined."

    class Meta:
        swagger_schema_fields = {
            'type': 'string',
            'title': "File Content",
            'description': "Content of the file base64 encoded",
            'read_only': False
        }

    def get_file_extension(self, filename, decoded_file):
        try:
            from PIL import Image
        except ImportError:
            raise ImportError("Pillow is not installed.")

        extension = imghdr.what(filename, decoded_file)

        # Try with PIL as fallback if format not detected due
        # to bug in imghdr https://bugs.python.org/issue16512
        if extension is None:
            try:
                image = Image.open(io.BytesIO(decoded_file))
            except OSError:
                raise ValidationError(self.INVALID_FILE_MESSAGE)

            extension = image.format.lower()

        extension = 'jpg' if extension == 'jpeg' else extension
        return extension

    def to_internal_value(self, base64_data):
        data = super().to_internal_value(base64_data)

        # Check file size (limit in bytes)
        max_size_bytes = settings.MAX_IMAGE_SIZE_MB * 1024 * 1024
        if data.size > max_size_bytes:
            raise ValidationError(f"Image size should not exceed {settings.MAX_IMAGE_SIZE_MB}MB.")

        return data
