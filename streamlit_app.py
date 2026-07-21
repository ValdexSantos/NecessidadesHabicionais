"""
Aplicação Streamlit para Sistema Fuzzy Modular - Necessidades Habitacionais

Interface interativa para simular:
1. Indicadores individuais (A1, A2, B1, B2, C1, C2, D1, D2, E1, E2, E3, E4)
2. Subíndices (SIF 1-12)
3. Índice Final (ISF)

Cada módulo pode ser simulado individualmente ou em conjunto.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fuzzy_system import HousingFuzzySystem, PriorityLevel


# Configuração da página
st.set_page_config(
    page_title="Sistema Fuzzy Modular - Necessidades Habitacionais",
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
    .priority-urgent {
        background-color: #d32f2f;
        color: white;
    }
    .priority-high {
        background-color: #f57c00;
        color: white;
    }
    .priority-medium {
        background-color: #fbc02d;
        color: #333;
    }
    .priority-low {
        background-color: #388e3c;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)


def get_priority_color(priority: str) -> str:
    colors = {
        'BAIXA': 'priority-low',
        'MÉDIA': 'priority-medium',
        'ALTA': 'priority-high',
        'URGENTE': 'priority-urgent'
    }
    return colors.get(priority, 'priority-medium')


def display_priority_badge(priority: str, score: float) -> str:
    color_class = get_priority_color(priority)
    return f'<span class="priority-badge {color_class}">{priority} ({score:.1f})</span>'


def main():
    # Header
    st.markdown('<p class="main-header">🏠 Sistema Fuzzy Modular</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Diagnóstico de Necessidades Habitacionais - Esquema Grupo</p>', unsafe_allow_html=True)
    
    # Inicializar o sistema fuzzy
    fuzzy_system = HousingFuzzySystem()
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/house-plan.png", width=80)
        st.title("Navegação")
        
        st.markdown("### Estrutura do Sistema")
        st.markdown("**Indicadores:** 14 (A1-E4)")
        st.markdown("**Subíndices:** 10 (SIF 1-11)")
        st.markdown("**Índice Final:** ISF")
        
        st.markdown("---")
        st.markdown("### Legenda")
        st.markdown("**🟢 Baixa**: Prioridade normal")
        st.markdown("**🟡 Média**: Atenção moderada")
        st.markdown("**🟠 Alta**: Prioridade elevada")
        st.markdown("**🔴 Urgente**: Intervenção imediata")
    
    # Abas principais
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Indicadores Individuais", 
        "📈 Subíndices (SIF)", 
        "🎯 Índice Final (ISF)",
        "ℹ️ Documentação"
    ])
    
    with tab1:
        st.header("Simulação de Indicadores Individuais")
        st.markdown("Avalie cada indicador individualmente.")
        
        # Seleção de categoria
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Seleção")
            category = st.selectbox(
                "Categoria",
                ["Todos", "Habitação (A)", "Saneamento (B)", "Edificação (C)", "Serviços (D)", "Renda (E)"]
            )
            
            # Listar módulos da categoria
            all_modules = fuzzy_system.get_module_names()
            indicator_modules = [m for m in all_modules if len(m) <= 2]
            
            if category == "Todos":
                selected_modules = indicator_modules
            elif category == "Habitação (A)":
                selected_modules = [m for m in indicator_modules if m.startswith('A')]
            elif category == "Saneamento (B)":
                selected_modules = [m for m in indicator_modules if m.startswith('B')]
            elif category == "Edificação (C)":
                selected_modules = [m for m in indicator_modules if m.startswith('C')]
            elif category == "Serviços (D)":
                selected_modules = [m for m in indicator_modules if m.startswith('D')]
            elif category == "Renda (E)":
                selected_modules = [m for m in indicator_modules if m.startswith('E')]
            
            modules_to_evaluate = st.multiselect(
                "Selecione os indicadores",
                options=selected_modules,
                default=selected_modules[:3] if len(selected_modules) >= 3 else selected_modules
            )
        
        with col2:
            st.subheader("Entradas")
            
            with st.form("indicator_form"):
                inputs = {}
                
                for module_name in modules_to_evaluate:
                    module_info = fuzzy_system.get_module_info(module_name)
                    if module_info.get('error'):
                        continue
                    
                    input_vars = module_info.get('input_vars', [])
                    
                    for var_name in input_vars:
                        if var_name not in inputs:
                            if var_name in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'E3', 'E4']:
                                inputs[var_name] = st.slider(
                                    f"{var_name}",
                                    min_value=0.0,
                                    max_value=1.0,
                                    value=0.0,
                                    step=0.1,
                                    help="0 = Não, 1 = Sim"
                                )
                            elif var_name in ['D1', 'D2', 'D3', 'D4']:
                                inputs[var_name] = st.slider(
                                    f"{var_name}",
                                    min_value=0.0,
                                    max_value=10.0,
                                    value=5.0,
                                    step=0.1,
                                    help="0 = Baixo, 5 = Médio, 10 = Alto"
                                )
                            elif var_name == 'E1':
                                inputs[var_name] = st.slider(
                                    f"{var_name} - Renda per capita (% SM)",
                                    min_value=0.0,
                                    max_value=100.0,
                                    value=50.0,
                                    step=1.0
                                )
                            elif var_name == 'E2':
                                inputs[var_name] = st.slider(
                                    f"{var_name} - Membros empregados",
                                    min_value=0,
                                    max_value=10,
                                    value=5
                                )
                
                submit_button = st.form_submit_button("Avaliar Indicadores", type="primary")
        
        if submit_button and modules_to_evaluate:
            st.markdown("---")
            st.subheader("Resultados")
            
            results = []
            for module_name in modules_to_evaluate:
                try:
                    result = fuzzy_system.evaluate_module(module_name, {module_name: inputs.get(module_name, 0)})
                    results.append((module_name, result))
                except Exception as e:
                    st.error(f"Erro ao avaliar {module_name}: {e}")
            
            # Exibir resultados
            cols_per_row = 3
            for i in range(0, len(results), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, (module_name, result) in enumerate(results[i:i+cols_per_row]):
                    with cols[j]:
                        module_info = fuzzy_system.get_module_info(module_name)
                        st.markdown(f"**{module_name}**")
                        st.markdown(f"{module_info.get('name', module_name)}")
                        badge_html = display_priority_badge(result.label.value, result.value)
                        st.markdown(badge_html, unsafe_allow_html=True)
    
    with tab2:
        st.header("Avaliação dos Subíndices (SIF)")
        st.markdown("Avalie os subíndices do sistema.")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Seleção de SIFs")
            sif_names = [m for m in fuzzy_system.get_module_names() if m.startswith('SIF')]
            sifs_to_evaluate = st.multiselect(
                "Selecione os SIFs",
                options=sif_names,
                default=['SIF1_HAP', 'SIF3_DEH', 'SIF4_SAB']
            )
        
        with col2:
            st.subheader("Entradas para SIFs")
            
            with st.form("sif_form"):
                sif_inputs = {}
                
                for sif_name in sifs_to_evaluate:
                    with st.expander(f"📋 {sif_name}"):
                        module_info = fuzzy_system.get_module_info(sif_name)
                        input_vars = module_info.get('input_vars', [])
                        
                        for var_name in input_vars:
                            if var_name not in sif_inputs:
                                if var_name in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'E3', 'E4']:
                                    sif_inputs[var_name] = st.slider(
                                        f"{var_name}",
                                        min_value=0.0,
                                        max_value=1.0,
                                        value=0.0,
                                        step=0.1,
                                        key=f"{sif_name}_{var_name}"
                                    )
                                elif var_name in ['D1', 'D2', 'D3', 'D4']:
                                    sif_inputs[var_name] = st.slider(
                                        f"{var_name}",
                                        min_value=0.0,
                                        max_value=10.0,
                                        value=5.0,
                                        step=0.1,
                                        key=f"{sif_name}_{var_name}"
                                    )
                                elif var_name == 'E1':
                                    sif_inputs[var_name] = st.slider(
                                        f"{var_name}",
                                        min_value=0.0,
                                        max_value=100.0,
                                        value=50.0,
                                        step=1.0,
                                        key=f"{sif_name}_{var_name}"
                                    )
                                elif var_name == 'E2':
                                    sif_inputs[var_name] = st.slider(
                                        f"{var_name}",
                                        min_value=0,
                                        max_value=10,
                                        value=5,
                                        key=f"{sif_name}_{var_name}"
                                    )
                
                submit_sif_button = st.form_submit_button("Avaliar SIFs", type="primary")
        
        if submit_sif_button and sifs_to_evaluate:
            st.markdown("---")
            st.subheader("Resultados dos SIFs")
            
            sif_results = {}
            for sif_name in sifs_to_evaluate:
                try:
                    module = fuzzy_system.get_module(sif_name)
                    required_inputs = {var_name: sif_inputs.get(var_name, 0) 
                                      for var_name in module.input_vars.keys()}
                    result = fuzzy_system.evaluate_module(sif_name, required_inputs)
                    sif_results[sif_name] = result
                except Exception as e:
                    st.error(f"Erro ao avaliar {sif_name}: {e}")
                    sif_results[sif_name] = None
            
            # Exibir resultados
            cols_per_row = 2
            for i in range(0, len(sif_results), cols_per_row):
                cols = st.columns(cols_per_row)
                for j, (sif_name, result) in enumerate(list(sif_results.items())[i:i+cols_per_row]):
                    if result:
                        with cols[j]:
                            st.markdown(f"**{sif_name}**")
                            badge_html = display_priority_badge(result.label.value, result.value)
                            st.markdown(badge_html, unsafe_allow_html=True)
                            
                            # Gráfico de pertinência
                            fig, ax = plt.subplots(figsize=(6, 2))
                            labels = list(result.memberships.keys())
                            values = list(result.memberships.values())
                            colors = ['#388e3c', '#fbc02d', '#f57c00', '#d32f2f']
                            bars = ax.bar(labels, values, color=colors[:len(labels)])
                            ax.set_ylim(0, 1.1)
                            ax.set_title('Pertinência')
                            st.pyplot(fig)
            
            # Armazenar resultados para uso no índice final
            st.session_state.sif_results = {k: v.value if v else 0 for k, v in sif_results.items()}
    
    with tab3:
        st.header("Cálculo do Índice Final (ISF)")
        st.markdown("Calcule o índice final com base nos resultados dos SIFs.")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.subheader("Opção 1: Usar resultados dos SIFs")
            
            if 'sif_results' in st.session_state:
                st.info("Resultados dos SIFs já calculados na aba anterior.")
                
                for sif_name, score in st.session_state.sif_results.items():
                    st.write(f"{sif_name}: {score:.2f}")
                
                if st.button("Calcular ISF com resultados armazenados"):
                    final_result = fuzzy_system.evaluate_final_index(st.session_state.sif_results)
                    
                    st.markdown("---")
                    st.subheader("Resultado do Índice Final (ISF)")
                    
                    col_a, col_b = st.columns([1, 2])
                    with col_a:
                        badge_html = display_priority_badge(final_result.label.value, final_result.value)
                        st.markdown(badge_html, unsafe_allow_html=True)
                    
                    with col_b:
                        st.metric("Score ISF", f"{final_result.value:.2f}/100")
                        
                        # Gráfico de pertinência
                        fig, ax = plt.subplots(figsize=(8, 3))
                        labels = list(final_result.memberships.keys())
                        values = list(final_result.memberships.values())
                        colors = ['#388e3c', '#fbc02d', '#f57c00', '#d32f2f']
                        bars = ax.bar(labels, values, color=colors[:len(labels)])
                        ax.set_ylim(0, 1.1)
                        ax.set_title('Pertinência do Índice Final')
                        st.pyplot(fig)
            else:
                st.warning("Nenhum resultado de SIF armazenado. Avalie os SIFs na aba anterior.")
        
        with col2:
            st.subheader("Opção 2: Entrada manual dos SIFs")
            
            with st.form("manual_sif_form"):
                manual_sif_inputs = {}
                for sif_name in ['SIF1_HAP', 'SIF3_DEH', 'SIF4_SAB', 'SIF6_CED', 'SIF11_PSE']:
                    manual_sif_inputs[sif_name] = st.slider(
                        sif_name,
                        min_value=0.0,
                        max_value=100.0,
                        value=50.0,
                        step=1.0,
                        key=f"manual_{sif_name}"
                    )
                
                submit_manual_button = st.form_submit_button("Calcular ISF Manual", type="primary")
            
            if submit_manual_button:
                final_result = fuzzy_system.evaluate_final_index(manual_sif_inputs)
                
                st.markdown("---")
                st.subheader("Resultado do Índice Final (ISF)")
                
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    badge_html = display_priority_badge(final_result.label.value, final_result.value)
                    st.markdown(badge_html, unsafe_allow_html=True)
                
                with col_b:
                    st.metric("Score ISF", f"{final_result.value:.2f}/100")
                    
                    # Gráfico de pertinência
                    fig, ax = plt.subplots(figsize=(8, 3))
                    labels = list(final_result.memberships.keys())
                    values = list(final_result.memberships.values())
                    colors = ['#388e3c', '#fbc02d', '#f57c00', '#d32f2f']
                    bars = ax.bar(labels, values, color=colors[:len(labels)])
                    ax.set_ylim(0, 1.1)
                    ax.set_title('Pertinência do Índice Final')
                    st.pyplot(fig)
    
    with tab4:
        st.header("Documentação do Sistema")
        
        st.markdown("""
        ## 📋 Estrutura do Sistema Fuzzy Modular
        
        ### Baseado no Esquema do Grupo
        
        O sistema é organizado em três níveis:
        
        #### 📌 Nível 1: Indicadores Individuais (14)
        
        **Habitação (A):**
        - **A1**: Domicílios rústicos (0-1)
        - **A2**: Domicílios improvisados (0-1)
        - **A3**: Unidades domésticas conviventes deficit (0-1)
        - **A4**: Domicílios Cômodos (0-1)
        
        **Saneamento Básico (B):**
        - **B1**: Inadequação de Esgotamento sanitário (0-1)
        - **B2**: Inadequação da Coleta de lixo (0-1)
        - **B3**: Inadequação de Abastecimento de água (0-1)
        - **B4**: Ausência de iluminação pública (0-1)
        
        **Carência Edílica (C):**
        - **C1**: Piso ou cobertura inadequados (0-1)
        - **C2**: Inexistência de banheiro exclusivo (0-1)
        - **C3**: Cômodos igual a dormitórios (0-1)
        
        **Serviços (D):**
        - **D1**: Acesso à Educação (0-10)
        - **D2**: Acesso à Saúde (0-10)
        - **D3**: Acesso a transporte (0-10)
        - **D4**: Conectividade Digital (0-10)
        
        **Renda (E):**
        - **E1**: Renda per capita (0-100%)
        - **E2**: Número de membros empregados (0-10)
        - **E3**: Famílias atendidas pelo PBF (0-1)
        - **E4**: Famílias beneficiárias do BPC (0-1)
        
        #### 📊 Nível 2: Subíndices (SIF) - 10 implementados
        
        | SIF | Nome | Indicadores |
        |-----|------|-------------|
        | SIF 1 | HAP - Habitação Precária | A1, A2, A3, A4 |
        | SIF 2 | COA - Coabitação | A4 |
        | SIF 3 | DEH - Déficit Habitacional | A1, A2, A3 |
        | SIF 4 | SAB - Saneamento Básico | B1, B2, B3, B4 |
        | SIF 6 | CED - Carência Edílica | C1, C2, C3 |
        | SIF 7 | SGC - Serviços de Garantia Constitucional | D1, D2, D3, D4 |
        | SIF 8 | ASP - Acesso a Serviços Prioritários | D1, D2, D3 |
        | SIF 9 | RED - Renda Direta | E1, E2 |
        | SIF 10 | PTR - Programas de Transferência de Renda | E3, E4 |
        | SIF 11 | PSE - Perfil Socioeconômico | E1, E2, E3, E4 |
        
        #### 🎯 Nível 3: Índice Final
        
        **ISF - RMs**: Índice de Satisfação das Necessidades Habitacionais
        
        Agrega os principais SIFs (SIF1, SIF3, SIF4, SIF6, SIF11) para gerar um score final.
        
        ---
        
        ### 🎨 Níveis de Prioridade
        
        | Nível | Score | Significado |
        |-------|-------|-------------|
        | 🟢 Baixa | 0-39 | Prioridade normal |
        | 🟡 Média | 40-69 | Atenção moderada |
        | 🟠 Alta | 70-89 | Prioridade elevada |
        | 🔴 Urgente | 90-100 | Intervenção imediata |
        
        ---
        
        ### 🔧 Como Usar o Sistema
        
        1. **Aba Indicadores Individuais**: Avalie indicadores específicos (A1, B2, etc.)
        2. **Aba Subíndices (SIF)**: Avalie os subíndices do sistema
        3. **Aba Índice Final (ISF)**: Calcule o índice final com base nos SIFs
        
        ---
        
        ### 📚 Sobre Lógica Fuzzy
        
        A lógica fuzzy permite lidar com incertezas e conceitos vagos, sendo ideal para 
        sistemas de decisão baseados em critérios subjetivos.
        
        ---
        
        ### 🛠️ Tecnologias Utilizadas
        
        - **Streamlit**: Framework para criação de aplicações web interativas
        - **scikit-fuzzy**: Biblioteca para implementação de sistemas fuzzy
        - **NumPy**: Biblioteca para computação numérica
        - **Matplotlib**: Biblioteca para visualização de dados
        """)


if __name__ == "__main__":
    main()
