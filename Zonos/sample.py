import torch
import torchaudio
from zonos.model import Zonos
from zonos.conditioning import make_cond_dict
from zonos.utils import DEFAULT_DEVICE as device

# model = Zonos.from_pretrained("Zyphra/Zonos-v0.1-hybrid", device=device)
model = Zonos.from_pretrained("Zyphra/Zonos-v0.1-transformer", device=device)

wav, sampling_rate = torchaudio.load("assets/VOLI_TTS_하람.wav")
speaker = model.make_speaker_embedding(wav, sampling_rate)

torch.manual_seed(421)

cond_dict = make_cond_dict(
    text="안녕하세요, 한국어 보이스 테스트입니다.", 
    speaker=speaker, 
    language="ko",
    #age="elderly",     # "child", "adult", "elderly" 등 가능 (모델 지원에 따라 다름)
    #emotion="angry"    # "neutral", "happy", "sad", "angry", "calm", "excited" 등
)
conditioning = model.prepare_conditioning(cond_dict)
codes = model.generate(conditioning)
wavs = model.autoencoder.decode(codes).cpu()
torchaudio.save("sample_하람.wav", wavs[0], model.autoencoder.sampling_rate)