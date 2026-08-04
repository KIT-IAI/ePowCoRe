import json
from pathlib import Path

import matplotlib.pyplot as plt
import networkx
import pandapower
from pandapower.topology import create_nxgraph, unsupplied_buses

from epowcore.plausibility.checker import PlausibilityChecker
from epowcore.plausibility.plausibility_result import PlausibilityResult


class PandapowerPlausibilityChecker(
    PlausibilityChecker[pandapower.pandapowerNet]
):
    """Run plausibility checks on a pandapower network."""

    def check(
        self,
        model: pandapower.pandapowerNet,
    ) -> PlausibilityResult:
        net = model
        result = PlausibilityResult()

        isolated_buses = set(
            unsupplied_buses(
                net,
                respect_switches=True,
            )
        )

        if isolated_buses:
            graph = create_nxgraph(
                net,
                respect_switches=True,
            )

            isolated_graph = graph.subgraph(isolated_buses)

            result.isolated_areas = [
                sorted(int(bus) for bus in component)
                for component in networkx.connected_components(
                    isolated_graph
                )
            ]

        try:
            pandapower.runpp(net)
            result.converged = bool(net.converged)
        except Exception as exc:
            result.errors.append(str(exc))
            return result

        if not result.converged:
            return result

        for bus_index, row in net.res_bus.iterrows():
            vm_pu = float(row["vm_pu"])

            if vm_pu < 0.8 or vm_pu > 1.2:
                result.hard_voltage_violations.append(
                    {
                        "bus_index": int(bus_index),
                        "vm_pu": vm_pu,
                    }
                )
            elif vm_pu < 0.9 or vm_pu > 1.1:
                result.soft_voltage_violations.append(
                    {
                        "bus_index": int(bus_index),
                        "vm_pu": vm_pu,
                    }
                )

        for line_index, row in net.res_line.iterrows():
            loading_percent = float(row["loading_percent"])

            if loading_percent > 100.0:
                result.overloaded_lines.append(
                    {
                        "line_index": int(line_index),
                        "loading_percent": loading_percent,
                    }
                )

        for transformer_index, row in net.res_trafo.iterrows():
            loading_percent = float(row["loading_percent"])

            if loading_percent > 100.0:
                result.overloaded_transformers.append(
                    {
                        "transformer_index": int(transformer_index),
                        "loading_percent": loading_percent,
                    }
                )

        return result

    def plot_isolated_areas(
        self,
        model: pandapower.pandapowerNet,
        result: PlausibilityResult,
        filepath: Path,
    ) -> None:
        net = model

        if not result.isolated_areas:
            return

        fig, ax = plt.subplots()

        for area_number, area in enumerate(
            result.isolated_areas,
            start=1,
        ):
            x_values = []
            y_values = []

            for bus_index in area:
                geo_value = net.bus.at[bus_index, "geo"]

                if not geo_value:
                    continue

                geo_data = json.loads(geo_value)
                coordinates = geo_data.get("coordinates")

                if not coordinates or len(coordinates) < 2:
                    continue

                x_value = float(coordinates[0])
                y_value = float(coordinates[1])

                x_values.append(x_value)
                y_values.append(y_value)

                ax.annotate(
                    str(bus_index),
                    (x_value, y_value),
                )

            if x_values:
                ax.scatter(
                    x_values,
                    y_values,
                    label=f"Isolated area {area_number}",
                )

        ax.set_title("Isolated network areas")
        ax.set_xlabel("x")
        ax.set_ylabel("y")

        if ax.has_data():
            ax.legend()

        fig.savefig(filepath)
        plt.close(fig)