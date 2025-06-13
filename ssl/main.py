<<<<<<< HEAD
import numpy as _np
# numpy에 Inf alias가 없으면 만들기
if not hasattr(_np, "Inf"):
    _np.Inf = _np.inf
from fastapi import FastAPI, UploadFile, File, Response, Query
=======
from fastapi import FastAPI, UploadFile, File, Response
>>>>>>> dev
from fastapi.middleware.cors import CORSMiddleware
from gtts import gTTS
import whisper
from rapidfuzz import process, fuzz
import json, tempfile, subprocess, os
<<<<<<< HEAD
import io, torch, torchaudio
import tempfile # 임시 파일을 사용하기 위한 모듈
import subprocess # subprocess 모듈을 사용하여 ffmpeg를 호출할 수 있습니다.
from zonos.model import Zonos
from zonos.conditioning import make_cond_dict
from zonos.utils import DEFAULT_DEVICE
import json
from threading import Thread
import time
from fastapi.staticfiles import StaticFiles

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("⏱️ Using device:", device)

app = FastAPI()
app.mount("/tts_cache", StaticFiles(directory="tts_cache"), name="tts_cache")

zonos = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=device)

_conan_wav, _conan_sr = torchaudio.load(
    os.path.join(os.path.dirname(__file__), "../Zonos/assets/TTS_코난.wav")
)
speaker_conan = zonos.make_speaker_embedding(_conan_wav, _conan_sr)

tts_status = {}  # (문항번호, age): {status, path, ...}
tts_queue = []   # [(문항번호, age), ...]

def tts_worker():
    while True:
        if tts_queue:
            qnum, age = tts_queue.pop(0)
            key = (qnum, age)
            fname = f"tts_cache/q{qnum}_{age}.wav"
            try:
                # 이미 만들어진 파일이 있으면 바로 ready
                if os.path.exists(fname):
                    tts_status[key] = {"status": "ready", "path": fname}
                    continue
                wav_bytes = zonos_tts(QUESTIONS[qnum], speaker_conan)
                os.makedirs("tts_cache", exist_ok=True)
                with open(fname, "wb") as f:
                    f.write(wav_bytes)
                tts_status[key] = {"status": "ready", "path": fname}
            except Exception as e:
                tts_status[key] = {"status": "error", "msg": str(e)}
        else:
            time.sleep(0.1)

# 서버 실행 시 백그라운드 TTS 생성 스레드 시작
Thread(target=tts_worker, daemon=True).start()

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
=======
import io
import tempfile # 임시 파일을 사용하기 위한 모듈
import subprocess # subprocess 모듈을 사용하여 ffmpeg를 호출할 수 있습니다.

app = FastAPI()

SUPPRESS = json.load(open("suppress.json"))   # ← ① 토큰 목록 로드
>>>>>>> dev

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
)

QUESTIONS = [
    "대화를 할 때 잘 듣지 않는 경우가 있다.",
<<<<<<< HEAD
    "지시를 잘 따르지 않거나 숙제, 임무 등을 완수하지 못하는 경우가 있다.",
    "과제나 업무를 수행하는 데 있어서 집중을 잘 못하고, 부주의로 인한 실수가 있다.",
    "지속적으로 정신력이 필요한 과제에 몰두하는 것을 피하거나, 거부하는 경우가 있다.",
    "수업이나 놀이에서 집중력을 유지하는 데 어려움을 겪는 경우가 있다.",
    "활동에 필요한 물건들을 종종 잃어버린다.(예: 준비물, 장난감, 숙제, 연필, 책 등)",
    "외부 자극에 의해 산만해진다.",
    "일상적인 일들을 종종 잊어버린다.",
    "대화 내용 또는 지시사항을 이해하거나 이행하기 등에 어려움을 느끼는 경우가 있다.",
    "손발이 가만히 있지 않으며, 자리에 앉아서는 계속 몸을 꿈틀거리는 일이 있다.",
    "조용히 앉아 있어야 하는 상황에 자리에서 일어나 다니는 경우가 종종 있다.",
    "상황에 맞지 않게 돌아다니거나 지나치게 산만해지는 경우가 있다.",
    "차분하게 노는 것, 놀이에 몰두하는 것에 어려움을 종종 느낀다.",
    "끊임없이 움직이거나, 꼼지락 거리는 행동을 하는 경우가 있다.",
    "지나치게 말을 많이 하는 경우가 있다.",
    "질문이 끝나기도 전에 불쑥 대답을 해버리는 경우가 있다",
    "자기 차례를 기다리지 못하는 경우가 있다.",
    "다른 사람들의 대화나 활동 사이에 끼어들거나 참견하는 경우가 있다.",
    "차분히 앉아 있거나, 조용히 있는 상황을 견디는 것에 어려움을 겪는 경우가 있다.",
    "과제나 활동을 체계적으로 하는 데 종종 어려움을 겪는다."
=======
    "지시를 잘 따르지 않거나 숙제, 임무 등을 완수하지 못하는 경우가 있다."
>>>>>>> dev
]

