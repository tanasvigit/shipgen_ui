import type { MockPlace } from '../mocks/data/places';

export function getPlaceRouteId(place: MockPlace): string {
  if (place.uuid) return place.uuid;
  if (place.id != null) return String(place.id);
  return '';
}
