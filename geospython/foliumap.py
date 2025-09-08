import folium

"""A class for creating interactive maps with Folium.
This module provides a Map class that extends folium.Map and includes methods
to add basemaps, GeoJSON data, vector data, and layer controls.
"""


class Map(folium.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        """Initialize the map.

        Args:
            center (list, optional): The initial center of the map. Defaults to [20, 0].
            zoom (int, optional): The initial zoom level of the map. Defaults to 2.
            height (str, optional): The height of the map. Defaults to "600px".
        """

        super().__init__(location=center, zoom_start=zoom, height=height, **kwargs)

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add a basemap to the map.

        Args:
            basemap (str): The name of the basemap to add.
        """

        import xyzservices.providers as xyz

        providers = xyz.flatten()

        basemaps = {
            "OpenStreetMap": folium.TileLayer("openstreetmap"),
            "CartoDB positron": folium.TileLayer("cartodb positron"),
            "CartoDB dark_matter": folium.TileLayer("cartodb dark_matter"),
            "Esri WorldImagery": folium.TileLayer("esri worldimagery"),
            "OpenTopoMap": folium.TileLayer(
                tiles=providers["OpenTopoMap"].build_url(),
                attr=providers["OpenTopoMap"].attribution,
                name=providers["OpenTopoMap"].name,
            ),
            "OSM HOT": folium.TileLayer(
                tiles=providers["OpenStreetMap.HOT"].build_url(),
                attr=providers["OpenStreetMap.HOT"].attribution,
                name=providers["OpenStreetMap.HOT"].name,
            ),
            "Satellite": folium.TileLayer(
                tiles=providers["Gaode.Satellite"].build_url(),
                attr=providers["Gaode.Satellite"].attribution,
                name=providers["Gaode.Satellite"].name,
            ),
            "Esri WorldStreetMap": folium.TileLayer(
                tiles=providers["Esri.WorldStreetMap"].build_url(),
                attr=providers["Esri.WorldStreetMap"].attribution,
                name=providers["Esri.WorldStreetMap"].name,
            ),
            "Esri NatGeo": folium.TileLayer(
                tiles=providers["Esri.NatGeoWorldMap"].build_url(),
                attr=providers["Esri.NatGeoWorldMap"].attribution,
                name=providers["Esri.NatGeoWorldMap"].name,
            ),
            "World At Night": folium.TileLayer(
                tiles=providers["NASAGIBS.ViirsEarthAtNight2012"].build_url(),
                attr=providers["NASAGIBS.ViirsEarthAtNight2012"].attribution,
                name=providers["NASAGIBS.ViirsEarthAtNight2012"].name,
            ),
            "Strava": folium.TileLayer(
                tiles=providers["Strava.All"].build_url(),
                attr=providers["Strava.All"].attribution,
                name=providers["Strava.All"].name,
            ),
        }

        if basemap in basemaps:
            basemaps[basemap].add_to(self)
        else:
            basemaps["OpenStreetMap"].add_to(self)

    def add_geojson(self, data, zoom_to_layer=True, hover_style=None, **kwargs):
        """Add GeoJSON data to the map.

        Args:
            data (str, dict): The GeoJSON data to add.
            zoom_to_layer (bool, optional): Whether to zoom to the layer's bounds. Defaults to True.
            hover_style (dict, optional): The style to apply on hover. Defaults to None.
        """

        import geopandas as gpd

        if isinstance(data, str):

            gdf = gpd.read_file(data)
            geojson_data = gdf.__geo_interface__

        elif isinstance(data, dict):

            geojson_data = data
            gdf = gpd.GeoDataFrame.from_features(geojson_data["features"])

        if hover_style is None:
            hover_style = {"color": "yellow", "fillOpacity": 0.5}

        folium.GeoJson(geojson_data, **kwargs).add_to(self)

        # if zoom_to_layer:
        #     bounds = gdf.total_bounds
        #     self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_vector(self, data, **kwargs):
        """Add vector data to the map.

        Args:
            data (str, dict): The vector data to add.

        Raises:
            ValueError: If the data is not a valid format.
        """

        import geopandas as gpd

        if isinstance(data, str):
            layer = gpd.read_file(data)
            geojson_data = layer.__geo_interface__

            self.add_geojson(geojson_data, **kwargs)

        elif isinstance(data, gpd.GeoDataFrame):
            geojson_data = data.__geo_interface__

            self.add_geojson(geojson_data, **kwargs)
        elif isinstance(data, dict):
            geojson_data = data
            self.add_geojson(geojson_data, **kwargs)
        else:
            raise ValueError(
                "Data must be a file path, GeoDataFrame, or GeoJSON dictionary."
            )

    def add_layer_control(self):
        """Add a layer control to the map."""

        folium.LayerControl().add_to(self)
