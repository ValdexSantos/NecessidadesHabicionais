# 🏠 Sistema Fuzzy Modular - Necessidades Habitacionais

Um sistema de inferência fuzzy **modular** para diagnóstico e priorização de necessidades habitacionais, baseado no esquema do grupo.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## 📋 Descrição

Este sistema implementa uma arquitetura modular para avaliar necessidades habitacionais em três níveis:

### 📌 Nível 1: Indicadores Individuais (14)
- **Habitação (A)**: A1, A2, A3, A4
- **Saneamento (B)**: B1, B2, B3, B4
- **Edificação (C)**: C1, C2, C3
- **Serviços (D)**: D1, D2, D3, D4
- **Renda (E)**: E1, E2, E3, E4

### 📊 Nível 2: Subíndices (SIF) - 10 implementados
- SIF 1 - HAP (Habitação Precária)
- SIF 2 - COA (Coabitação)
- SIF 3 - DEH (Déficit Habitacional)
- SIF 4 - SAB (Saneamento Básico)
- SIF 6 - CED (Carência Edílica)
- SIF 7 - SGC (Serviços de Garantia Constitucional)
- SIF 8 - ASP (Acesso a Serviços Prioritários)
- SIF 9 - RED (Renda Direta)
- SIF 10 - PTR (Programas de Transferência de Renda)
- SIF 11 - PSE (Perfil Socioeconômico)

### 🎯 Nível 3: Índice Final
- **ISF - RMs**: Índice de Satisfação das Necessidades Habitacionais

## 🚀 Como Executar

### Pré-requisitos

```bash
pip install streamlit scikit-fuzzy numpy matplotlib scipy networkx
```

### Execução

```bash
streamlit run streamlit_app.py
```

## 📊 Funcionalidades

### Aba 1: Indicadores Individuais
- Selecione indicadores por categoria (Habitação, Saneamento, Edificação, Serviços, Renda)
- Avalie cada indicador individualmente
- Visualize a prioridade de cada indicador

### Aba 2: Subíndices (SIF)
- Selecione os SIFs que deseja avaliar
- Insira os valores dos indicadores necessários para cada SIF
- Visualize a prioridade de cada SIF
- Resultados são armazenados para uso no índice final

### Aba 3: Índice Final (ISF)
- Calcule o índice final usando resultados armazenados dos SIFs
- Ou insira manualmente os valores dos SIFs
- Visualize a prioridade final

### Aba 4: Documentação
- Documentação completa do sistema
- Estrutura dos módulos
- Níveis de prioridade

## 🎨 Níveis de Prioridade

| Nível | Score | Significado |
|-------|-------|-------------|
| 🟢 **BAIXA** | 0-39 | Prioridade normal |
| 🟡 **MÉDIA** | 40-69 | Atenção moderada |
| 🟠 **ALTA** | 70-89 | Prioridade elevada |
| 🔴 **URGENTE** | 90-100 | Intervenção imediata |

## 📚 Sobre Lógica Fuzzy

A lógica fuzzy permite lidar com incertezas e conceitos vagos, sendo ideal para sistemas de decisão baseados em critérios subjetivos. Este sistema implementa:

1. **Fuzzificação**: Conversão de valores numéricos em graus de pertinência
2. **Inferência**: Aplicação de regras fuzzy para determinar a prioridade
3. **Defuzzificação**: Conversão do resultado fuzzy em valor interpretável (0-100)

## 🛠️ Tecnologias Utilizadas

- **Streamlit**: Framework para criação de aplicações web interativas
- **scikit-fuzzy**: Biblioteca para implementação de sistemas fuzzy
- **NumPy**: Biblioteca para computação numérica
- **Matplotlib**: Biblioteca para visualização de dados
- **SciPy**: Biblioteca para computação científica
- **NetworkX**: Biblioteca para manipulação de grafos

## 📁 Estrutura do Projeto

```
.
├── fuzzy_system.py          # Módulo do sistema fuzzy (25KB)
├── streamlit_app.py         # Interface Streamlit (22KB)
├── Esquema_Grupo.pdf       # Esquema de referência
├── pyproject.toml          # Dependências do projeto
├── requirements.txt         # Dependências para pip
└── README.md                # Documentação
```

## 🎯 Exemplo de Uso

```python
from fuzzy_system import HousingFuzzySystem

# Criar o sistema
fuzzy_system = HousingFuzzySystem()

# Avaliar um indicador individual
result = fuzzy_system.evaluate_module('A1', {'A1': 1.0})
print(f"A1: {result.label.value} ({result.value:.2f})")

# Avaliar um SIF
result = fuzzy_system.evaluate_module('SIF1_HAP', {
    'A1': 1.0, 'A2': 0.0, 'A3': 1.0, 'A4': 0.0
})
print(f"SIF1_HAP: {result.label.value} ({result.value:.2f})")

# Avaliar o índice final
sif_results = {
    'SIF1_HAP': 85.0,
    'SIF3_DEH': 70.0,
    'SIF4_SAB': 90.0,
    'SIF6_CED': 75.0,
    'SIF11_PSE': 85.0
}
result = fuzzy_system.evaluate_final_index(sif_results)
print(f"ISF: {result.label.value} ({result.value:.2f})")
```

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novos módulos
- Expandir os SIFs existentes

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
