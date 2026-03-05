"""
Sample Question Cards Component
"""
import streamlit as st
from typing import List, Dict, Callable


def render_sample_cards(
    categories: List[Dict[str, any]],
    on_question_selected: Callable[[str], None]
) -> None:
    """
    Render sample question cards in a grid layout.
    
    Args:
        categories: List of category dicts with 'name', 'icon', and 'questions' keys
        on_question_selected: Callback when a question is selected
    """
    st.markdown("### 💡 Try asking...")
    
    # Use columns for card layout (4 columns max)
    cols = st.columns(min(4, len(categories)))
    
    for idx, category in enumerate(categories[:4]):
        with cols[idx]:
            # Category header with icon
            icon = category.get('icon', '❓')
            name = category.get('name', 'Category')
            st.markdown(f"#### {icon} {name}")
            
            # Display questions as clickable cards
            for question in category.get('questions', [])[:3]:
                # Create card-like button
                if st.button(
                    question,
                    key=f"sample_{idx}_{hash(question)}",
                    use_container_width=True,
                    help=f"Ask: {question}"
                ):
                    on_question_selected(question)