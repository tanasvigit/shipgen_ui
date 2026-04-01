#!/usr/bin/env python3
"""
Export actual test data from database to JSON file.
This script queries the database and exports all test data with actual UUIDs.
"""

import sys
import json
import uuid
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.user import User
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.role import Role
from app.models.permission import Permission
from app.models.contact import Contact
from app.models.vendor import Vendor
from app.models.place import Place
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.order import Order
from app.models.service_rate import ServiceRate
from app.models.service_rate_fee import ServiceRateFee
from app.models.device import Device
from app.models.storefront_product import StorefrontProduct
from app.models.storefront_cart import StorefrontCart


def export_test_data():
    """Export all test data from database."""
    db: Session = SessionLocal()
    
    try:
        export_data = {}
        
        print("📊 Exporting test data from database...")
        
        # Export Users
        print("  📝 Exporting users...")
        users = db.query(User).filter(
            User.deleted_at.is_(None),
            (User.email.like("%test%")) | (User.email.like("%techliv.net%"))
        ).all()
        export_data["users"] = [
            {
                "uuid": u.uuid,
                "public_id": u.public_id,
                "name": u.name,
                "email": u.email,
                "phone": u.phone,
                "type": u.type,
                "status": u.status,
                "company_uuid": u.company_uuid
            }
            for u in users
        ]
        
        # Export Companies
        print("  🏢 Exporting companies...")
        companies = db.query(Company).filter(
            Company.deleted_at.is_(None)
        ).all()
        export_data["companies"] = [
            {
                "uuid": c.uuid,
                "public_id": c.public_id,
                "name": c.name,
                "description": c.description,
                "phone": c.phone,
                "currency": c.currency,
                "country": c.country,
                "timezone": c.timezone,
                "status": c.status
            }
            for c in companies
        ]
        
        # Export Roles
        print("  🔐 Exporting roles...")
        roles = db.query(Role).all()
        export_data["roles"] = [
            {
                "id": r.id,
                "name": r.name,
                "guard_name": r.guard_name
            }
            for r in roles
        ]
        
        # Export Permissions
        print("  🔐 Exporting permissions...")
        permissions = db.query(Permission).all()
        export_data["permissions"] = [
            {
                "id": p.id,
                "name": p.name,
                "guard_name": p.guard_name
            }
            for p in permissions
        ]
        
        # Export Contacts
        print("  📇 Exporting contacts...")
        contacts = db.query(Contact).filter(Contact.deleted_at.is_(None)).all()
        export_data["contacts"] = [
            {
                "uuid": c.uuid,
                "public_id": c.public_id,
                "name": c.name,
                "email": c.email,
                "phone": c.phone,
                "type": c.type,
                "company_uuid": c.company_uuid
            }
            for c in contacts
        ]
        
        # Export Vendors
        print("  🏪 Exporting vendors...")
        vendors = db.query(Vendor).filter(Vendor.deleted_at.is_(None)).all()
        export_data["vendors"] = [
            {
                "uuid": v.uuid,
                "public_id": v.public_id,
                "name": v.name,
                "email": v.email,
                "phone": v.phone,
                "company_uuid": v.company_uuid
            }
            for v in vendors
        ]
        
        # Export Places
        print("  📍 Exporting places...")
        places = db.query(Place).filter(Place.deleted_at.is_(None)).all()
        export_data["places"] = [
            {
                "uuid": p.uuid,
                "public_id": p.public_id,
                "name": p.name,
                "street1": p.street1,
                "city": p.city,
                "province": p.province,
                "postal_code": p.postal_code,
                "country": p.country,
                "latitude": float(p.latitude) if p.latitude else None,
                "longitude": float(p.longitude) if p.longitude else None,
                "company_uuid": p.company_uuid
            }
            for p in places
        ]
        
        # Export Drivers
        print("  🚗 Exporting drivers...")
        drivers = db.query(Driver).filter(Driver.deleted_at.is_(None)).all()
        export_data["drivers"] = []
        for d in drivers:
            # Get associated user
            user = db.query(User).filter(User.uuid == d.user_uuid).first() if d.user_uuid else None
            export_data["drivers"].append({
                "uuid": d.uuid,
                "public_id": d.public_id,
                "user_uuid": d.user_uuid,
                "user_name": user.name if user else None,
                "user_email": user.email if user else None,
                "user_phone": user.phone if user else None,
                "drivers_license_number": d.drivers_license_number,
                "status": d.status,
                "company_uuid": d.company_uuid
            })
        
        # Export Vehicles
        print("  🚚 Exporting vehicles...")
        vehicles = db.query(Vehicle).filter(Vehicle.deleted_at.is_(None)).all()
        export_data["vehicles"] = [
            {
                "uuid": v.uuid,
                "public_id": v.public_id,
                "make": v.make,
                "model": v.model,
                "year": v.year,
                "vin": v.vin,
                "plate_number": v.plate_number,
                "type": v.type,
                "status": v.status,
                "company_uuid": v.company_uuid
            }
            for v in vehicles
        ]
        
        # Export Orders
        print("  📦 Exporting orders...")
        orders = db.query(Order).filter(Order.deleted_at.is_(None)).all()
        export_data["orders"] = [
            {
                "uuid": o.uuid,
                "public_id": o.public_id,
                "internal_id": o.internal_id,
                "type": o.type,
                "status": o.status,
                "dispatched": o.dispatched,
                "started": o.started,
                "driver_assigned_uuid": o.driver_assigned_uuid,
                "company_uuid": o.company_uuid
            }
            for o in orders
        ]
        
        # Export Service Rates
        print("  💰 Exporting service rates...")
        service_rates = db.query(ServiceRate).filter(ServiceRate.deleted_at.is_(None)).all()
        export_data["service_rates"] = []
        for sr in service_rates:
            # Get associated rate fees
            rate_fees = db.query(ServiceRateFee).filter(
                ServiceRateFee.service_rate_uuid == sr.uuid,
                ServiceRateFee.deleted_at.is_(None)
            ).all()
            export_data["service_rates"].append({
                "uuid": sr.uuid,
                "public_id": sr.public_id,
                "service_name": sr.service_name,
                "service_type": sr.service_type,
                "base_fee": sr.base_fee,
                "per_meter_flat_rate_fee": sr.per_meter_flat_rate_fee,
                "per_meter_unit": sr.per_meter_unit,
                "rate_calculation_method": sr.rate_calculation_method,
                "currency": sr.currency,
                "has_cod_fee": sr.has_cod_fee,
                "cod_flat_fee": sr.cod_flat_fee,
                "company_uuid": sr.company_uuid,
                "rate_fees": [
                    {
                        "uuid": rf.uuid,
                        "distance": rf.distance,
                        "distance_unit": rf.distance_unit,
                        "fee": rf.fee,
                        "currency": rf.currency
                    }
                    for rf in rate_fees
                ]
            })
        
        # Export Devices
        print("  📱 Exporting devices...")
        devices = db.query(Device).filter(Device.deleted_at.is_(None)).all()
        export_data["devices"] = [
            {
                "uuid": d.uuid,
                "public_id": d.public_id,
                "name": d.name,
                "model": d.model,
                "manufacturer": d.manufacturer,
                "type": d.type,
                "device_id": d.device_id,
                "imei": d.imei,
                "status": d.status,
                "online": d.online,
                "attachable_type": d.attachable_type,
                "attachable_uuid": d.attachable_uuid,
                "company_uuid": d.company_uuid
            }
            for d in devices
        ]
        
        # Export Storefront Products
        print("  🛍️ Exporting storefront products...")
        products = db.query(StorefrontProduct).filter(StorefrontProduct.deleted_at.is_(None)).all()
        export_data["storefront_products"] = [
            {
                "uuid": p.uuid,
                "public_id": p.public_id,
                "name": p.name,
                "description": p.description,
                "price": p.price,
                "sale_price": p.sale_price,
                "is_on_sale": p.is_on_sale,
                "currency": p.currency,
                "sku": p.sku,
                "company_uuid": p.company_uuid
            }
            for p in products
        ]
        
        # Export Storefront Carts
        print("  🛒 Exporting storefront carts...")
        carts = db.query(StorefrontCart).filter(StorefrontCart.deleted_at.is_(None)).all()
        export_data["storefront_carts"] = [
            {
                "uuid": c.uuid,
                "public_id": c.public_id,
                "customer_uuid": c.customer_uuid,
                "items": c.items,
                "company_uuid": c.company_uuid
            }
            for c in carts
        ]
        
        # Save to JSON file
        output_file = Path(__file__).parent.parent / "test_data_export.json"
        with open(output_file, "w") as f:
            json.dump(export_data, f, indent=2, default=str)
        
        print(f"\n✅ Test data exported to: {output_file}")
        print("\n📊 Export Summary:")
        print(f"  - Users: {len(export_data['users'])}")
        print(f"  - Companies: {len(export_data['companies'])}")
        print(f"  - Roles: {len(export_data['roles'])}")
        print(f"  - Permissions: {len(export_data['permissions'])}")
        print(f"  - Contacts: {len(export_data['contacts'])}")
        print(f"  - Vendors: {len(export_data['vendors'])}")
        print(f"  - Places: {len(export_data['places'])}")
        print(f"  - Drivers: {len(export_data['drivers'])}")
        print(f"  - Vehicles: {len(export_data['vehicles'])}")
        print(f"  - Orders: {len(export_data['orders'])}")
        print(f"  - Service Rates: {len(export_data['service_rates'])}")
        print(f"  - Devices: {len(export_data['devices'])}")
        print(f"  - Storefront Products: {len(export_data['storefront_products'])}")
        print(f"  - Storefront Carts: {len(export_data['storefront_carts'])}")
        
        return export_data
        
    except Exception as e:
        print(f"❌ Error exporting test data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    export_test_data()

