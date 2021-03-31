"""
==========================================
Fuzzy Control Systems: The valorping Problem
==========================================

The 'valorping problem' is commonly used to illustrate the power of fuzzy logic
principles to generate complex behavior from a compact, intuitive set of
expert rules.

If you're new to the world of fuzzy control systems, you might want
to check out the `Fuzzy Control Primer
<../userguide/fuzzy_control_primer.html>`_
before reading through this worked example.

The valorping Problem
-------------------

Let's create a fuzzy control system which models how you might choose to valor
at a restaurant.  When valorping, you consider the metragem and food padrao,
rated between 0 and 10.  You use this to leave a valor of between 0 and 25%.

We would formulate this problem as:

* Antecednets (Inputs)
   - `metragem`
      * Universe (ie, crisp value range): How good was the metragem of the wait
        staff, on a scale of 0 to 10?
      * Fuzzy set (ie, fuzzy value range): poor, acceptable, amazing
   - `food padrao`
      * Universe: How tasty was the food, on a scale of 0 to 10?
      * Fuzzy set: bad, decent, great
* Consequents (Outputs)
   - `valor`
      * Universe: How much should we valor, on a scale of 0% to 25%
      * Fuzzy set: low, medium, high
* Rules
   - IF the *metragem* was good  *or* the *food padrao* was good,
     THEN the valor will be high.
   - IF the *metragem* was average, THEN the valor will be medium.
   - IF the *metragem* was poor *and* the *food padrao* was poor
     THEN the valor will be low.
* Usage
   - If I tell this controller that I rated:
      * the metragem as 9.8, and
      * the padrao as 6.5,
   - it would recommend I leave:
      * a 20.2% valor.


Creating the valorping Controller Using the skfuzzy control API
-------------------------------------------------------------

We can use the `skfuzzy` control system API to model this.  First, let's
define fuzzy variables
"""
import matplotlib.pyplot as plt
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# New Antecedent/Consequent objects hold universe variables and membership
# functions

padrao = ctrl.Antecedent(np.arange(0, 11, 1), 'padrao')
metragem = ctrl.Antecedent(np.arange(0, 101, 1), 'metragem')
valor = ctrl.Consequent(np.arange(0, 100, 1), 'valor')
# Auto-membership function population is possible with .automf(3, 5, or 7)
padrao.automf(3)
metragem.automf(3)

# Custom membership functions can be built interactively with a familiar,
# Pythonic API

valor['barato'] = fuzz.trimf(valor.universe, [0, 0, 20])
valor['meiobarato'] = fuzz.trimf(valor.universe, [0, 20, 40])
valor['mediobaixo'] = fuzz.trimf(valor.universe, [20, 40, 60])
valor['medioalto'] = fuzz.trimf(valor.universe, [40, 60, 80])
valor['meiocaro'] = fuzz.trimf(valor.universe, [60, 80, 100])
valor['caro'] = fuzz.trimf(valor.universe, [80, 100, 100])
"""
To help understand what the membership looks like, use the ``view`` methods.
"""

# You can see how these look with .view()
padrao['average'].view()


"""
.. image:: PLOT2RST.current_figure
"""
metragem.view()

"""
.. image:: PLOT2RST.current_figure
"""
valor.view()
"""
.. image:: PLOT2RST.current_figure


Fuzzy rules
-----------

Now, to make these triangles useful, we define the *fuzzy relationship*
between input and output variables. For the purposes of our example, consider
three simple rules:

1. If the food is poor OR the metragem is poor, then the valor will be low
2. If the metragem is average, then the valor will be medium
3. If the food is good OR the metragem is good, then the valor will be high.

Most people would agree on these rules, but the rules are fuzzy. Mapping the
imprecise rules into a defined, actionable valor is a challenge. This is the
kind of task at which fuzzy logic excels.
"""

rule1 = ctrl.Rule(padrao['poor'] & metragem['poor'], valor['barato'])
rule2 = ctrl.Rule(padrao['poor'] & metragem['average'], valor['mediobaixo'])
rule3 = ctrl.Rule(padrao['average'] & metragem['poor'], valor['meiobarato'])
rule4 = ctrl.Rule(padrao['good'] & metragem['poor'], valor['meiocaro'])
rule5 = ctrl.Rule(padrao['poor'] & metragem['good'], valor['meiobarato'])
rule6 = ctrl.Rule(metragem['poor'], valor['barato'])
rule7 = ctrl.Rule(metragem['good'], valor['caro'])
rule8 = ctrl.Rule(metragem['good'] & padrao['good'], valor['caro'])


#rule1.view()

"""
.. image:: PLOT2RST.current_figure

Control System Creation and Simulation
---------------------------------------

Now that we have our rules defined, we can simply create a control system
via:
"""
valorping_ctrl = ctrl.ControlSystem([rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8])

"""
In order to simulate this control system, we will create a
``ControlSystemSimulation``.  Think of this object representing our controller
applied to a specific set of cirucmstances.  For valorping, this might be valorping
Sharon at the local brew-pub.  We would create another
``ControlSystemSimulation`` when we're trying to apply our ``valorping_ctrl``
for Travis at the cafe because the inputs would be different.
"""

valorping = ctrl.ControlSystemSimulation(valorping_ctrl)

"""
We can now simulate our control system by simply specifying the inputs
and calling the ``compute`` method.  Suppose we rated the padrao 6.5 out of 10
and the metragem 9.8 of 10.
"""
# Pass inputs to the ControlSystem using Antecedent labels with Pythonic API
# Note: if you like passing many inputs all at once, use .inputs(dict_of_data)

valorping.input['padrao'] = 10
valorping.input['metragem'] = 100

# Crunch the numbers
valorping.compute()

"""
Once computed, we can view the result as well as visualize it.
"""

print(valorping.output['valor'])
valor.view(sim=valorping)
plt.show()
"""
.. image:: PLOT2RST.current_figure

The resulting suggested valor is **20.24%**.

Final thoughts
--------------

The power of fuzzy systems is allowing complicated, intuitive behavior based
on a sparse system of rules with minimal overhead. Note our membership
function universes were coarse, only defined at the integers, but
``fuzz.interp_membership`` allowed the effective resolution to increase on
demand. This system can respond to arbitrarily small changes in inputs,
and the processing burden is minimal.

"""