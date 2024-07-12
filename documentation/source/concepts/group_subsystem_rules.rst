Subsystem Group Rules
=====================
Subsystem Group Rules allow components to be grouped together in a subsystem if they match a rule set.
This can be useful for grouping common collections of components together
that might need to be further modified during export to another format.

The rules are defined in a :doc:`/configuration` file under the path `GDF.GroupRules` as a list of rules.

.. code-block:: yaml
    
    - name: "Example"
      priority: 0
      include_inner: false
      remove_inner: false
      rules:
        - component: "Core Component"
        distance: 0
        connections: []
        - component: "Component 1"
        distance: 1
        connections:
            - "A"
        - component: "Component 2"
        distance: 2
        connections:
            - "A"
            - "B"

If a component exists that matches all of the rules in a rule set, then all of the components in the rule set will be grouped together in a subsystem.
The component with distance 0 is called a core component in the code.
If a component matches multiple rule sets, then the rule set with the highest priority is used.

Port names for connections are always seen from the core component's direction outwards.
In the example above, the core component has a connection named "A" that connects to "Component 1".
"Component 1" has a connection named "B" that connects to "Component 2".
If the connections were reversed, then the rule set would not match.

If multiple components match a rule set, from the same core component,
then all matching components are moved in the same subsystem.

Rules Format
------------
* *name*: The name of the rule set
* *priority*: The priority of the rule set. Higher priority rule sets are matched first.
* inner: One of "include", "remove" or "ignore"
    * *include*: All-matching rules are inserted for each distance lower than the highest distance specified in the rules without defined rules. This moves the components in the subsystem to the core component.
    * *remove*: Remove inner components but keep their connections by directly connecting their neighbors. 
    * *ignore*: Ignore inner components. This is the default.
* *rules*: A list of matching rules

Rule:

* *component*: The type name of the component to match.
* *distance*: The number of connections between the core component and the component to match.
* *connections*: The names of the connections between the core component and the component to match.
  If empty or "-", all connections are matched.