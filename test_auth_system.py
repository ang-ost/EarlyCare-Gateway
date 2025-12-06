#!/usr/bin/env python3
"""
Quick test for authentication system
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from src.models.doctor import Doctor

def test_doctor_model():
    """Test Doctor model functionality"""
    print("Testing Doctor model...")
    
    # Test ID generation
    doctor_id_1 = Doctor.generate_doctor_id("Marco", "Rossi")
    print(f"✓ Generated ID 1: {doctor_id_1}")
    
    doctor_id_2 = Doctor.generate_doctor_id("Marco", "Rossi")
    print(f"✓ Generated ID 2: {doctor_id_2}")
    
    assert doctor_id_1 != doctor_id_2, "Generated IDs should be unique"
    print("✓ IDs are unique")
    
    # Test password hashing
    password = "password123"
    hashed = Doctor.hash_password(password)
    print(f"✓ Hashed password: {hashed[:20]}...")
    
    # Test password verification
    assert Doctor.verify_password(password, hashed), "Password verification failed"
    print("✓ Password verification works")
    
    assert not Doctor.verify_password("wrong_password", hashed), "Wrong password should not verify"
    print("✓ Wrong password correctly rejected")
    
    # Test Doctor creation
    doctor = Doctor(
        doctor_id="M_ROSSI_abc123",
        nome="Marco",
        cognome="Rossi",
        specializzazione="Cardiologia",
        ospedale_affiliato="Ospedale Centrale",
        password_hash=hashed
    )
    print(f"✓ Created Doctor: {doctor.nome} {doctor.cognome}")
    
    # Test serialization
    doctor_dict = doctor.to_dict()
    print(f"✓ Serialized to dict with keys: {list(doctor_dict.keys())}")
    
    # Test deserialization
    doctor_restored = Doctor.from_dict(doctor_dict)
    assert doctor_restored.doctor_id == doctor.doctor_id, "Deserialization failed"
    print(f"✓ Deserialized Doctor: {doctor_restored.nome} {doctor_restored.cognome}")
    
    print("\n✅ All Doctor model tests passed!")

if __name__ == "__main__":
    try:
        test_doctor_model()
        print("\n✅ Authentication system is ready!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
