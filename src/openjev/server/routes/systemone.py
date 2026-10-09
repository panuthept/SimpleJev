import json
import asyncio
from fastapi import APIRouter, Request
from openjev import Choice, Noul, Score, SystemOneRequest, SystemOneResponse
from fastapi.responses import JSONResponse, StreamingResponse

router = APIRouter(tags=["Systemone"])


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



    # from root.root import RØØT
    # root = RØØT(**root_configuration)

    # if body.get("stream"):
    #     return StreamingResponse(
    #         content=sse_wrapper(root.run(body=body)),
    #         media_type="text/event-stream",
    #     )

    # try:
    #     result = await asyncio.wait_for(
    #         asyncio.to_thread(root.run, body=body),
    #         timeout=timeout,
    #     )
    #     return JSONResponse(content=result, media_type="application/json")
    # except asyncio.TimeoutError:
    #     return JSONResponse(
    #         content={"error": "Request timed out."},
    #         status_code=504,
    #         media_type="application/json"
    #     )
    # except Exception as e:
    #     print(f"Error during chat completion: {e}")
    #     return JSONResponse(
    #         content={"error": str(e)},
    #         status_code=500,
    #         media_type="application/json"
    #     )
