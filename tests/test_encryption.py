#!/usr/bin/env python3
"""
Test script for the encrypted keylogger encryption/decryption functions
"""

import os
import sys
import tempfile

# Add the current directory to the path to import keylogger functions
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from keylogger import derive_key_from_password, encrypt_message, decrypt_message

def test_encryption_decryption():
    """Test the encryption and decryption functions"""
    print("Testing encryption/decryption functionality...")
    
    # Test data
    test_password = "test_password_123"
    test_salt = os.urandom(16)
    test_message = "2025-08-05T10:30:45.123456Z - Key: 'a'"
    
    try:
        # Derive key
        key = derive_key_from_password(test_password, test_salt)
        print("✓ Key derivation successful")
        
        # Encrypt message
        encrypted = encrypt_message(test_message, key)
        print("✓ Message encryption successful")
        
        # Decrypt message
        decrypted = decrypt_message(encrypted, key)
        print("✓ Message decryption successful")
        
        # Verify integrity
        if decrypted == test_message:
            print("✓ Message integrity verified - original and decrypted messages match")
            print(f"Original:  {test_message}")
            print(f"Decrypted: {decrypted}")
        else:
            print("✗ Message integrity failed - messages don't match")
            return False
        
        # Test with wrong password
        wrong_key = derive_key_from_password("wrong_password", test_salt)
        try:
            decrypt_message(encrypted, wrong_key)
            print("✗ Security test failed - wrong password should not decrypt")
            return False
        except:
            print("✓ Security test passed - wrong password cannot decrypt")
        
        print("\n🎉 All tests passed! Encryption system is working correctly.")
        return True
        
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        return False

if __name__ == "__main__":
    test_encryption_decryption()
