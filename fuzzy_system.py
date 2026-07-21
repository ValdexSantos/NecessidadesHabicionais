"""
Sistema Fuzzy Modular para Diagnóstico de Necessidades Habitacionais

Baseado no esquema do grupo com as especificações exatas do MATLAB:
- SIF 1 (HAP): DOM_RUSTICOS + DOM_IMPROVISADOS -> HAB_PRECARIA
- SIF 2 (COA): UNID_DOM_CONV + DOM_COMODOS -> COA
- SIF 3 (DEH): Hab_Precária (HAP) + Coabitação (COA) -> DEH

Cada módulo pode ser simulado individualmente ou em conjunto.
Regras ajustadas conforme especificação do usuário.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PriorityLevel(Enum):
    """Níveis de prioridade do sistema."""
    MUITO_BAIXO = "MUITO BAIXO"
    BAIXO = "BAIXO"
    MEDIO = "MÉDIO"
    ALTO = "ALTO"
    MUITO_ALTO = "MUITO ALTO"
    ALTISSIMA = "ALTÍSSIMA"


@dataclass
class FuzzyResult:
    """Resultado de uma avaliação fuzzy."""
    value: float
    label: PriorityLevel
    memberships: Dict[str, float]
    inputs: Dict[str, float]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'value': self.value,
            'label': self.label.value,
            'memberships': self.memberships,
            'inputs': self.inputs
        }


# ============================================================================
# FUNÇÕES AUXILIARES PARA CRIAÇÃO DE VARIÁVEIS
# ============================================================================

def create_percentage_var_4mf(name: str) -> ctrl.Antecedent:
    """Cria variável com 4 funções de pertinência: Ideal, Aceitável, Parcialmente Aceitável, Inaceitável"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Antecedent(universe, name)
    var['Ideal'] = fuzz.trimf(var.universe, [0, 0, 33])
    var['Aceitavel'] = fuzz.trimf(var.universe, [0, 33, 66])
    var['Parcialmente_aceitavel'] = fuzz.trimf(var.universe, [33, 66, 90])
    var['Inaceitavel'] = fuzz.trapmf(var.universe, [66, 100, 100, 100])
    return var


