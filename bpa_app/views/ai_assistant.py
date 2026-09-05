"""Natural language AI Assistant — context-aware bioprocess Q&A."""
import streamlit as st
import json

def _build_context() -> str:
    """Build a concise context string from current session state."""
    parts = []
    parts.append(f"Run: {st.session_state.get('run_name','(unnamed)')}")
    parts.append(f"Mode: {st.session_state.get('run_mode','Batch')}")
    parts.append(f"Substrates: {', '.join(st.session_state.get('substrates', ['Glucose']))}")
    parts.append(f"Products: {', '.join(st.session_state.get('products', ['Product']))}")

    # Kinetics
    mu = st.session_state.get("mu")
    td = st.session_state.get("doubling_time_min") or (round(0.693/mu*60,1) if mu else None)
    if mu:    parts.append(f"μ = {mu:.3f} h⁻¹")
    if td:    parts.append(f"Doubling time = {td:.0f} min")
    titer = st.session_state.get("titer")
    sty   = st.session_state.get("sty")
    if titer: parts.append(f"Titer = {titer:.3f} g/L")
    if sty:   parts.append(f"STY = {sty:.4f} g/L/h")
    yps = st.session_state.get("yps"); yxs = st.session_state.get("yxs")
    if yps:   parts.append(f"Yps = {yps:.4f} g/g")
    if yxs:   parts.append(f"Yxs = {yxs:.4f} g/g")
    cl = st.session_state.get("c_closure")
    rq = st.session_state.get("rq")
    if cl:    parts.append(f"C-balance closure = {cl:.1f}%")
    if rq:    parts.append(f"RQ = {rq:.3f}")

    # Mass balance
    mb = st.session_state.get("mb_result")
    if mb:
        parts.append(f"C in = {mb.get('C_in',0):.4f} g C/L")
        parts.append(f"C out = {mb.get('C_out',0):.4f} g C/L")
        if mb.get("yields"):
            y = mb["yields"]
            parts.append(f"YpsMax (theoretical) = {y.get('YpsMax',0):.4f}")
            parts.append(f"C efficiency = {y.get('Ceff',0):.1f}%")

    # Anomalies
    flags = st.session_state.get("anomaly_flags", [])
    if flags:
        parts.append(f"Anomaly flags: " + "; ".join(
            f"{f['param']} at t={f.get('time','?')}h - {f['msg']}" for f in flags[:3]))
    else:
        parts.append("No anomalies detected.")

    # Golden batch
    gb = st.session_state.get("golden_batch")
    if gb:
        parts.append(f"Golden batch ({gb.get('name','')}) titer = {gb.get('titer','—')} g/L, μ = {gb.get('mu','—')} h⁻¹")

    # Digital twin params
    dt = st.session_state.get("dt_params")
    if dt and dt.get("mu_max"):
        parts.append(f"Digital twin: μ_max={dt['mu_max']:.3f}, Ks={dt['Ks']:.4f}, Yxs={dt['Yxs']:.4f}")

    # Active strain
    strain = st.session_state.get("active_strain")
    if strain:
        parts.append(f"Active strain: {strain.get('name','—')} ({strain.get('organism','—')}), {len(strain.get('passages',[]))} passages")

    return "\n".join(parts)


SYSTEM_PROMPT = """You are an expert bioprocess engineer and fermentation scientist assistant embedded in a bioprocess analysis platform.

You have access to the scientist's current run data and computed parameters (provided below). Use this context to give specific, actionable answers.

Your expertise covers:
- Fermentation modes: batch, fed-batch, continuous/chemostat
- Growth kinetics: Monod kinetics, μ, doubling time, lag phase, Luedeking-Piret productivity
- Mass balances: carbon, hydrogen, oxygen, nitrogen, degree of reduction, RQ, yield coefficients
- Scale-up: kLa, P/V, mixing time, van't Riet correlation, Nienow mixing, tip speed criteria
- Strain biology: E. coli, S. cerevisiae, K. phaffii, C. glutamicum, clostridia, fungi
- Products: isoprenoids, organic acids, alcohols, amino acids, proteins, cannabinoids
- Contamination and anomaly detection
- Assay methods: HPLC, GC-MS, enzymatic assays
- Golden batch analysis and process optimisation

When referring to companies or technology providers, avoid naming specific companies. Use generic terms like "commercial platform", "industrial biotech", "established process" etc.

Always be concise. For calculations, show your working. For process problems, give ranked hypotheses. Never hallucinate data values — if uncertain, say so.

Current run context:
{context}"""

SUGGESTED = [
    "Why is my carbon balance not closing?",
    "What does my RQ tell me about the metabolic state?",
    "How do I reduce acetate overflow?",
    "My titer is lower than the golden batch — what should I check?",
    "What feeding strategy would improve Yps?",
    "Explain the Luedeking-Piret parameters for my run",
    "What are the main scale-up risks from 1L to 100L?",
    "How do I interpret a sudden OD drop?",
    "Is my μ consistent with the literature for this organism?",
    "What's causing my DO to crash?",
]


def _call_api(messages: list, context: str) -> str:
    """Call Anthropic API with run context in system prompt."""
    try:
        import anthropic
        client = anthropic.Anthropic()
        system = SYSTEM_PROMPT.format(context=context)
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
            system=system,
            messages=messages,
        )
        return response.content[0].text
    except ImportError:
        return "anthropic package not installed. Run: pip install anthropic"
    except Exception as e:
        return f"API error: {str(e)}\n\nTip: Set your ANTHROPIC_API_KEY environment variable."


def render():
    st.title("💬 AI Assistant")
    st.caption("Context-aware bioprocess Q&A — your run data is automatically included")

    context = _build_context()

    # ── Context summary ───────────────────────────────────────────────────────
    with st.expander("📋 Current run context sent to AI", expanded=False):
        st.code(context, language="text")
        if st.session_state.run_data is None:
            st.warning("No run loaded — AI will answer general questions only. Load data in **Data Import** for context-aware answers.")

    # ── Suggested questions ───────────────────────────────────────────────────
    st.subheader("Suggested questions")
    cols = st.columns(2)
    for i, q in enumerate(SUGGESTED):
        if cols[i % 2].button(q, key=f"sugg_{i}", use_container_width=True):
            st.session_state.chat_history.append({"role": "user", "content": q})
            with st.spinner("Thinking…"):
                reply = _call_api(st.session_state.chat_history, context)
            st.session_state.chat_history.append({"role": "assistant", "content": reply})
            st.rerun()

    st.divider()

    # ── Chat history ──────────────────────────────────────────────────────────
    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    # ── Input ─────────────────────────────────────────────────────────────────
    prompt = st.chat_input("Ask anything about your fermentation run…")
    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        with st.chat_message("assistant"):
            with st.spinner(""):
                reply = _call_api(st.session_state.chat_history, context)
            st.markdown(reply)
        st.session_state.chat_history.append({"role": "assistant", "content": reply})

    # ── Controls ──────────────────────────────────────────────────────────────
    if st.session_state.chat_history:
        if st.button("🗑 Clear conversation"):
            st.session_state.chat_history = []
            st.rerun()
