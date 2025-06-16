<script>
    import { onMount, tick } from 'svelte';
    import { goto } from '$app/navigation';

     const API = "https://192.168.3.19:5173";

    // 문항 리스트
    const questions = [
        "대화를 할 때 잘 듣지 않는 경우가 있다.",
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
    ];
    // 보기 라벨
    const options = [
        "전혀 아니다", "약간 그렇다", "그렇다", "자주 그렇다"
    ];
    // 설문 정보
    let gender = "", age = "", region = "", name = "";
    const genders = ["남성", "여성"];
    const ages = ["10대 이하", "20대", "30대", "40대", "50대 이상"];
    const regions = ["서울", "경기", "부산", "대구", "기타"];
    
    // 오디오 관리
    let audioUrls = Array(questions.length).fill("");

    $: if (age) {
        [0,1].forEach(idx => {
            if (idx < questions.length && !audioUrls[idx]) {
                if (age === "10대 이하") {
                    const url = `${API}/tts_cache/q${idx}_${encodeURIComponent(age)}.wav`;
                    // wav 파일 HEAD 체크 생략 가능 (캐시라면 바로 할당)
                    audioUrls[idx] = url;
                    audioUrls = [...audioUrls];
                } else {
                    // API로 음성 미리 가져오기
                    const url = `${API}/question/${idx}?age=${encodeURIComponent(age)}`;
                    fetch(url)
                        .then(res => res.blob())
                        .then(blob => {
                            if (audioUrls[idx]) URL.revokeObjectURL(audioUrls[idx]);
                            audioUrls[idx] = URL.createObjectURL(blob);
                            audioUrls = [...audioUrls];
                        })
                        .catch(err => console.warn("prefetch failed", err));
                }
            }
        });
    }

    // 마이크 테스트
    let micTestRecording = false;
    let micTestAudioChunks = [];
    let micTestResult = "";
    let micTestDone = false;
    let micTestMediaRecorder = null;

    // 상태 변수
    let surveyStarted = false;
    let curIdx = 0;
    let guideMsg = "";  // 안내 메시지(다시 말씀해주세요 등)
    let finishSurvey = false;
    // 각 문항 상태: 'idle'(대기), 'playing'(읽기중), 'recording'(녹음중), 'done'(완료)
    let questionStates = Array(questions.length).fill('idle');

    function startRecording(idx) {
        recordAndRecognize(idx);
    }

    // 오디오 재생 + 끝나면 상태 전환
    async function playTTS(idx) {
        if (age === "10대 이하") {
            // 기존 캐시 polling 방식 유지
            const triggerUrl = `${API}/question/${idx}?age=${encodeURIComponent(age)}`;
            await fetch(triggerUrl);
            
            while (true) {
                const wavUrl = `${API}/tts_cache/q${idx}_${encodeURIComponent(age)}.wav`;
                const res = await fetch(wavUrl, { method: 'HEAD' });
                if (res.status === 200) {
                    audioUrls[idx] = wavUrl;
                    audioUrls = [...audioUrls];
                    break;
                } else {
                    guideMsg = "음성 준비 중... 잠시만 기다려주세요.";
                    await new Promise(r => setTimeout(r, 1000));
                }
            }
        } else {
            // API에서 직접 받아와서 blob으로 재생
            const url = `${API}/question/${idx}?age=${encodeURIComponent(age)}`;
            const res = await fetch(url);
            const blob = await res.blob();
            // 기존 URL 있으면 해제
            if (audioUrls[idx]) URL.revokeObjectURL(audioUrls[idx]);
            audioUrls[idx] = URL.createObjectURL(blob);
            audioUrls = [...audioUrls];
        }

        await tick();
        const audioEl = document.getElementById(`audio-${idx}`);
        audioEl.preload = "auto";
        audioEl.load();
        await new Promise(r => audioEl.onloadedmetadata = r);
        audioEl.play();

        // 다음 문항 prefetch도 10대 이하만
        if (age === "10대 이하") {
            const next = idx + 1;
            if (next < questions.length && !audioUrls[next]) {
                const nextUrl = `${API}/tts_cache/q${next}_${encodeURIComponent(age)}.wav`;
                audioUrls[next] = nextUrl;
                audioUrls = [...audioUrls];
            }
        }

        return new Promise(resolve => {
            audioEl.onended = () => {
                startRecording(idx);
                resolve();
            };
        });
    }



    async function startMicTest() {
        micTestResult = "";
        micTestDone = false;
        micTestAudioChunks = [];
        micTestRecording = true;
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        micTestMediaRecorder = new MediaRecorder(stream);

        micTestMediaRecorder.ondataavailable = (e) => {
            micTestAudioChunks.push(e.data);
        };
        micTestMediaRecorder.onstop = async () => {
            if (micTestAudioChunks.length === 0) {
                micTestRecording = false;
                micTestDone = false;
                micTestResult = "(녹음 실패)";
                return;
            }
            const blob = new Blob(micTestAudioChunks, { type: 'audio/webm' });
            const formData = new FormData();
            formData.append("file", blob, "mic-test.webm");
            try {
                const res = await fetch("https://192.168.3.19:5173/stt", {
                    method: "POST",
                    body: formData
                });
                const data = await res.json();
                micTestResult = data.text || data.error || "(음성 인식 실패)";
                micTestDone = true;
            } catch (err) {
                micTestResult = "(서버 통신 실패)";
                micTestDone = false;
            }
            micTestAudioChunks = [];
            micTestRecording = false;
        };

        micTestMediaRecorder.start();
    }

    function stopMicTest() {
        if (micTestMediaRecorder && micTestRecording) {
            micTestMediaRecorder.stop();
            micTestRecording = false;
        }
    }

    let answerRecordings = Array(questions.length).fill(false);
    let answerTexts = Array(questions.length).fill("");
    let answers = Array(questions.length).fill("");

    let mediaRecorders = Array(questions.length).fill(null);
    let audioChunksArr = Array(questions.length).fill(null);

    function parseAnswer(text) {
        if (!text) return "";
        let cleaned = text.replace(/\s/g, "");
        cleaned = cleaned.replace(/^(네|음|아|예|응|그냥)+/g, "");

        if (/일번|일|하나/.test(cleaned)) return "1";
        if (/이번|이|둘/.test(cleaned)) return "2";
        if (/삼번|삼|셋/.test(cleaned)) return "3";
        if (/사번|사|넷/.test(cleaned)) return "4";
        if (/전혀|아니다|1번/.test(cleaned)) return "1";
        if (/약간|약간그렇다|2번/.test(cleaned)) return "2";
        if ((/그렇다|3번/.test(cleaned)) && !/자주/.test(cleaned)) return "3";
        if (/자주|4번|자주그렇다/.test(cleaned)) return "4";

        return "";
    }

    function setAnswer(qidx, value) {
        if (finishSurvey) {
            answers[qidx] = value.toString();
        }
    }

    function startSurvey() {
        console.log("[startSurvey] age =", age);
        if (!age) {
            alert("설문을 시작하려면 연령대를 선택해주세요.");
            return;
        }
        surveyStarted = true;
        questionStates = Array(questions.length).fill('idle');
        curIdx = 0;
        playTTS(curIdx);
    }

    async function recordAndRecognize(idx) {
        console.log(`[STT] recordAndRecognize start for idx=${idx}`);
        while (true) {
            guideMsg = "";
            audioChunksArr[idx] = [];
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            const recorder = new MediaRecorder(stream);
            recorder.ondataavailable = e => audioChunksArr[idx].push(e.data);

            recorder.start();
            await new Promise(resolve => setTimeout(resolve, 3000));
            if (recorder.state !== "inactive") recorder.stop();

            await new Promise(resolve => {
                recorder.onstop = resolve;
            });

            const blob = new Blob(audioChunksArr[idx], { type: 'audio/webm' });
            const formData = new FormData();
            formData.append("file", blob, `answer${idx}.webm`);

            try {
                const res = await fetch("https://192.168.3.19:5173/stt", { method: "POST", body: formData });
                const data = await res.json();
                answerTexts[idx] = data.text || data.error || "(음성 인식 실패)";
                const parsed = parseAnswer(answerTexts[idx]);
                answers[idx] = parsed;

                if (parsed) {
                    guideMsg = "";
                    questionStates[idx] = 'done';
                    questionStates = [...questionStates];
                    if (idx + 1 < questions.length) {
                        curIdx = idx + 1;
                        await playTTS(curIdx);
                    } else {
                        finishSurvey = true;
                        surveyStarted = false;
                    }
                    break;
                } else {
                    guideMsg = "인식 결과: '" + answerTexts[idx] + "' → 표시가 될 때까지 다시 말씀해 주세요 (1~4번 또는 보기 중 하나로)";
                    questionStates[idx] = 'recording';
                    questionStates = [...questionStates];
                    await new Promise(resolve => setTimeout(resolve, 900));
                }
            } catch (e) {
                guideMsg = "(서버 통신 오류: 다시 시도 중...)";
                await new Promise(resolve => setTimeout(resolve, 1200));
            }
        }
    }
    
    function onSurveyFinish() {
        if (!name || !gender || !age || !region || answers.some(ans => !ans)) {
            alert("모든 정보를 입력하고 각 문항에 답변을 완료해주세요.");
            return;
        }
        localStorage.setItem("surveyResult", JSON.stringify({ name, gender, age, region, answers }));
        goto('/result');
    }