def create_percentage_var_5mf(name: str) -> ctrl.Antecedent:
    """Cria variável com 5 funções de pertinência: Muito Baixa, Baixa, Média, Alta, Muito Alta"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Antecedent(universe, name)
    var['Muito_baixa'] = fuzz.trimf(var.universe, [0, 0, 20])
    var['Baixa'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['Media'] = fuzz.trimf(var.universe, [20, 40, 60])
    var['Alta'] = fuzz.trimf(var.universe, [40, 60, 80])
    var['Muito_Alta'] = fuzz.trapmf(var.universe, [60, 100, 100, 100])
    return var


def create_hap_output_var(name: str) -> ctrl.Consequent:
    """Cria variável de saída para HAP: 6 níveis"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Consequent(universe, name)
    var['Muito_Baixa'] = fuzz.trimf(var.universe, [0, 0, 20])
    var['Baixa'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['Media'] = fuzz.trimf(var.universe, [20, 40, 60])
    var['Alta'] = fuzz.trimf(var.universe, [40, 60, 80])
    var['Muito_Alta'] = fuzz.trimf(var.universe, [60, 80, 100])
    var['Altissima'] = fuzz.trimf(var.universe, [80, 100, 100])
    return var


def create_coa_output_var(name: str) -> ctrl.Consequent:
    """Cria variável de saída para COA: 6 níveis"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Consequent(universe, name)
    var['Muito_baixa'] = fuzz.trimf(var.universe, [0, 0, 20])
    var['baixa'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['media'] = fuzz.trimf(var.universe, [20, 40, 60])
    var['alta'] = fuzz.trimf(var.universe, [40, 60, 80])
    var['muito_alta'] = fuzz.trimf(var.universe, [60, 80, 100])
    var['altissima'] = fuzz.trimf(var.universe, [80, 100, 100])
    return var


def create_deh_input_var(name: str) -> ctrl.Antecedent:
    """Cria variável de entrada para DEH: 6 níveis (para HAP e COA)
    
    Note: As entradas do SIF3_DEH são os resultados dos SIFs 1 e 2 (0-100)
    que já são saídas fuzzy, então precisam ter as mesmas funções de pertinência
    que as saídas dos SIFs 1 e 2.
    """
    universe = np.arange(0, 101, 1)
    var = ctrl.Antecedent(universe, name)
    # SIF1_HAP tem 6 níveis: Muito_Baixa, Baixa, Media, Alta, Muito_Alta, Altissima
    # SIF2_COA tem 6 níveis: Muito_baixa, baixa, media, alta, muito_alta, altissima
    # Vamos usar os mesmos termos para compatibilidade
    var['Muito_baixa'] = fuzz.trimf(var.universe, [0, 0, 20])
    var['baixa'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['media'] = fuzz.trimf(var.universe, [20, 40, 60])
    var['alta'] = fuzz.trimf(var.universe, [40, 60, 80])
    var['muito_alta'] = fuzz.trimf(var.universe, [60, 80, 100])
    var['altissima'] = fuzz.trimf(var.universe, [80, 100, 100])
    return var


def create_deh_output_var(name: str) -> ctrl.Consequent:
    """Cria variável de saída para DEH: 5 níveis"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Consequent(universe, name)
    var['Muito_baixo'] = fuzz.trapmf(var.universe, [0, 0, 15, 30])
    var['Baixo'] = fuzz.trimf(var.universe, [15, 30, 45])
    var['Medio'] = fuzz.trimf(var.universe, [30, 45, 60])
    var['Alto'] = fuzz.trimf(var.universe, [45, 60, 75])
    var['Muito_alto'] = fuzz.trapmf(var.universe, [60, 75, 100, 100])
    return var


# ============================================================================
# CLASSE FuzzyModule
# ============================================================================

class FuzzyModule:
    """Módulo fuzzy genérico."""
    
    def __init__(self, name: str, input_vars: Dict[str, ctrl.Antecedent], 
                 output_var: ctrl.Consequent, rules: List[ctrl.Rule],
                 input_labels: List[str]):
        self.name = name
        self.input_vars = input_vars
        self.output_var = output_var
        self.input_labels = input_labels  # Nomes das entradas para o inputs()
        self.output_label = output_var.label  # Nome da saída
        self.ctrl_system = ctrl.ControlSystem(rules)
        self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)
    
    def evaluate(self, inputs: Dict[str, float]) -> FuzzyResult:
        """Avalia o módulo."""
        # Converter inputs para o formato esperado pelo skfuzzy
        simulation_inputs = {}
        for label in self.input_labels:
            if label in inputs:
                simulation_inputs[label] = inputs[label]
        
        # Criar uma nova simulação para evitar conflitos
        sim = ctrl.ControlSystemSimulation(self.ctrl_system)
        sim.inputs(simulation_inputs)
        
        try:
            sim.compute()
            # Obter o valor de saída
            if self.output_label in sim.output:
                value = sim.output[self.output_label]
            else:
                # Se não encontrar pelo label, tentar pelo nome da variável
                value = sim.output.get(self.output_var.label, 0)
        except Exception as e:
            return FuzzyResult(value=0, label=PriorityLevel.BAIXO, 
                             memberships={}, inputs=inputs)
        
        # Calcular pertinências usando os termos do output_var
        memberships = {}
        for mf_name, mf in self.output_var.terms.items():
            memberships[mf_name] = float(fuzz.interp_membership(
                self.output_var.universe, mf.mf, value
            ))
        
        # Classificar com base nas pertinências
        label = self._classify_priority(value, memberships)
        
        return FuzzyResult(value=value, label=label, memberships=memberships, inputs=inputs)
    
    def _classify_priority(self, value: float, memberships: Dict[str, float]) -> PriorityLevel:
        """Classifica o nível de prioridade com base nas pertinências."""
        # Ordenar por pertinência (maior primeiro)
        sorted_memberships = sorted(memberships.items(), key=lambda x: x[1], reverse=True)
        
        # Retornar o nível com maior pertinência
        if sorted_memberships:
            highest_mf = sorted_memberships[0][0]
            
            # Mapear para PriorityLevel
            mapping = {
                'Muito_Baixa': PriorityLevel.MUITO_BAIXO,
                'Muito_baixa': PriorityLevel.MUITO_BAIXO,
                'Baixa': PriorityLevel.BAIXO,
                'baixa': PriorityLevel.BAIXO,
                'Media': PriorityLevel.MEDIO,
                'media': PriorityLevel.MEDIO,
                'Medio': PriorityLevel.MEDIO,
                'Alta': PriorityLevel.ALTO,
                'alta': PriorityLevel.ALTO,
                'Muito_Alta': PriorityLevel.MUITO_ALTO,
                'muito_alta': PriorityLevel.MUITO_ALTO,
                'Muito_alto': PriorityLevel.MUITO_ALTO,
                'Altissima': PriorityLevel.ALTISSIMA,
                'altissima': PriorityLevel.ALTISSIMA,
                'Muito_baixo': PriorityLevel.MUITO_BAIXO,
                'Baixo': PriorityLevel.BAIXO,
            }
            
            return mapping.get(highest_mf, PriorityLevel.MEDIO)
        
        # Fallback por valor
        if value >= 80:
            return PriorityLevel.ALTISSIMA
        elif value >= 60:
            return PriorityLevel.MUITO_ALTO
        elif value >= 40:
            return PriorityLevel.ALTO
        elif value >= 20:
            return PriorityLevel.MEDIO
        else:
            return PriorityLevel.BAIXO


