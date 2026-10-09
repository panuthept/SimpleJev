from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from openjev import Choice, Noul, Score, SystemOneRequest, SystemOneResponse

router = APIRouter()


@router.post("/decisions")
async def decisions(request: Request):
    timeout = request.app.state.timeout
    backend = request.app.state.backend

    body: dict = await request.json()
    print(body)

    questions = {}
    questions_types = {}
    for value in body["questions"]:
        key = value["name"]
        if value["type"] == "choice":
            criteria = {choice["value"]: choice["description"] for choice in value["choices"]}
            question = Choice(instructions=value["instructions"], criteria=criteria)
            questions_types[key] = "choice"
        elif value["type"] == "predicate":
            question = Noul(instructions=value["instructions"])
            questions_types[key] = "predicate"
        elif value["type"] == "score":
            legend = {str(i): level["label"] for i, level in enumerate(value["levels"])}
            question = Score(instructions=value["instructions"], legend=legend)
            questions_types[key] = "score"
        questions[key] = question

    response: SystemOneResponse = backend.decide(SystemOneRequest(
        model=body["model"],
        state=body["input"],
        questions=questions,
    ))

    def format_answer(answer, name: str):
        if answer.type == "choice":
            return {
                "type": "choice",
                "name": name,
                "choice": answer.choice,
                "probabilities": [{"value": value, "probability": prob} for value, prob in answer.probabilities.items()],
                "confidence": answer.confidence
            }
        elif answer.type == "noul":
            return {
                "type": "predicate",
                "name": name,
                "probability": answer.noul
            }
        elif answer.type == "score":
            return {
                "type": "score",
                "name": name,
                "score": answer.score,
                "probabilities": [{"value": value, "label": answer.legend[value], "probability": prob} for value, prob in answer.probabilities.items()],
                "confidence": answer.confidence
            }

    return JSONResponse({
        "model": body["model"],
        "answers": [format_answer(response.answers[value["name"]], value["name"]) for value in body["questions"]],
        "usage": response.usage.model_dump()
    })