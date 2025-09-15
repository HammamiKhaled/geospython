"""Main module.
This module provides a Map class for creating and manipulating interactive maps using ipyleaflet.
It includes methods for adding various types of layers, such as basemaps, GeoJSON data, vector data,
raster data, images, WMS layers, and videos.
"""

import ipyleaflet


class Map(ipyleaflet.Map):
    def __init__(self, center=[20, 0], zoom=2, height="600px", **kwargs):
        """Initialize the map.

        Args:
            center (list, optional): The initial center of the map. Defaults to [20, 0].
            zoom (int, optional): The initial zoom level of the map. Defaults to 2.
            height (str, optional): The height of the map. Defaults to "600px".
            **kwargs: Additional keyword arguments for the ipyleaflet.Map class.
        """
        super().__init__(center=center, zoom=zoom, **kwargs)
        self.layout.height = height
        self.scroll_wheel_zoom = True

    def add_basemap(self, basemap="OpenStreetMap"):
        """Add a basemap to the map.

        Args:
            basemap (str): The name of the basemap to add.
        """

        basemaps = {
            "OpenStreetMap": ipyleaflet.basemaps.OpenStreetMap,
            "OpenTopoMap": ipyleaflet.basemaps.OpenTopoMap,
            "CartoDB positron": ipyleaflet.basemaps.CartoDB.Positron,
            "CartoDB dark_matter": ipyleaflet.basemaps.CartoDB.DarkMatter,
            "OSM HOT": ipyleaflet.basemaps.OpenStreetMap.HOT,
            "Satellite": ipyleaflet.basemaps.Gaode.Satellite,
            "Esri WorldStreetMap": ipyleaflet.basemaps.Esri.WorldStreetMap,
            "Esri WorldImagery": ipyleaflet.basemaps.Esri.WorldImagery,
            "Esri NatGeo": ipyleaflet.basemaps.Esri.NatGeoWorldMap,
            "World At Night": ipyleaflet.basemaps.NASAGIBS.ViirsEarthAtNight2012,
            "Strava": ipyleaflet.basemaps.Strava.All,
        }

        if basemap in basemaps:
            url = basemaps[basemap].build_url()
            layer = ipyleaflet.TileLayer(url=url, name=basemap)
            self.add_layer(layer)
        else:
            url = basemaps["OpenStreetMap"].build_url()
            layer = ipyleaflet.TileLayer(url=url, name="OpenStreetMap")
            self.add_layer(layer)

    def add_geojson(self, data, zoom_to_layer=True, hover_style=None, **kwargs):
        """Add GeoJSON data to the map.

        Args:
            data (str, dict): The GeoJSON data to add.
            zoom_to_layer (bool, optional): Whether to zoom to the layer's bounds. Defaults to True.
            hover_style (dict, optional): The style to apply on hover. Defaults to None.
            **kwargs: Additional keyword arguments for the ipyleaflet.GeoJSON layer.
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

        geojson_layer = ipyleaflet.GeoJSON(
            data=geojson_data, hover_style=hover_style, **kwargs
        )
        self.add_layer(geojson_layer)

        if zoom_to_layer:
            bounds = gdf.total_bounds
            self.fit_bounds([[bounds[1], bounds[0]], [bounds[3], bounds[2]]])

    def add_vector(self, data, **kwargs):
        """Add vector data to the map.

        Args:
            data (str, GeoDataFrame, dict): The vector data to add. Can be a file path, GeoDataFrame, or GeoJSON dictionary.
            **kwargs: Additional keyword arguments for the add_geojson method.

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
        control = ipyleaflet.LayersControl(position="topright")
        self.add_control(control)

    def add_raster(
        self, filepath, name=None, colormap="viridis", opacity=1.0, **kwargs
    ):
        """Add a raster layer to the map.

        Args:
            filepath (str): The file path to the raster data.
            name (str, optional): The name of the layer. Defaults to None.
            colormap (str, optional): The colormap to use. Defaults to "viridis".
            opacity (float, optional): The opacity of the layer. Defaults to 1.0
            **kwargs: Additional keyword arguments for the tile layer.
        """

        from localtileserver import TileClient, get_leaflet_tile_layer

        if name is None:
            name = "Tile Layer"

        client = TileClient(filepath)
        tile_layer = get_leaflet_tile_layer(
            client, name=name, colormap=colormap, opacity=opacity, **kwargs
        )
        self.add(tile_layer)
        self.center = client.center()
        self.zoom = client.default_zoom

    def add_image(self, image, bounds=None, opacity=1.0, **kwargs):
        """Adds an image to the map.

        Args:
            image (str): The file path to the image.
            bounds (list, optional): The bounds for the image. Defaults to None.
            opacity (float, optional): The opacity of the image. Defaults to 1.0.
            **kwargs: Additional keyword arguments for the ipyleaflet.ImageOverlay layer.
        """

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]

        overlay = ipyleaflet.ImageOverlay(
            url=image, bounds=bounds, opacity=opacity, **kwargs
        )
        self.add(overlay)

    def add_wms_layer(
        self, url, layers, format="image/png", transparent=True, **kwargs
    ):
        """Adds a WMS layer to the map.

        Args:
            url (str): The WMS service URL.
            layers (str): The layers to display.
            format (str, optional): The image format. Defaults to "image/png".
            transparent (bool, optional): Whether the layer is transparent. Defaults to True.
            **kwargs: Additional keyword arguments for the ipyleaflet.WMSLayer layer.
        """
        layer = ipyleaflet.WMSLayer(
            url=url, layers=layers, format=format, transparent=transparent, **kwargs
        )
        self.add(layer)

    def add_video(self, video, bounds=None, opacity=1.0, **kwargs):
        """Adds a video to the map.

        Args:
            video (str): The file path to the video.
            bounds (list, optional): The bounds for the video. Defaults to None.
            opacity (float, optional): The opacity of the video. Defaults to 1.0.
            **kwargs: Additional keyword arguments for the ipyleaflet.VideoOverlay layer.
        """

        if bounds is None:
            bounds = [[-90, -180], [90, 180]]
        overlay = ipyleaflet.VideoOverlay(
            url=video, bounds=bounds, opacity=opacity, **kwargs
        )
        self.add(overlay)
