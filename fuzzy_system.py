"""
Sistema Fuzzy Modular para Diagnóstico de Necessidades Habitacionais

Sistema simplificado baseado no esquema do grupo.
Permite simular indicadores individuais e subíndices (SIF) separadamente.
"""

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class PriorityLevel(Enum):
    LOW = "BAIXA"
    MEDIUM = "MÉDIA"
    HIGH = "ALTA"
    URGENT = "URGENTE"


@dataclass
class FuzzyResult:
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


# Funções auxiliares para criar variáveis fuzzy
def create_boolean_var(name: str) -> ctrl.Antecedent:
    universe = np.arange(0, 1.1, 0.1)
    var = ctrl.Antecedent(universe, name)
    var['no'] = fuzz.trimf(var.universe, [0, 0, 0.5])
    var['yes'] = fuzz.trimf(var.universe, [0.5, 1, 1])
    return var


def create_access_var(name: str) -> ctrl.Antecedent:
    universe = np.arange(0, 10.1, 0.1)
    var = ctrl.Antecedent(universe, name)
    var['low'] = fuzz.trimf(var.universe, [0, 0, 4])
    var['medium'] = fuzz.trimf(var.universe, [2, 5, 7])
    var['high'] = fuzz.trimf(var.universe, [6, 10, 10])
    return var


def create_priority_var() -> ctrl.Consequent:
    universe = np.arange(0, 101, 1)
    var = ctrl.Consequent(universe, 'priority')
    var['low'] = fuzz.trimf(var.universe, [0, 0, 35])
    var['medium'] = fuzz.trimf(var.universe, [25, 50, 75])
    var['high'] = fuzz.trimf(var.universe, [65, 85, 100])
    var['urgent'] = fuzz.trimf(var.universe, [90, 100, 100])
    return var


class FuzzyModule:
    """Módulo fuzzy genérico."""
    
    def __init__(self, name: str, input_vars: Dict[str, ctrl.Antecedent], 
                 output_var: ctrl.Consequent, rules: List[ctrl.Rule]):
        self.name = name
        self.input_vars = input_vars
        self.output_var = output_var
        self.ctrl_system = ctrl.ControlSystem(rules)
        self.simulation = ctrl.ControlSystemSimulation(self.ctrl_system)
    
    def evaluate(self, inputs: Dict[str, float]) -> FuzzyResult:
        """Avalia o módulo."""
        self.simulation.inputs(inputs)
        try:
            self.simulation.compute()
        except:
            return FuzzyResult(value=0, label=PriorityLevel.LOW, 
                             memberships={'low': 1, 'medium': 0, 'high': 0, 'urgent': 0}, inputs=inputs)
        
        value = self.simulation.output['priority']
        
        # Calcular pertinências
        memberships = {}
        for mf in ['low', 'medium', 'high', 'urgent']:
            try:
                memberships[mf] = float(fuzz.interp_membership(
                    self.output_var.universe,
                    getattr(self.output_var, mf).mf,
                    value
                ))
            except:
                memberships[mf] = 0.0
        
        # Classificar
        if value >= 90:
            label = PriorityLevel.URGENT
        elif value >= 70:
            label = PriorityLevel.HIGH
        elif value >= 40:
            label = PriorityLevel.MEDIUM
        else:
            label = PriorityLevel.LOW
        
        return FuzzyResult(value=value, label=label, memberships=memberships, inputs=inputs)


