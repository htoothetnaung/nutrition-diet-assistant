"""
Meal Analyzer Page with Qwen3-VL Vision Language Model Integration

This page provides:
1. Text-based meal analysis (describe your meal)
2. AI-powered image analysis using fine-tuned Qwen3-VL model
3. Meal logging to database
"""

import time
from datetime import datetime
from typing import Any
import streamlit as st
from PIL import Image

from utils import extract_ingredients_free_text, compute_nutrition
from vlm import (
    load_vlm_model,
    run_vlm_inference,
    parse_nutrition_from_response,
    PROMPT_TEMPLATES,
    HF_ADAPTER_IDS,
    get_device_options,
    is_local_adapter_available,
    CUDA_AVAILABLE,
)


def render_vlm_sidebar_controls():
    """Render VLM model controls in the sidebar area within the analyzer tab."""
    
    st.markdown("---")
    st.markdown("### ⚙️ VLM Model Settings")
    
    # Check for local adapter
    local_available = is_local_adapter_available()
    
    # Adapter source selection
    adapter_source = st.radio(
        "Adapter Source",
        options=["huggingface", "local"],
        index=0,
        help="Choose whether to load the LoRA adapter from HuggingFace Hub or local path",
        horizontal=True,
    )
    
    if adapter_source == "local" and not local_available:
        st.warning("⚠️ Local adapter not found. Using HuggingFace.")
        adapter_source = "huggingface"
    
    # Adapter version selection (only for HuggingFace)
    adapter_id = "Stage 2 (Clinical Nutrition)"
    if adapter_source == "huggingface":
        adapter_id = st.selectbox(
            "Model Version",
            options=list(HF_ADAPTER_IDS.keys()),
            index=1,  # Default to Stage 2
            help="Stage 1: General nutrition analysis | Stage 2: Clinical nutrition with CKD focus"
        )
    
    # Device selection
    device_options = get_device_options()
    device = st.selectbox(
        "Device",
        options=device_options,
        index=0,
        help="Select computation device (auto recommended)"
    )
    
    # Quantization option
    use_4bit = st.checkbox(
        "Use 4-bit quantization",
        value=CUDA_AVAILABLE,
        help="Enable 4-bit quantization to reduce VRAM usage (~4GB instead of ~16GB). CUDA only.",
        disabled=not CUDA_AVAILABLE
    )
    
    # Generation settings
    max_tokens = st.slider(
        "Max Tokens",
        min_value=64,
        max_value=512,
        value=256,
        step=32,
        help="Maximum number of tokens to generate"
    )
    
    st.markdown("---")
    
    # Model loading button
    load_button = st.button(
        "🚀 Load VLM Model" if not st.session_state.vlm_model_loaded else "🔄 Reload Model",
        type="primary",
        use_container_width=True,
    )
    
    if load_button:
        try:
            with st.spinner("Loading model... This may take a few minutes."):
                model, processor = load_vlm_model(
                    adapter_source=adapter_source,
                    device=device,
                    use_4bit=use_4bit,
                    adapter_id=adapter_id
                )
                st.session_state.vlm_model = model
                st.session_state.vlm_processor = processor
                st.session_state.vlm_model_loaded = True
                
                # Determine actual device
                if device == "auto":
                    st.session_state.vlm_device = "cuda" if CUDA_AVAILABLE else "cpu"
                else:
                    st.session_state.vlm_device = device
                    
            st.success("✅ Model loaded successfully!")
        except Exception as e:
            st.error(f"❌ Failed to load model: {str(e)}")
            st.session_state.vlm_model_loaded = False
    
    # Show model status
    if st.session_state.vlm_model_loaded:
        st.success(f"✅ Model loaded on {st.session_state.vlm_device}")
    else:
        st.info("👆 Click 'Load VLM Model' to start")
    
    return max_tokens


