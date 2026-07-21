"""
Aplicação Streamlit para Diagnóstico de Necessidades Habitacionais

Sistema Fuzzy para avaliação de prioridade de atendimento habitacional.
"""

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
from fuzzy_system import FuzzyHousingSystem


# Configuração da página
st.set_page_config(
    page_title="Sistema Fuzzy - Necessidades Habitacionais",
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
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .priority-badge {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        text-align: center;
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


def main():
    """Função principal da aplicação."""
    
    # Header
    st.markdown('<p class="main-header">🏠 Sistema Fuzzy - Necessidades Habitacionais</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Diagnóstico de Prioridade de Atendimento</p>', unsafe_allow_html=True)
    
    # Inicializar o sistema fuzzy
    fuzzy_system = FuzzyHousingSystem()
    
    # Sidebar com informações
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/house-plan.png", width=80)
        st.title("Sobre o Sistema")
        st.markdown("""
        Este sistema utiliza lógica fuzzy para avaliar a prioridade de atendimento 
        habitacional com base em:
        
        - **Renda familiar** (salários mínimos)
        - **Número de moradores**
        - **Condição da moradia** (0-10)
        - **Acesso a serviços** (0-10)
        
        O resultado indica a prioridade de atendimento: **Baixa, Média, Alta ou Urgente**.
        """)
        
        st.markdown("---")
        st.markdown("### Legenda")
        st.markdown("**🟢 Baixa**: Prioridade normal")
        st.markdown("**🟡 Média**: Atenção moderada")
        st.markdown("**🟠 Alta**: Prioridade elevada")
        st.markdown("**🔴 Urgente**: Intervenção imediata")
    
    # Abas principais
    tab1, tab2, tab3 = st.tabs(["📊 Avaliação", "📈 Análise Detalhada", "ℹ️ Sobre"])
    
    with tab1:
        # Formulário de entrada
        st.header("Avaliação de Necessidades Habitacionais")
        
        with st.form("evaluation_form"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Dados da Família")
                
                income = st.slider(
                    "Renda familiar (salários mínimos)",
                    min_value=0.0,
                    max_value=20.0,
                    value=5.0,
                    step=0.1,
                    help="Renda mensal total da família em salários mínimos"
                )
                
                residents = st.slider(
                    "Número de moradores",
                    min_value=1,
                    max_value=10,
                    value=4,
                    help="Número total de pessoas que residem no local"
                )
            
            with col2:
                st.subheader("Condições Habitacionais")
                
                housing_condition = st.slider(
                    "Condição da moradia (0-10)",
                    min_value=0.0,
                    max_value=10.0,
                    value=5.0,
                    step=0.1,
                    help="0 = Ruim, 5 = Regular, 10 = Excelente"
                )
                
                service_access = st.slider(
                    "Acesso a serviços (0-10)",
                    min_value=0.0,
                    max_value=10.0,
                    value=5.0,
                    step=0.1,
                    help="Acesso a água, esgoto, energia, saúde, educação, etc."
                )
            
            submit_button = st.form_submit_button("Avaliar Prioridade", type="primary")
        
        if submit_button:
            # Processar a avaliação
            result = fuzzy_system.evaluate(
                income_value=income,
                residents_value=residents,
                housing_condition_value=housing_condition,
                service_access_value=service_access
            )
            
            # Exibir resultados
            st.markdown("---")
            st.subheader("Resultado da Avaliação")
            
            # Badge de prioridade
            priority_class = {
                'BAIXA': 'priority-low',
                'MÉDIA': 'priority-medium',
                'ALTA': 'priority-high',
                'URGENTE': 'priority-urgent'
            }.get(result['priority_label'], 'priority-medium')
            
            st.markdown(f"""
                <div class="priority-badge {priority_class}">
                    {result['priority_label']}
                </div>
            """, unsafe_allow_html=True)
            
            # Score de prioridade
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Renda", f"{result['inputs']['income']:.1f} SM")
            with col2:
                st.metric("Moradores", f"{int(result['inputs']['residents'])}")
            with col3:
                st.metric("Condição", f"{result['inputs']['housing_condition']:.1f}/10")
            with col4:
                st.metric("Serviços", f"{result['inputs']['service_access']:.1f}/10")
            
            # Score de prioridade
            st.metric("Score de Prioridade", f"{result['priority_value']:.1f}/100")
            
            # Gráfico de pertinência
            st.subheader("Graus de Pertinência")
            
            membership_data = result['memberships']
            labels = list(membership_data.keys())
            values = list(membership_data.values())
            
            fig, ax = plt.subplots(figsize=(10, 4))
            bars = ax.bar(labels, values, color=['#388e3c', '#fbc02d', '#f57c00', '#d32f2f'])
            ax.set_ylabel('Grau de Pertinência')
            ax.set_ylim(0, 1.1)
            ax.set_title('Pertinência a cada categoria de prioridade')
            
            # Adicionar valores nos bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.02, 
                       f'{height:.2f}', ha='center', va='bottom')
            
            st.pyplot(fig)
    
    with tab2:
        st.header("Análise Detalhada do Sistema Fuzzy")
        
        st.markdown("""
        ### Funções de Pertinência
        
        O sistema fuzzy utiliza funções de pertinência triangulares para representar 
        as variáveis linguísticas de entrada e saída.
        """)
        
        # Obter dados das funções de pertinência
        membership_plots = fuzzy_system.get_membership_plots()
        
        # Plotar funções de pertinência para cada variável
        st.subheader("Variáveis de Entrada")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Renda Familiar")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(membership_plots['income']['universe'], 
                   membership_plots['income']['low'], label='Baixa', color='red')
            ax.plot(membership_plots['income']['universe'], 
                   membership_plots['income']['medium'], label='Média', color='blue')
            ax.plot(membership_plots['income']['universe'], 
                   membership_plots['income']['high'], label='Alta', color='green')
            ax.set_xlabel('Salários Mínimos')
            ax.set_ylabel('Pertinência')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
            st.markdown("#### Número de Moradores")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(membership_plots['residents']['universe'], 
                   membership_plots['residents']['few'], label='Poucos', color='red')
            ax.plot(membership_plots['residents']['universe'], 
                   membership_plots['residents']['medium'], label='Médio', color='blue')
            ax.plot(membership_plots['residents']['universe'], 
                   membership_plots['residents']['many'], label='Muitos', color='green')
            ax.set_xlabel('Número de Moradores')
            ax.set_ylabel('Pertinência')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        
        with col2:
            st.markdown("#### Condição da Moradia")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(membership_plots['housing_condition']['universe'], 
                   membership_plots['housing_condition']['bad'], label='Ruim', color='red')
            ax.plot(membership_plots['housing_condition']['universe'], 
                   membership_plots['housing_condition']['regular'], label='Regular', color='blue')
            ax.plot(membership_plots['housing_condition']['universe'], 
                   membership_plots['housing_condition']['good'], label='Boa', color='green')
            ax.set_xlabel('Condição (0-10)')
            ax.set_ylabel('Pertinência')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
            
            st.markdown("#### Acesso a Serviços")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(membership_plots['service_access']['universe'], 
                   membership_plots['service_access']['low'], label='Baixo', color='red')
            ax.plot(membership_plots['service_access']['universe'], 
                   membership_plots['service_access']['medium'], label='Médio', color='blue')
            ax.plot(membership_plots['service_access']['universe'], 
                   membership_plots['service_access']['high'], label='Alto', color='green')
            ax.set_xlabel('Acesso (0-10)')
            ax.set_ylabel('Pertinência')
            ax.legend()
            ax.grid(True, alpha=0.3)
            st.pyplot(fig)
        
        # Variável de saída
        st.subheader("Variável de Saída")
        st.markdown("#### Prioridade de Atendimento")
        
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(membership_plots['priority']['universe'], 
               membership_plots['priority']['low'], label='Baixa', color='green')
        ax.plot(membership_plots['priority']['universe'], 
               membership_plots['priority']['medium'], label='Média', color='orange')
        ax.plot(membership_plots['priority']['universe'], 
               membership_plots['priority']['high'], label='Alta', color='red')
        ax.plot(membership_plots['priority']['universe'], 
               membership_plots['priority']['urgent'], label='Urgente', color='darkred')
        ax.set_xlabel('Score de Prioridade (0-100)')
        ax.set_ylabel('Pertinência')
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)
        
        # Exibir regras fuzzy
        st.subheader("Regras Fuzzy do Sistema")
        st.markdown("""
        O sistema utiliza as seguintes regras para determinar a prioridade:
        
        **Regras para URGENTE:**
        - SE (renda = baixa) E (condição = ruim) E (serviços = baixo) ENTÃO prioridade = urgente
        - SE (renda = baixa) E (condição = ruim) E (moradores = muitos) ENTÃO prioridade = urgente
        - SE (condição = ruim) E (serviços = baixo) E (moradores = muitos) ENTÃO prioridade = urgente
        
        **Regras para ALTA:**
        - SE (renda = baixa) E (condição = ruim) ENTÃO prioridade = alta
        - SE (renda = baixa) E (serviços = baixo) ENTÃO prioridade = alta
        - SE (condição = ruim) E (moradores = muitos) ENTÃO prioridade = alta
        - SE (renda = baixa) E (moradores = muitos) ENTÃO prioridade = alta
        
        **Regras para MÉDIA:**
        - SE (renda = média) E (condição = regular) ENTÃO prioridade = média
        - SE (renda = baixa) E (condição = regular) E (serviços = médio) ENTÃO prioridade = média
        - SE (renda = média) E (serviços = baixo) ENTÃO prioridade = média
        - SE (condição = regular) E (moradores = muitos) ENTÃO prioridade = média
        
        **Regras para BAIXA:**
        - SE (renda = alta) E (condição = boa) ENTÃO prioridade = baixa
        - SE (renda = alta) E (serviços = alto) ENTÃO prioridade = baixa
        - SE (condição = boa) E (serviços = alto) ENTÃO prioridade = baixa
        - SE (renda = média) E (condição = boa) E (serviços = alto) ENTÃO prioridade = baixa
        """)
    
    with tab3:
        st.header("Sobre o Sistema")
        
        st.markdown("""
        ## Sistema Fuzzy para Diagnóstico de Necessidades Habitacionais
        
        ### O que é Lógica Fuzzy?
        
        A lógica fuzzy (ou nebulosa) é uma extensão da lógica booleana que permite 
        lidar com incertezas e conceitos vagos. Ao contrário da lógica tradicional 
        que usa apenas valores binários (0 ou 1, verdadeiro ou falso), a lógica fuzzy 
        permite graus de pertinência entre 0 e 1.
        
        ### Como o Sistema Funciona?
        
        1. **Fuzzificação**: Os valores de entrada (renda, moradores, condição, serviços) 
           são convertidos em graus de pertinência para cada categoria fuzzy.
        
        2. **Aplicação das Regras**: As regras fuzzy são aplicadas para determinar 
           a prioridade com base nas combinações dos valores de entrada.
        
        3. **Defuzzificação**: O resultado fuzzy é convertido em um valor numérico 
           (score de prioridade) que pode ser interpretado.
        
        ### Aplicação em Políticas Públicas
        
        Este sistema pode ser utilizado por órgãos públicos para:
        - Priorizar famílias em programas habitacionais
        - Alocar recursos de forma mais eficiente
        - Identificar situações de maior vulnerabilidade
        - Auxiliar na tomada de decisão baseada em múltiplos critérios
        
        ### Tecnologias Utilizadas
        
        - **Streamlit**: Framework para criação de aplicações web interativas
        - **scikit-fuzzy**: Biblioteca para implementação de sistemas fuzzy
        - **NumPy**: Biblioteca para computação numérica
        - **Matplotlib**: Biblioteca para visualização de dados
        
        ### Desenvolvedor
        
        Sistema desenvolvido para análise de necessidades habitacionais utilizando 
        inteligência computacional.
        """)
        
        st.markdown("---")
        st.markdown("### Referências")
        st.markdown("""
        - Zadeh, L. A. (1965). Fuzzy sets. Information and Control, 8(3), 338-353.
        - Ross, T. J. (2010). Fuzzy Logic with Engineering Applications. Wiley.
        - scikit-fuzzy documentation: https://pythonhosted.org/scikit-fuzzy/
        """)


if __name__ == "__main__":
    main()
