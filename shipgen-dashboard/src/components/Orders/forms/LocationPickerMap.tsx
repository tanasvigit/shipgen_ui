import React, { useEffect } from 'react';
import { MapContainer, Marker, TileLayer, useMap, useMapEvents } from 'react-leaflet';
import L from 'leaflet';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';

const marker = L.icon({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const DEFAULT_CENTER: [number, number] = [20.5937, 78.9629];
const ZOOM_DEFAULT = 12;
const ZOOM_SELECTED = 16;

const RecenterMap: React.FC<{ center: [number, number]; hasSelection: boolean }> = ({ center, hasSelection }) => {
  const map = useMap();
  useEffect(() => {
    map.setView(center, hasSelection ? ZOOM_SELECTED : ZOOM_DEFAULT, { animate: true });
  }, [map, center, hasSelection]);
  return null;
};

const ClickHandler: React.FC<{ onSelect: (lat: number, lng: number) => void }> = ({ onSelect }) => {
  useMapEvents({
    click(e) {
      onSelect(e.latlng.lat, e.latlng.lng);
    },
  });
  return null;
};

interface LocationPickerMapProps {
  lat: number | null;
  lng: number | null;
  onSelect: (lat: number, lng: number) => void;
}

const LocationPickerMap: React.FC<LocationPickerMapProps> = ({ lat, lng, onSelect }) => {
  const hasSelection = typeof lat === 'number' && typeof lng === 'number';
  const center: [number, number] = hasSelection ? [lat, lng] : DEFAULT_CENTER;

  return (
    <MapContainer center={center} zoom={hasSelection ? ZOOM_SELECTED : ZOOM_DEFAULT} style={{ height: 260, width: '100%' }} className="rounded-lg border border-gray-200">
      <TileLayer attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
      <RecenterMap center={center} hasSelection={hasSelection} />
      <ClickHandler onSelect={onSelect} />
      {hasSelection ? (
        <Marker
          position={[lat, lng]}
          icon={marker}
          draggable
          eventHandlers={{
            dragend: (event) => {
              const point = event.target.getLatLng();
              onSelect(point.lat, point.lng);
            },
          }}
        />
      ) : null}
    </MapContainer>
  );
};

export default LocationPickerMap;