</script>

<main>
    <div class="survey-header">
        <h1>ADHD 자가진단 설문</h1>
        <p>
            (필수) 자가진단테스트를 하시는 본인(대상자)의 성별, 연령대, 거주지역(시/도)을 선택해 주세요.<br />
            <span class="notice">※ 설문항목은 자가진단테스트 통계 자료로만 사용됩니다.</span>
        </p>
        <div class="survey-info">
            <input
                type="text"
                placeholder="이름"
                bind:value={name}
                class="input-name"
                maxlength="10"
                style="width:80px;"
            />
            <select bind:value={gender}>
                <option value="" disabled selected>성별</option>
                {#each genders as g}
                    <option value={g}>{g}</option>
                {/each}
            </select>
            <select bind:value={age}>
                <option value="" disabled selected>연령대</option>
                {#each ages as a}
                    <option value={a}>{a}</option>
                {/each}
            </select>
            <select bind:value={region}>
                <option value="" disabled selected>거주지역</option>
                {#each regions as r}
                    <option value={r}>{r}</option>
                {/each}
            </select>
        </div>
    </div>

    <div class="survey-guide">
        <b>답변 요령</b><br />
        - 설문 전 <b>마이크 테스트</b>를 해주세요.<br />
        - 각 문항은 <b>3초 이내</b>에 대답해 주세요.<br />
        - <b>답변을 수정하고 싶은 경우 설문 종료 후 해당 문항으로 가서 변경할 번호를 클릭하시면 됩니다.</b>
    </div>

    <div class="mic-test-wrap">
        <div style="margin: 7px 0;">
            {#if !micTestRecording}
                <button on:click={startMicTest} class="mic-test-btn">마이크 테스트 시작</button>
            {:else}
                <button on:click={stopMicTest} class="mic-test-btn">녹음 중지</button>
            {/if}
        </div>
        {#if micTestResult}
            <div class="mic-test-result">
                음성 인식 결과: <b>{micTestResult}</b>
            </div>
        {/if}
        {#if micTestDone}
            <div class="mic-ok" style="margin-top:7px;">마이크 테스트 완료</div>
        {/if}
    </div>
    
    {#if !surveyStarted && !finishSurvey}
        <div style="text-align:center; margin: 24px 0;">
            <button class="tts-btn" on:click={startSurvey} style="min-width:130px;">설문 시작</button>
        </div>
    {/if}

    <div class="questions-wrap">
        {#each questions as q, i}
        <div class="question-block" style="opacity:{finishSurvey ? 1 : (curIdx == i ? 1 : 0.5)};">
            <div class="q-row-between">
                <div>
                    <span class="q-num">{i + 1}</span>
                    <span class="q-text">{q}</span>
                </div>
            </div>
            <div class="q-row-between" style="margin-top:10px;">
                <div
                    class="option-numbers-inline"
                    style="
                        opacity: {questionStates[i] === 'playing' ? 0.4 : 1};
                        pointer-events: {questionStates[i] === 'playing' ? 'none' : 'auto'};
                    "
                >  
                    {#each options as o, j}
                        <span class="option-number-label">
                            <span
                                class="option-number"
                                style="background:{answers[i] == (j+1).toString() ? '#2176ff' : '#e5f1ff'};
                                    color:{answers[i] == (j+1).toString() ? '#fff' : '#2176ff'};
                                    border:1.2px solid #b6d4fe;
                                    cursor: {finishSurvey ? 'pointer' : 'default'}"
                                on:click={() => finishSurvey && setAnswer(i, j+1)}
                            >
                                {j + 1}
                            </span>
                            <span class="option-label">{o}</span>
                        </span>
                    {/each}
                </div>
            </div>
            <audio id="audio-{i}" src={audioUrls[i]} preload="auto"/>  
            {#if guideMsg && curIdx == i}
                <div style="color:red;margin-top:8px;">{guideMsg}</div>
            {/if}
            {#if answerTexts[i]}
                <div class="answer-stt-result">음성 인식: {answerTexts[i]}</div>
            {/if}
        </div>
        {/each}
    </div>

    {#if finishSurvey}
    <div style="text-align:center; margin: 30px 0 20px 0;">
        <button 
            on:click={onSurveyFinish}
            class="tts-btn" 
            style="min-width:120px;">
            설문 결과 보기
        </button>
    </div>
    {/if}
</main>

<style>
    main {
        font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
        max-width: 700px;
        margin: 0 auto;
        padding: 32px 10px;
        background: #f8fafc;
    }
    .survey-header {
        background: #e5f1ff;
        border-radius: 12px;
        padding: 18px 22px 12px 22px;
        margin-bottom: 28px;
        box-shadow: 0 2px 10px #eee;
    }
    h1 {
        margin: 0 0 6px 0;
        font-size: 2.0rem;
        color: #2176ff;
    }
    .notice {
        color: #888;
        font-size: 0.95em;
    }
    .survey-info {
        display: flex;
        gap: 10px;
        margin-top: 10px;
    }
    select {
        padding: 7px 14px;
        font-size: 1em;
        border-radius: 6px;
        border: 1px solid #b6d4fe;
        background: #fff;
        color: #444;
    }
    .questions-wrap {
        margin-top: 15px;
    }
    .question-block {
        background: #fff;
        border-radius: 10px;
        box-shadow: 0 1px 6px #dde;
        margin-bottom: 20px;
        padding: 18px 18px 10px 18px;
        display: flex;
        flex-direction: column;
        gap: 10px;
    }
    .q-num {
        float: left;
        margin-right: 12px;
        font-size: 1.22em;
        font-weight: bold;
        color: #2176ff;
    }
    .q-text {
        margin-bottom: 8px;
        font-size: 1.13em;
        font-weight: 500;
        color: #222;
    }
    .option-numbers {
        display: flex;
        gap: 36px;
        margin-left: 22px;
        margin-top: 12px;
    }
    .option-number {
        width: 32px; height: 32px;
        display: flex; align-items: center; justify-content: center;
        background: #e5f1ff;
        color: #2176ff;
        border-radius: 50%;
        font-size: 1.12em;
        font-weight: bold;
        border: 1.2px solid #b6d4fe;
        box-shadow: 0 0 4px #e5f1ff;
    }
    .tts-btn {
        margin-left: auto;
        padding: 5px 13px;
        border: none;
        border-radius: 16px;
        background: #2176ff;
        color: #fff;
        font-size: 1em;
        cursor: pointer;
        transition: background 0.17s;
    }
    .tts-btn:hover {
        background: #1455ad;
    }
    .option-numbers {
        display: flex;
        gap: 24px;
        margin-left: 22px;
        margin-top: 12px;
    }
    .option-number-label {
        display: flex;
        align-items: center;
        gap: 7px;
    }
    .option-number {
        width: 32px; height: 32px;
        display: flex; align-items: center; justify-content: center;
        background: #e5f1ff;
        color: #2176ff;
        border-radius: 50%;
        font-size: 1.12em;
        font-weight: bold;
        border: 1.2px solid #b6d4fe;
        box-shadow: 0 0 4px #e5f1ff;
    }
    .option-label {
        font-size: 1em;
        color: #333;
        margin-left: 2px;
        font-weight: 500;
    }
    .input-name {
        padding: 7px 10px;
        font-size: 1em;
        border-radius: 6px;
        border: 1px solid #b6d4fe;
        background: #fff;
        color: #444;
        margin-right: 8px;
    }
    .mic-test-wrap {
        background: #f7faff;
        border: 1px solid #b6d4fe;
        display: flex;
        flex-direction: column;
        align-items: center;       /* ← 버튼 등 전체를 가운데 정렬 */
        border-radius: 8px;
        padding: 12px 18px 8px 18px;
        margin: 13px 0 13px 0;
        gap: 7px;
    }
    .mic-test-btn {
        background: #2176ff;
        color: #fff;
        border-radius: 8px;
        border: none;
        padding: 5px 13px;
        font-size: 1em;
        cursor: pointer;
        margin-right: 13px;
    }
    .mic-test-btn:hover {
        background: #1455ad;
    }
    .mic-ok {
        color: #1eae00;
        font-weight: bold;
        margin-left: 8px;
    }
    .mic-test-result {
        color: #144c6d;
        margin-top: 6px;
        font-size: 0.98em;
        text-align: center;
        width: 100%;
    }
    .answer-stt-result {
        margin-left:10px; 
        color:#2176ff; 
        font-weight:500; 
        font-size:0.97em;
        text-align: center;
        width: 100%;
    }
    .record-row {
        margin: 8px 0 0 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .q-row-between {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 10px;
    }
    .option-numbers-inline {
        display: flex;
        gap: 24px;
    }
    .q-num {
        font-size: 1.18em;
        color: #2176ff;
        font-weight: bold;
        margin-right: 8px;
    }
    .q-text {
        font-size: 1.13em;
        font-weight: 500;
        color: #222;
    }
</style>
