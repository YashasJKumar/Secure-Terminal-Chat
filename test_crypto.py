#!/usr/bin/env python3
"""
Simple tests for cryptographic operations.
"""

import sys
import time
from secure_chat.core import CryptoManager


def test_rsa_keypair():
    """Test RSA key pair generation."""
    print("Testing RSA key pair generation...")
    crypto = CryptoManager()
    private_pem, public_pem = crypto.generate_rsa_keypair()
    
    assert len(private_pem) > 0, "Private key should not be empty"
    assert len(public_pem) > 0, "Public key should not be empty"
    assert b'BEGIN PRIVATE KEY' in private_pem, "Private key format incorrect"
    assert b'BEGIN PUBLIC KEY' in public_pem, "Public key format incorrect"
    
    print("✓ RSA key pair generation successful")
    return crypto


def test_signature():
    """Test digital signature."""
    print("Testing digital signature...")
    crypto = test_rsa_keypair()
    
    # Test data
    data = b"Hello, this is a test message!"
    
    # Sign data
    signature = crypto.sign_data(data)
    assert len(signature) > 0, "Signature should not be empty"
    
    # Verify signature
    is_valid = crypto.verify_signature(data, signature, crypto.rsa_public_key)
    assert is_valid, "Signature verification failed"
    
    # Test with wrong data
    wrong_data = b"This is different data"
    is_valid_wrong = crypto.verify_signature(wrong_data, signature, crypto.rsa_public_key)
    assert not is_valid_wrong, "Signature should not verify with wrong data"
    
    print("✓ Digital signature successful")
    return crypto


def test_dh_key_exchange():
    """Test Diffie-Hellman key exchange."""
    print("Testing Diffie-Hellman key exchange...")
    
    # Create two crypto managers (simulating two peers)
    crypto_a = CryptoManager()
    crypto_b = CryptoManager()
    
    # Generate RSA keys for both
    crypto_a.generate_rsa_keypair()
    crypto_b.generate_rsa_keypair()
    
    # Generate DH keys for both
    dh_public_a = crypto_a.generate_dh_keypair()
    dh_public_b = crypto_b.generate_dh_keypair()
    
    assert len(dh_public_a) > 0, "DH public key A should not be empty"
    assert len(dh_public_b) > 0, "DH public key B should not be empty"
    
    # Compute shared secrets
    crypto_a.compute_shared_secret(dh_public_b)
    crypto_b.compute_shared_secret(dh_public_a)
    
    # Both should have the same session key
    assert crypto_a.session_key == crypto_b.session_key, "Session keys don't match"
    assert len(crypto_a.session_key) == 32, "Session key should be 32 bytes (AES-256)"
    
    print("✓ Diffie-Hellman key exchange successful")
    return crypto_a, crypto_b


def test_message_encryption():
    """Test message encryption and decryption."""
    print("Testing message encryption and decryption...")
    
    crypto_a, crypto_b = test_dh_key_exchange()
    
    # Test message
    message = "Hello, this is a secure message! 🔒"
    
    # Encrypt with crypto_a
    encrypted = crypto_a.encrypt_message(message)
    assert len(encrypted) > len(message), "Encrypted message should be larger"
    
    # Decrypt with crypto_b (same session key)
    decrypted, counter = crypto_b.decrypt_message(encrypted, 0)
    assert decrypted == message, "Decrypted message doesn't match original"
    assert counter == 0, "Counter should be 0 for first message"
    
    print("✓ Message encryption/decryption successful")
    
    # Test multiple messages
    print("Testing multiple messages with counter...")
    
    # Reset counters for fresh test
    crypto_a.message_counter = 0
    receive_counter = 0
    
    messages = ["First message", "Second message", "Third message"]
    
    for i, msg in enumerate(messages):
        encrypted = crypto_a.encrypt_message(msg)
        decrypted, counter = crypto_b.decrypt_message(encrypted, receive_counter)
        assert decrypted == msg, f"Message {i} doesn't match"
        assert counter == i, f"Counter expected {i}, got {counter}"
        receive_counter = counter + 1
    
    print("✓ Multiple messages with counters successful")


def test_replay_protection():
    """Test replay attack protection."""
    print("Testing replay attack protection...")
    
    crypto_a, crypto_b = test_dh_key_exchange()
    
    # Encrypt a message
    message = "Test message"
    encrypted = crypto_a.encrypt_message(message)
    
    # First decryption should work
    decrypted, counter = crypto_b.decrypt_message(encrypted, 0)
    assert decrypted == message
    
    # Try to replay the same message (lower counter)
    try:
        crypto_b.decrypt_message(encrypted, 1)
        assert False, "Should have raised error for replay attack"
    except ValueError as e:
        assert "replay attack" in str(e).lower() or "counter is old" in str(e).lower()
        print("✓ Replay attack correctly detected")


def test_hmac():
    """Test HMAC computation and verification."""
    print("Testing HMAC...")
    
    crypto = CryptoManager()
    crypto.generate_rsa_keypair()
    
    # Need a session key for HMAC
    crypto.session_key = b'0' * 32  # Dummy session key
    
    data = b"Control message data"
    hmac_digest = crypto.compute_hmac(data)
    
    assert len(hmac_digest) == 32, "HMAC-SHA256 should be 32 bytes"
    
    # Verify HMAC
    is_valid = crypto.verify_hmac(data, hmac_digest)
    assert is_valid, "HMAC verification failed"
    
    # Test with wrong data
    wrong_data = b"Different data"
    is_valid_wrong = crypto.verify_hmac(wrong_data, hmac_digest)
    assert not is_valid_wrong, "HMAC should not verify with wrong data"
    
    print("✓ HMAC computation and verification successful")


def run_all_tests():
    """Run all tests."""
    print("\n" + "="*60)
    print("SECURE CHAT CRYPTOGRAPHY TESTS")
    print("="*60 + "\n")
    
    try:
        test_signature()
        print()
        test_dh_key_exchange()
        print()
        test_message_encryption()
        print()
        test_replay_protection()
        print()
        test_hmac()
        print()
        
        print("="*60)
        print("✓ ALL TESTS PASSED")
        print("="*60)
        return 0
    except AssertionError as e:
        print(f"\n✗ TEST FAILED: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(run_all_tests())
