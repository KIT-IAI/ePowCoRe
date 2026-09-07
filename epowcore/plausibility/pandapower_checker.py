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
                [
                    {
                        "component": "bus",
                        "name": str(net.bus.at[int(bus), "name"]),
                        "index": int(bus),
                    }
                    for bus in sorted(component)
                ]
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
            bus_name = str(net.bus.at[bus_index, "name"])

            if vm_pu < 0.8 or vm_pu > 1.2:
                result.hard_voltage_violations.append(
                    {
                        "component": "bus",
                        "name": bus_name,
                        "vm_pu": vm_pu,
                    }
                )
            elif vm_pu < 0.9 or vm_pu > 1.1:
                result.soft_voltage_violations.append(
                    {
                        "component": "bus",
                        "name": bus_name,
                        "vm_pu": vm_pu,
                    }
                )

        for generator_index, row in net.res_gen.iterrows():
            vm_pu = float(row["vm_pu"])
            generator_name = str(net.gen.at[generator_index, "name"])

            if vm_pu < 0.8 or vm_pu > 1.2:
                result.generator_hard_voltage_violations.append(
                    {
                        "component": "gen",
                        "name": generator_name,
                        "vm_pu": vm_pu,
                    }
                )
            elif vm_pu < 0.9 or vm_pu > 1.1:
                result.generator_soft_voltage_violations.append(
                    {
                        "component": "gen",
                        "name": generator_name,
                        "vm_pu": vm_pu,
                    }
                )

        for line_index, row in net.res_line.iterrows():
            loading_percent = float(row["loading_percent"])
            line_name = str(net.line.at[line_index, "name"])

            if loading_percent > 100.0:
                result.overloaded_lines.append(
                    {
                        "component": "line",
                        "name": line_name,
                        "loading_percent": loading_percent,
                    }
                )

        for transformer_index, row in net.res_trafo.iterrows():
            loading_percent = float(row["loading_percent"])
            transformer_name = str(
                net.trafo.at[transformer_index, "name"]
            )

            if loading_percent > 100.0:
                result.overloaded_transformers.append(
                    {
                        "component": "trafo",
                        "name": transformer_name,
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

        max_labels = 20

        fig, ax = plt.subplots()

        all_x = net.bus_geodata["x"].dropna().astype(float)
        all_y = net.bus_geodata["y"].dropna().astype(float)

        if all_x.empty or all_y.empty:
            plt.close(fig)
            return

        min_x = all_x.min()
        max_x = all_x.max()
        min_y = all_y.min()
        max_y = all_y.max()

        x_margin = max((max_x - min_x) * 0.15, 0.05)
        y_margin = max((max_y - min_y) * 0.2, 0.05)

        ax.set_xlim(min_x - x_margin, max_x + x_margin)
        ax.set_ylim(min_y - y_margin, max_y + y_margin)

        y_midpoint = (min_y + max_y) / 2

        for area_number, area in enumerate(
            result.isolated_areas,
            start=1,
        ):
            area_bus_indices = {bus["index"] for bus in area}

            x_values = []
            y_values = []

            # Draw lines inside the isolated area
            for _, line in net.line.iterrows():
                from_bus = int(line["from_bus"])
                to_bus = int(line["to_bus"])

                if (
                    from_bus not in area_bus_indices
                    or to_bus not in area_bus_indices
                ):
                    continue

                if (
                    from_bus not in net.bus_geodata.index
                    or to_bus not in net.bus_geodata.index
                ):
                    continue

                from_x = float(net.bus_geodata.at[from_bus, "x"])
                from_y = float(net.bus_geodata.at[from_bus, "y"])
                to_x = float(net.bus_geodata.at[to_bus, "x"])
                to_y = float(net.bus_geodata.at[to_bus, "y"])

                ax.plot(
                    [from_x, to_x],
                    [from_y, to_y],
                )

            generator_labels = []

            for generator_index, generator in net.gen.iterrows():
                generator_bus = int(generator["bus"])

                if generator_bus not in area_bus_indices:
                    continue

                if generator_bus not in net.bus_geodata.index:
                    continue

                x_value = float(net.bus_geodata.at[generator_bus, "x"])
                y_value = float(net.bus_geodata.at[generator_bus, "y"])

                generator_labels.append(
                    (
                        x_value,
                        y_value,
                        f'gen: {generator["name"]}',
                    )
                )

            transformer_labels = []

            for transformer_index, transformer in net.trafo.iterrows():
                hv_bus = int(transformer["hv_bus"])
                lv_bus = int(transformer["lv_bus"])

                if (
                    hv_bus not in area_bus_indices
                    or lv_bus not in area_bus_indices
                ):
                    continue

                if (
                    hv_bus not in net.bus_geodata.index
                    or lv_bus not in net.bus_geodata.index
                ):
                    continue

                hv_x = float(net.bus_geodata.at[hv_bus, "x"])
                hv_y = float(net.bus_geodata.at[hv_bus, "y"])
                lv_x = float(net.bus_geodata.at[lv_bus, "x"])
                lv_y = float(net.bus_geodata.at[lv_bus, "y"])

                ax.plot(
                    [hv_x, lv_x],
                    [hv_y, lv_y],
                )

                transformer_labels.append(
                    (
                        (hv_x + lv_x) / 2,
                        (hv_y + lv_y) / 2,
                        f'trafo: {transformer["name"]}',
                    )
                )

            total_labels = (
                len(area)
                + len(generator_labels)
                + len(transformer_labels)
            )

            has_priority_labels = bool(generator_labels or transformer_labels)
            show_bus_labels = not has_priority_labels and total_labels <= max_labels

            for bus in area:
                bus_index = bus["index"]

                if bus_index not in net.bus_geodata.index:
                    continue

                x_value = float(net.bus_geodata.at[bus_index, "x"])
                y_value = float(net.bus_geodata.at[bus_index, "y"])

                x_values.append(x_value)
                y_values.append(y_value)

                if not show_bus_labels:
                    continue

                if y_value >= y_midpoint:
                    offset = (5, -8)
                    vertical_alignment = "top"
                else:
                    offset = (5, 8)
                    vertical_alignment = "bottom"

                ax.annotate(
                    f'{bus["component"]}: {bus["name"]}',
                    (x_value, y_value),
                    xytext=offset,
                    textcoords="offset points",
                    va=vertical_alignment,
                )

            # Transformers and generators have label priority
            for x_value, y_value, label in transformer_labels:
                ax.annotate(
                    label,
                    (x_value, y_value),
                    xytext=(0, 14),
                    textcoords="offset points",
                    ha="center",
                    va="bottom",
                )

            for x_value, y_value, label in generator_labels:
                ax.annotate(
                    label,
                    (x_value, y_value),
                    xytext=(8, -14),
                    textcoords="offset points",
                    ha="left",
                    va="top",
                )               

            if x_values:
                ax.scatter(
                x_values,
                y_values,
                label=f"Isolated area {area_number}",
                zorder=3,
                )

        ax.set_title("Isolated network areas", pad=12)
        ax.set_xlabel("X coordinate")
        ax.set_ylabel("Y coordinate")
        ax.set_aspect("equal", adjustable="box")

        if ax.has_data():
            ax.legend()

        fig.tight_layout()
        fig.savefig(
            filepath,
            bbox_inches="tight",
        )
        plt.close(fig)