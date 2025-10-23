real_ipfs.py
import ipfs_api

class RealIPFS:
    def __init__(self):
        # Varmista, että IPFS-daemon on käynnissä
        # Varmista, että Libp2pStreamMounting on käytössä (katso aiempi ohje)
        print("Yhdistetään IPFS:ään...")
        # Tämä yrittää yhdistää automaattisesti oletusosoitteeseen
        # /ip4/127.0.0.1/tcp/5001

    def add_json(self, data):
        import json
        import tempfile
        import os
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            json.dump(data, f)
            temp_path = f.name
        try:
            res = ipfs_api.add(temp_path)
            cid = res[0]['Hash']
            return cid
        finally:
            os.unlink(temp_path)

    def get_json(self, cid):
        import tempfile
        import json
        import os
        # Lataa CID ja palauta JSON
        with tempfile.TemporaryDirectory() as tmpdir:
            path = os.path.join(tmpdir, 'data.json')
            ipfs_api.get(cid, path=path)
            with open(path, 'r') as f:
                return json.load(f)
