modular-trader documentation
============================

Modular-trader is a algorithmic trading framework written in Python, designed with focus on modularity and flexibility. The framework provides solution as building blocks for live deployment of algorithmic trading, consists of five modules; Asset Selection, Signal Generation, Portfolio Builder, Order Execution and, Risk Management.

.. toctree::
   :titlesonly:

   {% for page in pages|selectattr("is_top_level_object") %}
   {{ page.include_path }}
   {% endfor %}