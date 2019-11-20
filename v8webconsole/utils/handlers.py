import traceback
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.exceptions import (
    APIException,
    ValidationError,
)


def friendly_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if not response:
        exc = APIException(exc)
        response = exception_handler(exc, context)
    if response is not None:
        customized_response_data = dict()
        customized_response_data['errors'] = list()
        if 'code' in response.data and 'detail' in response.data:
            error = {'code': response.data['code'], 'detail': response.data['detail']}
            customized_response_data['errors'].append(error)
        else:
            for key, value in response.data.items():
                if type(value) == list:
                    value = value[0]
                error = {'code': key, 'detail': value}
                customized_response_data['errors'].append(error)
        if settings.DEBUG:
            if not issubclass(type(exc), ValidationError):
                customized_response_data['stacktrace'] = traceback.format_exc()
                traceback.print_exc()
        response.data = customized_response_data
    return response