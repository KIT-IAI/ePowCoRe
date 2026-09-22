from pathlib import Path

import matplotlib.pyplot as plt
import networkx
import pandapower
from pandapower.topology import create_nxgraph, unsupplied_buses

from epowcore.plausibility.checker import PlausibilityChecker
from epowcore.plausibility.plausibility_result import PlausibilityResult

try:
    import contextily as ctx
    import geopandas as gpd
    from shapely.geometry import Point
except ImportError:
    ctx = None
    gpd = None
    Point = None


class PandapowerPlausibilityChecker(
    PlausibilityChecker[pandapower.pandapowerNet]
):
    """Run plausibility checks on a pandapower network."""

    @staticmethod
    def _get_isolated_components(
        net: pandapower.pandapowerNet,
    ) -> list[list[int]]:
        isolated_buses = set(
            unsupplied_buses(
                net,
                respect_switches=True,
            )
        )

        if not isolated_buses:
            return []

        graph = create_nxgraph(
            net,
            respect_switches=True,
        )

        isolated_graph = graph.subgraph(isolated_buses)

        return [
            sorted(int(bus) for bus in component)
            for component in networkx.connected_components(
                isolated_graph
            )
        ]

    # STEP 4A: ADD THIS HERE
    def _has_bus_geodata(
        self,
        net: pandapower.pandapowerNet,
    ) -> bool:
        return (
            hasattr(net, "bus_geodata")
            and not net.bus_geodata.empty
            and "x" in net.bus_geodata.columns
            and "y" in net.bus_geodata.columns
        )

    # STEP 4B: ADD THIS DIRECTLY BELOW
    def _looks_like_lon_lat(
        self,
        net: pandapower.pandapowerNet,
    ) -> bool:
        if not self._has_bus_geodata(net):
            return False

        all_x = net.bus_geodata["x"].dropna().astype(float)
        all_y = net.bus_geodata["y"].dropna().astype(float)

        if all_x.empty or all_y.empty:
            return False

        return (
            all_x.between(-180, 180).all()
            and all_y.between(-90, 90).all()
        )

    # KEEP YOUR EXISTING CHECK METHOD HERE
    def check(
        self,
        model: pandapower.pandapowerNet,
    ) -> PlausibilityResult:
        net = model
        result = PlausibilityResult()

        isolated_components = self._get_isolated_components(net)

        result.isolated_areas = [
            [
                {
                    "component": "bus",
                    "name": str(net.bus.at[bus, "name"]),
                }
                for bus in component
            ]
            for component in isolated_components
        ]

        try:
            pandapower.runpp(net)
            result.converged = bool(net.converged)
        except Exception as exc:
            result.errors.append(str(exc))
            return result

        if not result.converged:
            return result

        # Bus voltage checks
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

        # Generator voltage checks
        for generator_index, row in net.res_gen.iterrows():
            vm_pu = float(row["vm_pu"])
            generator_name = str(
                net.gen.at[generator_index, "name"]
            )

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

        # Line loading checks
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

        # Transformer loading checks
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

    # STEP 5: REPLACE YOUR OLD plot_isolated_areas() WITH THIS
    def plot_isolated_areas(
        self,
        model: pandapower.pandapowerNet,
        result: PlausibilityResult,
        filepath: Path,
    ) -> None:
        net = model

        if not result.isolated_areas:
            return

        fig, ax = plt.subplots(figsize=(10, 8))

        has_geodata = self._has_bus_geodata(net)
        use_osm = (
            has_geodata
            and self._looks_like_lon_lat(net)
            and ctx is not None
            and gpd is not None
            and Point is not None
        )

        all_x = []
        all_y = []

        if has_geodata:
            all_x = net.bus_geodata["x"].dropna().astype(float)
            all_y = net.bus_geodata["y"].dropna().astype(float)

        if use_osm:
            points = []

            for bus_index in net.bus_geodata.index:
                x_value = float(net.bus_geodata.at[bus_index, "x"])
                y_value = float(net.bus_geodata.at[bus_index, "y"])

                points.append(
                    Point(
                        x_value,
                        y_value,
                    )
                )

            gdf = gpd.GeoDataFrame(
                {
                    "bus_index": list(net.bus_geodata.index),
                },
                geometry=points,
                crs="EPSG:4326",
            ).to_crs(epsg=3857)

            min_x, min_y, max_x, max_y = gdf.total_bounds

            x_margin = max(
                (max_x - min_x) * 0.05,
                100.0,
            )
            y_margin = max(
                (max_y - min_y) * 0.05,
                100.0,
            )

            ax.set_xlim(
                min_x - x_margin,
                max_x + x_margin,
            )
            ax.set_ylim(
                min_y - y_margin,
                max_y + y_margin,
            )

            ctx.add_basemap(
                ax,
                source=ctx.providers.CartoDB.Positron,
            )

        elif has_geodata and len(all_x) > 0 and len(all_y) > 0:
            min_x = all_x.min()
            max_x = all_x.max()
            min_y = all_y.min()
            max_y = all_y.max()

            x_margin = max(
                (max_x - min_x) * 0.05,
                0.01,
            )
            y_margin = max(
                (max_y - min_y) * 0.05,
                0.01,
            )

            ax.set_xlim(
                min_x - x_margin,
                max_x + x_margin,
            )
            ax.set_ylim(
                min_y - y_margin,
                max_y + y_margin,
            )

        isolated_components = self._get_isolated_components(net)

        for area_number, component in enumerate(
            isolated_components,
            start=1,
        ):
            area_bus_indices = set(component)

            bus_x_values = []
            bus_y_values = []

            # LINES
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

                from_x = float(
                    net.bus_geodata.at[from_bus, "x"]
                )
                from_y = float(
                    net.bus_geodata.at[from_bus, "y"]
                )
                to_x = float(
                    net.bus_geodata.at[to_bus, "x"]
                )
                to_y = float(
                    net.bus_geodata.at[to_bus, "y"]
                )

                if use_osm:
                    line_points = gpd.GeoSeries(
                        [
                            Point(from_x, from_y),
                            Point(to_x, to_y),
                        ],
                        crs="EPSG:4326",
                    ).to_crs(epsg=3857)

                    ax.plot(
                        [
                            line_points.iloc[0].x,
                            line_points.iloc[1].x,
                        ],
                        [
                            line_points.iloc[0].y,
                            line_points.iloc[1].y,
                        ],
                        zorder=2,
                    )
                else:
                    ax.plot(
                        [from_x, to_x],
                        [from_y, to_y],
                        zorder=2,
                    )

            transformer_points = []

            # TRANSFORMERS
            for _, transformer in net.trafo.iterrows():
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

                hv_x = float(
                    net.bus_geodata.at[hv_bus, "x"]
                )
                hv_y = float(
                    net.bus_geodata.at[hv_bus, "y"]
                )
                lv_x = float(
                    net.bus_geodata.at[lv_bus, "x"]
                )
                lv_y = float(
                    net.bus_geodata.at[lv_bus, "y"]
                )

                if use_osm:
                    trafo_points_geo = gpd.GeoSeries(
                        [
                            Point(hv_x, hv_y),
                            Point(lv_x, lv_y),
                        ],
                        crs="EPSG:4326",
                    ).to_crs(epsg=3857)

                    hv_plot_x = trafo_points_geo.iloc[0].x
                    hv_plot_y = trafo_points_geo.iloc[0].y
                    lv_plot_x = trafo_points_geo.iloc[1].x
                    lv_plot_y = trafo_points_geo.iloc[1].y
                else:
                    hv_plot_x = hv_x
                    hv_plot_y = hv_y
                    lv_plot_x = lv_x
                    lv_plot_y = lv_y

                ax.plot(
                    [hv_plot_x, lv_plot_x],
                    [hv_plot_y, lv_plot_y],
                    zorder=2,
                )

                transformer_points.append(
                    (
                        (hv_plot_x + lv_plot_x) / 2,
                        (hv_plot_y + lv_plot_y) / 2,
                    )
                )

            generator_points = []

            # GENERATORS
            for _, generator in net.gen.iterrows():
                generator_bus = int(generator["bus"])

                if generator_bus not in area_bus_indices:
                    continue

                if generator_bus not in net.bus_geodata.index:
                    continue

                gen_x = float(
                    net.bus_geodata.at[generator_bus, "x"]
                )
                gen_y = float(
                    net.bus_geodata.at[generator_bus, "y"]
                )

                if use_osm:
                    gen_point = gpd.GeoSeries(
                        [Point(gen_x, gen_y)],
                        crs="EPSG:4326",
                    ).to_crs(epsg=3857)

                    plot_x = gen_point.iloc[0].x
                    plot_y = gen_point.iloc[0].y
                else:
                    plot_x = gen_x
                    plot_y = gen_y

                generator_points.append(
                    (
                        plot_x,
                        plot_y,
                    )
                )

            # BUSES
            for bus_index in component:
                if bus_index not in net.bus_geodata.index:
                    continue

                x_value = float(
                    net.bus_geodata.at[bus_index, "x"]
                )
                y_value = float(
                    net.bus_geodata.at[bus_index, "y"]
                )

                if use_osm:
                    bus_point = gpd.GeoSeries(
                        [Point(x_value, y_value)],
                        crs="EPSG:4326",
                    ).to_crs(epsg=3857)


                    plot_x = bus_point.iloc[0].x
                    plot_y = bus_point.iloc[0].y
                else:
                    plot_x = x_value
                    plot_y = y_value

                bus_x_values.append(plot_x)
                bus_y_values.append(plot_y)

            # bus = circle
            if bus_x_values:
                ax.scatter(
                    bus_x_values,
                    bus_y_values,
                    marker="o",
                    s=50,
                    label="Bus",
                    zorder=3,
                )

            # transformer = square
            if transformer_points:
                ax.scatter(
                    [x for x, _ in transformer_points],
                    [y for _, y in transformer_points],
                    marker="s",
                    s=90,
                    label="Transformer",
                    zorder=4,
                )

            # generator = star
            if generator_points:
                ax.scatter(
                    [x for x, _ in generator_points],
                    [y for _, y in generator_points],
                    marker="*",
                    s=160,
                    label="Generator",
                    zorder=5,
                )

        ax.set_title(
            "Isolated network areas",
            pad=12,
        )

        if use_osm:
            ax.set_axis_off()
        else:
            ax.set_xlabel("X coordinate")
            ax.set_ylabel("Y coordinate")
            ax.set_aspect(
            "equal",
            adjustable="box",
            )

        if ax.has_data():
            handles, labels = ax.get_legend_handles_labels()

            unique = {}
            for handle, label in zip(handles, labels):
                if label not in unique:
                    unique[label] = handle

            ax.legend(
                unique.values(),
                unique.keys(),
            )

        fig.tight_layout()

        fig.savefig(
            filepath,
            bbox_inches="tight",
        )

        plt.close(fig)