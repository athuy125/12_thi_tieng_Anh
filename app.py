import re
import streamlit as st
import unicodedata
st.set_page_config(page_title="Luyện 12 thì Tiếng Anh", page_icon="📘", layout="centered")


def norm(s: str) -> str:
 
    s = s.lower().strip()
    s = unicodedata.normalize("NFC", s)
    s = re.sub(r"[^\w\s]", "", s)  
    return s

def any_match(text: str, patterns):
    t = norm(text)
    for p in patterns:
        if re.search(p, t):
            return True
    return False


IRREG = [
    ("go", "went", "gone"), ("eat", "ate", "eaten"), ("see", "saw", "seen"),
    ("write", "wrote", "written"), ("begin", "began", "begun"), ("come", "came", "come"),
    ("drink", "drank", "drunk"), ("sing", "sang", "sung"), ("swim", "swam", "swum"),
    ("run", "ran", "run"), ("speak", "spoke", "spoken"), ("take", "took", "taken"),
    ("give", "gave", "given"), ("drive", "drove", "driven"), ("break", "broke", "broken"),
    ("choose", "chose", "chosen"), ("forget", "forgot", "forgotten"), ("freeze", "froze", "frozen"),
    ("ride", "rode", "ridden"), ("fall", "fell", "fallen"), ("grow", "grew", "grown"),
    ("know", "knew", "known"), ("fly", "flew", "flown"), ("blow", "blew", "blown"),
    ("draw", "drew", "drawn"), ("show", "showed", "shown"), ("throw", "threw", "thrown"),
    ("wear", "wore", "worn"), ("tear", "tore", "torn"), ("ring", "rang", "rung"),
    ("get", "got", "gotten"), ("have", "had", "had"), ("be", "was/were", "been"),
    ("make", "made", "made"), ("say", "said", "said"), ("sell", "sold", "sold"),
    ("send", "sent", "sent"), ("set", "set", "set"), ("think", "thought", "thought"),
]
V2_SET = set(v2 for _, v2, _ in IRREG)
V3_SET = set(v3 for _, _, v3 in IRREG)


