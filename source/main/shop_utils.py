"""
Shop configuration utilities for loading and managing shop products.
"""
import json
import os
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

_shop_config_cache = None


def load_shop_config():
    """
    Load shop configuration from JSON file.
    Uses caching to avoid repeated file reads.

    Returns:
        dict: Shop configuration with products and categories
    """
    global _shop_config_cache

    if _shop_config_cache is not None:
        return _shop_config_cache

    config_path = getattr(
        settings,
        'SHOP_CONFIG_PATH',
        os.path.join(settings.BASE_DIR, 'main', 'shop_config.json')
    )

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            _shop_config_cache = json.load(f)
            logger.debug(f"Loaded shop config from {config_path}")
            return _shop_config_cache
    except FileNotFoundError:
        logger.warning(f"Shop config not found at {config_path}")
        return {'products': [], 'categories': [], 'version': '1.0', 'currency': 'USD'}
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in shop config: {e}")
        return {'products': [], 'categories': [], 'version': '1.0', 'currency': 'USD'}


def get_enabled_products():
    """
    Get list of enabled products.

    Returns:
        list: List of product dicts that are enabled
    """
    config = load_shop_config()
    return [p for p in config.get('products', []) if p.get('enabled', True)]


def get_product_config(product_id):
    """
    Get configuration for a specific product by ID.

    Args:
        product_id: The product ID (e.g., 'free_single', 'paid_10pack')

    Returns:
        dict or None: Product configuration dict, or None if not found
    """
    config = load_shop_config()
    for product in config.get('products', []):
        if product.get('id') == product_id:
            return product
    return None


def get_categories():
    """
    Get list of product categories, sorted by order.

    Returns:
        list: List of category dicts, sorted by 'order' field
    """
    config = load_shop_config()
    return sorted(config.get('categories', []), key=lambda x: x.get('order', 0))


def get_currency():
    """
    Get the shop currency.

    Returns:
        str: Currency code (e.g., 'USD')
    """
    config = load_shop_config()
    return config.get('currency', 'USD')


def clear_shop_config_cache():
    """
    Clear the configuration cache.
    Useful for testing or when config file is updated.
    """
    global _shop_config_cache
    _shop_config_cache = None
    logger.debug("Shop config cache cleared")


def format_price(price_cents, currency=None):
    """
    Format a price in cents to a display string.

    Args:
        price_cents: Price in cents (e.g., 999 for $9.99)
        currency: Currency code (defaults to shop currency)

    Returns:
        str: Formatted price string (e.g., '$9.99')
    """
    if currency is None:
        currency = get_currency()

    if price_cents == 0:
        return 'Free'

    # Simple formatting for USD
    if currency == 'USD':
        return f'${price_cents / 100:.2f}'
    elif currency == 'EUR':
        return f'{price_cents / 100:.2f}'
    else:
        return f'{price_cents / 100:.2f} {currency}'
