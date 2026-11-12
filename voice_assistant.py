import streamlit as st
import streamlit.components.v1 as components
from text_assistant import get_text_response

# Optional server-side speech recognition imports
try:
    import speech_recognition as sr
    from streamlit_mic_recorder import mic_recorder
    HAS_SERVER_SPEECH = True
except ImportError:
    HAS_SERVER_SPEECH = False


def _render_web_speech_widget(language: str):
    """
    Renders an in-browser Web Speech Recognition & SpeechSynthesis (TTS) widget.
    Zero local audio driver or PyAudio issues; directly leverages Google Speech API in Chrome/Edge.
    """
    lang_code = "te-IN" if language == "Telugu" else "en-IN"
    lang_name = "Telugu (తెలుగు)" if language == "Telugu" else "Indian English"

    html_code = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                margin: 0;
                padding: 10px;
                background: #f1f8e9;
                border-radius: 12px;
                border: 1.5px solid #a5d6a7;
            }}
            .speech-box {{
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 12px;
            }}
            .mic-btn {{
                background: #2e7d32;
                color: white;
                border: none;
                border-radius: 50%;
                width: 72px;
                height: 72px;
                font-size: 32px;
                cursor: pointer;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: all 0.3s ease;
                box-shadow: 0 4px 12px rgba(46, 125, 50, 0.25);
            }}
            .mic-btn:hover {{
                background: #1b5e20;
                transform: scale(1.05);
            }}
            .mic-btn.listening {{
                background: #d32f2f;
                animation: pulse 1.2s infinite;
                box-shadow: 0 0 0 10px rgba(211, 47, 47, 0.25);
            }}
            @keyframes pulse {{
                0% {{ transform: scale(1); }}
                50% {{ transform: scale(1.1); }}
                100% {{ transform: scale(1); }}
            }}
            .status-text {{
                font-weight: 600;
                font-size: 0.95rem;
                color: #2e7d32;
                text-align: center;
            }}
            .transcript-box {{
                background: white;
                border: 1px solid #c8e6c9;
                border-radius: 8px;
                padding: 10px 14px;
                width: 90%;
                min-height: 40px;
                font-size: 0.95rem;
                color: #333;
                text-align: center;
            }}
            .hint {{
                font-size: 0.8rem;
                color: #616161;
            }}
        </style>
    </head>
    <body>
        <div class="speech-box">
            <button id="mic-button" class="mic-btn" onclick="toggleRecognition()" title="Click to Speak">
                🎙️
            </button>
            <div id="status" class="status-text">Click microphone to speak in {lang_name}</div>
            <div id="transcript" class="transcript-box">Your speech will appear here...</div>
            <div class="hint">Microphone directly connects via browser Google Speech Recognition</div>
        </div>

        <script>
            let recognition = null;
            let isListening = false;
            const micBtn = document.getElementById("mic-button");
            const statusEl = document.getElementById("status");
            const transcriptEl = document.getElementById("transcript");

            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;

            if (SpeechRecognition) {{
                recognition = new SpeechRecognition();
                recognition.continuous = false;
                recognition.interimResults = true;
                recognition.lang = "{lang_code}";

                recognition.onstart = function() {{
                    isListening = true;
                    micBtn.classList.add("listening");
                    micBtn.innerText = "⏹️";
                    statusEl.innerText = "🔴 Listening... Please speak your question now!";
                    statusEl.style.color = "#d32f2f";
                }};

                recognition.onresult = function(event) {{
                    let interim = "";
                    let final = "";
                    for (let i = event.resultIndex; i < event.results.length; ++i) {{
                        if (event.results[i].isFinal) {{
                            final += event.results[i][0].transcript;
                        }} else {{
                            interim += event.results[i][0].transcript;
                        }}
                    }}
                    transcriptEl.innerText = final || interim;
                    if (final) {{
                        // Send text to parent Streamlit
                        window.parent.postMessage({{
                            type: "streamlit:setComponentValue",
                            value: final
                        }}, "*");
                    }}
                }};

                recognition.onerror = function(event) {{
                    console.warn("Speech error:", event.error);
                    statusEl.innerText = "Notice: " + event.error + ". (You can also type or use quick buttons)";
                    statusEl.style.color = "#b71c1c";
                    resetMic();
                }};

                recognition.onend = function() {{
                    resetMic();
                }};
            }} else {{
                statusEl.innerText = "Browser Web Speech API not supported. Please use Quick Buttons or Chrome/Edge.";
                micBtn.disabled = true;
                micBtn.style.background = "#ccc";
            }}

            function toggleRecognition() {{
                if (!recognition) return;
                if (!isListening) {{
                    try {{
                        recognition.start();
                    }} catch (e) {{
                        console.error(e);
                    }}
                }} else {{
                    recognition.stop();
                    resetMic();
                }}
            }}

            function resetMic() {{
                isListening = false;
                micBtn.classList.remove("listening");
                micBtn.innerText = "🎙️";
                statusEl.innerText = "Click microphone to speak again in {lang_name}";
                statusEl.style.color = "#2e7d32";
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_code, height=210)


def _render_tts_player(text_to_speak: str, language: str):
    """
    Generates browser Text-to-Speech audio so the assistant literally speaks out loud to the farmer.
    """
    lang_code = "te-IN" if language == "Telugu" else "en-IN"
    # Clean text of markdown asterisks and emojis for smooth TTS reading
    clean_text = text_to_speak.replace("*", "").replace("#", "").replace("•", "").replace("`", "")
    # Escape quotes for JS
    safe_text = clean_text.replace("\n", " ").replace('"', '\\"').replace("'", "\\'")

    tts_html = f"""
    <div style="background: #ffffff; border: 1.5px solid #a5d6a7; border-radius: 10px; padding: 12px 16px; margin: 12px 0; display: flex; align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 8px;">
            <span style="font-size: 1.4rem;">🔊</span>
            <div>
                <b style="color: #1b5e20; font-size: 0.95rem;">Voice Audio Response (సమాధానం వినండి)</b>
                <div style="font-size: 0.8rem; color: #555;">Click Play to hear speech in {language}</div>
            </div>
        </div>
        <div style="display: flex; gap: 8px;">
            <button id="tts-play-btn" onclick="playSpeech()" style="background: #2e7d32; color: white; border: none; border-radius: 6px; padding: 8px 16px; font-weight: bold; cursor: pointer; font-size: 0.9rem;">
                ▶️ Play Voice
            </button>
            <button onclick="stopSpeech()" style="background: #e0e0e0; color: #333; border: none; border-radius: 6px; padding: 8px 14px; font-weight: bold; cursor: pointer; font-size: 0.9rem;">
                ⏹️ Stop
            </button>
        </div>
    </div>

    <script>
        let synth = window.speechSynthesis;
        let currentUtterance = null;

        function playSpeech() {{
            if (!synth) return;
            synth.cancel();

            const text = "{safe_text}";
            currentUtterance = new SpeechSynthesisUtterance(text);
            currentUtterance.lang = "{lang_code}";
            currentUtterance.rate = 0.95; // Slightly slower for clarity
            currentUtterance.pitch = 1.0;

            const btn = document.getElementById("tts-play-btn");
            btn.innerText = "🔊 Speaking...";
            btn.style.background = "#1b5e20";

            currentUtterance.onend = function() {{
                btn.innerText = "▶️ Play Voice";
                btn.style.background = "#2e7d32";
            }};

            currentUtterance.onerror = function() {{
                btn.innerText = "▶️ Play Voice";
                btn.style.background = "#2e7d32";
            }};

            synth.speak(currentUtterance);
        }}

        function stopSpeech() {{
            if (synth) {{
                synth.cancel();
                const btn = document.getElementById("tts-play-btn");
                if (btn) {{
                    btn.innerText = "▶️ Play Voice";
                    btn.style.background = "#2e7d32";
                }}
            }}
        }}
    </script>
    """
    components.html(tts_html, height=85)


def render_voice_assistant():
    """
    Main entry point for AgriMarket Multilingual Voice Assistant.
    Supports Telugu, English, and Romanized Tanglish speech and audio answers.
    """
    st.subheader("🎤 AgriMarket Intelligent Voice Assistant")
    st.write(
        "Ask any question about APMC Mandi prices, crop diseases, fertilizers, high-profit crops, or government subsidies. "
        "Speak in **Telugu (తెలుగు)** or **English**, or click any quick topic prompt."
    )

    if "voice_history" not in st.session_state:
        st.session_state.voice_history = []

    c_lang, c_mode = st.columns([1, 2])
    with c_lang:
        language = st.selectbox(
            "🗣️ Speech Language",
            ["Telugu", "English"],
            key="voice_lang_select"
        )
    with c_mode:
        input_mode = st.radio(
            "🎙️ Voice Input Engine",
            ["Browser Web Speech API (Fast & Chrome/Edge Native)", "WAV Audio Recorder (Server Google STT)"],
            horizontal=True,
            key="voice_engine_mode"
        )

    # ----------------------------------------------------
    # VOICE INPUT SECTION
    # ----------------------------------------------------
    query_to_process = None

    if "Browser Web Speech" in input_mode:
        _render_web_speech_widget(language)
        # Direct text input fallback / speech paste
        manual_speech_text = st.text_input(
            "Type or paste question from microphone (లేదా ఇక్కడ టైప్ చేయండి):",
            placeholder="ఉదాహరణకు: టమాటా మార్కెట్ ధర ఎంత? లేదా vari ki ye eruvu veyali?",
            key="manual_speech_input"
        )
        if st.button("🔍 Get Agro-AI Response for Question", type="primary", use_container_width=True):
            if manual_speech_text.strip():
                query_to_process = manual_speech_text.strip()
            else:
                st.warning("Please enter or speak a question first.")

    else:
        # Server-side mic recorder
        if HAS_SERVER_SPEECH:
            st.write("Click below to record your voice:")
            audio = mic_recorder(
                start_prompt="🎙️ Start Speaking (మాట్లాడండి)",
                stop_prompt="⏹️ Stop Recording (పూర్తయింది)",
                key="farmer_voice_recorder",
                format="wav"
            )

            if audio and audio.get("bytes"):
                recognizer = sr.Recognizer()
                try:
                    with st.spinner("Processing speech recognition..."):
                        recorded_audio = sr.AudioData(
                            audio["bytes"],
                            audio["sample_rate"],
                            audio["sample_width"]
                        )
                        lang_code = "te-IN" if language == "Telugu" else "en-IN"
                        recognized_text = recognizer.recognize_google(
                            recorded_audio,
                            language=lang_code
                        )
                        query_to_process = recognized_text
                        st.success(f"✅ Speech Recognized: **{recognized_text}**")
                except sr.UnknownValueError:
                    st.warning("Could not clearly understand the audio. Please speak clearly into the microphone or use the quick buttons.")
                except sr.RequestError as e:
                    st.error(f"Speech Recognition service error: {e}")
                except Exception as e:
                    st.error(f"Voice processing error: {e}")
        else:
            st.info("Browser Web Speech API is active above for instant speech recognition.")

    st.divider()

    # ----------------------------------------------------
    # QUICK ONE-CLICK VOICE PROMPT CARDS (10 TOPICS)
    # ----------------------------------------------------
    st.markdown("#### 💡 Quick Voice Prompts (ఒకే క్లిక్ తో అడగండి)")

    if language == "Telugu":
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("🍅 టమాటా మార్కెట్ ధర", use_container_width=True):
                query_to_process = "టమాటా మార్కెట్ ధర ఎంత?"
            if st.button("💰 ఏ పంటతో లాభం?", use_container_width=True):
                query_to_process = "ఏ పంట వేస్తే ఎక్కువ లాభం వస్తుంది?"
        with col2:
            if st.button("🌾 వరి ఎరువుల మోతాదు", use_container_width=True):
                query_to_process = "వరి పంటలో ఎరువుల మోతాదు ఏమిటి?"
            if st.button("🏛️ పీఎం కిసాన్ పథకం", use_container_width=True):
                query_to_process = "పీఎం కిసాన్ పథకం వివరాలు ఏమిటి?"
        with col3:
            if st.button("🌶️ మిర్చి తెగుళ్ల నివారణ", use_container_width=True):
                query_to_process = "మిర్చిలో నల్ల తామర పురుగుల నివారణ"
            if st.button("💧 డ్రిప్ 90% సబ్సిడీ", use_container_width=True):
                query_to_process = "డ్రిప్ ఇరిగేషన్ సబ్సిడీ ఎలా పొందాలి?"
        with col4:
            if st.button("🌿 కలుపు మందులు ఏవి?", use_container_width=True):
                query_to_process = "పంటలలో కలుపు నివారణ మందులు ఏవి?"
            if st.button("🧪 భూసార పరీక్ష ఎలా?", use_container_width=True):
                query_to_process = "భూసార పరీక్ష ఎలా చేయించాలి?"
        with col5:
            if st.button("🌽 మొక్కజొన్న కత్తెర పురుగు", use_container_width=True):
                query_to_process = "మొక్కజొన్నలో కత్తెర పురుగు నివారణ"
            if st.button("🧅 ఉల్లి ధర & నిల్వ", use_container_width=True):
                query_to_process = "ఉల్లి మార్కెట్ ధర మరియు నిల్వ పద్ధతులు"
    else:
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            if st.button("🍅 Tomato Mandi Price", use_container_width=True):
                query_to_process = "What is the live mandi price for tomato?"
            if st.button("💰 High Profit Crops", use_container_width=True):
                query_to_process = "Which crop gives maximum profit per acre?"
        with col2:
            if st.button("🌾 Rice Fertilizer Dose", use_container_width=True):
                query_to_process = "What is the recommended fertilizer dose for paddy?"
            if st.button("🏛️ PM-Kisan Scheme", use_container_width=True):
                query_to_process = "How to apply for PM Kisan and Rythu Bharosa?"
        with col3:
            if st.button("🌶️ Chilli Pest Control", use_container_width=True):
                query_to_process = "How to control black thrips and mites in chilli?"
            if st.button("💧 90% Drip Subsidy", use_container_width=True):
                query_to_process = "How to get drip irrigation subsidy?"
        with col4:
            if st.button("🌿 Weed Management", use_container_width=True):
                query_to_process = "What are the best herbicides and weedicides for crops?"
            if st.button("🧪 Soil Health Card", use_container_width=True):
                query_to_process = "How to do soil testing for farming?"
        with col5:
            if st.button("🌽 Maize Armyworm", use_container_width=True):
                query_to_process = "How to treat Fall Armyworm in maize?"
            if st.button("🧅 Onion Price & Storage", use_container_width=True):
                query_to_process = "Onion market price and storage guidelines"

    # ----------------------------------------------------
    # PROCESS QUERY & RENDER RESPONSE WITH VOICE TTS
    # ----------------------------------------------------
    if query_to_process:
        st.markdown(f"### 🗣️ Question: *\"{query_to_process}\"*")

        with st.spinner("🤖 Agro-Intelligence engine analyzing question..."):
            answer = get_text_response(query_to_process, language)

        st.markdown("### 🤖 Assistant Response:")
        st.info(answer)

        # Voice Text-to-Speech Player
        _render_tts_player(answer, language)

        # Save to session history
        st.session_state.voice_history.insert(0, {
            "query": query_to_process,
            "answer": answer,
            "lang": language
        })

    # Recent Voice Questions History
    if st.session_state.voice_history:
        with st.expander("📜 Recent Voice Interactions History", expanded=False):
            for idx, item in enumerate(st.session_state.voice_history[:5]):
                st.markdown(f"**Q{idx+1} ({item['lang']}):** {item['query']}")
                st.caption(f"A: {item['answer'][:160]}...")
                st.divider()