def validate_example(tense_key: str, group: str, form: str, sent: str):
    """
    tense_key: mã thì nội bộ (present_simple, past_continuous, ...)
    group: 'verb' | 'tobe'
    form: 'Khẳng định' | 'Phủ định' | 'Nghi vấn'
    sent: câu ví dụ người dùng nhập
    """
    s = norm(sent)

    # Các regex tiện lợi
    BE_NOW = r"\b(am|is|are)\b"
    BE_PAST = r"\b(was|were)\b"
    DO_NOW = r"\b(do|does)\b"
    DID = r"\b(did)\b"
    HAVE_NOW = r"\b(have|has)\b"
    HAD = r"\b(had)\b"
    WILL = r"\b(will|shall)\b"
    BEEN = r"\bbeen\b"
    V_ING = r"\b\w+ing\b"
    V_ED = r"\b\w+ed\b"
    V3_END = r"\b\w+(ed|en|wn)\b"  # gần đúng
    NEG = r"\b(not|n't)\b"

    # một vài bộ nhận diện nhanh
    def has_any_v2_or_ed():
        return bool(re.search(V_ED, s) or any(w in s.split() for w in V2_SET))

    def has_any_v3():
        return bool(re.search(V3_END, s) or any(w in s.split() for w in V3_SET) or "been" in s)

    # Mỗi thì: đặt các quy tắc "điển hình" (affirm/neg/question)
    ok = False
    hint = ""  

    # ---- HIỆN TẠI ĐƠN
    if tense_key == "present_simple":
        if group == "verb":
            if form == "Khẳng định":
                # Không có will/ have/ has/ had/ was/were/ am/is/are/ did, không V-ing; cho phép động từ V/Vs
                ok = (not any_match(s, [WILL, HAVE_NOW, HAD, BE_PAST, BE_NOW, DID]) and not re.search(V_ING, s))
                hint = "Tránh dùng trợ động từ; dùng V/ V(s/es)."
            elif form == "Phủ định":
                ok = any_match(s, [r"\bdo not\b", r"\bdoes not\b", r"\bdon't\b", r"\bdoesn't\b"])
                hint = "Dùng do/does not + V."
            else:  # Nghi vấn
                ok = re.match(r"^(do|does)\b", s or "") is not None
                hint = "Bắt đầu bằng Do/Does + S + V?"
        else:  # tobe
            if form == "Khẳng định":
                ok = any_match(s, [BE_NOW])
                hint = "Dùng am/is/are."
            elif form == "Phủ định":
                ok = any_match(s, [r"\bam not\b", r"\bis not\b", r"\bare not\b", r"\bisn't\b", r"\baren't\b"])
                hint = "Dùng am/is/are + not."
            else:
                ok = re.match(r"^(am|is|are)\b", s or "") is not None
                hint = "Bắt đầu bằng Am/Is/Are + S?"

    # ---- HIỆN TẠI TIẾP DIỄN
    elif tense_key == "present_continuous":
        if form == "Khẳng định":
            ok = any_match(s, [BE_NOW]) and re.search(V_ING, s)
            hint = "am/is/are + V-ing."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bam not\b.*"+V_ING, r"\bis not\b.*"+V_ING, r"\bare not\b.*"+V_ING,
                               r"\bisn't\b.*"+V_ING, r"\baren't\b.*"+V_ING])
            hint = "am/is/are + not + V-ing."
        else:
            ok = re.match(r"^(am|is|are)\b.*\b\w+ing\b", s or "") is not None
            hint = "Bắt đầu bằng Am/Is/Are + S + V-ing?"

    # ---- HIỆN TẠI HOÀN THÀNH
    elif tense_key == "present_perfect":
        if form == "Khẳng định":
            ok = any_match(s, [HAVE_NOW]) and has_any_v3()
            hint = "have/has + V3."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bhave not\b.*"+V3_END, r"\bhas not\b.*"+V3_END, r"\bhaven't\b.*", r"\bhasn't\b.*"]) and has_any_v3()
            hint = "have/has + not + V3."
        else:
            ok = re.match(r"^(have|has)\b.*\b\w+(ed|en|wn)\b", s or "") is not None or \
                 re.match(r"^(have|has)\b.*\b(" + "|".join(map(re.escape, V3_SET)) + r")\b", s or "") is not None
            hint = "Bắt đầu bằng Have/Has + S + V3?"

    # ---- HIỆN TẠI HOÀN THÀNH TIẾP DIỄN
    elif tense_key == "present_perfect_continuous":
        if form == "Khẳng định":
            ok = any_match(s, [HAVE_NOW]) and "been" in s and re.search(V_ING, s)
            hint = "have/has been + V-ing."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bhave not been\b.*"+V_ING, r"\bhas not been\b.*"+V_ING,
                               r"\bhaven't been\b.*"+V_ING, r"\bhasn't been\b.*"+V_ING])
            hint = "have/has + not + been + V-ing."
        else:
            ok = re.match(r"^(have|has)\b.*\bbeen\b.*\b\w+ing\b", s or "") is not None
            hint = "Bắt đầu bằng Have/Has + S + been + V-ing?"

    # ---- QUÁ KHỨ ĐƠN
    elif tense_key == "past_simple":
        if group == "verb":
            if form == "Khẳng định":
                ok = has_any_v2_or_ed()
                hint = "Dùng V2/ Ved."
            elif form == "Phủ định":
                ok = any_match(s, [r"\bdid not\b", r"\bdidn't\b"]) and not has_any_v2_or_ed()
                hint = "did not + V (nguyên mẫu)."
            else:
                ok = re.match(r"^did\b", s or "") is not None
                hint = "Bắt đầu bằng Did + S + V?"
        else:  # to be
            if form == "Khẳng định":
                ok = any_match(s, [BE_PAST])
                hint = "Dùng was/were."
            elif form == "Phủ định":
                ok = any_match(s, [r"\bwas not\b", r"\bwere not\b", r"\bwasn't\b", r"\bweren't\b"])
                hint = "was/were + not."
            else:
                ok = re.match(r"^(was|were)\b", s or "") is not None
                hint = "Bắt đầu bằng Was/Were + S?"

    # ---- QUÁ KHỨ TIẾP DIỄN
    elif tense_key == "past_continuous":
        if form == "Khẳng định":
            ok = any_match(s, [BE_PAST]) and re.search(V_ING, s)
            hint = "was/were + V-ing."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bwas not\b.*"+V_ING, r"\bwere not\b.*"+V_ING, r"\bwasn't\b.*"+V_ING, r"\bweren't\b.*"+V_ING])
            hint = "was/were + not + V-ing."
        else:
            ok = re.match(r"^(was|were)\b.*\b\w+ing\b", s or "") is not None
            hint = "Bắt đầu bằng Was/Were + S + V-ing?"

    # ---- QUÁ KHỨ HOÀN THÀNH
    elif tense_key == "past_perfect":
        if form == "Khẳng định":
            ok = any_match(s, [HAD]) and has_any_v3()
            hint = "had + V3."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bhad not\b.*"+V3_END, r"\bhadn't\b.*"]) and has_any_v3()
            hint = "had not + V3."
        else:
            ok = re.match(r"^had\b.*\b\w+(ed|en|wn)\b", s or "") is not None or re.match(r"^had\b.*\b(" + "|".join(map(re.escape, V3_SET)) + r")\b", s or "") is not None
            hint = "Bắt đầu bằng Had + S + V3?"

    # ---- QUÁ KHỨ HOÀN THÀNH TIẾP DIỄN
    elif tense_key == "past_perfect_continuous":
        if form == "Khẳng định":
            ok = any_match(s, [HAD]) and "been" in s and re.search(V_ING, s)
            hint = "had been + V-ing."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bhad not been\b.*"+V_ING, r"\bhadn't been\b.*"+V_ING])
            hint = "had not been + V-ing."
        else:
            ok = re.match(r"^had\b.*\bbeen\b.*\b\w+ing\b", s or "") is not None
            hint = "Bắt đầu bằng Had + S + been + V-ing?"

    # ---- TƯƠNG LAI ĐƠN
    elif tense_key == "future_simple":
        if form == "Khẳng định":
            ok = any_match(s, [WILL]) and "will have" not in s and "will be" not in s
            hint = "will + V (nguyên mẫu)."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bwill not\b", r"\bwon't\b"])
            hint = "will not + V."
        else:
            ok = re.match(r"^(will|shall)\b", s or "") is not None
            hint = "Bắt đầu bằng Will/Shall + S + V?"

    # ---- TƯƠNG LAI TIẾP DIỄN
    elif tense_key == "future_continuous":
        if form == "Khẳng định":
            ok = "will be" in s and re.search(V_ING, s)
            hint = "will be + V-ing."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bwill not be\b.*"+V_ING, r"\bwon't be\b.*"+V_ING])
            hint = "will not be + V-ing."
        else:
            ok = re.match(r"^(will|shall)\b.*\bbe\b.*\b\w+ing\b", s or "") is not None
            hint = "Bắt đầu bằng Will + S + be + V-ing?"

    # ---- TƯƠNG LAI HOÀN THÀNH
    elif tense_key == "future_perfect":
        if form == "Khẳng định":
            ok = "will have" in s and has_any_v3()
            hint = "will have + V3."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bwill not have\b.*"+V3_END, r"\bwon't have\b.*"+V3_END]) or ("will not have" in s and has_any_v3())
            hint = "will not have + V3."
        else:
            ok = re.match(r"^(will|shall)\b.*\bhave\b.*\b\w+(ed|en|wn)\b", s or "") is not None or \
                 re.match(r"^(will|shall)\b.*\bhave\b.*\b(" + "|".join(map(re.escape, V3_SET)) + r")\b", s or "") is not None
            hint = "Bắt đầu bằng Will + S + have + V3?"

    # ---- TƯƠNG LAI HOÀN THÀNH TIẾP DIỄN
    elif tense_key == "future_perfect_continuous":
        if form == "Khẳng định":
            ok = "will have been" in s and re.search(V_ING, s)
            hint = "will have been + V-ing."
        elif form == "Phủ định":
            ok = any_match(s, [r"\bwill not have been\b.*"+V_ING, r"\bwon't have been\b.*"+V_ING])
            hint = "will not have been + V-ing."
        else:
            ok = re.match(r"^(will|shall)\b.*\bhave been\b.*\b\w+ing\b", s or "") is not None
            hint = "Bắt đầu bằng Will + S + have been + V-ing?"

    return ok, hint

