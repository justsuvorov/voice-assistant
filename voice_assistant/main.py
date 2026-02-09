
import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

import traceback

import config


app = FastAPI()


class AIAssistantService:
    pass


class ReportExport:
    pass


class PostProcessor:
    pass


class Report:
    pass


class Preprocessor:
    pass


class DBSpeakingObject:
    pass


class AIModel:
    pass


class APIRequest:
    pass


@app.post("/api/update")
def main(request: APIRequest):
    ai = AIAssistantService(
        ReportExport(
            PostProcessor(
                Report(
                    AIModel(
                        Preprocessor(
                            DBSpeakingObject(
                                APIRequest(request
                                           )
                                )
                            )
                        )
                    )
                )
            )
        )
    try:
        response = ai.result()
        status_code = status.HTTP_200_OK

    except Exception as exc:
        response = {"error": traceback.format_exc(exc)}
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(content=jsonable_encoder(response), status_code=status_code)