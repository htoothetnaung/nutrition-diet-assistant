from datetime import datetime
import pandas as pd
import plotly.express as px
import streamlit as st


def render_dashboard_page(db_manager):
    st.header("📊 Nutrition Dashboard")
    st.markdown("Visualize your nutrition data and track your progress")

    user_id = (
        st.session_state.user_data["id"] if st.session_state.user_data else None
    )
    prefs = db_manager.get_user_preferences(user_id) if user_id else {}
    plan = prefs.get("Plan_Macros") or {}

    targets = {
        "calories": float(plan.get("calories", 0) or 0),
        "protein_g": float(plan.get("protein_g", 0) or 0),
        "carbs_g": float(plan.get("carbs_g", 0) or 0),
        "fat_g": float(plan.get("fat_g", 0) or 0),
    }

    today_utc = datetime.utcnow().date()
    totals = {"calories": 0.0, "protein_g": 0.0, "carbs_g": 0.0, "fat_g": 0.0}
    if user_id:
        meals = db_manager.get_user_meal_logs(user_id, limit=100) or []
        for m in meals:
            try:
                mt = m.get("meal_time")
                dt_utc = (
                    datetime.fromisoformat(mt.replace("Z", "+00:00"))
                    if isinstance(mt, str)
                    else datetime.utcnow()
                )
                if dt_utc.date() != today_utc:
                    continue
            except Exception:
                continue
            ana = db_manager.get_nutrition_analysis_by_meal(m.get("id")) or {}
            totals["calories"] += float(ana.get("calories", 0) or 0)
            totals["protein_g"] += float(ana.get("protein_g", 0) or 0)
            totals["carbs_g"] += float(ana.get("carbs_g", 0) or 0)
            totals["fat_g"] += float(ana.get("fat_g", 0) or 0)

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📈 Daily Nutrition Breakdown (Actual vs Target)")
        categories = ["Calories", "Protein", "Fat", "Carbs"]
        actual_vals = [
            round(totals.get("calories", 0), 2),
            round(totals.get("protein_g", 0), 2),
            round(totals.get("fat_g", 0), 2),
            round(totals.get("carbs_g", 0), 2),
        ]
        target_vals = [
            round(targets.get("calories", 0), 2),
            round(targets.get("protein_g", 0), 2),
            round(targets.get("fat_g", 0), 2),
            round(targets.get("carbs_g", 0), 2),
        ]
        units = ["kcal", "g", "g", "g"]
        df_bar = pd.DataFrame(
            {
                "Nutrient": categories * 2,
                "Value": actual_vals + target_vals,
                "Type": ["Actual"] * 4 + ["Target"] * 4,
                "Unit": units * 2,
            }
        )
        fig_bar = px.bar(
            df_bar,
            x="Nutrient",
            y="Value",
            color="Type",
            barmode="group",
            title="Today's Intake vs Planned Target",
            color_discrete_sequence=px.colors.qualitative.Set2,
            hover_data={"Unit": True, "Type": True, "Nutrient": True},
        )
        st.plotly_chart(fig_bar, use_container_width=True)

    with col2:
        st.subheader("🥧 Macronutrient Distribution (by calories)")
        p_g = max(totals.get("protein_g", 0), 0)
        c_g = max(totals.get("carbs_g", 0), 0)
        f_g = max(totals.get("fat_g", 0), 0)
        p_kcal, c_kcal, f_kcal = 4 * p_g, 4 * c_g, 9 * f_g
        kcal_sum = p_kcal + c_kcal + f_kcal
        pie_vals = [
            round((p_kcal / kcal_sum * 100.0), 2) if kcal_sum > 0 else 0,
            round((f_kcal / kcal_sum * 100.0), 2) if kcal_sum > 0 else 0,
            round((c_kcal / kcal_sum * 100.0), 2) if kcal_sum > 0 else 0,
        ]
        fig_pie = px.pie(
            values=pie_vals,
            names=["Protein", "Fat", "Carbohydrates"],
            title="Macronutrient Breakdown (% of calories)",
            color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.divider()

    st.subheader("🎯 Goals Progress")
    g1, g2, g3, g4 = st.columns(4)

    def _delta_str(current: float, target: float, unit: str) -> str:
        if target <= 0:
            return "no target set"
        diff = current - target
        direction = "over" if diff > 0 else "under"
        return f"{abs(int(round(diff)))} {unit} {direction} goal"

    with g1:
        st.metric(
            "Calories",
            f"{int(round(totals.get('calories', 0)))} kcal",
            _delta_str(totals.get("calories", 0), targets.get("calories", 0), "kcal"),
        )
    with g2:
        st.metric(
            "Protein",
            f"{int(round(totals.get('protein_g', 0)))} g",
            _delta_str(totals.get("protein_g", 0), targets.get("protein_g", 0), "g"),
        )
    with g3:
        st.metric(
            "Carbs",
            f"{int(round(totals.get('carbs_g', 0)))} g",
            _delta_str(totals.get("carbs_g", 0), targets.get("carbs_g", 0), "g"),
        )
    with g4:
        st.metric(
            "Fats",
            f"{int(round(totals.get('fat_g', 0)))} g",
            _delta_str(totals.get("fat_g", 0), targets.get("fat_g", 0), "g"),
        )