# ==========================
# DỮ LIỆU 12 THÌ (tóm tắt – VN trước, EN trong ngoặc)
# ==========================
TENSES = {
    "Hiện tại đơn (Present Simple)": {
        "key": "present_simple",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + V(s/es)",
                "Phủ định": "S + do/does not + V",
                "Nghi vấn": "Do/Does + S + V ?"
            },
            "Động từ to be (To be)": {
                "Khẳng định": "S + am/is/are",
                "Phủ định": "S + am/is/are + not",
                "Nghi vấn": "Am/Is/Are + S ?"
            },
        },
        "uses": [
            "Diễn tả thói quen, sự thật hiển nhiên (Habits, general truths)",
            "Lịch trình, thời gian biểu (Schedules, timetables)"
        ],
        "signals": ["always", "often", "usually", "sometimes", "every day"]
    },
    "Hiện tại tiếp diễn (Present Continuous)": {
        "key": "present_continuous",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + am/is/are + V-ing",
                "Phủ định": "S + am/is/are + not + V-ing",
                "Nghi vấn": "Am/Is/Are + S + V-ing ?"
            }
        },
        "uses": [
            "Hành động đang xảy ra (Action happening now)",
            "Sự việc tạm thời (Temporary situations)"
        ],
        "signals": ["now", "at the moment", "right now", "currently"]
    },
    "Hiện tại hoàn thành (Present Perfect)": {
        "key": "present_perfect",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + have/has + V3",
                "Phủ định": "S + have/has + not + V3",
                "Nghi vấn": "Have/Has + S + V3 ?"
            }
        },
        "uses": [
            "Kinh nghiệm, kết quả đến hiện tại (Experiences, present results)",
            "Hành động vừa xảy ra/không rõ thời điểm (Recent/unspecified time)"
        ],
        "signals": ["already", "yet", "ever", "never", "just", "so far", "recently", "lately"]
    },
    "Hiện tại hoàn thành tiếp diễn (Present Perfect Continuous)": {
        "key": "present_perfect_continuous",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + have/has + been + V-ing",
                "Phủ định": "S + have/has + not + been + V-ing",
                "Nghi vấn": "Have/Has + S + been + V-ing ?"
            }
        },
        "uses": [
            "Nhấn mạnh độ dài hành động tới hiện tại (Duration up to now)",
            "Hành động vừa dừng lại và còn dấu vết (Recent activity)"
        ],
        "signals": ["for", "since", "all day", "recently", "lately"]
    },
    "Quá khứ đơn (Past Simple)": {
        "key": "past_simple",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + V2/V-ed",
                "Phủ định": "S + did not + V",
                "Nghi vấn": "Did + S + V ?"
            },
            "Động từ to be (To be)": {
                "Khẳng định": "S + was/were",
                "Phủ định": "S + was/were + not",
                "Nghi vấn": "Was/Were + S ?"
            },
        },
        "uses": [
            "Hành động đã kết thúc trong quá khứ (Finished past action)",
            "Chuỗi sự kiện trong quá khứ (sequence)"
        ],
        "signals": ["yesterday", "last night/week/year", "in 2010", "ago"]
    },
    "Quá khứ tiếp diễn (Past Continuous)": {
        "key": "past_continuous",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + was/were + V-ing",
                "Phủ định": "S + was/were + not + V-ing",
                "Nghi vấn": "Was/Were + S + V-ing ?"
            }
        },
        "uses": [
            "Hành động đang diễn ra tại 1 thời điểm quá khứ (action in progress in the past)",
            "Bối cảnh cho hành động khác xen vào (background action)"
        ],
        "signals": ["while", "at 5 pm yesterday", "when + Past Simple"]
    },
    "Quá khứ hoàn thành (Past Perfect)": {
        "key": "past_perfect",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + had + V3",
                "Phủ định": "S + had + not + V3",
                "Nghi vấn": "Had + S + V3 ?"
            }
        },
        "uses": [
            "Hành động xảy ra trước một thời điểm/quá khứ khác (earlier past)",
            "Nhấn mạnh thứ tự sự kiện"
        ],
        "signals": ["before", "after", "by the time", "already"]
    },
    "Quá khứ hoàn thành tiếp diễn (Past Perfect Continuous)": {
        "key": "past_perfect_continuous",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + had + been + V-ing",
                "Phủ định": "S + had + not + been + V-ing",
                "Nghi vấn": "Had + S + been + V-ing ?"
            }
        },
        "uses": [
            "Nhấn mạnh độ dài trước quá khứ (duration before a past point)"
        ],
        "signals": ["for", "since", "until", "before + Past Simple"]
    },
    "Tương lai đơn (Future Simple)": {
        "key": "future_simple",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + will + V",
                "Phủ định": "S + will not (won't) + V",
                "Nghi vấn": "Will + S + V ?"
            }
        },
        "uses": [
            "Quyết định tức thì, dự đoán (instant decisions, predictions)",
            "Lời hứa, đề nghị, yêu cầu"
        ],
        "signals": ["tomorrow", "next week", "soon", "probably"]
    },
    "Tương lai tiếp diễn (Future Continuous)": {
        "key": "future_continuous",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + will be + V-ing",
                "Phủ định": "S + will not be + V-ing",
                "Nghi vấn": "Will + S + be + V-ing ?"
            }
        },
        "uses": [
            "Hành động sẽ đang diễn ra tại thời điểm tương lai (action in progress in the future)"
        ],
        "signals": ["at this time tomorrow", "at 5 pm next Monday"]
    },
    "Tương lai hoàn thành (Future Perfect)": {
        "key": "future_perfect",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + will have + V3",
                "Phủ định": "S + will not have + V3",
                "Nghi vấn": "Will + S + have + V3 ?"
            }
        },
        "uses": [
            "Hoàn thành trước một mốc tương lai (completed before a future time)"
        ],
        "signals": ["by tomorrow", "by next year", "by the time"]
    },
    "Tương lai hoàn thành tiếp diễn (Future Perfect Continuous)": {
        "key": "future_perfect_continuous",
        "summary": {
            "Động từ thường (Verb)": {
                "Khẳng định": "S + will have been + V-ing",
                "Phủ định": "S + will not have been + V-ing",
                "Nghi vấn": "Will + S + have been + V-ing ?"
            }
        },
        "uses": [
            "Nhấn mạnh độ dài tới một mốc tương lai (duration up to a future point)"
        ],
        "signals": ["for", "since", "by the time + future"]
    },
}