# ============================================================================
# SISTEMA PRINCIPAL
# ============================================================================

class HousingFuzzySystem:
    """Sistema Fuzzy Modular para Necessidades Habitacionais."""
    
    def __init__(self):
        self.modules: Dict[str, FuzzyModule] = {}
        self._init_indicators()
        self._init_sifs()
    
    def _init_indicators(self):
        """Inicializa os indicadores individuais."""
        # A1 - DOM_RUSTICOS (0-100%)
        a1 = create_percentage_var_4mf('DOM_RUSTICOS')
        self.modules['A1'] = FuzzyModule('A1_DOM_RUSTICOS', {'DOM_RUSTICOS': a1}, a1, [], ['DOM_RUSTICOS'])
        
        # A2 - DOM_IMPROVISADOS (0-100%)
        a2 = create_percentage_var_4mf('DOM_IMPROVISADOS')
        self.modules['A2'] = FuzzyModule('A2_DOM_IMPROVISADOS', {'DOM_IMPROVISADOS': a2}, a2, [], ['DOM_IMPROVISADOS'])
        
        # A3 - UNID_DOM_CONV (0-100%)
        a3 = create_percentage_var_4mf('UNID_DOM_CONV')
        self.modules['A3'] = FuzzyModule('A3_UNID_DOM_CONV', {'UNID_DOM_CONV': a3}, a3, [], ['UNID_DOM_CONV'])
        
        # A4 - DOM_COMODOS (0-100%)
        a4 = create_percentage_var_4mf('DOM_COMODOS')
        self.modules['A4'] = FuzzyModule('A4_DOM_COMODOS', {'DOM_COMODOS': a4}, a4, [], ['DOM_COMODOS'])
        
        print("✅ Indicadores individuais carregados")
    
    def _init_sifs(self):
        """Inicializa os subíndices (SIF) com regras ajustadas."""
        
        # ========================================================================
        # SIF 1 - HAP (Habitação Precária)
        # Entradas: DOM_RUSTICOS, DOM_IMPROVISADOS
        # Saída: HAB_PRECARIA
        # Regras: 11 regras conforme especificação do usuário
        # ========================================================================
        dom_rusticos = create_percentage_var_4mf('DOM_RUSTICOS')
        dom_improvisados = create_percentage_var_4mf('DOM_IMPROVISADOS')
        hab_precarria = create_hap_output_var('HAB_PRECARIA')
        
        # Regras do SIF 1 (11 regras conforme especificação)
        hap_rules = [
            # Regra 1: Ideal + Ideal -> Muito Baixa
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Ideal'], hab_precarria['Muito_Baixa']),
            # Regra 2: Ideal + Aceitável -> Muito Baixa
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Aceitavel'], hab_precarria['Muito_Baixa']),
            # Regra 3: Ideal + Parcialmente aceitável -> Baixa
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Parcialmente_aceitavel'], hab_precarria['Baixa']),
            # Regra 4: Ideal + Inaceitável -> Média
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Inaceitavel'], hab_precarria['Media']),
            # Regra 5: Aceitável + Ideal -> Muito Baixa
            ctrl.Rule(dom_rusticos['Aceitavel'] & dom_improvisados['Ideal'], hab_precarria['Muito_Baixa']),
            # Regra 6: Aceitável + Aceitável -> Média
            ctrl.Rule(dom_rusticos['Aceitavel'] & dom_improvisados['Aceitavel'], hab_precarria['Media']),
            # Regra 7: Aceitável + Parcialmente aceitável -> Alta
            ctrl.Rule(dom_rusticos['Aceitavel'] & dom_improvisados['Parcialmente_aceitavel'], hab_precarria['Alta']),
            # Regra 8: Aceitável + Inaceitável -> Alta
            ctrl.Rule(dom_rusticos['Aceitavel'] & dom_improvisados['Inaceitavel'], hab_precarria['Alta']),
            # Regra 9: Parcialmente aceitável + Ideal -> Baixa
            ctrl.Rule(dom_rusticos['Parcialmente_aceitavel'] & dom_improvisados['Ideal'], hab_precarria['Baixa']),
            # Regra 10: Parcialmente aceitável + Aceitável -> Alta
            ctrl.Rule(dom_rusticos['Parcialmente_aceitavel'] & dom_improvisados['Aceitavel'], hab_precarria['Alta']),
            # Regra 11: Parcialmente aceitável + Parcialmente aceitável -> Alta
            ctrl.Rule(dom_rusticos['Parcialmente_aceitavel'] & dom_improvisados['Parcialmente_aceitavel'], hab_precarria['Alta']),
        ]
        
        self.modules['SIF1_HAP'] = FuzzyModule(
            'SIF1_HAP', 
            {'DOM_RUSTICOS': dom_rusticos, 'DOM_IMPROVISADOS': dom_improvisados},
            hab_precarria,
            hap_rules,
            ['DOM_RUSTICOS', 'DOM_IMPROVISADOS']
        )
        
        # ========================================================================
        # SIF 2 - COA (Coabitação) - CORRIGIDO
        # Entradas: UNID_DOM_CONV, DOM_COMODOS
        # Saída: COA
        # Regras: 16 regras conforme especificação do usuário
        # ========================================================================
        unid_dom_conv = create_percentage_var_4mf('UNID_DOM_CONV')
        dom_comodos = create_percentage_var_4mf('DOM_COMODOS')
        coa = create_coa_output_var('COA')
        
        # Regras do SIF 2 (16 regras conforme especificação)
        coa_rules = [
            # Regra 1: Ideal + Ideal -> Muito baixa
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Ideal'], coa['Muito_baixa']),
            # Regra 2: Ideal + Aceitável -> Muito baixa
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Aceitavel'], coa['Muito_baixa']),
            # Regra 3: Ideal + Parcialmente aceitável -> Baixa
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Parcialmente_aceitavel'], coa['baixa']),
            # Regra 4: Ideal + Inaceitável -> Média
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Inaceitavel'], coa['media']),
            # Regra 5: Aceitável + Ideal -> Muito baixa
            ctrl.Rule(unid_dom_conv['Aceitavel'] & dom_comodos['Ideal'], coa['Muito_baixa']),
            # Regra 6: Aceitável + Aceitável -> Média
            ctrl.Rule(unid_dom_conv['Aceitavel'] & dom_comodos['Aceitavel'], coa['media']),
            # Regra 7: Aceitável + Parcialmente aceitável -> Alta
            ctrl.Rule(unid_dom_conv['Aceitavel'] & dom_comodos['Parcialmente_aceitavel'], coa['alta']),
            # Regra 8: Aceitável + Inaceitável -> Muito alta
            ctrl.Rule(unid_dom_conv['Aceitavel'] & dom_comodos['Inaceitavel'], coa['muito_alta']),
            # Regra 9: Parcialmente aceitável + Ideal -> Baixa
            ctrl.Rule(unid_dom_conv['Parcialmente_aceitavel'] & dom_comodos['Ideal'], coa['baixa']),
            # Regra 10: Parcialmente aceitável + Aceitável -> Alta
            ctrl.Rule(unid_dom_conv['Parcialmente_aceitavel'] & dom_comodos['Aceitavel'], coa['alta']),
            # Regra 11: Parcialmente aceitável + Parcialmente aceitável -> Alta
            ctrl.Rule(unid_dom_conv['Parcialmente_aceitavel'] & dom_comodos['Parcialmente_aceitavel'], coa['alta']),
            # Regra 12: Parcialmente aceitável + Inaceitável -> Muito alta
            ctrl.Rule(unid_dom_conv['Parcialmente_aceitavel'] & dom_comodos['Inaceitavel'], coa['muito_alta']),
            # Regra 13: Inaceitável + Ideal -> Média
            ctrl.Rule(unid_dom_conv['Inaceitavel'] & dom_comodos['Ideal'], coa['media']),
            # Regra 14: Inaceitável + Aceitável -> Muito alta
            ctrl.Rule(unid_dom_conv['Inaceitavel'] & dom_comodos['Aceitavel'], coa['muito_alta']),
            # Regra 15: Inaceitável + Parcialmente aceitável -> Muito alta
            ctrl.Rule(unid_dom_conv['Inaceitavel'] & dom_comodos['Parcialmente_aceitavel'], coa['muito_alta']),
            # Regra 16: Inaceitável + Inaceitável -> Altíssima
            ctrl.Rule(unid_dom_conv['Inaceitavel'] & dom_comodos['Inaceitavel'], coa['altissima']),
        ]
        
        self.modules['SIF2_COA'] = FuzzyModule(
            'SIF2_COA',
            {'UNID_DOM_CONV': unid_dom_conv, 'DOM_COMODOS': dom_comodos},
            coa,
            coa_rules,
            ['UNID_DOM_CONV', 'DOM_COMODOS']
        )
        
        # ========================================================================
        # SIF 3 - DEH (Déficit Habitacional)
        # Entradas: Hab_Precária (HAP), Coabitação (COA)
        # Saída: DEH
        # Regras: 25 regras conforme especificação do usuário
        # NOTE: As entradas usam os termos das saídas dos SIFs 1 e 2
        # SIF1_HAP saída: Muito_Baixa, Baixa, Media, Alta, Muito_Alta, Altissima
        # SIF2_COA saída: Muito_baixa, baixa, media, alta, muito_alta, altissima
        # Vamos mapear para as entradas do SIF3_DEH
        # ========================================================================
        hab_precarria_deh = create_deh_input_var('Hab_Precaria')
        coabitacao_deh = create_deh_input_var('Coabitacao')
        deh = create_deh_output_var('DEH')
        
        # Regras do SIF 3 (25 regras conforme especificação)
        # Note: A especificação usa "Muito Alta" e "Muito alta", mas as entradas
        # têm "Altissima" para valores altos. Vamos ajustar para usar os termos
        # corretos das entradas.
        deh_rules = [
            # Regra 1: Muito baixa + Muito baixa -> Muito baixo
            ctrl.Rule(hab_precarria_deh['Muito_baixa'] & coabitacao_deh['Muito_baixa'], deh['Muito_baixo']),
            # Regra 2: Muito baixa + baixa -> Muito baixo
            ctrl.Rule(hab_precarria_deh['Muito_baixa'] & coabitacao_deh['baixa'], deh['Muito_baixo']),
            # Regra 3: Muito baixa + media -> Baixo
            ctrl.Rule(hab_precarria_deh['Muito_baixa'] & coabitacao_deh['media'], deh['Baixo']),
            # Regra 4: Muito baixa + alta -> Médio
            ctrl.Rule(hab_precarria_deh['Muito_baixa'] & coabitacao_deh['alta'], deh['Medio']),
            # Regra 5: Muito baixa + muito_alta -> Médio
            ctrl.Rule(hab_precarria_deh['Muito_baixa'] & coabitacao_deh['muito_alta'], deh['Medio']),
            # Regra 6: baixa + Muito baixa -> Baixo
            ctrl.Rule(hab_precarria_deh['baixa'] & coabitacao_deh['Muito_baixa'], deh['Baixo']),
            # Regra 7: baixa + baixa -> Baixo
            ctrl.Rule(hab_precarria_deh['baixa'] & coabitacao_deh['baixa'], deh['Baixo']),
            # Regra 8: baixa + media -> Médio
            ctrl.Rule(hab_precarria_deh['baixa'] & coabitacao_deh['media'], deh['Medio']),
            # Regra 9: baixa + alta -> Médio
            ctrl.Rule(hab_precarria_deh['baixa'] & coabitacao_deh['alta'], deh['Medio']),
            # Regra 10: baixa + muito_alta -> Alto
            ctrl.Rule(hab_precarria_deh['baixa'] & coabitacao_deh['muito_alta'], deh['Alto']),
            # Regra 11: media + Muito baixa -> Baixo
            ctrl.Rule(hab_precarria_deh['media'] & coabitacao_deh['Muito_baixa'], deh['Baixo']),
            # Regra 12: media + baixa -> Médio
            ctrl.Rule(hab_precarria_deh['media'] & coabitacao_deh['baixa'], deh['Medio']),
            # Regra 13: media + media -> Médio
            ctrl.Rule(hab_precarria_deh['media'] & coabitacao_deh['media'], deh['Medio']),
            # Regra 14: media + alta -> Médio
            ctrl.Rule(hab_precarria_deh['media'] & coabitacao_deh['alta'], deh['Medio']),
            # Regra 15: media + muito_alta -> Alto
            ctrl.Rule(hab_precarria_deh['media'] & coabitacao_deh['muito_alta'], deh['Alto']),
            # Regra 16: alta + Muito baixa -> Médio
            ctrl.Rule(hab_precarria_deh['alta'] & coabitacao_deh['Muito_baixa'], deh['Medio']),
            # Regra 17: alta + baixa -> Médio
            ctrl.Rule(hab_precarria_deh['alta'] & coabitacao_deh['baixa'], deh['Medio']),
            # Regra 18: alta + media -> Médio
            ctrl.Rule(hab_precarria_deh['alta'] & coabitacao_deh['media'], deh['Medio']),
            # Regra 19: alta + alta -> Alto
            ctrl.Rule(hab_precarria_deh['alta'] & coabitacao_deh['alta'], deh['Alto']),
            # Regra 20: alta + muito_alta -> Alto
            ctrl.Rule(hab_precarria_deh['alta'] & coabitacao_deh['muito_alta'], deh['Alto']),
            # Regra 21: muito_alta + Muito baixa -> Médio
            ctrl.Rule(hab_precarria_deh['muito_alta'] & coabitacao_deh['Muito_baixa'], deh['Medio']),
            # Regra 22: muito_alta + baixa -> Alto
            ctrl.Rule(hab_precarria_deh['muito_alta'] & coabitacao_deh['baixa'], deh['Alto']),
            # Regra 23: muito_alta + media -> Alto
            ctrl.Rule(hab_precarria_deh['muito_alta'] & coabitacao_deh['media'], deh['Alto']),
            # Regra 24: muito_alta + alta -> Muito alto
            ctrl.Rule(hab_precarria_deh['muito_alta'] & coabitacao_deh['alta'], deh['Muito_alto']),
            # Regra 25: muito_alta + muito_alta -> Muito alto
            ctrl.Rule(hab_precarria_deh['muito_alta'] & coabitacao_deh['muito_alta'], deh['Muito_alto']),
            # Regras adicionais para altissima
            # Regra 26: altissima + altissima -> Muito alto
            ctrl.Rule(hab_precarria_deh['altissima'] & coabitacao_deh['altissima'], deh['Muito_alto']),
            # Regra 27: altissima + muito_alta -> Muito alto
            ctrl.Rule(hab_precarria_deh['altissima'] & coabitacao_deh['muito_alta'], deh['Muito_alto']),
            # Regra 28: muito_alta + altissima -> Muito alto
            ctrl.Rule(hab_precarria_deh['muito_alta'] & coabitacao_deh['altissima'], deh['Muito_alto']),
        ]
        
        self.modules['SIF3_DEH'] = FuzzyModule(
            'SIF3_DEH',
            {'Hab_Precaria': hab_precarria_deh, 'Coabitacao': coabitacao_deh},
            deh,
            deh_rules,
            ['Hab_Precaria', 'Coabitacao']
        )
        
        print("✅ SIFs 1-3 carregados com regras ajustadas")
    
    def get_module_names(self) -> List[str]:
        return list(self.modules.keys())
    
    def get_module(self, name: str) -> Optional[FuzzyModule]:
        return self.modules.get(name)
    
    def evaluate_module(self, module_name: str, inputs: Dict[str, float]) -> FuzzyResult:
        if module_name not in self.modules:
            raise ValueError(f"Module '{module_name}' not found. Available: {self.get_module_names()}")
        return self.modules[module_name].evaluate(inputs)
    
    def evaluate_final_index(self, sif_results: Dict[str, float]) -> FuzzyResult:
        # Para o DEH, o índice final é o próprio SIF3
        # Mas podemos calcular uma média ponderada
        sif1 = sif_results.get('SIF1_HAP', 0)
        sif2 = sif_results.get('SIF2_COA', 0)
        sif3 = sif_results.get('SIF3_DEH', 0)
        
        # Média simples
        final_value = (sif1 + sif2 + sif3) / 3
        
        # Classificar
        if final_value >= 80:
            label = PriorityLevel.ALTISSIMA
        elif final_value >= 60:
            label = PriorityLevel.MUITO_ALTO
        elif final_value >= 40:
            label = PriorityLevel.ALTO
        elif final_value >= 20:
            label = PriorityLevel.MEDIO
        else:
            label = PriorityLevel.BAIXO
        
        return FuzzyResult(
            value=final_value,
            label=label,
            memberships={},
            inputs={'SIF1_HAP': sif1, 'SIF2_COA': sif2, 'SIF3_DEH': sif3}
        )
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        if module_name not in self.modules:
            return {'error': f'Module {module_name} not found'}
        module = self.modules[module_name]
        return {
            'name': module.name,
            'input_vars': module.input_labels,
            'output_var': module.output_label
        }


def create_fuzzy_system() -> HousingFuzzySystem:
    return HousingFuzzySystem()


if __name__ == "__main__":
    system = create_fuzzy_system()
    print("✅ Sistema Fuzzy Modular criado com sucesso!")
    print(f"Módulos disponíveis ({len(system.modules)}):")
    for name in system.get_module_names():
        print(f"  - {name}")
