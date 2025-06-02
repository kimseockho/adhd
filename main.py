from fastapi import FastAPI, UploadFile, File, Response
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import whisper
from rapidfuzz import process, fuzz
import json, tempfile, subprocess, os
import io
import tempfile # 임시 파일을 사용하기 위한 모듈
import subprocess # subprocess 모듈을 사용하여 ffmpeg를 호출할 수 있습니다.

app = FastAPI()

SUPPRESS = json.load(open("suppress.json"))   # ← ① 토큰 목록 로드

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

QUESTIONS = [
    "대화를 할 때 잘 듣지 않는 경우가 있다.",
    "지시를 잘 따르지 않거나 숙제, 임무 등을 완수하지 못하는 경우가 있다."
]

ANSWERS = ["1번", "2번", "3번", "4번",
        "일번", "이번", "삼번", "사번",
        "1", "2", "3", "4",
        "전혀아니다", "약간그렇다",
        "그렇다", "자주그렇다"]

# Whisper 모델 미리 로드 (GPU 가능)
stt_model = whisper.load_model("medium", device="cuda:1")

def transcribe(webm_path):
    txt = stt_model.transcribe(
        webm_path,
        language="ko",
        temperature=0,
        initial_prompt=("설문 응답: 일 1번 일번 이 2번 이번 삼 3번 삼번 사 4번 사번 전혀아니다 "
            "약간그렇다 그렇다 자주그렇다 중 하나"
        ), 
        suppress_tokens=SUPPRESS  # 영어·기호 억제
    )["text"].strip()

    best, score, _ = process.extractOne(
        txt, ANSWERS, scorer=fuzz.token_sort_ratio)
    return best if score >= 70 else txt

@app.get("/question/{num}")
def get_question(num: int):
    text = QUESTIONS[num]
    tts = gTTS(text, lang="ko")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return Response(content=buf.read(), media_type="audio/mpeg")

@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    raw = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as src:
        src.write(raw); src.flush()
        wav = src.name.replace(".webm", ".wav")

    # ③ WebM → 16 kHz 모노 + loudnorm
    subprocess.run([
    "ffmpeg", "-nostdin", "-loglevel", "quiet",
    "-i", src.name, "-ar", "16000", "-ac", "1",
    "-af", "dynaudnorm=f=200",          # ← 여기!
    wav, "-y"
    ], check=True)

    text = transcribe(wav)
    os.remove(src.name); os.remove(wav)
    return {"text": text}