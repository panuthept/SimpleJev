from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from openjev import Choice, Noul, Score, SystemOneRequest, SystemOneResponse

router = APIRouter()


@router.post("/systemone")
async def systemone(request: Request):
    timeout = request.app.state.timeout
    backend = request.app.state.backend

    body: dict = await request.json()
    print(body)

    questions = {}
    for key, value in body["questions"].items():
        if value["type"] == "choice":
            question = Choice(instructions=value["instructions"], options=value.get("options"), criteria=value.get("criteria"))
        elif value["type"] == "noul":
            question = Noul(instructions=value["instructions"])
        elif value["type"] == "score":
            question = Score(instructions=value["instructions"], criteria=value.get("criteria"), legend=value.get("legend"))
        questions[key] = question

    response: SystemOneResponse = backend.decide(SystemOneRequest(
        model=body["model"],
        state=body["state"],
        questions=questions,
    ))

    return JSONResponse(response.model_dump())