# ==========================
# APP UI
# ==========================
st.title("📘 Luyện 12 thì Tiếng Anh")

tense_name = st.selectbox("👉 Chọn thì muốn học:", list(TENSES.keys()))
tense = TENSES[tense_name]
tense_key = tense["key"]

# --------- BẢNG TÓM TẮT (chỉ hiện của thì đã chọn)
with st.expander("📖 Bảng tóm tắt (Summary) – chỉ thì đang chọn", expanded=True):
    for group, formulas in tense["summary"].items():
        st.markdown(f"**{group}:**")
        for form, formula in formulas.items():
            st.write(f"- {form}: {formula}")

st.divider()

# --------- KIỂM TRA CÔNG THỨC (mỗi dòng có nút kiểm tra riêng, không phân biệt hoa/thường)
st.subheader("✍️ Kiểm tra công thức (Formulas)")

for group, formulas in tense["summary"].items():
    st.markdown(f"**{group}**")
    for form, correct in formulas.items():
        key_input = f"formula-{tense_key}-{group}-{form}"
        key_btn = f"btn-formula-{tense_key}-{group}-{form}"
        user_input = st.text_input(f"{form} – nhập công thức (Enter formula):", key=key_input)
        if st.button(f"Kiểm tra {form}", key=key_btn):
            if norm(user_input) == norm(correct):
                st.success("✅ Chính xác!")
            else:
                st.error(f"❌ Sai rồi! Đúng là: {correct}")

