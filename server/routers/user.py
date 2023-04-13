from fastapi import APIRouter, Header, status, Depends, HTTPException
from ..schema import user as user_schema
from ..utils import db, exceptions, jwt as jwt_utils, user as user_utils
from ..models.user import UserModel
from sqlalchemy.orm import Session
from ..database import get_db
from pydantic import EmailStr
from datetime import datetime, timedelta

db = get_db()

router = APIRouter(prefix="/api/ums")


# Signup as a new user
@router.post(
    "/signup",
    status_code=status.HTTP_201_CREATED,
)
async def signup(user: user_schema.NewUser, db: Session = Depends(get_db)):
    # Creating new user
    try:
        return add_new_user_to_db(db, user.dict())
    except Exception as e:
        raise e


@router.post(
    "/verify-account",
    response_model=user_schema.ResponseModel,
    status_code=status.HTTP_200_OK,
)
async def verify_account(email: EmailStr, otp: str, db: Session = Depends(get_db)):
    try:
        user_from_db = db.query(UserModel).filter(UserModel.email == email)
        if user_from_db.first() is None:
            raise exceptions.e_user_not_found()

        if user_from_db.first().status == True:
            raise exceptions.e_user_already_verified()
        else:
            if otp and user_from_db.first().otp == otp:
                if user_from_db.first().otp_expiry_at > datetime.now():
                    user_from_db.update(
                        {
                            UserModel.otp: None,
                            UserModel.otp_expiry_at: None,
                            UserModel.status: True,
                        }
                    )
                    db.commit()
                    return {"data": {}, "message": "Account verified successfully"}
                else:
                    raise exceptions.e_otp_expired()
            else:
                if user_from_db.first().otp:
                    raise exceptions.e_otp_mistmached()
                else:
                    raise exceptions.e_generate_otp_first()
    except Exception as e:
        raise e


@router.post(
    "/resend-account-verification-otp", response_model=user_schema.ResponseModel
)
async def resend_account_verification_otp(
    user: user_schema.ExistingUser, db: Session = Depends(get_db)
):
    try:
        user_from_db = db.query(UserModel).filter(UserModel.email == user.email)
        if user_from_db.first():
            if user_from_db.first().status == True:
                print("User exists")
                raise exceptions.e_user_already_verified()

            if user_utils.verify_password(
                user.password, user_from_db.first().hashed_password
            ):
                otp, otp_expiry_at = user_utils.generate_otp()
                user_from_db.update(
                    {UserModel.otp: otp, UserModel.otp_expiry_at: otp_expiry_at}
                )
                db.commit()
                return {"data": {"otp": otp}, "message": "OTP sent successfully"}
            else:
                raise exceptions.e_invalid_credentials()
        else:
            raise exceptions.e_user_not_found()
    except Exception as e:
        raise e


# Login
@router.post(
    "/login", response_model=user_schema.ResponseModel, status_code=status.HTTP_200_OK
)
async def login(user: user_schema.ExistingUser, db: Session = Depends(get_db)):
    try:
        user_from_db = db.query(UserModel).filter(UserModel.email == user.email).first()
        if user_from_db is None:
            raise exceptions.e_user_not_found()
        else:
            if user_from_db.status == False:
                raise exceptions.e_user_not_verified()

            if user_utils.verify_password(
                password=user.password, hashed_password=user_from_db.hashed_password
            ):
                token = jwt_utils.create_access_token(
                    uid=user_from_db.uid,
                    email=user_from_db.email,
                    role=user_from_db.role,
                )
                return {
                    "data": {"access_token": token},
                    "message": "Logged in successfully",
                }
            else:
                raise exceptions.e_invalid_credentials()

    except Exception as e:
        raise e


# Fetch user details from token
@router.get(
    "/fetch-user-details",
    status_code=status.HTTP_200_OK,
    response_model=user_schema.UserDetails,
)
async def get_user_details(token: str = Header(), db: Session = Depends(get_db)):
    try:
        return fetch_user_from_db(db, token)
    except Exception as e:
        raise e


# send password reset email
@router.post(
    "/send-forgot-password-email",
    response_model=user_schema.ResponseModel,
)
async def send_forgot_password_email(email: EmailStr, db: Session = Depends(get_db)):
    try:
        user_from_db = db.query(UserModel).filter(UserModel.email == email)
        if user_from_db.first() is None:
            raise exceptions.e_user_not_found()

        if user_from_db.first().status == False:
            raise exceptions.e_user_not_verified()

        last_otp_expiry = user_from_db.first().otp_expiry_at
        if last_otp_expiry is not None and last_otp_expiry > datetime.now():
            raise exceptions.e_otp_not_expired(
                wait_time=(last_otp_expiry - datetime.now()).seconds
            )
        else:
            otp, otp_expiry_at = user_utils.generate_otp()
            user_from_db.update(
                {UserModel.otp: otp, UserModel.otp_expiry_at: otp_expiry_at}
            )
            db.commit()
            return {
                "data": {
                    "otp": otp,
                    "validity": otp_expiry_at,
                },
                "message": "Otp generated successfully",
            }
    except Exception as e:
        raise e


