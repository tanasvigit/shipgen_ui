import React, { useEffect, useMemo, useState } from 'react';
import PageContainer from '../ui/PageContainer';
import PageHeader from '../ui/PageHeader';
import Card from '../ui/Card';
import { tripsDispatchService, type UiTrip } from '../../services/tripsDispatchService';
import { getApiErrorMessage } from '../../services/apiErrors';

const TripsDispatch: React.FC = () => {
  const [trips, setTrips] = useState<UiTrip[]>([]);
  const [selectedId, setSelectedId] = useState<string>('');
  const [selected, setSelected] = useState<UiTrip | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  const [createForm, setCreateForm] = useState({
    vehicle_id: '',
    driver_id: '',
    start_location: '',
    end_location: '',
    total_capacity: 20,
  });
  const [stopsText, setStopsText] = useState('Annavaram,DROPOFF,1\nPitapuram,PICKUP,2\nKakinada,DROPOFF,3');
  const [assignForm, setAssignForm] = useState({ order_id: '', pickup_location: '', drop_location: '', load_units: 1 });
  const [completeForm, setCompleteForm] = useState({ stop_sequence: 1 });
  const [pickupForm, setPickupForm] = useState({ order_id: '', pickup_location: '', drop_location: '', load_units: 1 });
  const [locationForm, setLocationForm] = useState({ current_lat: 0, current_lng: 0 });

  const loadTrips = async () => {
    try {
      setLoading(true);
      setError(null);
      const rows = await tripsDispatchService.list();
      setTrips(rows);
      if (!selectedId && rows[0]) setSelectedId(String(rows[0].id));
    } catch (e) {
      setError(getApiErrorMessage(e, 'Failed to load trips'));
    } finally {
      setLoading(false);
    }
  };

  const loadSelected = async (id: string) => {
    if (!id) return;
    try {
      const row = await tripsDispatchService.getById(id);
      setSelected(row);
    } catch (e) {
      setError(getApiErrorMessage(e, 'Failed to load trip details'));
    }
  };

  useEffect(() => {
    void loadTrips();
  }, []);

  useEffect(() => {
    if (selectedId) void loadSelected(selectedId);
  }, [selectedId]);

  const tripOptions = useMemo(
    () =>
      trips.map((t) => ({
        value: String(t.id),
        label: `${t.public_id || t.uuid || t.id} (${t.driver_name || t.driver_id} / ${t.vehicle_plate_number || t.vehicle_id})`,
      })),
    [trips]
  );

  const parseStops = () =>
    stopsText
      .split('\n')
      .map((line) => line.trim())
      .filter(Boolean)
      .map((line) => {
        const [location_name, type, sequence] = line.split(',').map((x) => x.trim());
        return { location_name, type: (type || 'DROPOFF') as 'PICKUP' | 'DROPOFF', sequence: Number(sequence || 1) };
      });

  const onCreate = async () => {
    try {
      setBusy(true);
      const row = await tripsDispatchService.create({
        ...createForm,
        total_capacity: Number(createForm.total_capacity),
        stops: parseStops(),
      });
      await loadTrips();
      setSelectedId(String(row.id));
    } catch (e) {
      setError(getApiErrorMessage(e, 'Failed to create trip'));
    } finally {
      setBusy(false);
    }
  };

  const withSelected = async (run: (id: string) => Promise<void>) => {
    if (!selectedId) return;
    try {
      setBusy(true);
      await run(selectedId);
      await loadTrips();
      await loadSelected(selectedId);
    } catch (e) {
      setError(getApiErrorMessage(e, 'Trip action failed'));
    } finally {
      setBusy(false);
    }
  };

  return (
    <PageContainer flushHorizontal className="px-4 sm:px-5 lg:px-8">
      <PageHeader title="Trips & Dispatch" description="Trip-based dispatch operations with capacity and stop tracking." />

      {error ? <div className="mb-4 rounded-lg border border-red-200 bg-red-50 px-4 py-2 text-sm text-red-700">{error}</div> : null}

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card className="p-4">
          <h3 className="mb-3 font-semibold">Create Trip</h3>
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
            <input className="rounded border px-3 py-2 text-sm" placeholder="Vehicle plate number / UUID / public ID" value={createForm.vehicle_id} onChange={(e) => setCreateForm((p) => ({ ...p, vehicle_id: e.target.value }))} />
            <input className="rounded border px-3 py-2 text-sm" placeholder="Driver name / email / UUID / public ID" value={createForm.driver_id} onChange={(e) => setCreateForm((p) => ({ ...p, driver_id: e.target.value }))} />
            <input className="rounded border px-3 py-2 text-sm" placeholder="Start location" value={createForm.start_location} onChange={(e) => setCreateForm((p) => ({ ...p, start_location: e.target.value }))} />
            <input className="rounded border px-3 py-2 text-sm" placeholder="End location" value={createForm.end_location} onChange={(e) => setCreateForm((p) => ({ ...p, end_location: e.target.value }))} />
            <input className="rounded border px-3 py-2 text-sm" type="number" placeholder="Total capacity" value={createForm.total_capacity} onChange={(e) => setCreateForm((p) => ({ ...p, total_capacity: Number(e.target.value) }))} />
          </div>
          <textarea className="mt-2 h-24 w-full rounded border px-3 py-2 text-xs" value={stopsText} onChange={(e) => setStopsText(e.target.value)} />
          <p className="mt-1 text-xs text-gray-500">Stops format: `Location,TYPE,Sequence` (one per line).</p>
          <button disabled={busy} onClick={() => void onCreate()} className="mt-3 rounded bg-blue-600 px-4 py-2 text-sm text-white hover:bg-blue-700 disabled:opacity-50">Create Trip</button>
        </Card>

        <Card className="p-4">
          <h3 className="mb-3 font-semibold">Trips</h3>
          {loading ? <p className="text-sm text-gray-500">Loading...</p> : null}
          <select className="w-full rounded border px-3 py-2 text-sm" value={selectedId} onChange={(e) => setSelectedId(e.target.value)}>
            <option value="">Select trip</option>
            {tripOptions.map((o) => (
              <option key={o.value} value={o.value}>{o.label}</option>
            ))}
          </select>
          <button className="mt-2 rounded border px-3 py-1.5 text-xs" onClick={() => void loadTrips()}>Refresh List</button>
        </Card>
      </div>

      {selected ? (
        <div className="mt-4 grid grid-cols-1 gap-4 lg:grid-cols-2">
          <Card className="p-4">
            <h3 className="mb-2 font-semibold">Trip Details</h3>
            <div className="space-y-1 text-sm">
              <p><b>ID:</b> {selected.public_id || selected.uuid || selected.id}</p>
              <p><b>Status:</b> {selected.status}</p>
              <p><b>Vehicle:</b> {selected.vehicle_plate_number || selected.vehicle_id}</p>
              <p><b>Driver:</b> {selected.driver_name || selected.driver_id}</p>
              <p><b>Route:</b> {selected.start_location} → {selected.end_location}</p>
              <p><b>Capacity:</b> {selected.current_load}/{selected.total_capacity} (available {selected.available_capacity})</p>
              <p><b>Delivered:</b> {selected.dashboard?.delivered_orders_count || 0} | <b>Pending:</b> {selected.dashboard?.pending_orders_count || 0}</p>
              <p><b>Location:</b> {selected.current_lat ?? '-'}, {selected.current_lng ?? '-'} ({selected.last_location_update || '-'})</p>
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button disabled={busy} onClick={() => void withSelected(async (id) => { await tripsDispatchService.start(id); })} className="rounded bg-green-600 px-3 py-1.5 text-xs text-white disabled:opacity-50">Start Trip</button>
            </div>
          </Card>

          <Card className="p-4">
            <h3 className="mb-2 font-semibold">Live Location Update</h3>
            <div className="grid grid-cols-2 gap-2">
              <input type="number" className="rounded border px-3 py-2 text-sm" placeholder="Lat" value={locationForm.current_lat} onChange={(e) => setLocationForm((p) => ({ ...p, current_lat: Number(e.target.value) }))} />
              <input type="number" className="rounded border px-3 py-2 text-sm" placeholder="Lng" value={locationForm.current_lng} onChange={(e) => setLocationForm((p) => ({ ...p, current_lng: Number(e.target.value) }))} />
            </div>
            <button disabled={busy} onClick={() => void withSelected(async (id) => { await tripsDispatchService.updateLocation(id, locationForm); })} className="mt-2 rounded bg-indigo-600 px-3 py-1.5 text-xs text-white disabled:opacity-50">Update Location</button>
          </Card>

          <Card className="p-4">
            <h3 className="mb-2 font-semibold">Assign Order</h3>
            <div className="grid grid-cols-1 gap-2">
              <input className="rounded border px-3 py-2 text-sm" placeholder="Order UUID/Public ID" value={assignForm.order_id} onChange={(e) => setAssignForm((p) => ({ ...p, order_id: e.target.value }))} />
              <input className="rounded border px-3 py-2 text-sm" placeholder="Pickup location" value={assignForm.pickup_location} onChange={(e) => setAssignForm((p) => ({ ...p, pickup_location: e.target.value }))} />
              <input className="rounded border px-3 py-2 text-sm" placeholder="Drop location" value={assignForm.drop_location} onChange={(e) => setAssignForm((p) => ({ ...p, drop_location: e.target.value }))} />
              <input type="number" className="rounded border px-3 py-2 text-sm" placeholder="Load units" value={assignForm.load_units} onChange={(e) => setAssignForm((p) => ({ ...p, load_units: Number(e.target.value) }))} />
            </div>
            <button disabled={busy} onClick={() => void withSelected(async (id) => { await tripsDispatchService.assignOrder(id, assignForm); })} className="mt-2 rounded bg-blue-600 px-3 py-1.5 text-xs text-white disabled:opacity-50">Assign Order</button>
          </Card>

          <Card className="p-4">
            <h3 className="mb-2 font-semibold">Complete Stop</h3>
            <div className="grid grid-cols-1 gap-2">
              <input type="number" className="rounded border px-3 py-2 text-sm" placeholder="Stop sequence" value={completeForm.stop_sequence} onChange={(e) => setCompleteForm({ stop_sequence: Number(e.target.value) })} />
              <p className="text-xs text-gray-500">Optional new pickup at this stop:</p>
              <input className="rounded border px-3 py-2 text-sm" placeholder="Order UUID/Public ID" value={pickupForm.order_id} onChange={(e) => setPickupForm((p) => ({ ...p, order_id: e.target.value }))} />
              <input className="rounded border px-3 py-2 text-sm" placeholder="Pickup location" value={pickupForm.pickup_location} onChange={(e) => setPickupForm((p) => ({ ...p, pickup_location: e.target.value }))} />
              <input className="rounded border px-3 py-2 text-sm" placeholder="Drop location" value={pickupForm.drop_location} onChange={(e) => setPickupForm((p) => ({ ...p, drop_location: e.target.value }))} />
              <input type="number" className="rounded border px-3 py-2 text-sm" placeholder="Load units" value={pickupForm.load_units} onChange={(e) => setPickupForm((p) => ({ ...p, load_units: Number(e.target.value) }))} />
            </div>
            <button
              disabled={busy}
              onClick={() =>
                void withSelected(async (id) => {
                  const new_pickups =
                    pickupForm.order_id.trim()
                      ? [{ ...pickupForm, load_units: Number(pickupForm.load_units) }]
                      : [];
                  await tripsDispatchService.completeStop(id, { stop_sequence: Number(completeForm.stop_sequence), new_pickups });
                })
              }
              className="mt-2 rounded bg-amber-600 px-3 py-1.5 text-xs text-white disabled:opacity-50"
            >
              Complete Stop
            </button>
          </Card>

          <Card className="p-4 lg:col-span-2">
            <h3 className="mb-2 font-semibold">Stops / Orders / Events</h3>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-3">
              <div>
                <p className="mb-1 text-xs font-semibold uppercase text-gray-500">Stops</p>
                <div className="space-y-1 text-sm">
                  {selected.stops?.map((s) => (
                    <p key={`${s.sequence}-${s.location_name}`}>#{s.sequence} {s.location_name} ({s.type}) {s.is_completed ? '✓' : ''}</p>
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase text-gray-500">Orders</p>
                <div className="space-y-1 text-sm">
                  {selected.orders?.map((o) => (
                    <p key={`${o.order_id}`}>Order {o.order_id}: {o.pickup_location} → {o.drop_location} ({o.status}, load {o.load_units})</p>
                  ))}
                </div>
              </div>
              <div>
                <p className="mb-1 text-xs font-semibold uppercase text-gray-500">Events</p>
                <div className="max-h-48 space-y-1 overflow-auto text-sm">
                  {selected.events?.map((e, i) => (
                    <p key={`${e.event_type}-${e.created_at || i}`}>{e.event_type} - {e.created_at || '-'}</p>
                  ))}
                </div>
              </div>
            </div>
          </Card>
        </div>
      ) : null}
    </PageContainer>
  );
};

export default TripsDispatch;
