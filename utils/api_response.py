from http import HTTPStatus
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder


def success(
    response, status="Success", code=HTTPStatus.OK, message=None
) -> JSONResponse:
    return JSONResponse(
        content={
            "code": code,
            "response": jsonable_encoder(response),
            "status": status,
            "message": message,
        },
        status_code=code,
    )


def error(response, status="Failed", code=HTTPStatus.BAD_REQUEST) -> JSONResponse:
    return JSONResponse(
        content={
            "code": code,
            "response": jsonable_encoder(response),
            "status": status,
        },
        status_code=code,
    )
