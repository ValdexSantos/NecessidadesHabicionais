"""
Sistema Fuzzy Modular para Diagnóstico de Necessidades Habitacionais

Este módulo implementa um sistema de inferência fuzzy MODULAR para avaliar 
as necessidades habitacionais com base no esquema do grupo.

Estrutura:
- Indicadores individuais (A1, A2, B1, B2, C1, C2, D1, D2, E1, E2, E3, E4)
- Subíndices (SIF 1-12)
- Índice Final (ISF - RMs)

Cada módulo pode ser simulado individualmente ou em conjunto.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum


class PriorityLevel(Enum):
    """Níveis de prioridade do sistema."""
    LOW = "BAIXA"
    MEDIUM = "MÉDIA"
    HIGH = "ALTA"
    URGENT = "URGENTE"


@dataclass
class FuzzyResult:
    """Resultado de uma avaliação fuzzy."""
    value: float
    label: PriorityLevel
    memberships: Dict[str, float]
    inputs: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        """Converte para dicionário."""
        return {
            'value': self.value,
            'label': self.label.value,
            'memberships': self.memberships,
            'inputs': self.inputs
        }


class FuzzyModule:
    """Módulo fuzzy genérico para qualquer subíndice."""
    
    def __init__(self, name: str):
        """
        Inicializa um módulo fuzzy.
        
        Args:
            name: Nome do módulo
        """
        self.name = name
        self.ctrl_system = None
        self.simulation = None
        self.input_ranges: Dict[str, Tuple[float, float, float]] = {}
    
    def build_system(self, input_ranges: Dict[str, Tuple[float, float, float]],
                    rules: List[Any],
                    output_range: Tuple[float, float, float] = (0, 100, 1)):
        """
        Constrói o sistema de controle fuzzy.
        
        Args:
            input_ranges: Dicionário com faixas para cada entrada {var_name: (min, max, step)}
            rules: Lista de regras fuzzy
            output_range: Faixa para a saída (min, max, step)
        """
        self.input_ranges = input_ranges
        
        # Criar antecedentes
        antecedents = {}
        for var_name, (min_val, max_val, step) in input_ranges.items():
            universe = np.arange(min_val, max_val + step, step)
            antecedents[var_name] = ctrl.Antecedent(universe, var_name)
        
        # Criar consequente
        universe = np.arange(output_range[0], output_range[1] + output_range[2], output_range[2])
        consequent = ctrl.Consequent(universe, 'priority')
        
        # Adicionar funções de pertinência para cada antecedente
        for var_name, ante in antecedents.items():
            if var_name in ['A1', 'A2', 'A3', 'A4', 'B1', 'B2', 'B3', 'B4', 'C1', 'C2', 'C3', 'E3', 'E4']:
                ante['no'] = fuzz.trimf(ante.universe, [0, 0, 0.5])
                ante['yes'] = fuzz.trimf(ante.universe, [0.5, 1, 1])
            elif var_name in ['D1', 'D2', 'D3', 'D4']:
                ante['low'] = fuzz.trimf(ante.universe, [0, 0, 4])
                ante['medium'] = fuzz.trimf(ante.universe, [2, 5, 7])
                ante['high'] = fuzz.trimf(ante.universe, [6, 10, 10])
            elif var_name == 'E1':
                ante['low'] = fuzz.trimf(ante.universe, [0, 0, 33])
                ante['medium'] = fuzz.trimf(ante.universe, [25, 50, 75])
                ante['high'] = fuzz.trimf(ante.universe, [67, 100, 100])
            elif var_name == 'E2':
                ante['low'] = fuzz.trimf(ante.universe, [0, 0, 3])
                ante['medium'] = fuzz.trimf(ante.universe, [2, 5, 7])
                ante['high'] = fuzz.trimf(ante.universe, [6, 10, 10])
            else:
                ante['low'] = fuzz.trimf(ante.universe, [0, 0, 35])
                ante['medium'] = fuzz.trimf(ante.universe, [25, 50, 75])
                ante['high'] = fuzz.trimf(ante.universe, [65, 85, 100])
                ante['urgent'] = fuzz.trimf(ante.universe, [90, 100, 100])
        
        # Adicionar funções de pertinência para o consequente
        consequent['low'] = fuzz.trimf(consequent.universe, [0, 0, 35])
        consequent['medium'] = fuzz.trimf(consequent.universe, [25, 50, 75])
        consequent['high'] = fuzz.trimf(consequent.universe, [65, 85, 100])
        consequent['urgent'] = fuzz.trimf(consequent.universe, [90, 100, 100])
        
        # Criar regras
        rule_list = []
        for rule in rules:
            rule_list.append(rule)
        
        self.ctrl_system = ctrl.ControlSystem(rule_list)
        self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)
        self.antecedents = antecedents
        self.consequent = consequent
    
    def evaluate(self, inputs: Dict[str, float]) -> FuzzyResult:
        """
        Avalia o módulo com os valores de entrada.
        
        Args:
            inputs: Dicionário com valores para cada variável de entrada
        
        Returns:
            FuzzyResult com o resultado da avaliação
        """
        # Validar entradas
        for var_name in self.input_ranges.keys():
            if var_name not in inputs:
                raise ValueError(f"Missing input: {var_name}")
        
        # Configurar entradas
        input_dict = {var_name: inputs[var_name] for var_name in self.input_ranges.keys()}
        self.simulation.inputs(input_dict)
        
        # Computar
        try:
            self.simulation.compute()
        except Exception as e:
            return FuzzyResult(
                value=0.0,
                label=PriorityLevel.LOW,
                memberships={'low': 1.0, 'medium': 0.0, 'high': 0.0, 'urgent': 0.0},
                inputs=inputs
            )
        
        # Obter resultado
        output_value = self.simulation.output['priority']
        
        # Calcular pertinências
        memberships = {}
        for mf_name in ['low', 'medium', 'high', 'urgent']:
            try:
                memberships[mf_name] = float(fuzz.interp_membership(
                    self.consequent.universe,
                    getattr(self.consequent, mf_name).mf,
                    output_value
                ))
            except:
                memberships[mf_name] = 0.0
        
        # Classificar prioridade
        label = self._classify_priority(output_value, memberships)
        
        return FuzzyResult(
            value=float(output_value),
            label=label,
            memberships=memberships,
            inputs=inputs
        )
    
    def _classify_priority(self, value: float, memberships: Dict[str, float]) -> PriorityLevel:
        """Classifica o nível de prioridade."""
        if memberships.get('urgent', 0) > 0.5:
            return PriorityLevel.URGENT
        elif memberships.get('high', 0) > 0.5:
            return PriorityLevel.HIGH
        elif memberships.get('medium', 0) > 0.5:
            return PriorityLevel.MEDIUM
        else:
            return PriorityLevel.LOW


def create_boolean_antecedent(name: str) -> ctrl.Antecedent:
    """Cria um antecedente booleano (0-1)."""
    universe = np.arange(0, 1.1, 0.1)
    ante = ctrl.Antecedent(universe, name)
    ante['no'] = fuzz.trimf(ante.universe, [0, 0, 0.5])
    ante['yes'] = fuzz.trimf(ante.universe, [0.5, 1, 1])
    return ante


def create_access_antecedent(name: str) -> ctrl.Antecedent:
    """Cria um antecedente de acesso (0-10)."""
    universe = np.arange(0, 10.1, 0.1)
    ante = ctrl.Antecedent(universe, name)
    ante['low'] = fuzz.trimf(ante.universe, [0, 0, 4])
    ante['medium'] = fuzz.trimf(ante.universe, [2, 5, 7])
    ante['high'] = fuzz.trimf(ante.universe, [6, 10, 10])
    return ante


def create_percentage_antecedent(name: str) -> ctrl.Antecedent:
    """Cria um antecedente de porcentagem (0-100)."""
    universe = np.arange(0, 101, 1)
    ante = ctrl.Antecedent(universe, name)
    ante['low'] = fuzz.trimf(ante.universe, [0, 0, 33])
    ante['medium'] = fuzz.trimf(ante.universe, [25, 50, 75])
    ante['high'] = fuzz.trimf(ante.universe, [67, 100, 100])
    return ante


def create_count_antecedent(name: str, max_val: int = 10) -> ctrl.Antecedent:
    """Cria um antecedente de contagem (0-max_val)."""
    universe = np.arange(0, max_val + 1, 1)
    ante = ctrl.Antecedent(universe, name)
    ante['low'] = fuzz.trimf(ante.universe, [0, 0, max_val // 3])
    ante['medium'] = fuzz.trimf(ante.universe, [max_val // 3, max_val // 2, 2 * max_val // 3])
    ante['high'] = fuzz.trimf(ante.universe, [2 * max_val // 3, max_val, max_val])
    return ante


def create_priority_consequent() -> ctrl.Consequent:
    """Cria um consequente de prioridade (0-100)."""
    universe = np.arange(0, 101, 1)
    conse = ctrl.Consequent(universe, 'priority')
    conse['low'] = fuzz.trimf(conse.universe, [0, 0, 35])
    conse['medium'] = fuzz.trimf(conse.universe, [25, 50, 75])
    conse['high'] = fuzz.trimf(conse.universe, [65, 85, 100])
    conse['urgent'] = fuzz.trimf(conse.universe, [90, 100, 100])
    return conse


class HousingFuzzySystem:
    """
    Sistema Fuzzy Modular para Necessidades Habitacionais.
    
    Baseado no esquema do grupo com:
    - Indicadores individuais (A1, A2, B1, B2, C1, C2, D1, D2, E1, E2, E3, E4)
    - 12 Subíndices (SIF 1-12)
    - Índice Final (ISF - RMs)
    """
    
    def __init__(self):
        """Inicializa o sistema fuzzy modular."""
        self.modules: Dict[str, FuzzyModule] = {}
        self._initialize_all_modules()
    
    def _initialize_all_modules(self):
        """Inicializa todos os módulos do sistema."""
        priority_conseq = create_priority_consequent()
        
        # ========================================================================
        # MÓDULO A - HABITAÇÃO
        # ========================================================================
        
        # A1 - Domicílios rústicos
        a1 = create_boolean_antecedent('A1')
        rule1 = ctrl.Rule(a1['yes'], priority_conseq['urgent'])
        rule2 = ctrl.Rule(a1['no'], priority_conseq['low'])
        module_a1 = FuzzyModule('A1_Domicilios_Rusticos')
        module_a1.ctrl_system = ctrl.ControlSystem([rule1, rule2])
        module_a1.simulation = ctrl.ControlSystemSimulation(module_a1.ctrl_system)
        module_a1.input_ranges = {'A1': (0, 1, 0.1)}
        self.modules['A1'] = module_a1
        
        # A2 - Domicílios improvisados
        a2 = create_boolean_antecedent('A2')
        rule1 = ctrl.Rule(a2['yes'], priority_conseq['urgent'])
        rule2 = ctrl.Rule(a2['no'], priority_conseq['low'])
        module_a2 = FuzzyModule('A2_Domicilios_Improvisados')
        module_a2.ctrl_system = ctrl.ControlSystem([rule1, rule2])
        module_a2.simulation = ctrl.ControlSystemSimulation(module_a2.ctrl_system)
        module_a2.input_ranges = {'A2': (0, 1, 0.1)}
        self.modules['A2'] = module_a2
        
        # A3 - Unidades domésticas conviventes deficit
        a3 = create_boolean_antecedent('A3')
        rule1 = ctrl.Rule(a3['yes'], priority_conseq['high'])
        rule2 = ctrl.Rule(a3['no'], priority_conseq['low'])
        module_a3 = FuzzyModule('A3_Unidades_Conviventes_Deficit')
        module_a3.ctrl_system = ctrl.ControlSystem([rule1, rule2])
        module_a3.simulation = ctrl.ControlSystemSimulation(module_a3.ctrl_system)
        module_a3.input_ranges = {'A3': (0, 1, 0.1)}
        self.modules['A3'] = module_a3
        
        # A4 - Domicílios Cômodos
        a4 = create_boolean_antecedent('A4')
        rule1 = ctrl.Rule(a4['yes'], priority_conseq['high'])
        rule2 = ctrl.Rule(a4['no'], priority_conseq['low'])
        module_a4 = FuzzyModule('A4_Domicilios_Comodos')
        module_a4.ctrl_system = ctrl.ControlSystem([rule1, rule2])
        module_a4.simulation = ctrl.ControlSystemSimulation(module_a4.ctrl_system)
        module_a4.input_ranges = {'A4': (0, 1, 0.1)}
        self.modules['A4'] = module_a4
        
        # ========================================================================
        # SIF 1 - HAP (Habitação Precária)
        # ========================================================================
        a1_hap = create_boolean_antecedent('A1')
        a2_hap = create_boolean_antecedent('A2')
        a3_hap = create_boolean_antecedent('A3')
        a4_hap = create_boolean_antecedent('A4')
        priority_hap = create_priority_consequent()
        
        rules_hap = [
            ctrl.Rule(a1_hap['yes'] & a2_hap['yes'], priority_hap['urgent']),
            ctrl.Rule(a1_hap['yes'] & a3_hap['yes'], priority_hap['urgent']),
            ctrl.Rule(a2_hap['yes'] & a4_hap['yes'], priority_hap['urgent']),
            ctrl.Rule(a1_hap['yes'], priority_hap['high']),
            ctrl.Rule(a2_hap['yes'], priority_hap['high']),
            ctrl.Rule(a3_hap['yes'] & a4_hap['yes'], priority_hap['high']),
            ctrl.Rule(a3_hap['yes'], priority_hap['medium']),
            ctrl.Rule(a4_hap['yes'], priority_hap['medium']),
            ctrl.Rule(a1_hap['no'] & a2_hap['no'] & a3_hap['no'] & a4_hap['no'], priority_hap['low'])
        ]
        
        module_hap = FuzzyModule('SIF1_HAP_Habitacao_Precaria')
        module_hap.ctrl_system = ctrl.ControlSystem(rules_hap)
        module_hap.simulation = ctrl.ControlSystemSimulation(module_hap.ctrl_system)
        module_hap.input_ranges = {'A1': (0, 1, 0.1), 'A2': (0, 1, 0.1), 'A3': (0, 1, 0.1), 'A4': (0, 1, 0.1)}
        self.modules['SIF1_HAP'] = module_hap
        
        print("✅ Módulos A e SIF1 carregados")
    
    def get_module_names(self) -> List[str]:
        """Retorna a lista de todos os módulos disponíveis."""
        return list(self.modules.keys())
    
    def get_module(self, name: str) -> Optional[FuzzyModule]:
        """Retorna um módulo pelo nome."""
        return self.modules.get(name)
    
    def evaluate_module(self, module_name: str, inputs: Dict[str, float]) -> FuzzyResult:
        """
        Avalia um módulo específico.
        
        Args:
            module_name: Nome do módulo (ex: 'A1', 'SIF1_HAP', 'ISF_FINAL')
            inputs: Dicionário com os valores de entrada
        
        Returns:
            FuzzyResult com o resultado
        """
        if module_name not in self.modules:
            raise ValueError(f"Module '{module_name}' not found. Available: {self.get_module_names()}")
        
        return self.modules[module_name].evaluate(inputs)


def create_fuzzy_system() -> HousingFuzzySystem:
    """Factory function para criar o sistema fuzzy."""
    return HousingFuzzySystem()


if __name__ == "__main__":
    system = create_fuzzy_system()
    print("Sistema criado com sucesso!")
    print(f"Módulos disponíveis: {system.get_module_names()}")
