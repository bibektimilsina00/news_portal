from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, status


class BaseAppException(HTTPException):
    """Base exception for the application"""

    def __init__(
        self,
        status_code: int,
        detail: Any = None,
        headers: Optional[Dict[str, str]] = None,
        error_code: Optional[str] = None,
    ) -> None:
        super().__init__(status_code=status_code, detail=detail, headers=headers)
        self.error_code = error_code


class InvalidUserDataException(BaseAppException):
    """Raised when user provides invalid data"""

    def __init__(self, detail: str = "Invalid user data provided") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_USER_DATA",
        )


class InvalidPostDataException(BaseAppException):
    """Raised when user provides invalid post data"""

    def __init__(self, detail: str = "Invalid post data provided") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_POST_DATA",
        )


class PostNotFoundException(BaseAppException):
    """Raised when post is not found"""

    def __init__(self, detail: str = "Post not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="POST_NOT_FOUND",
        )


class UnauthorizedException(BaseAppException):
    """Raised when user is not authorized to perform an action"""

    def __init__(self, detail: str = "Unauthorized access") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="UNAUTHORIZED",
        )


class UserAlreadyExistsException(BaseAppException):
    """Raised when trying to create a user that already exists"""

    def __init__(self, detail: str = "User already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="USER_ALREADY_EXISTS",
        )


class UserNotFoundException(BaseAppException):
    """Raised when user is not found"""

    def __init__(self, detail: str = "User not found") -> None:
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            error_code="USER_NOT_FOUND",
        )


class AuthenticationException(BaseAppException):
    """Raised when authentication fails"""

    def __init__(self, detail: str = "Authentication failed") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="AUTHENTICATION_FAILED",
        )


class InvalidCredentialsException(BaseAppException):
    """Raised when login credentials are invalid"""

    def __init__(self, detail: str = "Invalid email/username or password") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="INVALID_CREDENTIALS",
        )


class AccountNotVerifiedException(BaseAppException):
    """Raised when user account is not verified"""

    def __init__(
        self, detail: str = "Account not verified. Please verify your email"
    ) -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="ACCOUNT_NOT_VERIFIED",
        )


class AccountDisabledException(BaseAppException):
    """Raised when user account is disabled"""

    def __init__(self, detail: str = "Account is disabled") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="ACCOUNT_DISABLED",
        )


class PrivateAccountException(BaseAppException):
    """Raised when trying to access private account without permission"""

    def __init__(self, detail: str = "This account is private") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PRIVATE_ACCOUNT",
        )


class UsernameAlreadyExistsException(BaseAppException):
    """Raised when username is already taken"""

    def __init__(self, detail: str = "Username already exists") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="USERNAME_ALREADY_EXISTS",
        )


class EmailAlreadyExistsException(BaseAppException):
    """Raised when email is already registered"""

    def __init__(self, detail: str = "Email already registered") -> None:
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
            error_code="EMAIL_ALREADY_EXISTS",
        )


class InvalidPasswordException(BaseAppException):
    """Raised when password is invalid"""

    def __init__(self, detail: str = "Invalid password") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_PASSWORD",
        )


class PasswordTooWeakException(BaseAppException):
    """Raised when password doesn't meet requirements"""

    def __init__(self, detail: str = "Password is too weak") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="PASSWORD_TOO_WEAK",
        )


class InvalidUsernameException(BaseAppException):
    """Raised when username is invalid"""

    def __init__(self, detail: str = "Invalid username format") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="INVALID_USERNAME",
        )


class VerificationFailedException(BaseAppException):
    """Raised when account verification fails"""

    def __init__(self, detail: str = "Account verification failed") -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            error_code="VERIFICATION_FAILED",
        )


class TokenExpiredException(BaseAppException):
    """Raised when authentication token has expired"""

    def __init__(self, detail: str = "Authentication token has expired") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="TOKEN_EXPIRED",
        )


class TokenInvalidException(BaseAppException):
    """Raised when authentication token is invalid"""

    def __init__(self, detail: str = "Invalid authentication token") -> None:
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            error_code="TOKEN_INVALID",
        )


class PermissionDeniedException(BaseAppException):
    """Raised when user doesn't have required permissions"""

    def __init__(self, detail: str = "Permission denied") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="PERMISSION_DENIED",
        )


class SuperuserDeleteException(BaseAppException):
    """Raised when trying to delete a superuser"""

    def __init__(self, detail: str = "Cannot delete superuser") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="SUPERUSER_DELETE_FORBIDDEN",
        )


class SelfDeleteException(BaseAppException):
    """Raised when superuser tries to delete themselves"""

    def __init__(self, detail: str = "Super users cannot delete themselves") -> None:
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            error_code="SELF_DELETE_FORBIDDEN",
        )


class RateLimitExceededException(BaseAppException):
    """Raised when user exceeds rate limit"""

    def __init__(
        self, detail: str = "Rate limit exceeded. Please try again later"
    ) -> None:
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=detail,
            error_code="RATE_LIMIT_EXCEEDED",
        )


class DatabaseException(BaseAppException):
    """Raised when database operation fails"""

    def __init__(self, detail: str = "Database operation failed") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="DATABASE_ERROR",
        )


class EmailSendException(BaseAppException):
    """Raised when email sending fails"""

    def __init__(self, detail: str = "Failed to send email") -> None:
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=detail,
            error_code="EMAIL_SEND_FAILED",
        )


# Exception mapping for centralized error handling
EXCEPTION_MAPPING = {
    "INVALID_USER_DATA": InvalidUserDataException,
    "UNAUTHORIZED": UnauthorizedException,
    "USER_ALREADY_EXISTS": UserAlreadyExistsException,
    "USER_NOT_FOUND": UserNotFoundException,
    "AUTHENTICATION_FAILED": AuthenticationException,
    "INVALID_CREDENTIALS": InvalidCredentialsException,
    "ACCOUNT_NOT_VERIFIED": AccountNotVerifiedException,
    "ACCOUNT_DISABLED": AccountDisabledException,
    "PRIVATE_ACCOUNT": PrivateAccountException,
    "USERNAME_ALREADY_EXISTS": UsernameAlreadyExistsException,
    "EMAIL_ALREADY_EXISTS": EmailAlreadyExistsException,
    "INVALID_PASSWORD": InvalidPasswordException,
    "PASSWORD_TOO_WEAK": PasswordTooWeakException,
    "INVALID_USERNAME": InvalidUsernameException,
    "VERIFICATION_FAILED": VerificationFailedException,
    "TOKEN_EXPIRED": TokenExpiredException,
    "TOKEN_INVALID": TokenInvalidException,
    "PERMISSION_DENIED": PermissionDeniedException,
    "SUPERUSER_DELETE_FORBIDDEN": SuperuserDeleteException,
    "SELF_DELETE_FORBIDDEN": SelfDeleteException,
    "RATE_LIMIT_EXCEEDED": RateLimitExceededException,
    "DATABASE_ERROR": DatabaseException,
    "EMAIL_SEND_FAILED": EmailSendException,
}


def get_exception_by_code(error_code: str, detail: str = None) -> BaseAppException:
    """Get exception instance by error code"""
    exception_class = EXCEPTION_MAPPING.get(error_code, BaseAppException)
    if detail:
        return exception_class(detail=detail)
    return exception_class()
