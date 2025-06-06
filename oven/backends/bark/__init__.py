import json
import requests
from typing import Dict, Tuple, Optional

from oven.consts import REQ_TIMEOUT
from oven.backends.api import NotifierBackendBase, RespStatus

from .info import BarkBackendInfo

class BarkBackend(NotifierBackendBase):
    def __init__(self, cfg: Dict):
        """
        Initialize Bark backend with configuration.
        
        Args:
            cfg: Configuration dictionary containing:
                - api_key: Bark device key (required)
                - base_url: Optional custom Bark server URL
        """
        # Validate configuration
        assert 'api_key' in cfg, 'Bark backend requires "api_key" in configuration'
        assert isinstance(cfg['api_key'], str), 'Bark api_key must be a string'
        assert len(cfg['api_key']) == 22 and cfg['api_key'].isalnum(), (
            'Invalid Bark API key format - should be 22 alphanumeric characters'
        )

        self.cfg = cfg
        self.base_url = cfg.get('base_url', 'https://api.day.app').rstrip('/')
        self.api_key = cfg['api_key']

    def notify(self, info: BarkBackendInfo) -> RespStatus:
        """
        Send notification via Bark API.
        
        Args:
            info: BarkBackendInfo object containing notification details
            
        Returns:
            RespStatus object indicating success/failure
        """
        url = f"{self.base_url}/{self.api_key}"
        
        payload = {
            'body': info.get_content(),
            'title': info.get_title(),
            'sound': info.sound,
            'icon': info.icon,
            'group': info.group,
            'level': info.level,
            'url': info.url,
            'badge': info.badge,
            'autoCopy': info.auto_copy,
            'copy': info.copy_text
        }
        
        # Remove None values
        payload = {k: v for k, v in payload.items() if v is not None}

        has_err, err_msg = False, ''
        try:
            resp = requests.post(url, json=payload, timeout=REQ_TIMEOUT)
            resp_dict = resp.json()
            
            # Bark returns 200 even for some errors
            if resp_dict.get('code') != 200:
                has_err = True
                err_msg = resp_dict.get('message', 'Unknown Bark API error')
        except Exception as e:
            has_err = True
            err_msg = f'Bark API request failed: {str(e)}'

        return RespStatus(has_err=has_err, err_msg=err_msg)

    def get_meta(self) -> Dict:
        """Generate meta information about this backend"""
        return {
            'backend': 'BarkBackend',
            'base_url': self.base_url,
            'api_key_truncated': f"{self.api_key[:4]}...{self.api_key[-4:]}"
        }