# reset password using otp
@router.put(
    "/forgot-password",
    response_model=user_schema.ResponseModel,
)
async def forgot_password(
    new_password: user_schema.ResetPassword, db: Session = Depends(get_db)
):
    try:
        user_from_db = db.query(UserModel).filter(UserModel.email == new_password.email)
        if user_from_db is None:
            raise exceptions.e_user_not_found()

        if user_from_db.first().status == False:
            raise exceptions.e_user_not_verified()

        otp, otp_expiry = user_from_db.first().otp, user_from_db.first().otp_expiry_at

        if otp is None:
            raise exceptions.e_generate_otp_first()

        if datetime.now() > otp_expiry:
            raise exceptions.e_otp_expired()

        if otp == new_password.otp:
            user_from_db.update(
                {
                    UserModel.hashed_password: user_utils.generate_hash(
                        new_password.new_password
                    ),
                    UserModel.otp: None,
                    UserModel.otp_expiry_at: None,
                }
            )
            db.commit()
            return {"data": {}, "message": "Password Reset Successfully"}
        else:
            raise exceptions.e_otp_mistmached()
    except Exception as e:
        raise e


@router.put("/change-password", response_model=user_schema.ResponseModel)
async def change_password(
    payload: user_schema.ChangePassword,
    token: str = Header(),
    db: Session = Depends(get_db),
):
    try:
        jwt_decoded = jwt_utils.validate_access_token(token)
        user_from_db = db.query(UserModel).filter(
            UserModel.email == jwt_decoded["email"], UserModel.uid == jwt_decoded["uid"]
        )

        # Check if user exists in db
        if user_from_db.first() is None:
            raise exceptions.e_user_not_found()

        # Verify the old password
        if user_utils.verify_password(
            password=payload.old_password,
            hashed_password=user_from_db.first().hashed_password,
        ):
            # Verify that he entered the same passwords
            if payload.new_password == payload.confirm_password:
                # Verify that he didnot entered his old password again for the new password
                if user_utils.verify_password(
                    password=payload.new_password,
                    hashed_password=user_from_db.first().hashed_password,
                ):
                    # If yes then we raise exception
                    raise exceptions.e_existing_password()

                # Else we update the db
                user_from_db.update(
                    {
                        UserModel.hashed_password: user_utils.generate_hash(
                            payload.new_password
                        )
                    }
                )
                # Committing
                db.commit()
                return {"data": {}, "message": "Password Changed Successfully"}
            else:
                # Passwprd mismatched error
                raise exceptions.e_password_mismatched()
        else:
            # Invalid credentials for the old password
            raise exceptions.e_invalid_credentials()
    except Exception as e:
        raise e


# validate-token
@router.post(
    "/validate-token",
    response_model=user_schema.ResponseModel,
)
async def validate_token(token: str = Header()):
    try:
        payload = jwt_utils.validate_access_token(access_token=token)
        return {"data": payload, "message": "Token Validated"}
    except Exception as e:
        raise e


#######################################################################################################################################
def fetch_user_from_db(db: Session, token: str):
    try:
        payload = jwt_utils.validate_access_token(access_token=token)
        email = payload["email"]
        user = db.query(UserModel).filter(UserModel.email == email).first()

        # If no user exists
        if user is None:
            raise exceptions.e_user_not_found()
        else:
            if user.status == False:
                raise exceptions.e_user_not_verified()

            return user

    # Handling exceptions from JWT failure
    except Exception as e:
        raise (e)


#######################################################################################################################################
def add_new_user_to_db(db: Session, user: dict):
    try:
        user_from_db = (
            db.query(UserModel).filter(UserModel.email == user["email"]).first()
        )

        if user_from_db is not None:
            raise exceptions.e_user_already_exists()
        else:
            otp, otp_expiry_at = user_utils.generate_otp()
            user_in_db = user_utils.create_new_user(
                **user, otp=otp, otp_expiry_at=otp_expiry_at
            )
            print(user_in_db)
            db.add(user_in_db)
            db.commit()

            # Send an otp to the user email for verification

            return {
                "data": {"otp": otp},
                "message": "User added successfully, Please verify the account to continue",
            }
    except Exception as e:
        if e is HTTPException:
            raise e
        else:
            raise e