st.divider()

# --------- KIỂM TRA CÁCH DÙNG
st.subheader("📌 Cách dùng (Uses)")
for i, use in enumerate(tense["uses"], 1):
    key_use_in = f"use-{tense_key}-{i}"
    key_use_btn = f"btn-use-{tense_key}-{i}"
    user_use = st.text_input(f"Cách dùng {i} (Use {i}):", key=key_use_in)

    if st.button(f"Kiểm tra cách dùng {i}", key=key_use_btn):
        nu, na = norm(user_use), norm(use)

        # ✅ đúng nếu 1 trong 2 chứa nhau
        if nu in na or na in nu:
            st.success("✅ Chính xác!")
        else:
            st.error(f"❌ Sai rồi! Gợi ý: {use}")
st.divider()

# --------- KIỂM TRA DẤU HIỆU NHẬN BIẾT
st.subheader("🔑 Dấu hiệu nhận biết (Signal words)")
for i, sig in enumerate(tense["signals"], 1):
    key_sig_in = f"sig-{tense_key}-{i}"
    key_sig_btn = f"btn-sig-{tense_key}-{i}"
    user_sig = st.text_input(f"Dấu hiệu {i} (Signal {i}):", key=key_sig_in)
    if st.button(f"Kiểm tra dấu hiệu {i}", key=key_sig_btn):
        if norm(user_sig) == norm(sig):
            st.success("✅ Chính xác!")
        else:
            st.error(f"❌ Sai rồi! Đúng là: {sig}")

