class ApplicationError(Exception):
    pass


class NameIsNotValidError(ApplicationError):
    pass


class NameIsTooLongError(NameIsNotValidError):
    pass