class HousingFuzzySystem:
    """Sistema Fuzzy Modular para Necessidades Habitacionais."""
    
    def __init__(self):
        self.modules: Dict[str, FuzzyModule] = {}
        self._init_indicators()
        self._init_sifs()
        self._init_final_index()
    
    def _init_indicators(self):
        """Inicializa os indicadores individuais."""
        priority = create_priority_var()
        
        # A1 - Domicílios rústicos
        a1 = create_boolean_var('A1')
        self.modules['A1'] = FuzzyModule(
            'A1_Domicilios_Rusticos', {'A1': a1}, priority,
            [ctrl.Rule(a1['yes'], priority['urgent']), ctrl.Rule(a1['no'], priority['low'])]
        )
        
        # A2 - Domicílios improvisados
        a2 = create_boolean_var('A2')
        self.modules['A2'] = FuzzyModule(
            'A2_Domicilios_Improvisados', {'A2': a2}, priority,
            [ctrl.Rule(a2['yes'], priority['urgent']), ctrl.Rule(a2['no'], priority['low'])]
        )
        
        # A3 - Unidades domésticas conviventes deficit
        a3 = create_boolean_var('A3')
        self.modules['A3'] = FuzzyModule(
            'A3_Unidades_Conviventes', {'A3': a3}, priority,
            [ctrl.Rule(a3['yes'], priority['high']), ctrl.Rule(a3['no'], priority['low'])]
        )
        
        # A4 - Domicílios Cômodos
        a4 = create_boolean_var('A4')
        self.modules['A4'] = FuzzyModule(
            'A4_Domicilios_Comodos', {'A4': a4}, priority,
            [ctrl.Rule(a4['yes'], priority['high']), ctrl.Rule(a4['no'], priority['low'])]
        )
        
        # B1 - Inadequação de Esgotamento sanitário
        b1 = create_boolean_var('B1')
        self.modules['B1'] = FuzzyModule(
            'B1_Esgotamento', {'B1': b1}, priority,
            [ctrl.Rule(b1['yes'], priority['high']), ctrl.Rule(b1['no'], priority['low'])]
        )
        
        # B2 - Inadequação da Coleta de lixo
        b2 = create_boolean_var('B2')
        self.modules['B2'] = FuzzyModule(
            'B2_Coleta_Lixo', {'B2': b2}, priority,
            [ctrl.Rule(b2['yes'], priority['high']), ctrl.Rule(b2['no'], priority['low'])]
        )
        
        # B3 - Inadequação de Abastecimento de água
        b3 = create_boolean_var('B3')
        self.modules['B3'] = FuzzyModule(
            'B3_Abastecimento_Agua', {'B3': b3}, priority,
            [ctrl.Rule(b3['yes'], priority['urgent']), ctrl.Rule(b3['no'], priority['low'])]
        )
        
        # B4 - Ausência de iluminação pública
        b4 = create_boolean_var('B4')
        self.modules['B4'] = FuzzyModule(
            'B4_Iluminacao', {'B4': b4}, priority,
            [ctrl.Rule(b4['yes'], priority['high']), ctrl.Rule(b4['no'], priority['low'])]
        )
        
        # C1 - Piso ou cobertura inadequados
        c1 = create_boolean_var('C1')
        self.modules['C1'] = FuzzyModule(
            'C1_Piso_Cobertura', {'C1': c1}, priority,
            [ctrl.Rule(c1['yes'], priority['high']), ctrl.Rule(c1['no'], priority['low'])]
        )
        
        # C2 - Inexistência de banheiro exclusivo
        c2 = create_boolean_var('C2')
        self.modules['C2'] = FuzzyModule(
            'C2_Banheiro', {'C2': c2}, priority,
            [ctrl.Rule(c2['yes'], priority['urgent']), ctrl.Rule(c2['no'], priority['low'])]
        )
        
        # C3 - Cômodos igual a dormitórios
        c3 = create_boolean_var('C3')
        self.modules['C3'] = FuzzyModule(
            'C3_Comodos', {'C3': c3}, priority,
            [ctrl.Rule(c3['yes'], priority['high']), ctrl.Rule(c3['no'], priority['low'])]
        )
        
        # D1 - Acesso à Educação
        d1 = create_access_var('D1')
        self.modules['D1'] = FuzzyModule(
            'D1_Educacao', {'D1': d1}, priority,
            [ctrl.Rule(d1['low'], priority['urgent']), 
             ctrl.Rule(d1['medium'], priority['medium']), 
             ctrl.Rule(d1['high'], priority['low'])]
        )
        
        # D2 - Acesso à Saúde
        d2 = create_access_var('D2')
        self.modules['D2'] = FuzzyModule(
            'D2_Saude', {'D2': d2}, priority,
            [ctrl.Rule(d2['low'], priority['urgent']), 
             ctrl.Rule(d2['medium'], priority['medium']), 
             ctrl.Rule(d2['high'], priority['low'])]
        )
        
        # D3 - Acesso a transporte
        d3 = create_access_var('D3')
        self.modules['D3'] = FuzzyModule(
            'D3_Transporte', {'D3': d3}, priority,
            [ctrl.Rule(d3['low'], priority['high']), 
             ctrl.Rule(d3['medium'], priority['medium']), 
             ctrl.Rule(d3['high'], priority['low'])]
        )
        
        # D4 - Conectividade Digital
        d4 = create_access_var('D4')
        self.modules['D4'] = FuzzyModule(
            'D4_Conectividade', {'D4': d4}, priority,
            [ctrl.Rule(d4['low'], priority['medium']), 
             ctrl.Rule(d4['medium'], priority['low']), 
             ctrl.Rule(d4['high'], priority['low'])]
        )
        
        # E1 - Renda per capita (0-100%)
        e1_universe = np.arange(0, 101, 1)
        e1 = ctrl.Antecedent(e1_universe, 'E1')
        e1['low'] = fuzz.trimf(e1.universe, [0, 0, 33])
        e1['medium'] = fuzz.trimf(e1.universe, [25, 50, 75])
        e1['high'] = fuzz.trimf(e1.universe, [67, 100, 100])
        self.modules['E1'] = FuzzyModule(
            'E1_Renda_Per_Capita', {'E1': e1}, priority,
            [ctrl.Rule(e1['low'], priority['urgent']), 
             ctrl.Rule(e1['medium'], priority['medium']), 
             ctrl.Rule(e1['high'], priority['low'])]
        )
        
        # E2 - Número de membros empregados (0-10)
        e2_universe = np.arange(0, 11, 1)
        e2 = ctrl.Antecedent(e2_universe, 'E2')
        e2['low'] = fuzz.trimf(e2.universe, [0, 0, 3])
        e2['medium'] = fuzz.trimf(e2.universe, [2, 5, 7])
        e2['high'] = fuzz.trimf(e2.universe, [6, 10, 10])
        self.modules['E2'] = FuzzyModule(
            'E2_Membros_Empregados', {'E2': e2}, priority,
            [ctrl.Rule(e2['low'], priority['urgent']), 
             ctrl.Rule(e2['medium'], priority['medium']), 
             ctrl.Rule(e2['high'], priority['low'])]
        )
        
        # E3 - Famílias atendidas pelo PBF
        e3 = create_boolean_var('E3')
        self.modules['E3'] = FuzzyModule(
            'E3_PBF', {'E3': e3}, priority,
            [ctrl.Rule(e3['yes'], priority['urgent']), ctrl.Rule(e3['no'], priority['low'])]
        )
        
        # E4 - Famílias beneficiárias do BPC
        e4 = create_boolean_var('E4')
        self.modules['E4'] = FuzzyModule(
            'E4_BPC', {'E4': e4}, priority,
            [ctrl.Rule(e4['yes'], priority['urgent']), ctrl.Rule(e4['no'], priority['low'])]
        )
        
        print("✅ Indicadores individuais carregados")
    
    def _init_sifs(self):
        """Inicializa os subíndices (SIF)."""
        priority = create_priority_var()
        
        # SIF 1 - HAP (Habitação Precária): A1, A2, A3, A4
        a1 = create_boolean_var('A1')
        a2 = create_boolean_var('A2')
        a3 = create_boolean_var('A3')
        a4 = create_boolean_var('A4')
        
        self.modules['SIF1_HAP'] = FuzzyModule(
            'SIF1_HAP', {'A1': a1, 'A2': a2, 'A3': a3, 'A4': a4}, priority,
            [
                ctrl.Rule(a1['yes'] & a2['yes'], priority['urgent']),
                ctrl.Rule(a1['yes'] & a3['yes'], priority['urgent']),
                ctrl.Rule(a2['yes'] & a4['yes'], priority['urgent']),
                ctrl.Rule(a1['yes'], priority['high']),
                ctrl.Rule(a2['yes'], priority['high']),
                ctrl.Rule(a3['yes'] & a4['yes'], priority['high']),
                ctrl.Rule(a3['yes'], priority['medium']),
                ctrl.Rule(a4['yes'], priority['medium']),
                ctrl.Rule(a1['no'] & a2['no'] & a3['no'] & a4['no'], priority['low'])
            ]
        )
        
        # SIF 2 - COA (Coabitação): A4
        a4_coa = create_boolean_var('A4')
        self.modules['SIF2_COA'] = FuzzyModule(
            'SIF2_COA', {'A4': a4_coa}, priority,
            [ctrl.Rule(a4_coa['yes'], priority['high']), ctrl.Rule(a4_coa['no'], priority['low'])]
        )
        
        # SIF 3 - DEH (Déficit Habitacional): A1, A2, A3
        a1_deh = create_boolean_var('A1')
        a2_deh = create_boolean_var('A2')
        a3_deh = create_boolean_var('A3')
        
        self.modules['SIF3_DEH'] = FuzzyModule(
            'SIF3_DEH', {'A1': a1_deh, 'A2': a2_deh, 'A3': a3_deh}, priority,
            [
                ctrl.Rule(a1_deh['yes'] & a2_deh['yes'], priority['urgent']),
                ctrl.Rule(a1_deh['yes'] & a3_deh['yes'], priority['urgent']),
                ctrl.Rule(a2_deh['yes'] & a3_deh['yes'], priority['urgent']),
                ctrl.Rule(a1_deh['yes'], priority['high']),
                ctrl.Rule(a2_deh['yes'], priority['high']),
                ctrl.Rule(a3_deh['yes'], priority['medium']),
                ctrl.Rule(a1_deh['no'] & a2_deh['no'] & a3_deh['no'], priority['low'])
            ]
        )
        
        # SIF 4 - SAB (Saneamento Básico): B1, B2, B3, B4
        b1 = create_boolean_var('B1')
        b2 = create_boolean_var('B2')
        b3 = create_boolean_var('B3')
        b4 = create_boolean_var('B4')
        
        self.modules['SIF4_SAB'] = FuzzyModule(
            'SIF4_SAB', {'B1': b1, 'B2': b2, 'B3': b3, 'B4': b4}, priority,
            [
                ctrl.Rule(b1['yes'] & b2['yes'] & b3['yes'], priority['urgent']),
                ctrl.Rule(b3['yes'] & b4['yes'], priority['urgent']),
                ctrl.Rule(b1['yes'] & b3['yes'], priority['high']),
                ctrl.Rule(b2['yes'] & b3['yes'], priority['high']),
                ctrl.Rule(b1['yes'] & b2['yes'], priority['high']),
                ctrl.Rule(b3['yes'], priority['high']),
                ctrl.Rule(b1['yes'], priority['medium']),
                ctrl.Rule(b2['yes'], priority['medium']),
                ctrl.Rule(b4['yes'], priority['medium']),
                ctrl.Rule(b1['no'] & b2['no'] & b3['no'] & b4['no'], priority['low'])
            ]
        )
        
        # SIF 6 - CED (Carência Edílica): C1, C2, C3
        c1 = create_boolean_var('C1')
        c2 = create_boolean_var('C2')
        c3 = create_boolean_var('C3')
        
        self.modules['SIF6_CED'] = FuzzyModule(
            'SIF6_CED', {'C1': c1, 'C2': c2, 'C3': c3}, priority,
            [
                ctrl.Rule(c1['yes'] & c2['yes'], priority['urgent']),
                ctrl.Rule(c2['yes'] & c3['yes'], priority['urgent']),
                ctrl.Rule(c1['yes'] & c3['yes'], priority['high']),
                ctrl.Rule(c2['yes'], priority['urgent']),
                ctrl.Rule(c1['yes'], priority['high']),
                ctrl.Rule(c3['yes'], priority['high']),
                ctrl.Rule(c1['no'] & c2['no'] & c3['no'], priority['low'])
            ]
        )
        
        # SIF 7 - SGC (Serviços de Garantia Constitucional): D1, D2, D3, D4
        d1 = create_access_var('D1')
        d2 = create_access_var('D2')
        d3 = create_access_var('D3')
        d4 = create_access_var('D4')
        
        self.modules['SIF7_SGC'] = FuzzyModule(
            'SIF7_SGC', {'D1': d1, 'D2': d2, 'D3': d3, 'D4': d4}, priority,
            [
                ctrl.Rule(d1['low'] & d2['low'], priority['urgent']),
                ctrl.Rule(d1['low'] & d3['low'], priority['urgent']),
                ctrl.Rule(d2['low'] & d3['low'], priority['urgent']),
                ctrl.Rule(d1['low'], priority['high']),
                ctrl.Rule(d2['low'], priority['high']),
                ctrl.Rule(d3['low'], priority['high']),
                ctrl.Rule(d4['low'], priority['medium']),
                ctrl.Rule(d1['medium'] & d2['medium'] & d3['medium'] & d4['medium'], priority['medium']),
                ctrl.Rule(d1['high'] & d2['high'] & d3['high'] & d4['high'], priority['low'])
            ]
        )
        
        # SIF 8 - ASP (Acesso a Serviços Prioritários): D1, D2, D3
        d1_asp = create_access_var('D1')
        d2_asp = create_access_var('D2')
        d3_asp = create_access_var('D3')
        
        self.modules['SIF8_ASP'] = FuzzyModule(
            'SIF8_ASP', {'D1': d1_asp, 'D2': d2_asp, 'D3': d3_asp}, priority,
            [
                ctrl.Rule(d1_asp['low'] & d2_asp['low'], priority['urgent']),
                ctrl.Rule(d1_asp['low'] & d3_asp['low'], priority['urgent']),
                ctrl.Rule(d2_asp['low'] & d3_asp['low'], priority['urgent']),
                ctrl.Rule(d1_asp['low'], priority['high']),
                ctrl.Rule(d2_asp['low'], priority['high']),
                ctrl.Rule(d3_asp['low'], priority['high']),
                ctrl.Rule(d1_asp['medium'] & d2_asp['medium'] & d3_asp['medium'], priority['medium']),
                ctrl.Rule(d1_asp['high'] & d2_asp['high'] & d3_asp['high'], priority['low'])
            ]
        )
        
        # SIF 9 - RED (Renda Direta): E1, E2
        e1_red_universe = np.arange(0, 101, 1)
        e1_red = ctrl.Antecedent(e1_red_universe, 'E1')
        e1_red['low'] = fuzz.trimf(e1_red.universe, [0, 0, 33])
        e1_red['medium'] = fuzz.trimf(e1_red.universe, [25, 50, 75])
        e1_red['high'] = fuzz.trimf(e1_red.universe, [67, 100, 100])
        
        e2_red_universe = np.arange(0, 11, 1)
        e2_red = ctrl.Antecedent(e2_red_universe, 'E2')
        e2_red['low'] = fuzz.trimf(e2_red.universe, [0, 0, 3])
        e2_red['medium'] = fuzz.trimf(e2_red.universe, [2, 5, 7])
        e2_red['high'] = fuzz.trimf(e2_red.universe, [6, 10, 10])
        
        self.modules['SIF9_RED'] = FuzzyModule(
            'SIF9_RED', {'E1': e1_red, 'E2': e2_red}, priority,
            [
                ctrl.Rule(e1_red['low'] & e2_red['low'], priority['urgent']),
                ctrl.Rule(e1_red['low'], priority['urgent']),
                ctrl.Rule(e2_red['low'], priority['high']),
                ctrl.Rule(e1_red['medium'] & e2_red['medium'], priority['medium']),
                ctrl.Rule(e1_red['high'] & e2_red['high'], priority['low'])
            ]
        )
        
        # SIF 10 - PTR (Programas de Transferência de Renda): E3, E4
        e3 = create_boolean_var('E3')
        e4 = create_boolean_var('E4')
        
        self.modules['SIF10_PTR'] = FuzzyModule(
            'SIF10_PTR', {'E3': e3, 'E4': e4}, priority,
            [
                ctrl.Rule(e3['yes'] & e4['yes'], priority['urgent']),
                ctrl.Rule(e3['yes'], priority['high']),
                ctrl.Rule(e4['yes'], priority['high']),
                ctrl.Rule(e3['no'] & e4['no'], priority['low'])
            ]
        )
        
        # SIF 11 - PSE (Perfil Socioeconômico): E1, E2, E3, E4
        e1_pse_universe = np.arange(0, 101, 1)
        e1_pse = ctrl.Antecedent(e1_pse_universe, 'E1')
        e1_pse['low'] = fuzz.trimf(e1_pse.universe, [0, 0, 33])
        e1_pse['medium'] = fuzz.trimf(e1_pse.universe, [25, 50, 75])
        e1_pse['high'] = fuzz.trimf(e1_pse.universe, [67, 100, 100])
        
        e2_pse_universe = np.arange(0, 11, 1)
        e2_pse = ctrl.Antecedent(e2_pse_universe, 'E2')
        e2_pse['low'] = fuzz.trimf(e2_pse.universe, [0, 0, 3])
        e2_pse['medium'] = fuzz.trimf(e2_pse.universe, [2, 5, 7])
        e2_pse['high'] = fuzz.trimf(e2_pse.universe, [6, 10, 10])
        
        e3_pse = create_boolean_var('E3')
        e4_pse = create_boolean_var('E4')
        
        self.modules['SIF11_PSE'] = FuzzyModule(
            'SIF11_PSE', {'E1': e1_pse, 'E2': e2_pse, 'E3': e3_pse, 'E4': e4_pse}, priority,
            [
                ctrl.Rule(e1_pse['low'] & e2_pse['low'] & e3_pse['yes'], priority['urgent']),
                ctrl.Rule(e1_pse['low'] & e4_pse['yes'], priority['urgent']),
                ctrl.Rule(e1_pse['low'] & e2_pse['low'], priority['urgent']),
                ctrl.Rule(e3_pse['yes'] & e4_pse['yes'], priority['urgent']),
                ctrl.Rule(e1_pse['low'], priority['high']),
                ctrl.Rule(e2_pse['low'], priority['high']),
                ctrl.Rule(e3_pse['yes'], priority['high']),
                ctrl.Rule(e4_pse['yes'], priority['high']),
                ctrl.Rule(e1_pse['medium'] & e2_pse['medium'] & e3_pse['no'] & e4_pse['no'], priority['medium']),
                ctrl.Rule(e1_pse['high'] & e2_pse['high'], priority['low'])
            ]
        )
        
        print("✅ Subíndices (SIF) carregados")
    
    def _init_final_index(self):
        """Inicializa o índice final (ISF)."""
        priority = create_priority_var()
        
        # Variáveis para os SIFs (0-100)
        sif1 = ctrl.Antecedent(np.arange(0, 101, 1), 'SIF1_HAP')
        sif1['low'] = fuzz.trimf(sif1.universe, [0, 0, 35])
        sif1['medium'] = fuzz.trimf(sif1.universe, [25, 50, 75])
        sif1['high'] = fuzz.trimf(sif1.universe, [65, 85, 100])
        sif1['urgent'] = fuzz.trimf(sif1.universe, [90, 100, 100])
        
        sif3 = ctrl.Antecedent(np.arange(0, 101, 1), 'SIF3_DEH')
        sif3['low'] = fuzz.trimf(sif3.universe, [0, 0, 35])
        sif3['medium'] = fuzz.trimf(sif3.universe, [25, 50, 75])
        sif3['high'] = fuzz.trimf(sif3.universe, [65, 85, 100])
        sif3['urgent'] = fuzz.trimf(sif3.universe, [90, 100, 100])
        
        sif4 = ctrl.Antecedent(np.arange(0, 101, 1), 'SIF4_SAB')
        sif4['low'] = fuzz.trimf(sif4.universe, [0, 0, 35])
        sif4['medium'] = fuzz.trimf(sif4.universe, [25, 50, 75])
        sif4['high'] = fuzz.trimf(sif4.universe, [65, 85, 100])
        sif4['urgent'] = fuzz.trimf(sif4.universe, [90, 100, 100])
        
        sif6 = ctrl.Antecedent(np.arange(0, 101, 1), 'SIF6_CED')
        sif6['low'] = fuzz.trimf(sif6.universe, [0, 0, 35])
        sif6['medium'] = fuzz.trimf(sif6.universe, [25, 50, 75])
        sif6['high'] = fuzz.trimf(sif6.universe, [65, 85, 100])
        sif6['urgent'] = fuzz.trimf(sif6.universe, [90, 100, 100])
        
        sif11 = ctrl.Antecedent(np.arange(0, 101, 1), 'SIF11_PSE')
        sif11['low'] = fuzz.trimf(sif11.universe, [0, 0, 35])
        sif11['medium'] = fuzz.trimf(sif11.universe, [25, 50, 75])
        sif11['high'] = fuzz.trimf(sif11.universe, [65, 85, 100])
        sif11['urgent'] = fuzz.trimf(sif11.universe, [90, 100, 100])
        
        isf_priority = create_priority_var()
        
        self.modules['ISF_FINAL'] = FuzzyModule(
            'ISF_FINAL', 
            {'SIF1_HAP': sif1, 'SIF3_DEH': sif3, 'SIF4_SAB': sif4, 'SIF6_CED': sif6, 'SIF11_PSE': sif11},
            isf_priority,
            [
                ctrl.Rule(sif1['urgent'], isf_priority['urgent']),
                ctrl.Rule(sif3['urgent'], isf_priority['urgent']),
                ctrl.Rule(sif4['urgent'], isf_priority['urgent']),
                ctrl.Rule(sif6['urgent'], isf_priority['urgent']),
                ctrl.Rule(sif11['urgent'], isf_priority['urgent']),
                ctrl.Rule(sif1['high'] & sif3['high'], isf_priority['urgent']),
                ctrl.Rule(sif4['high'] & sif6['high'], isf_priority['urgent']),
                ctrl.Rule(sif1['high'] & sif4['high'], isf_priority['urgent']),
                ctrl.Rule(sif1['high'] & sif3['medium'] & sif4['medium'], isf_priority['high']),
                ctrl.Rule(sif1['medium'] & sif3['medium'] & sif4['medium'] & sif6['medium'], isf_priority['high']),
                ctrl.Rule(sif1['medium'] & sif3['medium'], isf_priority['medium']),
                ctrl.Rule(sif1['low'] & sif3['low'] & sif4['low'] & sif6['low'], isf_priority['low'])
            ]
        )
        
        print("✅ Índice Final (ISF) carregado")
    
    def get_module_names(self) -> List[str]:
        return list(self.modules.keys())
    
    def get_module(self, name: str) -> Optional[FuzzyModule]:
        return self.modules.get(name)
    
    def evaluate_module(self, module_name: str, inputs: Dict[str, float]) -> FuzzyResult:
        if module_name not in self.modules:
            raise ValueError(f"Module '{module_name}' not found. Available: {self.get_module_names()}")
        return self.modules[module_name].evaluate(inputs)
    
    def evaluate_all_indicators(self, inputs: Dict[str, float]) -> Dict[str, FuzzyResult]:
        results = {}
        for name in self.modules:
            if len(name) <= 2:  # Indicadores individuais
                try:
                    result = self.evaluate_module(name, {name: inputs.get(name, 0)})
                    results[name] = result
                except:
                    pass
        return results
    
    def evaluate_all_sifs(self, inputs: Dict[str, float]) -> Dict[str, FuzzyResult]:
        results = {}
        for name in self.modules:
            if name.startswith('SIF'):
                try:
                    module = self.modules[name]
                    module_inputs = {v: inputs.get(v, 0) for v in module.input_vars.keys()}
                    result = self.evaluate_module(name, module_inputs)
                    results[name] = result
                except:
                    pass
        return results
    
    def evaluate_final_index(self, sif_results: Dict[str, float]) -> FuzzyResult:
        inputs = {}
        for sif in ['SIF1_HAP', 'SIF3_DEH', 'SIF4_SAB', 'SIF6_CED', 'SIF11_PSE']:
            inputs[sif] = sif_results.get(sif, 0)
        return self.evaluate_module('ISF_FINAL', inputs)
    
    def get_module_info(self, module_name: str) -> Dict[str, Any]:
        if module_name not in self.modules:
            return {'error': f'Module {module_name} not found'}
        module = self.modules[module_name]
        return {
            'name': module.name,
            'input_vars': list(module.input_vars.keys()),
            'output_var': 'priority'
        }


def create_fuzzy_system() -> HousingFuzzySystem:
    return HousingFuzzySystem()
