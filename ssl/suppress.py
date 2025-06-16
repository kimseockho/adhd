import whisper, json

stt_model = whisper.load_model("medium", device="cuda")
tok = whisper.tokenizer.get_tokenizer(multilingual=True, task="transcribe")

ENG_SYM_TOKENS = set()

# 1) 알파벳
for ch in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
    ENG_SYM_TOKENS.update(tok.encode(ch, allowed_special=set()))   # ← 수정!

# 2) 흔한 기호
for sym in ".,?!%":
    ENG_SYM_TOKENS.update(tok.encode(sym, allowed_special=set()))

# 저장
with open("suppress.json", "w") as f:
    json.dump(sorted(ENG_SYM_TOKENS), f)

print("suppress.json ✓  |  토큰 개수:", len(ENG_SYM_TOKENS))
