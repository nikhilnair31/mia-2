import os
import logging
import requests
import numpy as np

logger = logging.getLogger()
logger.setLevel("INFO")

def vectorize_query_text(query_text):
    logger.info(f"\nVectorizing query text: {query_text}")

    REPLICATE_API_KEY = os.environ.get("REPLICATE_API_KEY")
    if not REPLICATE_API_KEY:
        raise ValueError("REPLICATE_API_KEY environment variable not set.")
    
    try:
        api_url = "daanelson/imagebind:0383f62e173dc821ec52663ed22a076d9c970549c209666ac3db181618b7a304"
        payload = {
            "text": query_text
        }
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {REPLICATE_API_KEY}"
        }
        
        response = requests.post(api_url, json=payload, headers=headers)
        response.raise_for_status()
        
        result = response.json()
        
        embedding = np.array(result["embedding"], dtype=np.float32)
        
        return embedding
    
    except Exception as e:
        logger.error(f"Error vectorizing query text: {e}")
        return None