def render_vlm_image_analysis(db_manager: Any, max_tokens: int):
    """
    Render the VLM-based image analysis UI with the original qwen3_vl_inference_app.py layout.
    """
    
    st.markdown("""
    **Fine-tuned Vision-Language Model for Food & Nutrition Analysis**
    
    Upload a food image and get detailed nutritional insights powered by Qwen3-VL-4B-Nutrition model.
    """)
    
    # Two-column layout matching original qwen3_vl_inference_app.py style
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 📷 Upload Food Image")
        
        uploaded_file = st.file_uploader(
            "Choose an image...",
            type=["jpg", "jpeg", "png", "webp"],
            help="Upload a food image for analysis",
            key="vlm_image_uploader"
        )
        
        if uploaded_file is not None:
            image = Image.open(uploaded_file)
            st.image(image, caption="Uploaded Image", use_container_width=True)
        else:
            image = None
            st.info("📸 Please upload an image to analyze")
    
    with col2:
        st.markdown("#### 💬 Analysis Task")
        
        # Prompt template selection (key feature from original app)
        template_name = st.selectbox(
            "Select analysis type",
            options=list(PROMPT_TEMPLATES.keys()),
            index=1,  # Default to "Nutrition Analysis"
            help="Choose what kind of analysis you want to perform"
        )
        
        # Get template text
        template_text = PROMPT_TEMPLATES[template_name]
        
        # Custom prompt input
        if template_name == "Custom":
            prompt = st.text_area(
                "Enter your custom prompt",
                value="",
                height=120,
                placeholder="Enter your question about the food image...",
                key="vlm_custom_prompt"
            )
        else:
            prompt = st.text_area(
                "Prompt (editable)",
                value=template_text,
                height=120,
                key="vlm_prompt"
            )
        
        # Optional meal description for logging
        meal_description = st.text_input(
            "Meal description (for logging)",
            placeholder="e.g., Lunch - Grilled chicken salad",
            help="Optional: Add a description for your meal log",
            key="vlm_meal_desc"
        )
        
        # Run inference button
        analyze_button = st.button(
            "🔍 Analyze Image",
            type="primary",
            use_container_width=True,
            disabled=not st.session_state.vlm_model_loaded or image is None,
            key="vlm_analyze_btn"
        )
    
    # Results section
    st.divider()
    st.markdown("### 📊 Analysis Results")
    
    if analyze_button:
        if not st.session_state.vlm_model_loaded:
            st.error("⚠️ Please load the VLM model first using the controls above.")
        elif image is None:
            st.error("⚠️ Please upload an image first.")
        elif not prompt.strip():
            st.error("⚠️ Please enter a prompt.")
        else:
            with st.spinner("🔄 Analyzing image..."):
                start_time = time.time()
                try:
                    result = run_vlm_inference(
                        model=st.session_state.vlm_model,
                        processor=st.session_state.vlm_processor,
                        image=image,
                        prompt=prompt,
                        max_tokens=max_tokens,
                        device=st.session_state.vlm_device
                    )
                    elapsed_time = time.time() - start_time
                    
                    # Display results
                    st.success(f"✅ Analysis completed in {elapsed_time:.2f} seconds")
                    
                    # Results in a nice container
                    with st.container():
                        st.markdown("#### 🍽️ Model Response")
                        st.markdown(result)
                    
                    # Try to parse nutrition from response
                    parsed_nutrition = parse_nutrition_from_response(result)
                    has_nutrition = any(v > 0 for v in parsed_nutrition.values())
                    
                    if has_nutrition:
                        st.markdown("#### 📈 Parsed Nutrition Values")
                        nutrition_cols = st.columns(4)
                        with nutrition_cols[0]:
                            st.metric("Calories", f"{parsed_nutrition['calories']:.0f} kcal")
                        with nutrition_cols[1]:
                            st.metric("Protein", f"{parsed_nutrition['protein_g']:.1f} g")
                        with nutrition_cols[2]:
                            st.metric("Carbs", f"{parsed_nutrition['carbs_g']:.1f} g")
                        with nutrition_cols[3]:
                            st.metric("Fat", f"{parsed_nutrition['fat_g']:.1f} g")
                    
                    # Store in session state for history
                    st.session_state.vlm_history.append({
                        "prompt": prompt,
                        "response": result,
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "inference_time": elapsed_time,
                        "task_type": template_name,
                    })
                    
                    # Meal logging integration
                    if st.session_state.user_data:
                        # Auto-generate description if not provided
                        log_description = meal_description.strip() if meal_description.strip() else f"VLM Analysis: {template_name}"
                        
                        # Save to database
                        meal_log_id = db_manager.save_meal_log(
                            st.session_state.user_data["id"],
                            log_description,
                            uploaded_file.name if hasattr(uploaded_file, "name") else None,
                        )
                        
                        # Save nutrition analysis
                        db_manager.save_nutrition_analysis(
                            meal_log_id,
                            calories=float(parsed_nutrition.get("calories", 0)),
                            protein=float(parsed_nutrition.get("protein_g", 0)),
                            carbs=float(parsed_nutrition.get("carbs_g", 0)),
                            fat=float(parsed_nutrition.get("fat_g", 0)),
                            recommendation=f"VLM Analysis ({template_name}): {result[:200]}...",
                            sugar=float(parsed_nutrition.get("sugar_g", 0)),
                            fiber=float(parsed_nutrition.get("fiber_g", 0)),
                        )
                        st.success("💾 Analysis saved to your meal log!")
                    else:
                        st.info("💡 Login to save this analysis to your history.")
                    
                except Exception as e:
                    st.error(f"❌ Inference failed: {str(e)}")
                    import traceback
                    with st.expander("Error Details"):
                        st.code(traceback.format_exc())
    
    # History section (from original app)
    if st.session_state.vlm_history:
        st.divider()
        with st.expander("📜 Session Analysis History", expanded=False):
            for i, entry in enumerate(reversed(st.session_state.vlm_history)):
                st.markdown(f"**[{entry['timestamp']}]** - {entry['task_type']} ({entry['inference_time']:.2f}s)")
                st.markdown(f"**Prompt:** {entry['prompt'][:100]}...")
                st.markdown(f"**Response:** {entry['response'][:300]}...")
                if i < len(st.session_state.vlm_history) - 1:
                    st.divider()


