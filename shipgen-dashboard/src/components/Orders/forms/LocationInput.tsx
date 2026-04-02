import React, { Suspense, lazy, useEffect, useMemo, useRef, useState } from 'react';
import { AlertCircle, Loader2, LocateFixed, MapPin, Search } from 'lucide-react';
import { FormField } from '../../common/form';
import { Button } from '../../ui/Button';
const LazyLocationPickerMap = lazy(() => import('./LocationPickerMap'));

type LocationMode = 'search' | 'map' | 'manual';

export interface LocationValue {
  address: string;
  lat: number | null;
  lng: number | null;
}

interface LocationInputProps {
  label: string;
  value: LocationValue;
  error?: string;
  onChange: (next: LocationValue) => void;
  onValidityChange?: (valid: boolean) => void;
}

interface FallbackSuggestion {
  display_name: string;
  lat: string;
  lon: string;
}

interface ReverseGeocodeResponse {
  display_name?: string;
}

interface GooglePrediction {
  description: string;
  place_id: string;
}

const locationModeButton = (active: boolean) =>
  `rounded-md border px-3 py-1.5 text-xs font-medium transition ${
    active ? 'border-blue-600 bg-blue-600 text-white' : 'border-gray-200 bg-white text-gray-700 hover:bg-gray-50'
  }`;

const getGoogleApiKey = () => import.meta.env.VITE_GOOGLE_MAPS_API_KEY;

const loadGoogleMapsPlaces = async (): Promise<boolean> => {
  const win = window as Window & { google?: unknown };
  if (win.google) return true;
  const apiKey = getGoogleApiKey();
  if (!apiKey) return false;
  const existing = document.querySelector<HTMLScriptElement>('script[data-google-maps-places="1"]');
  if (existing) {
    await new Promise<void>((resolve) => {
      if ((window as Window & { google?: unknown }).google) resolve();
      existing.addEventListener('load', () => resolve(), { once: true });
      existing.addEventListener('error', () => resolve(), { once: true });
    });
    return Boolean((window as Window & { google?: unknown }).google);
  }

  await new Promise<void>((resolve) => {
    const script = document.createElement('script');
    script.src = `https://maps.googleapis.com/maps/api/js?key=${encodeURIComponent(apiKey)}&libraries=places`;
    script.async = true;
    script.defer = true;
    script.dataset.googleMapsPlaces = '1';
    script.onload = () => resolve();
    script.onerror = () => resolve();
    document.head.appendChild(script);
  });
  return Boolean((window as Window & { google?: unknown }).google);
};

const staticPreviewUrl = (lat: number, lng: number) =>
  `https://www.openstreetmap.org/export/embed.html?bbox=${lng - 0.01}%2C${lat - 0.01}%2C${lng + 0.01}%2C${lat + 0.01}&layer=mapnik&marker=${lat}%2C${lng}`;

