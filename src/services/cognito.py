"""
AWS Cognito service integration for user authentication.
"""
from typing import Dict, Optional
import boto3
from botocore.exceptions import ClientError
import streamlit as st
from utils.config import get_settings
from utils.exceptions import AuthError

class CognitoService:
    """
    Handles AWS Cognito authentication operations.
    """
    def __init__(self):
        self.settings = get_settings()
        self.client = boto3.client(
            'cognito-idp',
            region_name=self.settings.AWS_REGION
        )
        self.user_pool_id = self.settings.COGNITO_USER_POOL_ID
        self.client_id = self.settings.COGNITO_CLIENT_ID

    def authenticate(self, username: str, password: str) -> Dict:
        """
        Authenticate user with Cognito.

        Args:
            username: User's username
            password: User's password

        Returns:
            Dict: Authentication result including tokens

        Raises:
            AuthError: If authentication fails
        """
        try:
            response = self.client.initiate_auth(
                AuthFlow='USER_PASSWORD_AUTH',
                AuthParameters={
                    'USERNAME': username,
                    'PASSWORD': password
                },
                ClientId=self.client_id
            )
            
            return {
                'AccessToken': response['AuthenticationResult']['AccessToken'],
                'RefreshToken': response['AuthenticationResult']['RefreshToken'],
                'ExpiresIn': response['AuthenticationResult']['ExpiresIn'],
                'Username': username
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'NotAuthorizedException':
                raise AuthError("Invalid username or password")
            elif error_code == 'UserNotConfirmedException':
                raise AuthError("Please verify your email address")
            else:
                raise AuthError(f"Authentication failed: {error_message}")

    def sign_up(
        self,
        username: str,
        email: str,
        password: str,
        attributes: Optional[Dict] = None
    ) -> Dict:
        """
        Register a new user with Cognito.

        Args:
            username: Desired username
            email: User's email
            password: Desired password
            attributes: Additional user attributes

        Returns:
            Dict: Sign up result

        Raises:
            AuthError: If sign up fails
        """
        user_attributes = [
            {'Name': 'email', 'Value': email},
        ]

        if attributes:
            for key, value in attributes.items():
                user_attributes.append({'Name': key, 'Value': str(value)})

        try:
            response = self.client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                UserAttributes=user_attributes
            )
            
            return {
                'UserSub': response['UserSub'],
                'UserConfirmed': response['UserConfirmed']
            }
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'UsernameExistsException':
                raise AuthError("Username already exists")
            elif error_code == 'InvalidPasswordException':
                raise AuthError("Password does not meet requirements")
            else:
                raise AuthError(f"Sign up failed: {error_message}")

    def confirm_sign_up(self, username: str, confirmation_code: str):
        """
        Confirm user registration with verification code.

        Args:
            username: User's username
            confirmation_code: Email verification code

        Raises:
            AuthError: If confirmation fails
        """
        try:
            self.client.confirm_sign_up(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=confirmation_code
            )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'CodeMismatchException':
                raise AuthError("Invalid verification code")
            elif error_code == 'ExpiredCodeException':
                raise AuthError("Verification code has expired")
            else:
                raise AuthError(f"Confirmation failed: {error_message}")

    def refresh_token(self, refresh_token: str) -> Dict:
        """
        Refresh the access token using a refresh token.

        Args:
            refresh_token: Valid refresh token

        Returns:
            Dict: New authentication tokens

        Raises:
            AuthError: If token refresh fails
        """
        try:
            response = self.client.initiate_auth(
                AuthFlow='REFRESH_TOKEN_AUTH',
                AuthParameters={
                    'REFRESH_TOKEN': refresh_token
                },
                ClientId=self.client_id
            )
            
            return {
                'AccessToken': response['AuthenticationResult']['AccessToken'],
                'ExpiresIn': response['AuthenticationResult']['ExpiresIn']
            }
            
        except ClientError as e:
            error_message = e.response['Error']['Message']
            raise AuthError(f"Token refresh failed: {error_message}")

    def forgot_password(self, username: str):
        """
        Initiate forgot password flow.

        Args:
            username: User's username

        Raises:
            AuthError: If request fails
        """
        try:
            self.client.forgot_password(
                ClientId=self.client_id,
                Username=username
            )
        except ClientError as e:
            error_message = e.response['Error']['Message']
            raise AuthError(f"Failed to initiate password reset: {error_message}")

    def confirm_forgot_password(
        self,
        username: str,
        confirmation_code: str,
        new_password: str
    ):
        """
        Complete forgot password flow with verification code.

        Args:
            username: User's username
            confirmation_code: Password reset code
            new_password: New password

        Raises:
            AuthError: If password reset fails
        """
        try:
            self.client.confirm_forgot_password(
                ClientId=self.client_id,
                Username=username,
                ConfirmationCode=confirmation_code,
                Password=new_password
            )
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            
            if error_code == 'CodeMismatchException':
                raise AuthError("Invalid verification code")
            elif error_code == 'InvalidPasswordException':
                raise AuthError("Password does not meet requirements")
            else:
                raise AuthError(f"Password reset failed: {error_message}")