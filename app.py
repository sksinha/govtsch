"""
NMC-Aware Medical & Health Scholarship Portal (MVP)
----------------------------------------------------
Narrow, deliberately: foreign scholarships open to medicine/public
health/nursing for Indian students, PLUS the one piece of information
generic scholarship sites don't carry -- approximate historical
FMGE/NExT pass rates by source country, so a scholarship offer can be
weighed against the real, post-return licensing risk.

Run with: streamlit run app.py
"""

import pandas as pd
import plotly.express as px
import streamlit as st

from data_store import load_country_outcomes, load_scholarships

st.set_page_config(
    page_title="Medical & Health Scholarships Abroad",
    page_icon="🩺",
    layout="wide",
)

st.title("🩺 Foreign Medical & Health Scholarship Portal")
st.caption(
    "Scholarships open to medicine, public health, and nursing for Indian "
    "students — cross-checked against real FMGE/NExT return-to-India outcomes."
)

st.info(
    "⚠️ **Universal rule, not country-specific**: since the 2002 Screening "
    "Test Regulations, every Indian citizen / OCI pursuing a primary "
    "medical qualification abroad must hold an **NMC Eligibility "
    "Certificate obtained before enrolling**, and must clear **FMGE/NExT** "
    "after returning to practice in India — regardless of country or "
    "university. No country is blanket 'NMC recognized'; the pass-rate "
    "table below is the closest real signal of how graduates from each "
    "country actually fare.",
    icon="⚠️",
)

tab1, tab2 = st.tabs(["🎓 Scholarships", "📊 Country FMGE/NExT outcomes"])

# ----------------------------------------------------------------------
# Tab 1: Scholarships
# ----------------------------------------------------------------------
with tab1:
    df = load_scholarships()

    c1, c2 = st.columns(2)
    countries = ["All"] + sorted(df["country"].unique().tolist())
    levels = ["All"] + sorted(df["degree_level"].unique().tolist())
    sel_country = c1.selectbox("Country", countries)
    sel_level = c2.selectbox("Degree level", levels)

    filtered = df.copy()
    if sel_country != "All":
        filtered = filtered[filtered["country"] == sel_country]
    if sel_level != "All":
        filtered = filtered[filtered["degree_level"] == sel_level]

    k1, k2 = st.columns(2)
    k1.metric("Scholarships listed", len(filtered))
    k2.metric("Countries covered", filtered["country"].nunique())

    st.subheader("Funding type breakdown")
    fc = filtered["funding_type"].value_counts().reset_index()
    fc.columns = ["funding_type", "count"]
    if not fc.empty:
        fig = px.bar(fc, x="funding_type", y="count", color="funding_type")
        fig.update_layout(showlegend=False, xaxis_title="", yaxis_title="Scholarships")
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Listings")
    table = filtered.rename(columns={
        "name": "Scholarship",
        "country": "Country",
        "health_fields_eligible": "Health fields eligible",
        "degree_level": "Degree Level",
        "grade_requirement": "Grade Requirement",
        "funding_type": "Funding Type",
        "work_experience_required": "Work Experience Needed",
        "url": "Source",
        "notes": "Notes",
        "last_verified": "Last Verified",
    })
    st.dataframe(
        table,
        use_container_width=True,
        height=420,
        hide_index=True,
        column_config={
            "Source": st.column_config.LinkColumn("Source", display_text="Visit official site ↗"),
        },
    )
    st.download_button(
        "⬇️ Download as CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="medical_scholarships.csv",
        mime="text/csv",
    )
    st.caption(
        "Every field lists what the source explicitly states. Where a "
        "scholarship is research-focused rather than a route to clinical "
        "residency (e.g. Gates Cambridge), that's flagged in Notes."
    )

# ----------------------------------------------------------------------
# Tab 2: Country FMGE/NExT outcomes
# ----------------------------------------------------------------------
with tab2:
    outc = load_country_outcomes()
    outc["mid_pct"] = outc["approx_pass_rate_pct_range"].apply(
        lambda r: sum(map(int, r.split("-"))) / 2 if "-" in str(r) else None
    )

    st.subheader("Approximate FMGE/NExT pass rate by source country")
    plot_df = outc.dropna(subset=["mid_pct"]).sort_values("mid_pct", ascending=False)
    fig2 = px.bar(
        plot_df, x="country", y="mid_pct",
        hover_data=["approx_pass_rate_pct_range", "reference_period"],
    )
    fig2.update_layout(xaxis_title="", yaxis_title="Approx. pass rate % (midpoint of range)")
    st.plotly_chart(fig2, use_container_width=True)

    st.dataframe(
        outc.drop(columns=["mid_pct"]).rename(columns={
            "country": "Country",
            "approx_pass_rate_pct_range": "Approx. Pass Rate %",
            "reference_period": "Reference Period",
            "data_confidence": "Data Confidence",
            "notes": "Notes",
        }),
        use_container_width=True,
        height=420,
        hide_index=True,
    )

    st.warning(
        "These figures are **aggregated from third-party education-"
        "consultancy reporting on NBE results**, not pulled directly "
        "from an official NBE dataset — sources disagree by a few "
        "points session to session. Treat this as a directional signal "
        "to investigate further, not a guarantee. Always verify the "
        "latest official result at **natboard.edu.in** before deciding "
        "on a country or university.",
        icon="📌",
    )

st.divider()
st.caption(
    "This is a narrow, curated MVP — not a comprehensive scholarship "
    "database. It exists to combine two things that are usually siloed: "
    "funding options and real post-return licensing outcomes."
)
