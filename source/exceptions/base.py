class GatherException(Exception):
    status_code = 500
    cause = 'Exception in code raises GatherException'
    code = 'One of coroutines in asyncio.gather return Exception object'


class OperatorNotFound(Exception):
    status_code = 400
    cause = ''
    code = ''


class AttributeMustBeSetException(Exception):
    status_code = 500
    cause = 'Adapter attribute in db layer must be set'
    code = 'Exception was raised in db layer'


class IncorrectReferenceNameException(Exception):
    status_code = 400
    cause = 'Incorrect object reference name was passed'
    code = 'Exception was raised on db layer'


class ColumnDoesNotExistException(Exception):
    status_code = 400
    cause = 'Column with passed name does not exist in table'
    code = 'Exception was raised in db layer'


class ColumnIsUniqueException(Exception):
    status_code = 500
    cause = 'Column that was passed cannot be handled'
    code = 'Exception was raised in db layer'


class LookupOperatorNotFoundException(Exception):
    status_code = 500
    cause = f'Passed lookup operator not found in [e, ne, l, le, g, ge, like, ilike, in]'
    code = 'Exception was raised in db layer'


class ObjectDoesNotExist(Exception):
    status_code = 404
    cause = 'Object does not exist'
    code = 'Object with such attrs does not exist in db'


class ObjectAlreadyExist(Exception):
    status_code = 401 # FIXME
    cause = 'Object already exist'
    code = 'Object with such attrs already exist in db'


class PKMustBePassedException(Exception):
    status_code = 400
    cause = 'Object identifier must be passed'
    code = 'Exception was raised in db layer'


class FiltersMustBePassedException(Exception):
    status_code = 400
    cause = 'Filters must be passed'
    code = 'Exception was raised in db layer'


class ForbiddenException(Exception):
    status_code = 401 # FIXME
    cause = 'Forbidden request, you don\'t have rights for this request'
    code = 'Forbidden exception has been raised'


class ServiceUnavailableException(Exception):
    status_code = 500 # FIXME
    cause = 'Service Unavailable'
    code = 'Service Unavailable exception has been raised'


class UnavailableSortFieldException(Exception):
    status_code = 400
    cause = 'Unavailable sort field for this object'
    code = 'Unavailble sort field exception has been raised'


class EmptyStringException(Exception):
    status_code = 400
    cause = 'Empty string was passed'
    code = 'Exception was raised in services layer'