def render_text_meal_analysis(db_manager: Any, uploaded_file):
    """Render the text-based meal analysis section."""
    
    meal_description = st.text_area(
        "Describe your meal (What did you eat today):",
        placeholder="e.g., 1 bowl of chicken curry with rice and salad",
        height=100,
        key="text_meal_desc"
    )
    
    analyze_text = st.button("🔍 Analyze Meal", key="analyze_text_btn")
    
    if analyze_text:
        if not meal_description:
            st.error("Please describe your meal first!")
        else:
            extraction = extract_ingredients_free_text(meal_description)
            if isinstance(extraction, dict):
                note = extraction.get("notes", "")
                if note in ("llm_unavailable", "llm_error"):
                    st.error(
                        "Text parsing requires LLM. Please set LLM_API_KEY and try again."
                    )
                    st.stop()
            items = (
                extraction.get("items", []) if isinstance(extraction, dict) else []
            )
            if not items:
                st.warning(
                    "Couldn't parse ingredients. Try listing items with quantities, e.g., '150g chicken, 1 cup rice'."
                )
                st.stop()

            result = compute_nutrition(items)
            totals = result.get("totals", {})
            details = result.get("details", [])
            if not details or all(v == 0 for v in totals.values()):
                st.warning("No recognizable foods found. Please refine your description.")
                st.stop()

            st.subheader("🧾 Parsed Ingredients")
            rows = []
            for d in details:
                it = d.get("item", {})
                nut = d.get("nutrients", {})
                rows.append(
                    {
                        "Item": it.get("name", "-"),
                        "Qty": it.get("quantity", "-"),
                        "Unit": it.get("unit", "-"),
                        "kcal": nut.get("calories", 0),
                        "Protein(g)": nut.get("protein_g", 0),
                        "Carbs(g)": nut.get("carbs_g", 0),
                        "Fat(g)": nut.get("fat_g", 0),
                        "Fiber(g)": nut.get("fiber_g", 0),
                        "Sugar(g)": nut.get("sugar_g", 0),
                    }
                )
            st.dataframe(rows, use_container_width=True)

            st.subheader("📊 Estimated Totals")
            st.info(
                f"Calories: {totals.get('calories',0)} kcal | "
                f"Protein: {totals.get('protein_g',0)} g | "
                f"Carbs: {totals.get('carbs_g',0)} g | "
                f"Fat: {totals.get('fat_g',0)} g | "
                f"Fiber: {totals.get('fiber_g',0)} g | "
                f"Sugar: {totals.get('sugar_g',0)} g"
            )

            if st.session_state.user_data and details:
                meal_log_id = db_manager.save_meal_log(
                    st.session_state.user_data["id"],
                    meal_description,
                    uploaded_file.name if uploaded_file else None,
                )
                db_manager.save_nutrition_analysis(
                    meal_log_id,
                    calories=totals.get("calories", 0),
                    protein=totals.get("protein_g", 0),
                    carbs=totals.get("carbs_g", 0),
                    fat=totals.get("fat_g", 0),
                    recommendation="Auto-estimated from ingredients",
                    sugar=totals.get("sugar_g", 0),
                    fiber=totals.get("fiber_g", 0),
                )
                st.success("💾 Analysis saved to your meal log!")


