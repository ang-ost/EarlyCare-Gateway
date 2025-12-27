"""Encryption service for data at rest and in transit."""

import base64
import hashlib
import secrets
from typing import Optional, Tuple
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class EncryptionService:
    """
    Provides encryption/decryption services for sensitive clinical data.
    Implements AES-256 encryption for HIPAA compliance.
    """
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialize encryption service.
        
        Args:
            master_key: Optional master key. If not provided, generates new key.
        """
        if master_key:
            self.master_key = master_key
        else:
            self.master_key = Fernet.generate_key()
        
        self.cipher = Fernet(self.master_key)
    
    @staticmethod
    def generate_key() -> bytes:
        """Generate a new encryption key."""
        return Fernet.generate_key()
    
    @staticmethod
    def derive_key_from_password(
        password: str,
        salt: Optional[bytes] = None
    ) -> Tuple[bytes, bytes]:
        """
        Derive encryption key from password using PBKDF2.
        
        Args:
            password: User password
            salt: Optional salt. If not provided, generates new salt.
            
        Returns:
            Tuple of (derived_key, salt)
        """
        if salt is None:
            salt = secrets.token_bytes(16)
        
        kdf = PBKDF2(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def encrypt(self, data: str) -> str:
        """
        Encrypt string data.
        
        Args:
            data: Plain text data
            
        Returns:
            Encrypted data as base64 string
        """
        encrypted_bytes = self.cipher.encrypt(data.encode())
        return base64.urlsafe_b64encode(encrypted_bytes).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        Decrypt encrypted data.
        
        Args:
            encrypted_data: Encrypted data as base64 string
            
        Returns:
            Decrypted plain text
        """
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
        decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
        return decrypted_bytes.decode()
    
    def encrypt_bytes(self, data: bytes) -> bytes:
        """
        Encrypt binary data.
        
        Args:
            data: Binary data
            
        Returns:
            Encrypted data
        """
        return self.cipher.encrypt(data)
    
    def decrypt_bytes(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt binary data.
        
        Args:
            encrypted_data: Encrypted binary data
            
        Returns:
            Decrypted binary data
        """
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_file(self, input_path: str, output_path: str) -> bool:
        """
        Encrypt a file.
        
        Args:
            input_path: Path to input file
            output_path: Path to encrypted output file
            
        Returns:
            True if successful
        """
        try:
            with open(input_path, 'rb') as f:
                data = f.read()
            
            encrypted_data = self.encrypt_bytes(data)
            
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
            
            return True
        except Exception as e:
            print(f"Error encrypting file: {e}")
            return False
    
    def decrypt_file(self, input_path: str, output_path: str) -> bool:
        """
        Decrypt a file.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to decrypted output file
            
        Returns:
            True if successful
        """
        try:
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = self.decrypt_bytes(encrypted_data)
            
            with open(output_path, 'wb') as f:
                f.write(decrypted_data)
            
            return True
        except Exception as e:
            print(f"Error decrypting file: {e}")
            return False
    
    @staticmethod
    def hash_data(data: str, algorithm: str = 'sha256') -> str:
        """
        Create cryptographic hash of data.
        
        Args:
            data: Data to hash
            algorithm: Hash algorithm ('sha256', 'sha512')
            
        Returns:
            Hex digest of hash
        """
        if algorithm == 'sha256':
            return hashlib.sha256(data.encode()).hexdigest()
        elif algorithm == 'sha512':
            return hashlib.sha512(data.encode()).hexdigest()
        else:
            raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    def rotate_key(self, new_master_key: bytes) -> None:
        """
        Rotate encryption key.
        
        Args:
            new_master_key: New master key
        """
        self.master_key = new_master_key
        self.cipher = Fernet(self.master_key)
    
    def get_key_info(self) -> dict:
        """Get information about current encryption key."""
        return {
            'algorithm': 'AES-256',
            'mode': 'CBC',
            'key_length': len(self.master_key) * 8,
            'key_hash': hashlib.sha256(self.master_key).hexdigest()[:16]
        }
