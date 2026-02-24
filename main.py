from fastapi import FastAPI, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

from voice_assistant.ai.encoders import VoiceEncoder
from voice_assistant.ai.model import AIModel, GeminiModel
from voice_assistant.ai.postprocessor import PostProcessor
from voice_assistant.ai.preprocessor import Preprocessor, VoicePreprocessor, ProcessingTask
from voice_assistant.ai.promt_builders import PromptEngine
from voice_assistant.core.config import settings
from voice_assistant.core.database import get_db_connection
from voice_assistant.models.request import APIRequest
from voice_assistant.models.schema import DBSpeakingObject
from voice_assistant.reports.report_export import ReportExport

import traceback

from voice_assistant.services.assistant import AIAssistantService
from voice_assistant.core.database import init_db

# Вызываем сразу при загрузке модуля
init_db()
app = FastAPI()

voice_encoder = VoiceEncoder(model_name='base')

@app.post("/api/update")
def main(request: APIRequest):

    processing_task = ProcessingTask(message_id=request.message_id)
    print('Запрос получен'+str(request.message_id), flush=True)
    db_session = get_db_connection()
    db = DBSpeakingObject(connection=db_session)
    print('Запрос запуск обработки',  flush=True)
    ai = AIAssistantService(
        preprocessor= VoicePreprocessor(db_speaking_object=db,
                                        request=processing_task,
                                        encoder=voice_encoder,
                                        prompt_engine=PromptEngine(role=settings.ai_role,
                                                                   template=settings.ai_prompt_template,
                                                                   ),
        ),
        postprocessor=PostProcessor(),
        ai_model= GeminiModel(),
        report_export=ReportExport(db, processing_task),
    )

    try:
        response = ai.result()
        status_code = status.HTTP_200_OK
        return JSONResponse(content=jsonable_encoder(response), status_code=status_code)
    except Exception as exc:
        response = {"error": traceback.format_exc(exc)}
        status_code = status.HTTP_400_BAD_REQUEST

        return JSONResponse(content=jsonable_encoder(response), status_code=status_code)
    finally:

        db_session.close()
