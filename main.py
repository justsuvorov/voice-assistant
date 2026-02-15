
import uvicorn
from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware

import traceback

from voice_assistant.ai.encoders import VoiceEncoder
from voice_assistant.ai.preprocessor import Preprocessor, VoicePreprocessor, ProcessingTask
from voice_assistant.ai.promt_builders import PromptEngine
from voice_assistant.core.database import get_db_connection
from voice_assistant.models.schema import DBSpeakingObject

app = FastAPI()




class ReportExport:
    pass


class PostProcessor:
    pass


class Report:
    pass



class AIModel:
    pass


class APIRequest:
    pass


class AIAssistantService:
    def __init__(self,
                 preprocessor: Preprocessor,
                 postprocessor: PostProcessor,
                 ai_model: AIModel,
                 request: APIRequest,
                 report_export: ReportExport,
                 ):
        self._preprocessor = preprocessor
        self._postprocessor = postprocessor
        self._model = ai_model
        self._request = request
        self._report_export = report_export

    def result(self):
        model_query = self._preprocessor.query(self._request)
        model_response = self._model.response(model_query)
        report = self._postprocessor.report(model_response)
        return self._report_export.response(report)



@app.post("/api/update")
def main(request: APIRequest):
    processing_task = ProcessingTask(message_id=request.message_id)
    ai = AIAssistantService(
        preprocessor= VoicePreprocessor(db_speaking_object=DBSpeakingObject(connection=get_db_connection()),
                                        request=processing_task,
                                        encoder=VoiceEncoder(model_name='base'),
                                        prompt_engine=PromptEngine(role='default_role',
                                                                   template='None'),


        ),
        postprocessor=PostProcessor(),
        ai_model= AIModel(),
        request=request,
        report_export=ReportExport(),
    )

    try:
        response = ai.result()
        status_code = status.HTTP_200_OK

    except Exception as exc:
        response = {"error": traceback.format_exc(exc)}
        status_code = status.HTTP_400_BAD_REQUEST

    return JSONResponse(content=jsonable_encoder(response), status_code=status_code)