const LocationInput: React.FC<LocationInputProps> = ({ label, value, error, onChange, onValidityChange }) => {
  const [mode, setMode] = useState<LocationMode>('search');
  const [query, setQuery] = useState(value.address || '');
  const [googleReady, setGoogleReady] = useState(false);
  const [suggestions, setSuggestions] = useState<GooglePrediction[]>([]);
  const [fallbackSuggestions, setFallbackSuggestions] = useState<FallbackSuggestion[]>([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [lookupLoading, setLookupLoading] = useState(false);
  const [lookupError, setLookupError] = useState<string | null>(null);
  const [manualAddressLine, setManualAddressLine] = useState('');
  const [manualCity, setManualCity] = useState('');
  const [manualState, setManualState] = useState('');
  const [manualPincode, setManualPincode] = useState('');
  const searchToken = useRef(0);

  useEffect(() => {
    if (value.address && !query) setQuery(value.address);
  }, [value.address, query]);

  useEffect(() => {
    if (!onValidityChange) return;
    const valid = Boolean(value.address && value.lat != null && value.lng != null);
    onValidityChange(valid);
  }, [onValidityChange, value.address, value.lat, value.lng]);

  useEffect(() => {
    let mounted = true;
    void (async () => {
      const ok = await loadGoogleMapsPlaces();
      if (mounted) setGoogleReady(ok);
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const manualAddress = useMemo(
    () => [manualAddressLine, manualCity, manualState, manualPincode].map((x) => x.trim()).filter(Boolean).join(', '),
    [manualAddressLine, manualCity, manualState, manualPincode]
  );

  useEffect(() => {
    if (mode !== 'search') return;
    const q = query.trim();
    if (q.length < 3) {
      setSuggestions([]);
      setFallbackSuggestions([]);
      return;
    }

    const id = window.setTimeout(async () => {
      const runId = ++searchToken.current;
      setSearchLoading(true);
      try {
        if (googleReady) {
          const googleObj = (window as Window & { google?: any }).google;
          if (googleObj?.maps?.places?.AutocompleteService) {
            const service = new googleObj.maps.places.AutocompleteService();
            const result = await service.getPlacePredictions({
              input: q,
              componentRestrictions: { country: ['in'] },
            });
            if (searchToken.current !== runId) return;
            setSuggestions((result?.predictions ?? []).map((p: any) => ({ description: p.description, place_id: p.place_id })));
            setFallbackSuggestions([]);
            return;
          }
        }

        const ctrl = new AbortController();
        const res = await fetch(
          `https://nominatim.openstreetmap.org/search?format=jsonv2&limit=5&q=${encodeURIComponent(q)}`,
          { signal: ctrl.signal }
        );
        const data = (await res.json()) as FallbackSuggestion[];
        if (searchToken.current !== runId) return;
        setFallbackSuggestions(data || []);
        setSuggestions([]);
      } catch {
        if (searchToken.current !== runId) return;
        setSuggestions([]);
        setFallbackSuggestions([]);
      } finally {
        if (searchToken.current === runId) setSearchLoading(false);
      }
    }, 400);

    return () => {
      window.clearTimeout(id);
    };
  }, [mode, query, googleReady]);

  const reverseGeocode = async (lat: number, lng: number) => {
    setLookupError(null);
    setLookupLoading(true);
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/reverse?format=jsonv2&lat=${encodeURIComponent(String(lat))}&lon=${encodeURIComponent(String(lng))}`
      );
      const data = (await res.json()) as ReverseGeocodeResponse;
      onChange({ address: data.display_name || value.address || '', lat, lng });
    } catch {
      onChange({ address: value.address || '', lat, lng });
      setLookupError('Could not resolve address for this coordinate. Please try again.');
    } finally {
      setLookupLoading(false);
    }
  };

  const geocodeManualAddress = async () => {
    if (!manualAddress) return;
    setLookupError(null);
    setLookupLoading(true);
    try {
      if (googleReady) {
        const googleObj = (window as Window & { google?: any }).google;
        const geocoder = googleObj?.maps?.Geocoder ? new googleObj.maps.Geocoder() : null;
        if (geocoder) {
          const resp = await geocoder.geocode({ address: manualAddress });
          const first = resp?.results?.[0];
          const loc = first?.geometry?.location;
          if (first && loc) {
            onChange({ address: first.formatted_address || manualAddress, lat: Number(loc.lat()), lng: Number(loc.lng()) });
            return;
          }
        }
      }
      const res = await fetch(`https://nominatim.openstreetmap.org/search?format=jsonv2&limit=1&q=${encodeURIComponent(manualAddress)}`);
      const data = (await res.json()) as FallbackSuggestion[];
      if (data[0]?.lat && data[0]?.lon) {
        onChange({
          address: manualAddress,
          lat: Number(data[0].lat),
          lng: Number(data[0].lon),
        });
      } else {
        onChange({ address: manualAddress, lat: null, lng: null });
        setLookupError('Unable to fetch coordinates for this manual address.');
      }
    } catch {
      onChange({ address: manualAddress, lat: null, lng: null });
      setLookupError('Failed to geocode manual address. Please refine the address and retry.');
    } finally {
      setLookupLoading(false);
    }
  };

  const selectGooglePrediction = async (prediction: GooglePrediction) => {
    setLookupError(null);
    setLookupLoading(true);
    try {
      const googleObj = (window as Window & { google?: any }).google;
      const service = googleObj?.maps?.places?.PlacesService
        ? new googleObj.maps.places.PlacesService(document.createElement('div'))
        : null;
      if (!service) throw new Error('PlacesService unavailable');
      const detail = await new Promise<any>((resolve, reject) => {
        service.getDetails(
          { placeId: prediction.place_id, fields: ['formatted_address', 'geometry.location'] },
          (place: any, status: string) => {
            if (status === googleObj.maps.places.PlacesServiceStatus.OK) resolve(place);
            else reject(new Error(status));
          }
        );
      });
      const lat = Number(detail.geometry.location.lat());
      const lng = Number(detail.geometry.location.lng());
      onChange({ address: detail.formatted_address || prediction.description, lat, lng });
      setQuery(detail.formatted_address || prediction.description);
      setSuggestions([]);
    } catch {
      setLookupError('Failed to fetch place details. Please try another suggestion.');
    } finally {
      setLookupLoading(false);
    }
  };

  return (
    <div className="space-y-3 rounded-lg border border-gray-200 bg-white p-4 md:col-span-2">
      <div className="flex items-center justify-between">
        <p className="text-sm font-semibold text-gray-900">{label}</p>
        {lookupLoading ? (
          <span className="inline-flex items-center gap-1 text-xs text-gray-500">
            <Loader2 size={12} className="animate-spin" />
            Fetching coordinates...
          </span>
        ) : null}
      </div>

      <div className="flex flex-wrap gap-2">
        <button type="button" className={locationModeButton(mode === 'search')} onClick={() => setMode('search')}>
          Search Address
        </button>
        <button type="button" className={locationModeButton(mode === 'map')} onClick={() => setMode('map')}>
          Select on Map
        </button>
        <button type="button" className={locationModeButton(mode === 'manual')} onClick={() => setMode('manual')}>
          Enter Manually
        </button>
      </div>

      {mode === 'search' ? (
        <div className="space-y-2">
          <div className="relative">
            <Search size={14} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
            <input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder={`Search ${label.toLowerCase()} address`}
              className="h-10 w-full rounded-md border border-gray-200 bg-white pl-9 pr-3 text-sm text-gray-900"
            />
          </div>
          {!googleReady ? (
            <p className="text-xs text-amber-700">
              Google Places key not configured. Using fallback suggestions (replaceable with Google later).
            </p>
          ) : null}
          {searchLoading ? <p className="text-xs text-gray-500">Loading suggestions...</p> : null}
          {!searchLoading && suggestions.length > 0 ? (
            <div className="max-h-40 overflow-y-auto rounded-md border border-gray-200">
              {suggestions.map((s) => (
                <button
                  type="button"
                  key={s.place_id}
                  className="block w-full border-b border-gray-100 px-3 py-2 text-left text-xs text-gray-700 hover:bg-gray-50 last:border-b-0"
                  onClick={() => void selectGooglePrediction(s)}
                >
                  {s.description}
                </button>
              ))}
            </div>
          ) : null}
          {!searchLoading && fallbackSuggestions.length > 0 ? (
            <div className="max-h-40 overflow-y-auto rounded-md border border-gray-200">
              {fallbackSuggestions.map((s) => (
                <button
                  type="button"
                  key={`${s.display_name}-${s.lat}-${s.lon}`}
                  className="block w-full border-b border-gray-100 px-3 py-2 text-left text-xs text-gray-700 hover:bg-gray-50 last:border-b-0"
                  onClick={() => {
                    onChange({ address: s.display_name, lat: Number(s.lat), lng: Number(s.lon) });
                    setQuery(s.display_name);
                    setFallbackSuggestions([]);
                  }}
                >
                  {s.display_name}
                </button>
              ))}
            </div>
          ) : null}
        </div>
      ) : null}

      {mode === 'map' ? (
        <div className="space-y-2">
          <Suspense
            fallback={
              <div className="flex h-[260px] items-center justify-center rounded-lg border border-gray-200 bg-gray-50 text-sm text-gray-500">
                Loading map...
              </div>
            }
          >
            <LazyLocationPickerMap lat={value.lat} lng={value.lng} onSelect={(lat, lng) => void reverseGeocode(lat, lng)} />
          </Suspense>
          <p className="text-xs text-gray-500">Click map to move marker. Drag marker to fine-tune location and auto-update address.</p>
        </div>
      ) : null}

      {mode === 'manual' ? (
        <div className="space-y-3">
          <FormField label="Address line" htmlFor={`${label}-address-line`}>
            <input
              id={`${label}-address-line`}
              value={manualAddressLine}
              onChange={(e) => setManualAddressLine(e.target.value)}
              className="h-10 w-full rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-900"
            />
          </FormField>
          <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
            <FormField label="City" htmlFor={`${label}-city`}>
              <input
                id={`${label}-city`}
                value={manualCity}
                onChange={(e) => setManualCity(e.target.value)}
                className="h-10 w-full rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-900"
              />
            </FormField>
            <FormField label="State" htmlFor={`${label}-state`}>
              <input
                id={`${label}-state`}
                value={manualState}
                onChange={(e) => setManualState(e.target.value)}
                className="h-10 w-full rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-900"
              />
            </FormField>
            <FormField label="Pincode" htmlFor={`${label}-pincode`}>
              <input
                id={`${label}-pincode`}
                value={manualPincode}
                onChange={(e) => setManualPincode(e.target.value)}
                className="h-10 w-full rounded-md border border-gray-200 bg-white px-3 text-sm text-gray-900"
              />
            </FormField>
          </div>
          <div className="flex flex-wrap gap-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              icon={LocateFixed}
              loading={lookupLoading}
              onClick={() => void geocodeManualAddress()}
              disabled={!manualAddress}
            >
              Use manual address (fetch coordinates)
            </Button>
          </div>
        </div>
      ) : null}

      <div className="rounded-md border border-gray-200 bg-gray-50 p-3">
        <div className="mb-2 flex items-center gap-1 text-xs font-semibold uppercase text-gray-500">
          <MapPin size={12} />
          Selected location
        </div>
        <p className="text-sm text-gray-800">{value.address || 'No address selected yet'}</p>
        <p className="mt-1 text-xs text-gray-500">
          Lat: {typeof value.lat === 'number' ? value.lat.toFixed(6) : '—'} | Lng:{' '}
          {typeof value.lng === 'number' ? value.lng.toFixed(6) : '—'}
        </p>
        {typeof value.lat === 'number' && typeof value.lng === 'number' ? (
          <div className="mt-2">
            <iframe
              title={`${label} preview map`}
              src={staticPreviewUrl(value.lat, value.lng)}
              className="h-[120px] w-full rounded-md border border-gray-200"
              loading="lazy"
            />
          </div>
        ) : null}
      </div>
      {lookupError ? (
        <p className="inline-flex items-center gap-1 text-xs text-amber-700">
          <AlertCircle size={12} />
          {lookupError}
        </p>
      ) : null}
      {error ? <p className="text-xs text-red-600">{error}</p> : null}
    </div>
  );
};

export default LocationInput;
