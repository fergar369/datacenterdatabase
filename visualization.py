"""
Interactive map visualization for data center facilities
"""

import folium
from folium.plugins import MarkerCluster
from typing import List, Dict
import config


class MapVisualizer:
    """Create interactive map of data center facilities"""

    def __init__(self):
        self.map = None

    def create_map(self, facilities: List[Dict], output_file: str = config.OUTPUT_MAP):
        """
        Create interactive Folium map

        Args:
            facilities: List of facility dictionaries
            output_file: Output HTML filename
        """

        # Filter facilities with valid coordinates
        valid_facilities = [f for f in facilities
                          if f.get('latitude') and f.get('longitude')]

        if not valid_facilities:
            print("⚠ No facilities with valid coordinates to map")
            return

        # Calculate map center (average of all coordinates)
        avg_lat = sum(f['latitude'] for f in valid_facilities) / len(valid_facilities)
        avg_lon = sum(f['longitude'] for f in valid_facilities) / len(valid_facilities)

        # Create base map
        self.map = folium.Map(
            location=[avg_lat, avg_lon],
            zoom_start=5,
            tiles='OpenStreetMap'
        )

        # Add marker cluster for better performance
        marker_cluster = MarkerCluster().add_to(self.map)

        # Add markers for each facility
        for facility in valid_facilities:
            self._add_marker(facility, marker_cluster)

        # Add legend
        self._add_legend()

        # Save map
        self.map.save(output_file)
        print(f"✓ Interactive map saved: {output_file}")
        print(f"  Mapped {len(valid_facilities)} facilities")

    def _add_marker(self, facility: Dict, marker_cluster):
        """Add a marker for a facility"""

        # Determine marker color based on status
        status = facility.get('status', config.STATUS_PROPOSED)
        color = config.MAP_COLORS.get(status, 'gray')

        # Determine marker size based on capacity
        capacity = facility.get('capacity_mw', 0)
        if capacity > 200:
            icon_size = 'large'
            radius = 15
        elif capacity > 100:
            icon_size = 'medium'
            radius = 10
        else:
            icon_size = 'small'
            radius = 7

        # Create popup content
        popup_html = self._create_popup(facility)

        # Create marker
        folium.CircleMarker(
            location=[facility['latitude'], facility['longitude']],
            radius=radius,
            popup=folium.Popup(popup_html, max_width=300),
            color=color,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(marker_cluster)

    def _create_popup(self, facility: Dict) -> str:
        """Create HTML popup content for a facility"""

        name = facility.get('project_name', 'Unknown')
        operator = facility.get('operator_company', 'Unknown')
        capacity = facility.get('capacity_mw', 0)
        status = facility.get('status', 'Unknown')
        location = self._format_location(facility)
        online_date = facility.get('expected_online_date', 'Unknown')
        source = facility.get('data_source', 'Unknown')
        match_reason = facility.get('match_reason', 'N/A')

        html = f"""
        <div style="font-family: Arial, sans-serif; font-size: 12px;">
            <h4 style="margin: 0 0 10px 0; color: #333;">{name}</h4>

            <table style="width: 100%; border-collapse: collapse;">
                <tr>
                    <td style="padding: 3px; font-weight: bold;">Operator:</td>
                    <td style="padding: 3px;">{operator}</td>
                </tr>
                <tr>
                    <td style="padding: 3px; font-weight: bold;">Capacity:</td>
                    <td style="padding: 3px;"><strong>{capacity:.1f} MW</strong></td>
                </tr>
                <tr>
                    <td style="padding: 3px; font-weight: bold;">Status:</td>
                    <td style="padding: 3px;">{status}</td>
                </tr>
                <tr>
                    <td style="padding: 3px; font-weight: bold;">Location:</td>
                    <td style="padding: 3px;">{location}</td>
                </tr>
                <tr>
                    <td style="padding: 3px; font-weight: bold;">Expected Online:</td>
                    <td style="padding: 3px;">{online_date}</td>
                </tr>
                <tr>
                    <td style="padding: 3px; font-weight: bold;">Data Source:</td>
                    <td style="padding: 3px;">{source}</td>
                </tr>
                <tr>
                    <td style="padding: 3px; font-weight: bold;">Match Reason:</td>
                    <td style="padding: 3px; font-size: 10px;"><em>{match_reason}</em></td>
                </tr>
            </table>
        </div>
        """

        return html

    def _format_location(self, facility: Dict) -> str:
        """Format location string"""
        parts = []

        if facility.get('location_city'):
            parts.append(facility['location_city'])
        if facility.get('location_county'):
            parts.append(f"{facility['location_county']} County")
        if facility.get('location_state'):
            parts.append(facility['location_state'])

        return ", ".join(parts) if parts else "Unknown"

    def _add_legend(self):
        """Add legend to map"""

        legend_html = """
        <div style="
            position: fixed;
            bottom: 50px;
            right: 50px;
            width: 200px;
            background-color: white;
            border: 2px solid grey;
            border-radius: 5px;
            z-index: 9999;
            font-family: Arial, sans-serif;
            font-size: 12px;
            padding: 10px;
        ">
            <h4 style="margin-top: 0;">Legend</h4>

            <p style="margin: 5px 0;">
                <span style="display: inline-block; width: 15px; height: 15px;
                       background-color: green; border-radius: 50%; margin-right: 5px;"></span>
                Operational
            </p>

            <p style="margin: 5px 0;">
                <span style="display: inline-block; width: 15px; height: 15px;
                       background-color: yellow; border-radius: 50%; margin-right: 5px;"></span>
                Under Construction
            </p>

            <p style="margin: 5px 0;">
                <span style="display: inline-block; width: 15px; height: 15px;
                       background-color: blue; border-radius: 50%; margin-right: 5px;"></span>
                Planned
            </p>

            <p style="margin: 5px 0;">
                <span style="display: inline-block; width: 15px; height: 15px;
                       background-color: gray; border-radius: 50%; margin-right: 5px;"></span>
                Proposed
            </p>

            <hr>

            <p style="margin: 5px 0; font-size: 10px;">
                <em>Marker size = MW capacity</em>
            </p>
        </div>
        """

        self.map.get_root().html.add_child(folium.Element(legend_html))