ANSWERS = ["1번", "2번", "3번", "4번",
        "일번", "이번", "삼번", "사번",
        "1", "2", "3", "4",
        "전혀아니다", "약간그렇다",
        "그렇다", "자주그렇다"]

# Whisper 모델 미리 로드 (GPU 가능)
<<<<<<< HEAD
stt_model = whisper.load_model("medium", device=device)
=======
stt_model = whisper.load_model("medium", device="cuda:0")
>>>>>>> dev

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

<<<<<<< HEAD
@app.get("/question/{num}")
def get_question(num: int, age: str = Query(None)):
    print(f"[API] /question/{num} - age={age}")
    text = QUESTIONS[num]
    if age == "10대 이하":
        key = (num, age)
        fname = f"tts_cache/q{num}_{age}.wav"
        print(f"[API] key={key}, tts_status={tts_status.keys()}")
        if key not in tts_status:
            tts_status[key] = {"status": "pending"}
            tts_queue.append((num, age))
            print(f"[API] tts_queue에 등록: {key}")
        # 준비된 경우만 바로 반환
        if tts_status[key].get("status") == "ready" and os.path.exists(fname):
            with open(fname, "rb") as f:
                return Response(content=f.read(), media_type="audio/wav")
        # 아직 준비 중일 때는 204 No Content 또는 커스텀 메시지 반환
        return Response(status_code=204)

    # 20대, 30대, 40대, 50대 이상 모두 gTTS 사용(느림 여부만 다름)
    slow = age in ["40대", "50대 이상"]
    tts = gTTS(text, lang="ko", slow=slow)
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)

    # gTTS의 반환 포맷은 mpeg이지만, 만약 wav로 강제 변환이 필요하다면 별도 추가 가능
    return Response(content=buf.read(), media_type="audio/mpeg")


=======
@app.get("/")
def root():
    return {"message": "FastAPI 서버 정상 작동 중"}

@app.get("/question/{num}")
def get_question(num: int):
    text = QUESTIONS[num]
    tts = gTTS(text, lang="ko")
    buf = io.BytesIO()
    tts.write_to_fp(buf)
    buf.seek(0)
    return Response(content=buf.read(), media_type="audio/mpeg")

>>>>>>> dev
@app.post("/stt")
async def stt(file: UploadFile = File(...)):
    raw = await file.read()
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as src:
        src.write(raw); src.flush()
        wav = src.name.replace(".webm", ".wav")
<<<<<<< HEAD
        
=======

>>>>>>> dev
    # ③ WebM → 16 kHz 모노 + loudnorm
    subprocess.run([
    "ffmpeg", "-nostdin", "-loglevel", "quiet",
    "-i", src.name, "-ar", "16000", "-ac", "1",
    "-af", "dynaudnorm=f=200",          # ← 여기!
    wav, "-y"
    ], check=True)

    text = transcribe(wav)
    os.remove(src.name); os.remove(wav)
<<<<<<< HEAD
    return {"text": text}

@app.get("/")
def root():
    return {"message": "FastAPI 서버 정상 작동 중"}
=======
    return {"text": text}
>>>>>>> dev
