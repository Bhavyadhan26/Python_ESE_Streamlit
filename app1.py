import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

st.set_page_config(
    page_title="GATEWAYS-2025 Participation Analysis",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("GATEWAYS-2025 Participation Analysis Dashboard")
st.markdown("This dashboard analyzes participation trends, state-wise presence in India, and participant feedback quality in GATEWAYS 2025")


df = pd.read_csv("FestDataset.csv")

df["Rating"] = pd.to_numeric(df["Rating"], errors="coerce")
df["Amount Paid"] = pd.to_numeric(df["Amount Paid"], errors="coerce")

st.sidebar.title("Filters and Navigation")

states = st.sidebar.multiselect(
    "State",
    options=sorted(df["State"].dropna().unique()),
    default=sorted(df["State"].dropna().unique()),
    help="Select states to include"
)

event_types = st.sidebar.multiselect(
    "Event Type",
    options=sorted(df["Event Type"].dropna().unique()),
    default=sorted(df["Event Type"].dropna().unique()),
    help="Select event types"
)

events = st.sidebar.multiselect(
    "Event Name",
    options=sorted(df["Event Name"].dropna().unique()),
    default=sorted(df["Event Name"].dropna().unique()),
    help="Select events to analyze"
)

colleges = st.sidebar.multiselect(
    "College",
    options=sorted(df["College"].dropna().unique()),
    default=sorted(df["College"].dropna().unique()),
    help="Select colleges to analyze"
)

rating_min, rating_max = st.sidebar.slider(
    "Rating Range",
    min_value=int(df["Rating"].min()),
    max_value=int(df["Rating"].max()),
    value=(int(df["Rating"].min()), int(df["Rating"].max())),
    help="Select rating range"
)

filtered_df = df[
    (df["State"].isin(states)) &
    (df["Event Type"].isin(event_types)) &
    (df["Event Name"].isin(events)) &
    (df["College"].isin(colleges)) &
    (df["Rating"].between(rating_min, rating_max))
].copy()

if filtered_df.empty:
    st.warning("No records found for your selected filters.")
    st.stop()

st.subheader("Fest at a Glance")
col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric(
        label="Unique States",
        value=f"{df['State'].nunique():,}",
        delta=None
    )

with col2:
    st.metric(
        label="Unique Colleges",
        value=f"{df['College'].nunique():,}",
        delta=None
    )

with col3:
    st.metric(
        label="Total Participants",
        value=f"{len(df):,}",
        delta=None
    )

with col4:
    st.metric(
        label="Average Rating",
        value=f"{df['Rating'].mean():.2f}",
        delta=None
    )

with col5:
    st.metric(
        label="Total Revenue Collected",
        value=f"INR {df['Amount Paid'].sum():,.0f}",
        delta=None
    )

st.subheader("Metrics Based on Applied Filters")
col6, col7, col8, col9, col10 = st.columns(5)

with col6:
    st.metric(
        label="Unique States",
        value=f"{filtered_df['State'].nunique():,}",
        delta=None
    )

with col7:
    st.metric(
        label="Unique Colleges",
        value=f"{filtered_df['College'].nunique():,}",
        delta=None
    )

with col8:
    st.metric(
        label="Total Participants",
        value=f"{len(filtered_df):,}",
        delta=None
    )

with col9:
    st.metric(
        label="Average Rating",
        value=f"{filtered_df['Rating'].mean():.2f}",
        delta=None
    )

with col10:
    st.metric(
        label="Total Revenue Collected",
        value=f"INR {filtered_df['Amount Paid'].sum():,.0f}",
        delta=None
    )

st.subheader("Participant Count by Event Type and Rating Group")

rating_bins = [0, 2, 3, 4, 5.1]
rating_labels = ["1-2", "3", "4", "5"]
filtered_df["Rating Group"] = pd.cut(filtered_df["Rating"], bins=rating_bins, labels=rating_labels, right=False)

summary_table = filtered_df.groupby(["Event Type", "Rating Group"], observed=False).size().reset_index(name="Count")
st.dataframe(summary_table, use_container_width=True)

tab1, tab2, tab3, tab4 = st.tabs([
    "Participation Distribution",
    "Trends and India Map",
    "Feedback and Ratings",
    "Student Info"
])

with tab1:
    st.subheader("Event-wise Participation")

    with st.expander("Chart Details", expanded=True):
        event_count = filtered_df["Event Name"].value_counts().reset_index()
        event_count.columns = ["Event Name", "Participant Count"]

        fig_bar = px.bar(
            event_count,
            x="Event Name",
            y="Participant Count",
            title="Participants by Event",
            color="Event Name",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_bar.update_layout(showlegend=False, xaxis_tickangle=-35)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("College-wise Participation Share")
    with st.expander("College Participation Details", expanded=True):
        college_count = filtered_df["College"].value_counts().reset_index()
        college_count.columns = ["College", "Participant Count"]

        fig_pie = px.pie(
            college_count,
            names="College",
            values="Participant Count",
            title="Percentage of Participation from Each College",
            hole=0.2
        )
        fig_pie.update_traces(textposition="inside", textinfo="percent+label")
        st.plotly_chart(fig_pie, use_container_width=True)

        top_college = college_count.iloc[0]
        st.markdown(
            f" {top_college['College']} with {int(top_college['Participant Count'])} participants is the highest."
        )

with tab2:
    st.subheader("Participation Trends and India State-wise View")

    col_a, col_b = st.columns(2)

    with col_a:
        with st.expander("Trend by State", expanded=True):
            state_trend = filtered_df.groupby("State").size().reset_index(name="Participants")
            state_trend = state_trend.sort_values("Participants", ascending=False)
            fig_line_state = px.line(
                state_trend,
                x="State",
                y="Participants",
                title="Participants by State",
                markers=True
            )
            fig_line_state.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig_line_state, use_container_width=True)

    with col_b:
        with st.expander("Trend by Event", expanded=True):
            event_rating_trend = filtered_df.groupby("Event Name")["Rating"].mean().reset_index()
            event_rating_trend = event_rating_trend.sort_values("Rating", ascending=False)
            fig_line_event = px.line(
                event_rating_trend,
                x="Event Name",
                y="Rating",
                title="Average Rating by Event",
                markers=True
            )
            fig_line_event.update_layout(xaxis_tickangle=-35)
            st.plotly_chart(fig_line_event, use_container_width=True)

    with st.expander("India Map: State-wise Participants", expanded=True):
        state_counts = filtered_df.groupby("State").size().reset_index(name="Participants")

        # Approximate state centroid coordinates for India map plotting
        state_coords = pd.DataFrame({
            "State": [
                "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
                "Delhi", "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
                "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
                "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan",
                "Sikkim", "Tamil Nadu", "Telangana", "Tripura", "Uttar Pradesh",
                "Uttarakhand", "West Bengal", "Jammu and Kashmir"
            ],
            "lat": [
                15.9129, 28.2180, 26.2006, 25.0961, 21.2787,
                28.7041, 15.2993, 22.2587, 29.0588, 31.1048, 23.6102,
                15.3173, 10.8505, 22.9734, 19.7515, 24.6637,
                25.4670, 23.1645, 26.1584, 20.9517, 31.1471, 27.0238,
                27.5330, 11.1271, 18.1124, 23.9408, 26.8467,
                30.0668, 22.9868, 33.7782
            ],
            "lon": [
                79.7400, 94.7278, 92.9376, 85.3131, 81.8661,
                77.1025, 74.1240, 71.1924, 76.0856, 77.1734, 85.2799,
                75.7139, 76.2711, 78.6569, 75.7139, 93.9063,
                91.3662, 92.9376, 94.5624, 85.0985, 75.3412, 74.2179,
                88.5122, 78.6569, 79.0193, 91.9882, 80.9462,
                79.0193, 87.8550, 76.5762
            ]
        })

        map_df = state_counts.merge(state_coords, on="State", how="left")
        map_df = map_df.dropna(subset=["lat", "lon"])

        if map_df.empty:
            st.info("State coordinates are not available for current selection.")
        else:
            fig_map = px.scatter_geo(
                map_df,
                lat="lat",
                lon="lon",
                size="Participants",
                color="Participants",
                hover_name="State",
                scope="asia",
                projection="natural earth",
                title="State-wise Participants in India"
            )
            
            # To name the state behind the dots in India Map
            fig_map.add_trace(
                dict(
                    type="scattergeo",
                    lon=map_df["lon"],
                    lat=map_df["lat"],
                    text=map_df["State"],
                    mode="text",
                    textposition="top center",
                    textfont=dict(size=8, color="darkblue"),
                    hoverinfo="skip",
                    showlegend=False
                )
            )
            
            fig_map.update_geos(
                center={"lat": 22.5, "lon": 79.0},
                lataxis_range=[6, 37],
                lonaxis_range=[68, 98],
                showcountries=True,
                countrycolor="Black"
            )
            
            fig_map.update_layout(height=700)
            st.plotly_chart(fig_map, use_container_width=True)
            
            top_state = state_counts.loc[state_counts["Participants"].idxmax()]
            st.markdown(
                f"**State with Highest Participation is** {top_state['State']}"
            )

with tab3:
    st.subheader("Feedback and Rating Relationship")

    st.subheader("Overall Satisfaction Level")
    satisfied_pct = (filtered_df["Rating"] >= 4).mean() * 100
    col_s1, col_s2 = st.columns(2)

    with col_s1:
        st.metric("Overall Satisfaction", f"{satisfied_pct:.1f}%")

    with col_s2:
        if satisfied_pct >= 80:
            st.success("High satisfaction: most participants rated the fest 4 or 5.")
        elif satisfied_pct >= 60:
            st.info("Moderate satisfaction: participant experience is generally positive.")
        else:
            st.warning("Satisfaction needs improvement: many ratings are below 4.")

    with st.expander("Scatter Plot Details", expanded=True):
        scatter_df = (
            filtered_df.groupby(["Event Name", "Event Type"], as_index=False)
            .agg(
                Participants=("Student Name", "count"),
                Average_Rating=("Rating", "mean"),
                Total_Revenue=("Amount Paid", "sum"),
            )
        )

        fig_scatter = px.scatter(
            scatter_df,
            x="Participants",
            y="Average_Rating",
            color="Event Type",
            size="Total_Revenue",
            title="Event Performance: Participants vs Average Rating",
            opacity=0.8,
            size_max=40,
            hover_data={
                "Event Name": True,
                "Participants": True,
                "Average_Rating": ":.2f",
                "Total_Revenue": ":,.0f",
            },
        )
        fig_scatter.update_layout(
            xaxis_title="Number of Participants",
            yaxis_title="Average Rating",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

    st.subheader("Most Common Feedback Texts")
    with st.expander("Feedback Text Details", expanded=True):
        feedback_counts = filtered_df["Feedback on Fest"].value_counts().reset_index().head(10)
        feedback_counts.columns = ["Feedback", "Count"]

        fig_feedback = px.bar(
            feedback_counts,
            x="Count",
            y="Feedback",
            orientation="h",
            title="Top 10 Feedback Statements",
            color="Count",
            color_continuous_scale="Blues"
        )
        fig_feedback.update_layout(yaxis={"categoryorder": "total ascending"})
        st.plotly_chart(fig_feedback, use_container_width=True)

    st.subheader("Word Cloud from Feedback on Fest")
    with st.expander("Word Cloud Details", expanded=True):
        feedback_text = " ".join(filtered_df["Feedback on Fest"].dropna().astype(str))

        if feedback_text.strip():
            wc = WordCloud(
                width=1200,
                height=500,
                background_color="white",
                stopwords=STOPWORDS,
                colormap="viridis"
            ).generate(feedback_text)

            fig_wc, ax_wc = plt.subplots(figsize=(12, 5))
            ax_wc.imshow(wc, interpolation="bilinear")
            ax_wc.axis("off")
            st.pyplot(fig_wc)
            plt.close(fig_wc)
        else:
            st.info("No feedback text available for current filters.")

with tab4:
    st.subheader("Student Information Based on Selected Filters")

    display_columns = [
        "Student Name",
        "College",
        "Phone Number",
        "Place",
        "State",
        "Event Name",
        "Event Type",
        "Amount Paid",
        "Rating",
        "Feedback on Fest"
    ]

    available_columns = [col for col in display_columns if col in filtered_df.columns]

    st.metric("Filtered Student Records", f"{len(filtered_df):,}")

    with st.expander("View Student Details", expanded=True):
        st.dataframe(
            filtered_df[available_columns].reset_index(drop=True),
            use_container_width=True,
            hide_index=True
        )
