# HAI-Net Seed Framework - Quick Start Guide

## Constitutional Principles ⚖️
This installation enforces HAI-Net's four core constitutional principles:
- **Privacy First**: Your data stays local, encryption enabled by default
- **Human Rights**: You maintain control, accessibility features enabled  
- **Decentralization**: No central authority, peer-to-peer networking
- **Community Focus**: Collaborative governance, community participation

## Starting HAI-Net

### Method 1: Development Mode
```bash
# Activate the constitutional environment
source venv/bin/activate

# Start the HAI-Net framework
python -m core.web.server

# Open your browser to: http://localhost:8080
```

### Method 2: Docker (Production)
```bash
# Build constitutional Docker image
docker build -t hainet-seed:constitutional .

# Run with constitutional compliance
docker run -d \
  --name hainet-hub \
  -p 8080:8080 \
  -p 8000:8000 \
  -p 4001:4001 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/config:/app/config \
  hainet-seed:constitutional
```

### Method 3: System Service (Linux)
```bash
# Enable and start the service
sudo systemctl enable hainet
sudo systemctl start hainet

# Check status
sudo systemctl status hainet

# View logs
sudo journalctl -u hainet -f
```

## Web Interface
- **Network Visualization**: http://localhost:8080 (WebGPU accelerated)
- **API Documentation**: http://localhost:8000/docs
- **Constitutional Dashboard**: http://localhost:8080/constitutional

## Configuration
Edit `config/constitutional.yaml` to customize your local hub while maintaining constitutional compliance.

## Testing Constitutional Compliance
```bash
# Run constitutional compliance tests
python -m pytest tests/test_constitutional_compliance.py -v

# Run full integration tests
python -m pytest tests/test_e2e_integration.py -v
```

## Troubleshooting
- **Port conflicts**: Change ports in `core/config/settings.py`
- **Permission errors**: Ensure proper file permissions: `chmod +x install.sh`
- **Constitutional violations**: Check logs for educational guidance
- **Network issues**: Verify firewall allows P2P connections (port 4001)

## Constitutional Governance
As a HAI-Net participant, you can:
- ✅ Maintain full control over your data (Privacy First)
- ✅ Override any AI decisions (Human Rights)  
- ✅ Participate in decentralized governance (Decentralization)
- ✅ Contribute to community development (Community Focus)

For more information, see: https://github.com/hai-net/hai-net-seed
