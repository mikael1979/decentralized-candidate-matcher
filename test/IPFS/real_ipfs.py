# real_ipfs.py
import ipfshttpclient

class RealIPFS:
    def __init__(self, host='localhost', port=5001):
        self.client = ipfshttpclient.connect('/ip4/127.0.0.1/tcp/5001')
    
    def add_json(self, data):
        """Lisää JSON-datan oikeaan IPFS-verkkoon"""
        result = self.client.add_json(data)
        return {
            "Hash": result,
            "Size": len(str(data)),
            "Name": result
        }
    
    def get_json(self, cid):
        """Hakee JSON-datan oikeasta IPFS-verkosta"""
        return self.client.get_json(cid)
    
    def pin_add(self, cid):
        """Pinnaa CID:n oikeaan IPFS:ään"""
        return self.client.pin.add(cid)