st.divider()

# --------- KIỂM TRA VÍ DỤ (tự động nhận diện theo thì) ---------
st.subheader("🧪 Kiểm tra ví dụ (Examples)")

for group in tense["summary"].keys():
    # xác định group_key cho validator
    group_key = "tobe" if "to be" in group.lower() else "verb"

    st.markdown(f"**{group}**")
    for form in ["Khẳng định", "Phủ định", "Nghi vấn"]:
        key_ex_in = f"ex-{tense_key}-{group_key}-{form}"
        key_ex_btn = f"btn-ex-{tense_key}-{group_key}-{form}"
        example = st.text_input(f"Ví dụ {form} ({form} example):", key=key_ex_in, placeholder="Nhập câu ví dụ của bạn...")
        if st.button(f"Kiểm tra ví dụ {form}", key=key_ex_btn):
            ok, hint = validate_example(tense_key, group_key, form, example)
            if ok:
                st.success("✅ Có vẻ đúng thì này!")
            else:
                st.error(f"❌ Chưa khớp dấu hiệu thì. Gợi ý: {hint}")

# Gợi ý nhỏ ở cuối
st.info("💡 Lưu ý: Trình kiểm tra ví dụ dùng luật nhận dạng đơn giản (trợ động từ, V-ing/V-ed/V3...). Bạn cứ tập trung đúng **công thức** và **dấu hiệu** là ổn nhé!")
