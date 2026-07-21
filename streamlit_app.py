"""
Aplicação Streamlit para Sistema Fuzzy Modular - Necessidades Habitacionais

Interface interativa para simular:
1. SIF 1 - HAP (DOM_RUSTICOS + DOM_IMPROVISADOS -> HAB_PRECARIA)
2. SIF 2 - COA (UNID_DOM_CONV + DOM_COMODOS -> COA) - CORRIGIDO
3. SIF 3 - DEH (Hab_Precária + Coabitação -> DEH)
4. Índice Final (média dos SIFs)

Baseado nas especificações do MATLAB.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fuzzy_system import HousingFuzzySystem, PriorityLevel


# Configuração da página
st.set_page_config(
    page_title="Sistema Fuzzy Modular - SIF 1-3",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo personalizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .priority-badge {
        font-size: 1.2rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
        display: inline-block;
    }
    .priority-altissima {
        background-color: #9c27b0;
        color: white;
    }
    .priority-muito-alto {
        background-color: #d32f2f;
        color: white;
    }
    .priority-alto {
        background-color: #f57c00;
        color: white;
    }
    .priority-medio {
        background-color: #fbc02d;
        color: #333;
    }
    .priority-baixo {
        background-color: #388e3c;
        color: white;
    }
    .priority-muito-baixo {
        background-color: #006400;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


def get_priority_color(priority: str) -> str:
    colors = {
        'MUITO BAIXO': 'priority-muito-baixo',
        'BAIXO': 'priority-baixo',
        'MÉDIO': 'priority-medio',
        'ALTO': 'priority-alto',
        'MUITO ALTO': 'priority-muito-alto',
        'ALTÍSSIMA': 'priority-altissima'
    }
    return colors.get(priority, 'priority-medio')


def display_priority_badge(priority: str, score: float) -> str:
    color_class = get_priority_color(priority)
    return f'<span class="priority-badge {color_class}">{priority} ({score:.1f})</span>'


def main():
    # Header
    st.markdown('<p class="main-header">🏠 Sistema Fuzzy Modular - SIF 1-3</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Baseado nas especificações do MATLAB (SIF 2 corrigido)</p>', unsafe_allow_html=True)
    
    # Inicializar o sistema fuzzy
    fuzzy_system = HousingFuzzySystem()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/house-plan.png", width=80)
        st.title("Navegação")
        
        st.markdown("### Estrutura do Sistema")
        st.markdown("**SIF 1 - HAP:** DOM_RUSTICOS + DOM_IMPROVISADOS → HAB_PRECARIA")
        st.markdown("**SIF 2 - COA:** UNID_DOM_CONV + DOM_COMODOS → COA")
        st.markdown("**SIF 3 - DEH:** Hab_Precária + Coabitação → DEH")
        st.markdown("**Índice Final:** Média dos SIFs 1-3")
        
        st.markdown("---")
        st.markdown("### Legenda")
        st.markdown("**🟢 Muito Baixo/Baixo**: Prioridade normal")
        st.markdown("**🟡 Médio**: Atenção moderada")
        st.markdown("**🟠 Alto**: Prioridade elevada")
        st.markdown("**🔴 Muito Alto**: Prioridade alta")
        st.markdown("**🟣 Altíssima**: Intervenção imediata")
    
    # Abas principais
    tab1, tab2, tab3 = st.tabs([
        "📊 SIF 1 - HAP", 
        "📈 SIF 2 - COA e SIF 3 - DEH",
        "🎯 Índice Final"
    ])
    
    with tab1:
        st.header("SIF 1 - HAP (Habitação Precária)")
        st.markdown("""
        **Entradas:**
        - DOM_RUSTICOS (0-100%): Percentual de domicílios rústicos
        - DOM_IMPROVISADOS (0-100%): Percentual de domicílios improvisados
        
        **Saída:** HAB_PRECARIA (0-100)
        
        **Funções de pertinência de entrada (4):**
        - Ideal: [0, 0, 33]
        - Aceitável: [0, 33, 66]
        - Parcialmente aceitável: [33, 66, 90]
        - Inaceitável: [66, 100, 100, 100] (trapezoidal)
        
        **Funções de pertinência de saída (6):**
        - Muito Baixa: [0, 0, 20]
        - Baixa: [0, 20, 40]
        - Média: [20, 40, 60]
        - Alta: [40, 60, 80]
        - Muito Alta: [60, 80, 100]
        - Altíssima: [80, 100, 100]
        
        **Regras:** 16 regras conforme MATLAB
        """)
        
        with st.form("sif1_form"):
            col1, col2 = st.columns(2)
            with col1:
                dom_rusticos = st.slider("DOM_RUSTICOS (%)", 0, 100, 50, 1)
            with col2:
                dom_improvisados = st.slider("DOM_IMPROVISADOS (%)", 0, 100, 50, 1)
            
            submit_sif1 = st.form_submit_button("Avaliar SIF 1 - HAP", type="primary")
        
        if submit_sif1:
            result = fuzzy_system.evaluate_module('SIF1_HAP', {
                'DOM_RUSTICOS': dom_rusticos,
                'DOM_IMPROVISADOS': dom_improvisados
            })
            
            st.markdown("---")
            st.subheader("Resultado do SIF 1 - HAP")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                badge_html = display_priority_badge(result.label.value, result.value)
                st.markdown(badge_html, unsafe_allow_html=True)
            with col2:
                st.metric("HAB_PRECARIA", f"{result.value:.2f}/100")
                
                # Gráfico de pertinência
                fig, ax = plt.subplots(figsize=(8, 3))
                labels = list(result.memberships.keys())
                values = list(result.memberships.values())
                colors = ['#006400', '#388e3c', '#fbc02d', '#f57c00', '#d32f2f', '#9c27b0']
                bars = ax.bar(labels, values, color=colors[:len(labels)])
                ax.set_ylim(0, 1.1)
                ax.set_title('Graus de Pertinência - HAB_PRECARIA')
                st.pyplot(fig)
            
            # Armazenar resultado para uso posterior
            st.session_state.sif1_result = result.value
    
    with tab2:
        st.header("SIF 2 - COA (Coabitação) - CORRIGIDO")
        st.markdown("""
        **Entradas:**
        - UNID_DOM_CONV (0-100%): Unidades domésticas conviventes
        - DOM_COMODOS (0-100%): Domicílios cômodos
        
        **Saída:** COA (0-100)
        
        **Funções de pertinência de entrada (4):**
        - Ideal: [0, 0, 33]
        - Aceitável: [0, 33, 66]
        - Parcialmente aceitável: [33, 66, 90]
        - Inaceitável: [66, 100, 100, 100] (trapezoidal)
        
        **Funções de pertinência de saída (6):**
        - Muito baixa: [0, 0, 20]
        - baixa: [0, 20, 40]
        - média: [20, 40, 60]
        - alta: [40, 60, 80]
        - muito alta: [60, 80, 100]
        - altíssima: [80, 100, 100]
        
        **Regras:** 16 regras conforme MATLAB
        """)
        
        with st.form("sif2_form"):
            col1, col2 = st.columns(2)
            with col1:
                unid_dom_conv = st.slider("UNID_DOM_CONV (%)", 0, 100, 50, 1, key="unid_dom_conv")
            with col2:
                dom_comodos = st.slider("DOM_COMODOS (%)", 0, 100, 50, 1, key="dom_comodos")
            
            submit_sif2 = st.form_submit_button("Avaliar SIF 2 - COA", type="primary")
        
        if submit_sif2:
            result = fuzzy_system.evaluate_module('SIF2_COA', {
                'UNID_DOM_CONV': unid_dom_conv,
                'DOM_COMODOS': dom_comodos
            })
            
            st.markdown("---")
            st.subheader("Resultado do SIF 2 - COA")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                badge_html = display_priority_badge(result.label.value, result.value)
                st.markdown(badge_html, unsafe_allow_html=True)
            with col2:
                st.metric("COA", f"{result.value:.2f}/100")
                
                # Gráfico de pertinência
                fig, ax = plt.subplots(figsize=(8, 3))
                labels = list(result.memberships.keys())
                values = list(result.memberships.values())
                colors = ['#006400', '#388e3c', '#fbc02d', '#f57c00', '#d32f2f', '#9c27b0']
                bars = ax.bar(labels, values, color=colors[:len(labels)])
                ax.set_ylim(0, 1.1)
                ax.set_title('Graus de Pertinência - COA')
                st.pyplot(fig)
            
            # Armazenar resultado
            st.session_state.sif2_result = result.value
        
        st.markdown("---")
        st.markdown("### SIF 3 - DEH (Déficit Habitacional)")
        st.markdown("""
        **Entradas:**
        - Hab_Precária (0-100): Resultado do SIF 1
        - Coabitação (0-100): Resultado do SIF 2
        
        **Saída:** DEH (0-100)
        
        **Funções de pertinência de entrada e saída (5):**
        - Muito baixa: [0, 0, 20]
        - Baixa: [0, 20, 40]
        - Média: [20, 40, 60]
        - Alta: [40, 60, 80]
        - Muito Alta: [60, 100, 100, 100] (trapezoidal)
        
        **Regras:** 25 regras conforme MATLAB
        """)
        
        with st.form("sif3_form"):
            col1, col2 = st.columns(2)
            with col1:
                hab_precarria = st.slider("Hab_Precária (do SIF 1)", 0, 100, 
                                         int(st.session_state.sif1_result) if 'sif1_result' in st.session_state else 50, 1)
            with col2:
                coabitacao = st.slider("Coabitação (do SIF 2)", 0, 100,
                                       int(st.session_state.sif2_result) if 'sif2_result' in st.session_state else 50, 1)
            
            submit_sif3 = st.form_submit_button("Avaliar SIF 3 - DEH", type="primary")
        
        if submit_sif3:
            result = fuzzy_system.evaluate_module('SIF3_DEH', {
                'Hab_Precária': hab_precarria,
                'Coabitação': coabitacao
            })
            
            st.markdown("---")
            st.subheader("Resultado do SIF 3 - DEH")
            
            col1, col2 = st.columns([1, 2])
            with col1:
                badge_html = display_priority_badge(result.label.value, result.value)
                st.markdown(badge_html, unsafe_allow_html=True)
            with col2:
                st.metric("DEH", f"{result.value:.2f}/100")
                
                # Gráfico de pertinência
                fig, ax = plt.subplots(figsize=(8, 3))
                labels = list(result.memberships.keys())
                values = list(result.memberships.values())
                colors = ['#006400', '#388e3c', '#fbc02d', '#f57c00', '#d32f2f']
                bars = ax.bar(labels, values, color=colors[:len(labels)])
                ax.set_ylim(0, 1.1)
                ax.set_title('Graus de Pertinência - DEH')
                st.pyplot(fig)
            
            # Armazenar resultado
            st.session_state.sif3_result = result.value
    
    with tab3:
        st.header("Índice Final")
        st.markdown("Cálculo do índice final como média dos SIFs 1, 2 e 3.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Usar resultados armazenados")
            
            sif1_val = st.session_state.get('sif1_result', 0)
            sif2_val = st.session_state.get('sif2_result', 0)
            sif3_val = st.session_state.get('sif3_result', 0)
            
            st.write(f"SIF 1 (HAP): {sif1_val:.2f}")
            st.write(f"SIF 2 (COA): {sif2_val:.2f}")
            st.write(f"SIF 3 (DEH): {sif3_val:.2f}")
            
            if st.button("Calcular Índice Final"):
                result = fuzzy_system.evaluate_final_index({
                    'SIF1_HAP': sif1_val,
                    'SIF2_COA': sif2_val,
                    'SIF3_DEH': sif3_val
                })
                
                st.markdown("---")
                st.subheader("Resultado do Índice Final")
                
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    badge_html = display_priority_badge(result.label.value, result.value)
                    st.markdown(badge_html, unsafe_allow_html=True)
                
                with col_b:
                    st.metric("Índice Final", f"{result.value:.2f}/100")
        
        with col2:
            st.subheader("Entrada manual")
            
            with st.form("manual_final_form"):
                sif1_manual = st.slider("SIF 1 - HAP", 0, 100, 50, 1)
                sif2_manual = st.slider("SIF 2 - COA", 0, 100, 50, 1)
                sif3_manual = st.slider("SIF 3 - DEH", 0, 100, 50, 1)
                
                submit_manual = st.form_submit_button("Calcular", type="primary")
            
            if submit_manual:
                result = fuzzy_system.evaluate_final_index({
                    'SIF1_HAP': sif1_manual,
                    'SIF2_COA': sif2_manual,
                    'SIF3_DEH': sif3_manual
                })
                
                st.markdown("---")
                st.subheader("Resultado do Índice Final")
                
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    badge_html = display_priority_badge(result.label.value, result.value)
                    st.markdown(badge_html, unsafe_allow_html=True)
                
                with col_b:
                    st.metric("Índice Final", f"{result.value:.2f}/100")


if __name__ == "__main__":
    main()
