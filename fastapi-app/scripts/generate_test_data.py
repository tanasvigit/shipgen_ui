#!/usr/bin/env python3
"""
Comprehensive test data generator for TechLiv API.
Generates test data for all endpoints and validates database mapping.
"""

import sys
import uuid
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path to import app modules
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.core.security import get_password_hash
from app.models.user import User
from app.models.company import Company
from app.models.company_user import CompanyUser
from app.models.role import Role
from app.models.permission import Permission
from app.models.policy import Policy
from app.models.order import Order
from app.models.driver import Driver
from app.models.vehicle import Vehicle
from app.models.contact import Contact
from app.models.vendor import Vendor
from app.models.place import Place
from app.models.service_rate import ServiceRate
from app.models.service_rate_fee import ServiceRateFee
from app.models.device import Device
# StorefrontCustomer model may not exist, using StorefrontProduct as reference
from app.models.storefront_product import StorefrontProduct
from app.models.storefront_cart import StorefrontCart


class TestDataGenerator:
    """Generate comprehensive test data for all API endpoints."""
    
    def __init__(self, db: Session):
        self.db = db
        self.test_data: Dict[str, Any] = {}
        
    def generate(self):
        """Generate all test data."""
        print("🚀 Starting test data generation...")
        
        # Core IAM
        self._generate_users()
        self._generate_companies()
        self._generate_roles_permissions()
        
        # FleetOps Core
        self._generate_contacts()
        self._generate_vendors()
        self._generate_places()
        self._generate_drivers()
        self._generate_vehicles()
        self._generate_orders()
        
        # Service Rates & Quotes
        self._generate_service_rates()
        
        # Devices & Telematics
        self._generate_devices()
        
        # Storefront
        self._generate_storefront_customers()
        self._generate_storefront_products()
        self._generate_storefront_carts()
        
        self.db.commit()
        print("✅ Test data generation complete!")
        
        return self.test_data
    
    def _generate_users(self):
        """Generate test users."""
        print("  📝 Generating users...")
        
        # Get or create company first
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        users_data = [
            {
                "name": "Test Manager",
                "email": "manager@test.techliv.net",
                "phone": "+1234567890",
                "password": "Test123",
                "type": "manager",
                "status": "active"
            },
            {
                "name": "Test Dispatcher",
                "email": "dispatcher@test.techliv.net",
                "phone": "+1234567891",
                "password": "Test123",
                "type": "dispatcher",
                "status": "active"
            },
            {
                "name": "Test Driver",
                "email": "driver@test.techliv.net",
                "phone": "+1234567892",
                "password": "Test123",
                "type": "driver",
                "status": "active"
            }
        ]
        
        created_users = []
        for user_data in users_data:
            existing = self.db.query(User).filter(User.email == user_data["email"]).first()
            if existing:
                created_users.append(existing)
                continue
                
            user = User(
                uuid=str(uuid.uuid4()),
                public_id=f"user_{uuid.uuid4().hex[:12]}",
                name=user_data["name"],
                email=user_data["email"],
                phone=user_data["phone"],
                password=get_password_hash(user_data["password"]),
                company_uuid=company.uuid,
                timezone="UTC",
                country="US",
                type=user_data["type"],
                status=user_data["status"],
                email_verified_at=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(user)
            self.db.flush()
            
            # Create company_user relationship
            company_user = CompanyUser(
                uuid=str(uuid.uuid4()),
                company_uuid=company.uuid,
                user_uuid=user.uuid,
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(company_user)
            created_users.append(user)
        
        self.test_data["users"] = [
            {
                "uuid": u.uuid,
                "email": u.email,
                "password": "Test123!",
                "name": u.name
            }
            for u in created_users
        ]
        
    def _create_test_company(self) -> Company:
        """Create a test company."""
        company = Company(
            uuid=str(uuid.uuid4()),
            public_id=f"comp_{uuid.uuid4().hex[:12]}",
            name="Test Company",
            description="Test company for API testing",
            phone="+1234567890",
            timezone="UTC",
            country="US",
            currency="USD",
            status="active",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(company)
        self.db.flush()
        return company
    
    def _generate_companies(self):
        """Generate test companies."""
        print("  🏢 Generating companies...")
        
        companies_data = [
            {
                "name": "Acme Logistics",
                "description": "Logistics company for testing",
                "phone": "+1987654321",
                "currency": "USD",
                "country": "US",
                "timezone": "America/New_York"
            },
            {
                "name": "Global Shipping Co",
                "description": "International shipping company",
                "phone": "+1987654322",
                "currency": "EUR",
                "country": "DE",
                "timezone": "Europe/Berlin"
            }
        ]
        
        created_companies = []
        for comp_data in companies_data:
            existing = self.db.query(Company).filter(Company.name == comp_data["name"]).first()
            if existing:
                created_companies.append(existing)
                continue
                
            company = Company(
                uuid=str(uuid.uuid4()),
                public_id=f"comp_{uuid.uuid4().hex[:12]}",
                name=comp_data["name"],
                description=comp_data["description"],
                phone=comp_data["phone"],
                timezone=comp_data["timezone"],
                country=comp_data["country"],
                currency=comp_data["currency"],
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(company)
            created_companies.append(company)
        
        self.test_data["companies"] = [
            {
                "uuid": c.uuid,
                "name": c.name,
                "public_id": c.public_id
            }
            for c in created_companies
        ]
    
    def _generate_roles_permissions(self):
        """Generate test roles and permissions."""
        print("  🔐 Generating roles and permissions...")
        
        # Create roles
        roles_data = [
            {"name": "fleet-manager", "guard_name": "web"},
            {"name": "dispatcher", "guard_name": "web"},
            {"name": "driver", "guard_name": "web"},
        ]
        
        created_roles = []
        for role_data in roles_data:
            existing = self.db.query(Role).filter(
                Role.name == role_data["name"],
                Role.guard_name == role_data["guard_name"]
            ).first()
            if existing:
                created_roles.append(existing)
                continue
                
            role = Role(
                id=str(uuid.uuid4()),
                name=role_data["name"],
                guard_name=role_data["guard_name"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(role)
            created_roles.append(role)
        
        # Create permissions
        permissions_data = [
            {"name": "orders.create", "guard_name": "web"},
            {"name": "orders.view", "guard_name": "web"},
            {"name": "orders.update", "guard_name": "web"},
            {"name": "drivers.manage", "guard_name": "web"},
            {"name": "vehicles.manage", "guard_name": "web"},
        ]
        
        created_permissions = []
        for perm_data in permissions_data:
            existing = self.db.query(Permission).filter(
                Permission.name == perm_data["name"],
                Permission.guard_name == perm_data["guard_name"]
            ).first()
            if existing:
                created_permissions.append(existing)
                continue
                
            permission = Permission(
                id=str(uuid.uuid4()),
                name=perm_data["name"],
                guard_name=perm_data["guard_name"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(permission)
            created_permissions.append(permission)
        
        self.test_data["roles"] = [{"id": r.id, "name": r.name} for r in created_roles]
        self.test_data["permissions"] = [{"id": p.id, "name": p.name} for p in created_permissions]
    
    def _generate_contacts(self):
        """Generate test contacts."""
        print("  📇 Generating contacts...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        contacts_data = [
            {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1555123456",
                "type": "customer"
            },
            {
                "name": "Jane Smith",
                "email": "jane.smith@example.com",
                "phone": "+1555123457",
                "type": "vendor"
            }
        ]
        
        created_contacts = []
        for contact_data in contacts_data:
            contact = Contact(
                uuid=str(uuid.uuid4()),
                public_id=f"contact_{uuid.uuid4().hex[:12]}",
                company_uuid=company.uuid,
                name=contact_data["name"],
                email=contact_data["email"],
                phone=contact_data["phone"],
                type=contact_data["type"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(contact)
            created_contacts.append(contact)
        
        self.test_data["contacts"] = [
            {
                "uuid": c.uuid,
                "name": c.name,
                "email": c.email
            }
            for c in created_contacts
        ]
    
    def _generate_vendors(self):
        """Generate test vendors."""
        print("  🏪 Generating vendors...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        vendors_data = [
            {
                "name": "Fast Fuel Co",
                "email": "contact@fastfuel.com",
                "phone": "+1555987654"
            },
            {
                "name": "Quick Parts Supply",
                "email": "sales@quickparts.com",
                "phone": "+1555987655"
            }
        ]
        
        created_vendors = []
        for vendor_data in vendors_data:
            vendor = Vendor(
                uuid=str(uuid.uuid4()),
                public_id=f"vendor_{uuid.uuid4().hex[:12]}",
                company_uuid=company.uuid,
                name=vendor_data["name"],
                email=vendor_data["email"],
                phone=vendor_data["phone"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(vendor)
            created_vendors.append(vendor)
        
        self.test_data["vendors"] = [
            {
                "uuid": v.uuid,
                "name": v.name,
                "email": v.email
            }
            for v in created_vendors
        ]
    
    def _generate_places(self):
        """Generate test places."""
        print("  📍 Generating places...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        places_data = [
            {
                "name": "Main Warehouse",
                "street1": "123 Main St",
                "city": "New York",
                "province": "NY",
                "postal_code": "10001",
                "country": "US",
                "latitude": 40.7128,
                "longitude": -74.0060
            },
            {
                "name": "Distribution Center",
                "street1": "456 Oak Ave",
                "city": "Los Angeles",
                "province": "CA",
                "postal_code": "90001",
                "country": "US",
                "latitude": 34.0522,
                "longitude": -118.2437
            }
        ]
        
        created_places = []
        for place_data in places_data:
            place = Place(
                uuid=str(uuid.uuid4()),
                public_id=f"place_{uuid.uuid4().hex[:12]}",
                company_uuid=company.uuid,
                name=place_data["name"],
                street1=place_data["street1"],
                city=place_data["city"],
                province=place_data["province"],
                postal_code=place_data["postal_code"],
                country=place_data["country"],
                latitude=place_data["latitude"],
                longitude=place_data["longitude"],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(place)
            created_places.append(place)
        
        self.test_data["places"] = [
            {
                "uuid": p.uuid,
                "name": p.name,
                "city": p.city
            }
            for p in created_places
        ]
    
    def _generate_drivers(self):
        """Generate test drivers."""
        print("  🚗 Generating drivers...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        drivers_data = [
            {
                "name": "Mike Johnson",
                "phone": "+1555111111",
                "email": "mike.johnson@test.com",
                "license_number": "DL123456"
            },
            {
                "name": "Sarah Williams",
                "phone": "+1555222222",
                "email": "sarah.williams@test.com",
                "license_number": "DL789012"
            }
        ]
        
        created_drivers = []
        for driver_data in drivers_data:
            # Create or get user for driver
            user = self.db.query(User).filter(User.email == driver_data["email"]).first()
            if not user:
                user = User(
                    uuid=str(uuid.uuid4()),
                    public_id=f"user_{uuid.uuid4().hex[:12]}",
                    name=driver_data["name"],
                    email=driver_data["email"],
                    phone=driver_data["phone"],
                    password=get_password_hash("Test123"),
                    company_uuid=company.uuid,
                    timezone="UTC",
                    country="US",
                    type="driver",
                    status="active",
                    email_verified_at=datetime.now(timezone.utc),
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                )
                self.db.add(user)
                self.db.flush()
            
            # Create driver record
            driver = Driver(
                uuid=str(uuid.uuid4()),
                public_id=f"driver_{uuid.uuid4().hex[:12]}",
                company_uuid=company.uuid,
                user_uuid=user.uuid,
                drivers_license_number=driver_data["license_number"],
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(driver)
            created_drivers.append(driver)
        
        self.test_data["drivers"] = [
            {
                "uuid": d.uuid,
                "user_uuid": d.user_uuid,
                "license_number": d.drivers_license_number
            }
            for d in created_drivers
        ]
    
    def _generate_vehicles(self):
        """Generate test vehicles."""
        print("  🚚 Generating vehicles...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        driver = self.db.query(Driver).first()
        
        vehicles_data = [
            {
                "vin": "1HGBH41JXMN109186",
                "year": "2020",
                "make": "Ford",
                "model": "Transit",
                "plate_number": "ABC-1234",
                "type": "van"
            },
            {
                "vin": "1FTFW1ET5DFC12345",
                "year": "2021",
                "make": "Ford",
                "model": "F-150",
                "plate_number": "XYZ-5678",
                "type": "truck"
            }
        ]
        
        created_vehicles = []
        for vehicle_data in vehicles_data:
            vehicle = Vehicle(
                uuid=str(uuid.uuid4()),
                public_id=f"vehicle_{uuid.uuid4().hex[:12]}",
                company_uuid=company.uuid,
                vin=vehicle_data["vin"],
                year=vehicle_data["year"],
                make=vehicle_data["make"],
                model=vehicle_data["model"],
                plate_number=vehicle_data["plate_number"],
                type=vehicle_data["type"],
                status="active",
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(vehicle)
            created_vehicles.append(vehicle)
        
        self.test_data["vehicles"] = [
            {
                "uuid": v.uuid,
                "make": v.make,
                "model": v.model,
                "plate_number": v.plate_number
            }
            for v in created_vehicles
        ]
    
    def _generate_orders(self):
        """Generate test orders."""
        print("  📦 Generating orders...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        driver = self.db.query(Driver).first()
        place = self.db.query(Place).first()
        
        orders_data = [
            {
                "internal_id": "ORD-001",
                "type": "delivery",
                "status": "pending"
            },
            {
                "internal_id": "ORD-002",
                "type": "pickup",
                "status": "assigned"
            }
        ]
        
        created_orders = []
        for order_data in orders_data:
            order = Order(
                uuid=str(uuid.uuid4()),
                public_id=f"order_{uuid.uuid4().hex[:12]}",
                company_uuid=company.uuid,
                internal_id=order_data["internal_id"],
                type=order_data["type"],
                status=order_data["status"],
                driver_assigned_uuid=driver.uuid if driver else None,
                dispatched=False,
                started=False,
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(order)
            created_orders.append(order)
        
        self.test_data["orders"] = [
            {
                "uuid": o.uuid,
                "internal_id": o.internal_id,
                "status": o.status
            }
            for o in created_orders
        ]
    
    def _generate_service_rates(self):
        """Generate test service rates."""
        print("  💰 Generating service rates...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        service_rate = ServiceRate(
            uuid=str(uuid.uuid4()),
            public_id=f"rate_{uuid.uuid4().hex[:12]}",
            company_uuid=company.uuid,
            service_name="Standard Delivery",
            service_type="delivery",
            base_fee=500,  # $5.00 in cents
            per_meter_flat_rate_fee=10,  # $0.10 per meter
            per_meter_unit="m",
            rate_calculation_method="per_meter",
            currency="USD",
            has_cod_fee=True,
            cod_calculation_method="flat",
            cod_flat_fee=200,  # $2.00
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(service_rate)
        self.db.flush()
        
        # Create rate fee
        rate_fee = ServiceRateFee(
            uuid=str(uuid.uuid4()),
            service_rate_uuid=service_rate.uuid,
            distance=1000,  # 1km
            distance_unit="m",
            fee=1000,  # $10.00
            currency="USD",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(rate_fee)
        
        self.test_data["service_rates"] = [
            {
                "uuid": service_rate.uuid,
                "service_name": service_rate.service_name,
                "base_fee": service_rate.base_fee
            }
        ]
    
    def _generate_devices(self):
        """Generate test devices."""
        print("  📱 Generating devices...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        vehicle = self.db.query(Vehicle).first()
        
        device = Device(
            uuid=str(uuid.uuid4()),
            public_id=f"device_{uuid.uuid4().hex[:12]}",
            company_uuid=company.uuid,
            name="GPS Tracker 1",
            model="GPS-2024",
            manufacturer="ShipGen",
            type="gps_tracker",
            device_id="GPS-001",
            imei="123456789012345",
            status="active",
            online=True,
            # Use polymorphic relationship to attach to vehicle
            attachable_type="App\\Models\\Vehicle" if vehicle else None,
            attachable_uuid=vehicle.uuid if vehicle else None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(device)
        
        self.test_data["devices"] = [
            {
                "uuid": device.uuid,
                "name": device.name,
                "model": device.model,
                "device_id": device.device_id
            }
        ]
    
    def _generate_storefront_customers(self):
        """Generate test storefront customers."""
        print("  🛒 Generating storefront customers...")
        
        # StorefrontCustomer model - using placeholder data
        # Actual model structure may vary
        self.test_data["storefront_customers"] = [
            {
                "name": "Retail Customer",
                "email": "customer@example.com",
                "phone": "+1555999999"
            }
        ]
    
    def _generate_storefront_products(self):
        """Generate test storefront products."""
        print("  🛍️ Generating storefront products...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        product = StorefrontProduct(
            uuid=str(uuid.uuid4()),
            public_id=f"prod_{uuid.uuid4().hex[:12]}",
            company_uuid=company.uuid,
            name="Test Product",
            description="A test product for API testing",
            price=1999,  # $19.99 in cents
            sale_price=1499,  # $14.99 in cents
            is_on_sale=True,
            currency="USD",
            sku="PROD-001",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        self.db.add(product)
        
        self.test_data["storefront_products"] = [
            {
                "uuid": product.uuid,
                "name": product.name,
                "price": product.price
            }
        ]
    
    def _generate_storefront_carts(self):
        """Generate test storefront carts."""
        print("  🛒 Generating storefront carts...")
        
        company = self.db.query(Company).first()
        if not company:
            company = self._create_test_company()
        
        product = self.db.query(StorefrontProduct).first()
        
        if product:
            cart = StorefrontCart(
                uuid=str(uuid.uuid4()),
                public_id=f"cart_{uuid.uuid4().hex[:12]}",
                company_uuid=company.uuid,
                customer_uuid=str(uuid.uuid4()),  # Placeholder customer UUID
                items=[
                    {
                        "product_uuid": product.uuid,
                        "quantity": 2,
                        "price": product.price
                    }
                ],
                created_at=datetime.now(timezone.utc),
                updated_at=datetime.now(timezone.utc),
            )
            self.db.add(cart)
            
            self.test_data["storefront_carts"] = [
                {
                    "uuid": cart.uuid,
                    "customer_uuid": cart.customer_uuid
                }
            ]


def main():
    """Main function to generate test data."""
    db: Session = SessionLocal()
    
    try:
        generator = TestDataGenerator(db)
        test_data = generator.generate()
        
        # Save test data to JSON file
        output_file = Path(__file__).parent.parent / "test_data.json"
        with open(output_file, "w") as f:
            json.dump(test_data, f, indent=2, default=str)
        
        print(f"\n📄 Test data saved to: {output_file}")
        print("\n✅ Test data generation completed successfully!")
        print("\n📊 Generated data summary:")
        for key, value in test_data.items():
            if isinstance(value, list):
                print(f"  - {key}: {len(value)} items")
            else:
                print(f"  - {key}: {value}")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error generating test data: {e}")
        import traceback
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()

