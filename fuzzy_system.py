"""
Sistema Fuzzy para Diagnóstico de Necessidades Habitacionais

Este módulo implementa um sistema de inferência fuzzy para avaliar 
as necessidades habitacionais com base em múltiplos critérios.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyHousingSystem:
    """
    Sistema Fuzzy para avaliação de necessidades habitacionais.
    
    Variáveis de entrada:
    - Renda familiar (baixa, média, alta)
    - Número de moradores (poucos, médio, muitos)
    - Condição da moradia (ruim, regular, boa)
    - Acesso a serviços (baixo, médio, alto)
    
    Variável de saída:
    - Prioridade de atendimento (baixa, média, alta, urgente)
    """
    
    def __init__(self):
        self._initialize_variables()
        self._initialize_rules()
        self._create_control_system()
    
    def _initialize_variables(self):
        """Inicializa as variáveis fuzzy de entrada e saída."""
        
        # Renda familiar (em salários mínimos)
        self.income = ctrl.Antecedent(np.arange(0, 21, 0.1), 'income')
        self.income['low'] = fuzz.trimf(self.income.universe, [0, 0, 5])
        self.income['medium'] = fuzz.trimf(self.income.universe, [2, 7, 12])
        self.income['high'] = fuzz.trimf(self.income.universe, [8, 15, 20])
        
        # Número de moradores
        self.residents = ctrl.Antecedent(np.arange(0, 11, 1), 'residents')
        self.residents['few'] = fuzz.trimf(self.residents.universe, [0, 0, 3])
        self.residents['medium'] = fuzz.trimf(self.residents.universe, [1, 4, 6])
        self.residents['many'] = fuzz.trimf(self.residents.universe, [4, 8, 10])
        
        # Condição da moradia (0-10)
        self.housing_condition = ctrl.Antecedent(np.arange(0, 11, 0.1), 'housing_condition')
        self.housing_condition['bad'] = fuzz.trimf(self.housing_condition.universe, [0, 0, 4])
        self.housing_condition['regular'] = fuzz.trimf(self.housing_condition.universe, [2, 5, 7])
        self.housing_condition['good'] = fuzz.trimf(self.housing_condition.universe, [6, 10, 10])
        
        # Acesso a serviços (0-10)
        self.service_access = ctrl.Antecedent(np.arange(0, 11, 0.1), 'service_access')
        self.service_access['low'] = fuzz.trimf(self.service_access.universe, [0, 0, 4])
        self.service_access['medium'] = fuzz.trimf(self.service_access.universe, [2, 5, 7])
        self.service_access['high'] = fuzz.trimf(self.service_access.universe, [6, 10, 10])
        
        # Prioridade de atendimento (0-100)
        self.priority = ctrl.Consequent(np.arange(0, 101, 1), 'priority')
        self.priority['low'] = fuzz.trimf(self.priority.universe, [0, 0, 35])
        self.priority['medium'] = fuzz.trimf(self.priority.universe, [25, 50, 75])
        self.priority['high'] = fuzz.trimf(self.priority.universe, [65, 85, 100])
        self.priority['urgent'] = fuzz.trimf(self.priority.universe, [90, 100, 100])
    
    def _initialize_rules(self):
        """Define as regras fuzzy para o sistema."""
        self.rules = []
        
        # Regras para prioridade URGENTE
        self.rules.append(ctrl.Rule(
            self.income['low'] & 
            self.housing_condition['bad'] & 
            self.service_access['low'],
            self.priority['urgent']
        ))
        
        self.rules.append(ctrl.Rule(
            self.income['low'] & 
            self.housing_condition['bad'] & 
            self.residents['many'],
            self.priority['urgent']
        ))
        
        self.rules.append(ctrl.Rule(
            self.housing_condition['bad'] & 
            self.service_access['low'] & 
            self.residents['many'],
            self.priority['urgent']
        ))
        
        # Regras para prioridade ALTA
        self.rules.append(ctrl.Rule(
            self.income['low'] & 
            self.housing_condition['bad'],
            self.priority['high']
        ))
        
        self.rules.append(ctrl.Rule(
            self.income['low'] & 
            self.service_access['low'],
            self.priority['high']
        ))
        
        self.rules.append(ctrl.Rule(
            self.housing_condition['bad'] & 
            self.residents['many'],
            self.priority['high']
        ))
        
        self.rules.append(ctrl.Rule(
            self.income['low'] & 
            self.residents['many'],
            self.priority['high']
        ))
        
        # Regras para prioridade MÉDIA
        self.rules.append(ctrl.Rule(
            self.income['medium'] & 
            self.housing_condition['regular'],
            self.priority['medium']
        ))
        
        self.rules.append(ctrl.Rule(
            self.income['low'] & 
            self.housing_condition['regular'] & 
            self.service_access['medium'],
            self.priority['medium']
        ))
        
        self.rules.append(ctrl.Rule(
            self.income['medium'] & 
            self.service_access['low'],
            self.priority['medium']
        ))
        
        self.rules.append(ctrl.Rule(
            self.housing_condition['regular'] & 
            self.residents['many'],
            self.priority['medium']
        ))
        
        # Regras para prioridade BAIXA
        self.rules.append(ctrl.Rule(
            self.income['high'] & 
            self.housing_condition['good'],
            self.priority['low']
        ))
        
        self.rules.append(ctrl.Rule(
            self.income['high'] & 
            self.service_access['high'],
            self.priority['low']
        ))
        
        self.rules.append(ctrl.Rule(
            self.housing_condition['good'] & 
            self.service_access['high'],
            self.priority['low']
        ))
        
        self.rules.append(ctrl.Rule(
            self.income['medium'] & 
            self.housing_condition['good'] & 
            self.service_access['high'],
            self.priority['low']
        ))
    
    def _create_control_system(self):
        """Cria o sistema de controle fuzzy."""
        self.ctrl_system = ctrl.ControlSystem(self.rules)
        self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)
    
    def evaluate(self, income_value, residents_value, housing_condition_value, service_access_value):
        """
        Avalia a prioridade de atendimento com base nos valores de entrada.
        
        Args:
            income_value: Renda familiar em salários mínimos
            residents_value: Número de moradores
            housing_condition_value: Condição da moradia (0-10)
            service_access_value: Acesso a serviços (0-10)
        
        Returns:
            dict: Resultado com a prioridade e valores de pertinência
        """
        # Limpar inputs anteriores
        self.simulation.inputs(dict(zip(
            ['income', 'residents', 'housing_condition', 'service_access'],
            [income_value, residents_value, housing_condition_value, service_access_value]
        )))
        
        # Computar o resultado
        self.simulation.compute()
        
        # Obter o valor de prioridade
        priority_value = self.simulation.output['priority']
        
        # Calcular pertinência a cada categoria
        memberships = {
            'low': fuzz.interp_membership(
                self.priority.universe, 
                self.priority['low'].mf, 
                priority_value
            ),
            'medium': fuzz.interp_membership(
                self.priority.universe, 
                self.priority['medium'].mf, 
                priority_value
            ),
            'high': fuzz.interp_membership(
                self.priority.universe, 
                self.priority['high'].mf, 
                priority_value
            ),
            'urgent': fuzz.interp_membership(
                self.priority.universe, 
                self.priority['urgent'].mf, 
                priority_value
            )
        }
        
        # Classificar a prioridade
        priority_label = self._classify_priority(priority_value, memberships)
        
        return {
            'priority_value': float(priority_value),
            'priority_label': priority_label,
            'memberships': memberships,
            'inputs': {
                'income': income_value,
                'residents': residents_value,
                'housing_condition': housing_condition_value,
                'service_access': service_access_value
            }
        }
    
    def _classify_priority(self, priority_value, memberships):
        """Classifica a prioridade com base no valor e pertinências."""
        # Se pertinência a urgente for significativa
        if memberships['urgent'] > 0.5:
            return 'URGENTE'
        elif memberships['high'] > 0.5:
            return 'ALTA'
        elif memberships['medium'] > 0.5:
            return 'MÉDIA'
        elif memberships['low'] > 0.5:
            return 'BAIXA'
        else:
            # Usar o valor numérico para classificar
            if priority_value >= 90:
                return 'URGENTE'
            elif priority_value >= 70:
                return 'ALTA'
            elif priority_value >= 40:
                return 'MÉDIA'
            else:
                return 'BAIXA'
    
    def get_membership_plots(self):
        """Retorna dados para plotagem das funções de pertinência."""
        return {
            'income': {
                'universe': self.income.universe,
                'low': self.income['low'].mf,
                'medium': self.income['medium'].mf,
                'high': self.income['high'].mf
            },
            'residents': {
                'universe': self.residents.universe,
                'few': self.residents['few'].mf,
                'medium': self.residents['medium'].mf,
                'many': self.residents['many'].mf
            },
            'housing_condition': {
                'universe': self.housing_condition.universe,
                'bad': self.housing_condition['bad'].mf,
                'regular': self.housing_condition['regular'].mf,
                'good': self.housing_condition['good'].mf
            },
            'service_access': {
                'universe': self.service_access.universe,
                'low': self.service_access['low'].mf,
                'medium': self.service_access['medium'].mf,
                'high': self.service_access['high'].mf
            },
            'priority': {
                'universe': self.priority.universe,
                'low': self.priority['low'].mf,
                'medium': self.priority['medium'].mf,
                'high': self.priority['high'].mf,
                'urgent': self.priority['urgent'].mf
            }
        }


def create_fuzzy_system():
    """Factory function para criar o sistema fuzzy."""
    return FuzzyHousingSystem()
