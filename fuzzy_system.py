"""
Sistema Fuzzy Modular para Diagnóstico de Necessidades Habitacionais

Baseado no esquema do grupo com as especificações exatas do MATLAB:
- SIF 1 (HAP): DOM_RUSTICOS + DOM_IMPROVISADOS -> HAB_PRECARIA
- SIF 2 (COA): UNID_DOM_CONV + DOM_COMODOS -> COA
- SIF 3 (DEH): Hab_Precária + Coabitação -> DEH

Cada módulo pode ser simulado individualmente ou em conjunto.
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
    var['Aceitável'] = fuzz.trimf(var.universe, [0, 33, 66])
    var['Parcialmente aceitável'] = fuzz.trimf(var.universe, [33, 66, 90])
    var['Inaceitável'] = fuzz.trapmf(var.universe, [66, 100, 100, 100])
    return var


def create_percentage_var_5mf(name: str) -> ctrl.Antecedent:
    """Cria variável com 5 funções de pertinência: Muito Baixa, Baixa, Média, Alta, Muito Alta"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Antecedent(universe, name)
    var['Muito baixa'] = fuzz.trimf(var.universe, [0, 0, 20])
    var['Baixa'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['Média'] = fuzz.trimf(var.universe, [20, 40, 60])
    var['Alta'] = fuzz.trimf(var.universe, [40, 60, 80])
    var['Muito Alta'] = fuzz.trapmf(var.universe, [60, 100, 100, 100])
    return var


def create_hap_output_var(name: str) -> ctrl.Consequent:
    """Cria variável de saída para HAP: 6 níveis"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Consequent(universe, name)
    var['Muito Baixa'] = fuzz.trimf(var.universe, [0, 0, 20])
    var['Baixa'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['Média'] = fuzz.trimf(var.universe, [20, 40, 60])
    var['Alta'] = fuzz.trimf(var.universe, [40, 60, 80])
    var['Muito Alta'] = fuzz.trimf(var.universe, [60, 80, 100])
    var['Altíssima'] = fuzz.trimf(var.universe, [80, 100, 100])
    return var


def create_coa_output_var(name: str) -> ctrl.Consequent:
    """Cria variável de saída para COA: 6 níveis (CORRIGIDO)"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Consequent(universe, name)
    var['Muito baixa'] = fuzz.trimf(var.universe, [0, 0, 20])
    var['baixa'] = fuzz.trimf(var.universe, [0, 20, 40])
    var['média'] = fuzz.trimf(var.universe, [20, 40, 60])
    var['alta'] = fuzz.trimf(var.universe, [40, 60, 80])
    var['muito alta'] = fuzz.trimf(var.universe, [60, 80, 100])
    var['altíssima'] = fuzz.trimf(var.universe, [80, 100, 100])
    return var


def create_deh_output_var(name: str) -> ctrl.Consequent:
    """Cria variável de saída para DEH: 5 níveis"""
    universe = np.arange(0, 101, 1)
    var = ctrl.Consequent(universe, name)
    var['Muito baixo'] = fuzz.trapmf(var.universe, [0, 0, 15, 30])
    var['Baixo'] = fuzz.trimf(var.universe, [15, 30, 45])
    var['Médio'] = fuzz.trimf(var.universe, [30, 45, 60])
    var['Alto'] = fuzz.trimf(var.universe, [45, 60, 75])
    var['Muito alto'] = fuzz.trapmf(var.universe, [60, 75, 100, 100])
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
        self.ctrl_system = ctrl.ControlSystem(rules)
        self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)
    
    def evaluate(self, inputs: Dict[str, float]) -> FuzzyResult:
        """Avalia o módulo."""
        # Converter inputs para o formato esperado pelo skfuzzy
        simulation_inputs = {}
        for label in self.input_labels:
            if label in inputs:
                simulation_inputs[label] = inputs[label]
        
        self.simulation.inputs(simulation_inputs)
        try:
            self.simulation.compute()
        except Exception as e:
            return FuzzyResult(value=0, label=PriorityLevel.BAIXO, 
                             memberships={}, inputs=inputs)
        
        value = self.simulation.output[self.output_var.label]
        
        # Calcular pertinências
        memberships = {}
        for mf_name in [mf for mf in dir(self.output_var) if not mf.startswith('_') and mf not in ['label', 'universe', 'mf']]:
            try:
                mf = getattr(self.output_var, mf_name)
                if hasattr(mf, 'mf'):
                    memberships[mf_name] = float(fuzz.interp_membership(
                        self.output_var.universe, mf.mf, value
                    ))
            except:
                pass
        
        # Classificar
        label = self._classify_priority(value, memberships)
        
        return FuzzyResult(value=value, label=label, memberships=memberships, inputs=inputs)
    
    def _classify_priority(self, value: float, memberships: Dict[str, float]) -> PriorityLevel:
        """Classifica o nível de prioridade."""
        # Verificar pertinências
        if 'Altíssima' in memberships and memberships['Altíssima'] > 0.5:
            return PriorityLevel.ALTISSIMA
        elif 'altíssima' in memberships and memberships['altíssima'] > 0.5:
            return PriorityLevel.ALTISSIMA
        elif 'Muito Alta' in memberships and memberships['Muito Alta'] > 0.5:
            return PriorityLevel.MUITO_ALTO
        elif 'muito alta' in memberships and memberships['muito alta'] > 0.5:
            return PriorityLevel.MUITO_ALTO
        elif 'Muito alto' in memberships and memberships['Muito alto'] > 0.5:
            return PriorityLevel.MUITO_ALTO
        elif 'Alto' in memberships and memberships['Alto'] > 0.5:
            return PriorityLevel.ALTO
        elif 'alta' in memberships and memberships['alta'] > 0.5:
            return PriorityLevel.ALTO
        elif 'Média' in memberships and memberships['Média'] > 0.5:
            return PriorityLevel.MEDIO
        elif 'média' in memberships and memberships['média'] > 0.5:
            return PriorityLevel.MEDIO
        elif 'Baixa' in memberships and memberships['Baixa'] > 0.5:
            return PriorityLevel.BAIXO
        elif 'baixa' in memberships and memberships['baixa'] > 0.5:
            return PriorityLevel.BAIXO
        elif 'Muito Baixa' in memberships and memberships['Muito Baixa'] > 0.5:
            return PriorityLevel.MUITO_BAIXO
        elif 'Muito baixo' in memberships and memberships['Muito baixo'] > 0.5:
            return PriorityLevel.MUITO_BAIXO
        elif 'muito baixa' in memberships and memberships['muito baixa'] > 0.5:
            return PriorityLevel.MUITO_BAIXO
        else:
            # Classificar por valor
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
        """Inicializa os subíndices (SIF)."""
        
        # ========================================================================
        # SIF 1 - HAP (Habitação Precária)
        # Entradas: DOM_RUSTICOS (A1), DOM_IMPROVISADOS (A2)
        # Saída: HAB_PRECARIA
        # ========================================================================
        dom_rusticos = create_percentage_var_4mf('DOM_RUSTICOS')
        dom_improvisados = create_percentage_var_4mf('DOM_IMPROVISADOS')
        hab_precarria = create_hap_output_var('HAB_PRECARIA')
        
        # Regras do SIF 1 (16 regras do MATLAB)
        hap_rules = [
            # DOM_RUSTICOS = Ideal (1)
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Ideal'], hab_precarria['Muito Baixa']),
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Aceitável'], hab_precarria['Muito Baixa']),
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Parcialmente aceitável'], hab_precarria['Baixa']),
            ctrl.Rule(dom_rusticos['Ideal'] & dom_improvisados['Inaceitável'], hab_precarria['Média']),
            # DOM_RUSTICOS = Aceitável (2)
            ctrl.Rule(dom_rusticos['Aceitável'] & dom_improvisados['Ideal'], hab_precarria['Muito Baixa']),
            ctrl.Rule(dom_rusticos['Aceitável'] & dom_improvisados['Aceitável'], hab_precarria['Baixa']),
            ctrl.Rule(dom_rusticos['Aceitável'] & dom_improvisados['Parcialmente aceitável'], hab_precarria['Alta']),
            ctrl.Rule(dom_rusticos['Aceitável'] & dom_improvisados['Inaceitável'], hab_precarria['Muito Alta']),
            # DOM_RUSTICOS = Parcialmente aceitável (3)
            ctrl.Rule(dom_rusticos['Parcialmente aceitável'] & dom_improvisados['Ideal'], hab_precarria['Baixa']),
            ctrl.Rule(dom_rusticos['Parcialmente aceitável'] & dom_improvisados['Aceitável'], hab_precarria['Alta']),
            ctrl.Rule(dom_rusticos['Parcialmente aceitável'] & dom_improvisados['Parcialmente aceitável'], hab_precarria['Alta']),
            ctrl.Rule(dom_rusticos['Parcialmente aceitável'] & dom_improvisados['Inaceitável'], hab_precarria['Muito Alta']),
            # DOM_RUSTICOS = Inaceitável (4)
            ctrl.Rule(dom_rusticos['Inaceitável'] & dom_improvisados['Ideal'], hab_precarria['Média']),
            ctrl.Rule(dom_rusticos['Inaceitável'] & dom_improvisados['Aceitável'], hab_precarria['Muito Alta']),
            ctrl.Rule(dom_rusticos['Inaceitável'] & dom_improvisados['Parcialmente aceitável'], hab_precarria['Muito Alta']),
            ctrl.Rule(dom_rusticos['Inaceitável'] & dom_improvisados['Inaceitável'], hab_precarria['Altíssima']),
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
        # Entradas: UNID_DOM_CONV (A3), DOM_COMODOS (A4)
        # Saída: COA
        # ========================================================================
        unid_dom_conv = create_percentage_var_4mf('UNID_DOM_CONV')
        dom_comodos = create_percentage_var_4mf('DOM_COMODOS')
        coa = create_coa_output_var('COA')
        
        # Regras do SIF 2 (16 regras do MATLAB CORRIGIDO)
        coa_rules = [
            # UNID_DOM_CONV = Ideal (1)
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Ideal'], coa['Muito baixa']),
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Aceitável'], coa['Muito baixa']),
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Parcialmente aceitável'], coa['baixa']),
            ctrl.Rule(unid_dom_conv['Ideal'] & dom_comodos['Inaceitável'], coa['média']),
            # UNID_DOM_CONV = Aceitável (2)
            ctrl.Rule(unid_dom_conv['Aceitável'] & dom_comodos['Ideal'], coa['Muito baixa']),
            ctrl.Rule(unid_dom_conv['Aceitável'] & dom_comodos['Aceitável'], coa['baixa']),
            ctrl.Rule(unid_dom_conv['Aceitável'] & dom_comodos['Parcialmente aceitável'], coa['alta']),
            ctrl.Rule(unid_dom_conv['Aceitável'] & dom_comodos['Inaceitável'], coa['muito alta']),
            # UNID_DOM_CONV = Parcialmente aceitável (3)
            ctrl.Rule(unid_dom_conv['Parcialmente aceitável'] & dom_comodos['Ideal'], coa['baixa']),
            ctrl.Rule(unid_dom_conv['Parcialmente aceitável'] & dom_comodos['Aceitável'], coa['alta']),
            ctrl.Rule(unid_dom_conv['Parcialmente aceitável'] & dom_comodos['Parcialmente aceitável'], coa['alta']),
            ctrl.Rule(unid_dom_conv['Parcialmente aceitável'] & dom_comodos['Inaceitável'], coa['muito alta']),
            # UNID_DOM_CONV = Inaceitável (4)
            ctrl.Rule(unid_dom_conv['Inaceitável'] & dom_comodos['Ideal'], coa['média']),
            ctrl.Rule(unid_dom_conv['Inaceitável'] & dom_comodos['Aceitável'], coa['muito alta']),
            ctrl.Rule(unid_dom_conv['Inaceitável'] & dom_comodos['Parcialmente aceitável'], coa['muito alta']),
            ctrl.Rule(unid_dom_conv['Inaceitável'] & dom_comodos['Inaceitável'], coa['altíssima']),
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
        # Entradas: Hab_Precária (SIF1), Coabitação (SIF2)
        # Saída: DEH
        # ========================================================================
        hab_precarria_deh = create_percentage_var_5mf('Hab_Precária')
        coabitacao_deh = create_percentage_var_5mf('Coabitação')
        deh = create_deh_output_var('DEH')
        
        # Regras do SIF 3 (25 regras do MATLAB)
        deh_rules = [
            # Hab_Precária = Muito baixa (1)
            ctrl.Rule(hab_precarria_deh['Muito baixa'] & coabitacao_deh['Muito baixa'], deh['Muito baixo']),
            ctrl.Rule(hab_precarria_deh['Muito baixa'] & coabitacao_deh['Baixa'], deh['Muito baixo']),
            ctrl.Rule(hab_precarria_deh['Muito baixa'] & coabitacao_deh['Média'], deh['Baixo']),
            ctrl.Rule(hab_precarria_deh['Muito baixa'] & coabitacao_deh['Alta'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Muito baixa'] & coabitacao_deh['Muito Alta'], deh['Médio']),
            # Hab_Precária = Baixa (2)
            ctrl.Rule(hab_precarria_deh['Baixa'] & coabitacao_deh['Muito baixa'], deh['Baixo']),
            ctrl.Rule(hab_precarria_deh['Baixa'] & coabitacao_deh['Baixa'], deh['Baixo']),
            ctrl.Rule(hab_precarria_deh['Baixa'] & coabitacao_deh['Média'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Baixa'] & coabitacao_deh['Alta'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Baixa'] & coabitacao_deh['Muito Alta'], deh['Alto']),
            # Hab_Precária = Média (3)
            ctrl.Rule(hab_precarria_deh['Média'] & coabitacao_deh['Muito baixa'], deh['Baixo']),
            ctrl.Rule(hab_precarria_deh['Média'] & coabitacao_deh['Baixa'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Média'] & coabitacao_deh['Média'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Média'] & coabitacao_deh['Alta'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Média'] & coabitacao_deh['Muito Alta'], deh['Alto']),
            # Hab_Precária = Alta (4)
            ctrl.Rule(hab_precarria_deh['Alta'] & coabitacao_deh['Muito baixa'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Alta'] & coabitacao_deh['Baixa'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Alta'] & coabitacao_deh['Média'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Alta'] & coabitacao_deh['Alta'], deh['Alto']),
            ctrl.Rule(hab_precarria_deh['Alta'] & coabitacao_deh['Muito Alta'], deh['Muito alto']),
            # Hab_Precária = Muito Alta (5)
            ctrl.Rule(hab_precarria_deh['Muito Alta'] & coabitacao_deh['Muito baixa'], deh['Médio']),
            ctrl.Rule(hab_precarria_deh['Muito Alta'] & coabitacao_deh['Baixa'], deh['Alto']),
            ctrl.Rule(hab_precarria_deh['Muito Alta'] & coabitacao_deh['Média'], deh['Alto']),
            ctrl.Rule(hab_precarria_deh['Muito Alta'] & coabitacao_deh['Alta'], deh['Alto']),
            ctrl.Rule(hab_precarria_deh['Muito Alta'] & coabitacao_deh['Muito Alta'], deh['Muito alto']),
        ]
        
        self.modules['SIF3_DEH'] = FuzzyModule(
            'SIF3_DEH',
            {'Hab_Precária': hab_precarria_deh, 'Coabitação': coabitacao_deh},
            deh,
            deh_rules,
            ['Hab_Precária', 'Coabitação']
        )
        
        print("✅ SIFs 1-3 carregados (SIF 2 corrigido)")
    
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
            'output_var': module.output_var.label
        }


def create_fuzzy_system() -> HousingFuzzySystem:
    return HousingFuzzySystem()


if __name__ == "__main__":
    system = create_fuzzy_system()
    print("✅ Sistema Fuzzy Modular criado com sucesso!")
    print(f"Módulos disponíveis ({len(system.modules)}):")
    for name in system.get_module_names():
        print(f"  - {name}")
