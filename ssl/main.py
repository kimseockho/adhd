import numpy as _np
# numpy에 Inf alias가 없으면 만들기
if not hasattr(_np, "Inf"):
    _np.Inf = _np.inf
from fastapi import FastAPI, UploadFile, File, Response, Query
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import whisper
from rapidfuzz import process, fuzz
import json, tempfile, subprocess, os
import io, torch, torchaudio
import tempfile # 임시 파일을 사용하기 위한 모듈
import subprocess # subprocess 모듈을 사용하여 ffmpeg를 호출할 수 있습니다.
from zonos.model import Zonos
from zonos.conditioning import make_cond_dict
from zonos.utils import DEFAULT_DEVICE
import json

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("⏱️ Using device:", device)

app = FastAPI()

zonos = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=device)

_conan_wav, _conan_sr = torchaudio.load(
    os.path.join(os.path.dirname(__file__), "../Zonos/assets/VOLI_TTS_코난.wav")
)
speaker_conan = zonos.make_speaker_embedding(_conan_wav, _conan_sr)

def zonos_tts(text: str, speaker_emb):
    """Zonos 로 TTS 음성(바이너리)을 생성해서 리턴"""
    cond = make_cond_dict(text=text, speaker=speaker_emb, language="ko")
    conditioning = zonos.prepare_conditioning(cond)
    codes = zonos.generate(conditioning)
    wavs = zonos.autoencoder.decode(codes).cpu()

    buf = io.BytesIO()
    torchaudio.save(buf, wavs[0], zonos.autoencoder.sampling_rate, format="wav")
    buf.seek(0)
    return buf.read()

suppress_path = os.path.join(os.path.dirname(__file__), "suppress.json")
SUPPRESS = json.load(open(suppress_path))   # ← ① 토큰 목록 로드

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
stt_model = whisper.load_model("medium", device=device)

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
def get_question(num: int, age: str = Query(None, description="ex: '10대 이하'")):
    text = QUESTIONS[num]
    if age == "10대 이하":
        wav_bytes = zonos_tts(text, speaker_conan)
        return Response(content=wav_bytes, media_type="audio/wav")
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

@app.get("/")
def root():
    return {"message": "FastAPI 서버 정상 작동 중"}