def render_todays_meals(db_manager: Any):
    """Render today's logged meals section."""
    
    st.divider()
    st.subheader("📒 Today's Logged Meals")
    
    if st.session_state.user_data:
        _uid = st.session_state.user_data["id"]
        today_utc = datetime.utcnow().date()
        logs = db_manager.get_user_meal_logs(_uid, limit=100) or []
        rows = []
        entries = []
        totals_today = {
            "calories": 0.0,
            "protein_g": 0.0,
            "carbs_g": 0.0,
            "fat_g": 0.0,
            "fiber_g": 0.0,
            "sugar_g": 0.0,
        }
        for m in logs:
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
            cal = float(ana.get("calories", 0) or 0)
            pr = float(ana.get("protein_g", 0) or 0)
            cb = float(ana.get("carbs_g", 0) or 0)
            ft = float(ana.get("fat_g", 0) or 0)
            fib = float(ana.get("fiber_g", 0) or 0)
            sug = float(ana.get("sugar_g", 0) or 0)
            row = {
                "Description": m.get("meal_description", "-"),
                "Calories (kcal)": round(cal, 1),
                "Protein (g)": round(pr, 1),
                "Carbs (g)": round(cb, 1),
                "Fat (g)": round(ft, 1),
                "Fiber (g)": round(fib, 1),
                "Sugar (g)": round(sug, 1),
            }
            rows.append(row)
            entries.append({"id": m.get("id"), **row})
            totals_today["calories"] += cal
            totals_today["protein_g"] += pr
            totals_today["carbs_g"] += cb
            totals_today["fat_g"] += ft
            totals_today["fiber_g"] += fib
            totals_today["sugar_g"] += sug

        if rows:
            # Show daily totals
            st.markdown("#### 📊 Today's Totals")
            total_cols = st.columns(6)
            with total_cols[0]:
                st.metric("Calories", f"{totals_today['calories']:.0f} kcal")
            with total_cols[1]:
                st.metric("Protein", f"{totals_today['protein_g']:.1f} g")
            with total_cols[2]:
                st.metric("Carbs", f"{totals_today['carbs_g']:.1f} g")
            with total_cols[3]:
                st.metric("Fat", f"{totals_today['fat_g']:.1f} g")
            with total_cols[4]:
                st.metric("Fiber", f"{totals_today['fiber_g']:.1f} g")
            with total_cols[5]:
                st.metric("Sugar", f"{totals_today['sugar_g']:.1f} g")
            
            st.markdown("---")
            
            with st.expander("🗂️ Meal Entries", expanded=True):
                for entry in entries:
                    with st.container():
                        c1, c2, c3 = st.columns([5, 5, 1])
                        with c1:
                            st.write(f"**{entry['Description']}**")
                        with c2:
                            st.write(
                                f"{entry['Calories (kcal)']} kcal · "
                                f"P: {entry['Protein (g)']}g · "
                                f"C: {entry['Carbs (g)']}g · "
                                f"F: {entry['Fat (g)']}g"
                            )
                        with c3:
                            if st.button("🗑️", key=f"remove_{entry['id']}", help="Remove this entry"):
                                ok = db_manager.delete_meal_log(entry["id"])
                                if ok:
                                    st.success("Removed entry.")
                                    try:
                                        st.rerun()
                                    except Exception:
                                        st.experimental_rerun()
                                else:
                                    st.error("Failed to remove entry.")
            
            with st.expander("🔧 Maintenance", expanded=False):
                if st.button("Clear previous days", key="clear_prev_days"):
                    ok = db_manager.delete_user_meals_not_today(
                        _uid, today_utc.isoformat()
                    )
                    if ok:
                        st.success("Cleared older entries.")
                        try:
                            st.rerun()
                        except Exception:
                            st.experimental_rerun()
                    else:
                        st.error("Failed to clear older entries.")
        else:
            st.info("No meals logged today. Analyze a meal above to get started!")
    else:
        st.info("🔐 Login to view and save your meal history.")


def render_analyzer_page(db_manager: Any):
    """Main analyzer page render function."""
    
    st.header("🍽️ Meal Analyzer")
    st.markdown(
        "Analyze your meals for nutrition content using AI-powered vision and text analysis"
    )
    
    # Create main layout with sidebar-like controls area
    control_col, main_col = st.columns([1, 3])
    
    with control_col:
        # VLM Model controls (replaces sidebar approach - now in tab content area)
        max_tokens = render_vlm_sidebar_controls()
    
    with main_col:
        # Create tabs for different analysis methods
        photo_tab, text_tab = st.tabs(["📸 AI Photo Analysis (VLM)", "📝 Text Description"])
        
        with photo_tab:
            render_vlm_image_analysis(db_manager, max_tokens)
        
        with text_tab:
            st.markdown("### Describe Your Meal")
            st.markdown("Enter a text description of what you ate and we'll estimate the nutrition.")
            render_text_meal_analysis(db_manager, None)
    
    # Today's meals section (full width)
    render_todays_meals(db_manager)
    
    # Footer
    st.divider()
    st.markdown("""
    ---
    **Model:** Qwen3-VL-4B-Nutrition-SFT (Fine-tuned for nutrition analysis)  
    **Base Model:** Qwen/Qwen3-VL-4B-Instruct  
    **Adapter:** LoRA fine-tuned on nutrition and food datasets
    """)
