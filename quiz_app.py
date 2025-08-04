
import streamlit as st
import pandas as pd
import os
from quiz_data import quiz_data

st.title("♻️ 분리배출 퀴즈 게임")

username = st.text_input("당신의 이름을 입력하세요:")

if "score" not in st.session_state:
    st.session_state.score = 0
if "current_q" not in st.session_state:
    st.session_state.current_q = 0

if st.session_state.current_q < len(quiz_data):
    q_idx = st.session_state.current_q
    q = quiz_data[q_idx]

    st.subheader(f"Q{q_idx + 1}. {q['question']}")
    choice = st.radio("선택하세요:", q["options"], key=f"radio_{q_idx}")

    if f"answered_{q_idx}" not in st.session_state:
        st.session_state[f"answered_{q_idx}"] = False
    if f"correct_{q_idx}" not in st.session_state:
        st.session_state[f"correct_{q_idx}"] = None

    if not st.session_state[f"answered_{q_idx}"]:
        if st.button("정답 확인"):
            is_correct = choice == q["answer"]
            st.session_state[f"answered_{q_idx}"] = True
            st.session_state[f"correct_{q_idx}"] = is_correct

            if is_correct:
                st.session_state.score += 1

            log_df = pd.DataFrame([{
                "사용자": username,
                "문제번호": q_idx + 1,
                "선택지": choice,
                "정답여부": "정답" if is_correct else "오답"
            }])
            log_df.to_csv("quiz_logs.csv", mode="a", header=not os.path.exists("quiz_logs.csv"), index=False)
            st.rerun()

    if st.session_state[f"answered_{q_idx}"]:
        if st.session_state[f"correct_{q_idx}"]:
            st.success("정답입니다! 🎉")
        else:
            st.error("틀렸습니다. 😢")
        st.info(f"📝 해설: {q['explanation']}")

        if st.button("다음 문제"):
            st.session_state.current_q += 1
            st.rerun()
else:
    st.success(f"✅ {username}님의 점수는 {st.session_state.score} / {len(quiz_data)} 입니다.")
    df = pd.DataFrame([[username, st.session_state.score]], columns=["이름", "점수"])
    df.to_csv("quiz_scores.csv", mode="a", header=not os.path.exists("quiz_scores.csv"), index=False)

    if st.button("다시 풀기"):
        for i in range(len(quiz_data)):
            st.session_state.pop(f"answered_{i}", None)
            st.session_state.pop(f"correct_{i}", None)
        st.session_state.score = 0
        st.session_state.current_q = 0
        st.rerun()

    st.markdown("---")
    st.subheader("📊 문제별 정답률 분석")
    try:
        logs = pd.read_csv("quiz_logs.csv")
        summary = logs.groupby("문제번호")["정답여부"].value_counts().unstack().fillna(0)
        summary["총시도"] = summary.sum(axis=1)
        summary["정답률(%)"] = (summary.get("정답", 0) / summary["총시도"] * 100).round(1)
        st.dataframe(summary[["총시도", "정답", "오답", "정답률(%)"]])
        st.bar_chart(summary["정답률(%)"])
    except:
        st.warning("분석 기록이 아직 없습니다.")
