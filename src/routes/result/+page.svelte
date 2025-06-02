<script>
  const options = ["1. 전혀 아니다", "2. 약간 그렇다", "3. 그렇다", "4. 자주 그렇다"];
  let name = "", gender = "", age = "", region = "", answers = [];

  // 로컬에서 복원
  if (typeof window !== "undefined") {
    const saved = localStorage.getItem('surveyResult');
    if (saved) {
      try {
        const data = JSON.parse(saved);
        name = data.name || "";
        gender = data.gender || "";
        age = data.age || "";
        region = data.region || "";
        answers = data.answers || [];
      } catch {}
    }
  }

  // 총점/총평
  let totalScore = 0, summary = "";
  if (answers && answers.length > 0) {
    totalScore = answers.reduce((sum, a) => sum + (parseInt(a) || 0), 0);
    if (totalScore <= 13)      summary = '주의력 문제는 거의 없는 것으로 보입니다.';
    else if (totalScore <= 20) summary = '약간의 주의력 문제가 있을 수 있습니다.';
    else if (totalScore <= 26) summary = '주의력 문제 가능성이 중간 정도로 보입니다.';
    else                      summary = '높은 수준의 주의력 문제 가능성이 있습니다.';
  }

  function downloadCSV() {
    const header = "ID,날짜시간,이름,성별,연령대,거주지역,응답,총점,총평";
    const row = makeCSVRow();
    const csv = header + "\n" + row;
    const BOM = "\uFEFF";
    const blob = new Blob([BOM + csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `설문결과.csv`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
  }

  function makeCSVRow() {
    const id = 0;
    const datetime = new Date().toLocaleString("ko-KR", { hour12: false });
    const row = [
      id,
      `"${datetime}"`,
      `"${name}"`,
      `"${gender}"`,
      `"${age}"`,
      `"${region}"`,
      ...answers.map(a => options[parseInt(a) - 1] || (a || "")),
      `"${totalScore}"`,
      `"${summary}"`
    ];
    return row.join(',');
  }
</script>

<main>
  <div class="survey-header">
    <h1>설문 결과</h1>
    <p class="notice">입력된 정보 및 각 항목에 대한 응답 결과입니다.</p>
  </div>

  {#if !name}
    <div style="color:red; text-align:center; margin:40px 0;">
      설문 데이터가 없습니다. <br> 설문을 먼저 완료해 주세요.
    </div>

  {:else}
    <div class="survey-info">
      <div>👤 이름: <b>{name}</b></div>
      <div>⚥ 성별: <b>{gender}</b></div>
      <div>🎂 연령대: <b>{age}</b></div>
      <div>🏠 거주지역: <b>{region}</b></div>
    </div>

    <div class="questions-wrap">
      {#each answers as a, i}
        <div class="question-block">
          <div class="q-text">
            문항 {i + 1} 응답: 
            <span class="answer">
              {options[parseInt(a) - 1] || (a || "미응답")}
            </span>
          </div>
        </div>
      {/each}
    </div>

    <div class="score-summary">
      <div>📊 총점: <b>{totalScore}점</b></div>
      <div>📝 총평: <b>{summary}</b></div>
    </div>

    <div style="text-align:center; margin-top: 30px;">
      <button class="tts-btn" on:click={downloadCSV}>CSV 다운로드</button>
    </div>
  {/if}
</main>

<style>
  main {
    font-family: 'Pretendard', 'Noto Sans KR', sans-serif;
    max-width: 850px;
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
    background: #f7faff;
    border: 1px solid #b6d4fe;
    border-radius: 8px;
    padding: 14px 20px;
    margin-bottom: 24px;
    display: flex;
    flex-wrap: wrap;
    gap: 20px;
    font-size: 1.05em;
    color: #333;
  }
  .questions-wrap {
    margin-top: 15px;
  }
  .question-block {
    background: #fff;
    border-radius: 10px;
    box-shadow: 0 1px 6px #dde;
    margin-bottom: 18px;
    padding: 14px 20px;
  }
  .q-text {
    font-size: 1.1em;
    color: #222;
  }
  .answer {
    color: #2176ff;
    font-weight: bold;
    margin-left: 6px;
  }
  .score-summary {
    background: #e9f5ff;
    padding: 16px 20px;
    margin-top: 25px;
    border-radius: 10px;
    box-shadow: 0 1px 6px #cce;
    font-size: 1.1em;
    color: #444;
  }
  .tts-btn {
    padding: 7px 18px;
    background: #2176ff;
    color: #fff;
    font-size: 1em;
    border: none;
    border-radius: 16px;
    cursor: pointer;
    transition: background 0.2s ease;
  }
  .tts-btn:hover {
    background: #1455ad;
  }
</style>
