# 🏠 Sistema Fuzzy - Necessidades Habitacionais

Um sistema de inferência fuzzy para diagnóstico e priorização de necessidades habitacionais.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://share.streamlit.io/)

## 📋 Descrição

Este sistema utiliza lógica fuzzy para avaliar a prioridade de atendimento habitacional com base em quatro critérios:
- **Renda familiar** (em salários mínimos)
- **Número de moradores**
- **Condição da moradia** (escala 0-10)
- **Acesso a serviços** (escala 0-10)

O resultado indica uma das quatro categorias de prioridade: **Baixa, Média, Alta ou Urgente**.

## 🚀 Como Executar

### Pré-requisitos

Instale o `uv` (gerenciador de pacotes):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Instalação e Execução

1. Sincronize as dependências:

   ```bash
   uv sync
   ```

2. Execute a aplicação:

   ```bash
   uv run streamlit run streamlit_app.py
   ```

Ou utilize o pip tradicional:

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## 📊 Funcionalidades

- **Avaliação Interativa**: Interface intuitiva para inserção de dados
- **Análise Detalhada**: Visualização das funções de pertinência
- **Regras Fuzzy**: Exibição das regras do sistema
- **Visualização**: Gráficos de pertinência e resultados

## 🎯 Variáveis do Sistema

### Variáveis de Entrada

| Variável | Tipo | Faixa | Categorias |
|----------|------|-------|------------|
| Renda | Antecedent | 0-20 SM | Baixa, Média, Alta |
| Moradores | Antecedent | 1-10 | Poucos, Médio, Muitos |
| Condição | Antecedent | 0-10 | Ruim, Regular, Boa |
| Serviços | Antecedent | 0-10 | Baixo, Médio, Alto |

### Variável de Saída

| Variável | Tipo | Faixa | Categorias |
|----------|------|-------|------------|
| Prioridade | Consequent | 0-100 | Baixa, Média, Alta, Urgente |

## 🔧 Arquitetura

```
fuzzy_system.py          # Módulo do sistema fuzzy
streamlit_app.py         # Interface Streamlit
pyproject.toml          # Dependências do projeto
```

## 📚 Sobre Lógica Fuzzy

A lógica fuzzy permite lidar com incertezas e conceitos vagos, sendo ideal para sistemas de decisão baseados em critérios subjetivos. Este sistema implementa:

1. **Fuzzificação**: Conversão de valores numéricos em graus de pertinência
2. **Inferência**: Aplicação de regras fuzzy para determinar a prioridade
3. **Defuzzificação**: Conversão do resultado fuzzy em valor interpretável

## 🎨 Interface

A aplicação Streamlit oferece:
- Aba **Avaliação**: Para inserção de dados e obtenção de resultados
- Aba **Análise Detalhada**: Para visualização das funções de pertinência e regras
- Aba **Sobre**: Documentação do sistema

## 📈 Exemplo de Uso

```python
from fuzzy_system import FuzzyHousingSystem

# Criar o sistema
fuzzy_system = FuzzyHousingSystem()

# Avaliar uma família
result = fuzzy_system.evaluate(
    income_value=3.5,           # 3.5 salários mínimos
    residents_value=6,          # 6 moradores
    housing_condition_value=2,  # Condição ruim
    service_access_value=3      # Acesso baixo a serviços
)

print(f"Prioridade: {result['priority_label']}")
print(f"Score: {result['priority_value']:.2f}")
```

## 🤝 Contribuição

Contribuições são bem-vindas! Sinta-se à vontade para:
- Reportar bugs
- Sugerir melhorias
- Adicionar novas funcionalidades

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.
