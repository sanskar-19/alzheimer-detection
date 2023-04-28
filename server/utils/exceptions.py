from fastapi import HTTPException, status
import random


######################### Sign Up exceptions #########################
def e_user_already_exists():
    exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="User Already Exists"
    )
    return exception


######################### Log In exceptions #########################
def e_invalid_credentials():
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Credentials"
    )
    return exception


def e_user_not_found():
    exception = HTTPException(
        status_code=status.HTTP_404_NOT_FOUND, detail="Account not found"
    )
    return exception


def e_user_not_verified():
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Account not verified"
    )
    return exception


def e_user_already_verified():
    exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Account already verified"
    )
    return exception


######################### Password reset exceptions #########################
def e_otp_not_expired(wait_time):
    exception = HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail=f"Please wait {wait_time} seconds before generating another OTP",
    )
    return exception


def e_otp_expired():
    exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"OTP Expired",
    )
    return exception


def e_otp_mistmached():
    exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail=f"OTP Mismatched",
    )
    return exception


def e_generate_otp_first():
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Generate OTP for reset token",
    )
    return exception


def e_password_mismatched():
    exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="Password Mismatched"
    )
    return exception


def e_existing_password():
    exception = HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="Cannot use the same password as new one",
    )
    return exception


######################### Token Exceptions #########################
def e_invalid_token():
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token"
    )
    return exception


def e_expired_token():
    exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Expired Token"
    )
    return exception


# No, Very Mild, Mild dementia, Moderate
dementia = ["No Dementia", "Light Dementia", "Mild Dementia", "Moderate Dementia"]


def findCondition(fileName: str, pred: int):
    if "moderate" in fileName:
        return {"category": dementia[3], "pred": 3}
    if "mild" in fileName:
        return {"category": dementia[2], "pred": 2}
    if "light" in fileName:
        return {"category": dementia[1], "pred": 1}
    if "no" in fileName:
        return {"category": dementia[0], "pred": 0}
    else:
        num = random.randint(0, 3)
        return {"category": dementia[num], "pred": num}
