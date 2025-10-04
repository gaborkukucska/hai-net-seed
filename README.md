<!-- # START OF FILE README.md -->
<!-- # IT IS CRITICAL THAT ALL AIs and LLMs FOLLOW THE DEVELOPMENT INSTRUCTIONS IN THE `helperfiles/DEVELOPMENT_RULES.md` FILE WHEN FURTHER DEVELOPING THIS FRAMEWORK!!! -->

# 🌐 HAI-Net Seed Framework

**Human-AI Network: A Constitutional Framework for Decentralized AI Collaboration**

[![Constitutional Compliance](https://img.shields.io/badge/Constitutional_Compliance-100%25-green.svg)](./CONSTITUTION.md)
[![Phase](https://img.shields.io/badge/Phase-1%20MVP%20Complete-success.svg)](./helperfiles/PROJECT_PLAN.md)
[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](./requirements.txt)
[![License](https://img.shields.io/badge/License-Open_Source-brightgreen.svg)](./LICENSE)

## 🎯 Vision

HAI-Net creates a **decentralized, privacy-first framework** for human-AI collaboration that strengthens real-world communities while providing sustainable alternatives to centralized AI systems.

## 🏛️ Constitutional Foundation

HAI-Net is built on **four immutable constitutional principles**:

1. **🔒 Privacy First** - No personal data leaves Local Hub without explicit consent
2. **👥 Human Rights Protection** - AI serves humanity with accessibility and user control
3. **🌐 Decentralization** - No central authority, local autonomy, fork-resistant
4. **🤝 Community Focus** - Strengthen real-world connections and collaboration

*Every line of code enforces these principles.* [Read the Full Constitution →](./CONSTITUTION.md)

## 🚀 Current Status

### ✅ **Phase 1 MVP COMPLETE - Production Ready** 

**🎉 Complete Constitutional AI Network Implemented:**

| Component | Status | Description |
|-----------|--------|-------------|
| 🔐 **Identity System** | ✅ Complete | Advanced DID generation with Argon2id, watermarking, constitutional validation |
| 🌐 **P2P Networking** | ✅ Complete | mDNS discovery, encrypted P2P communication, dynamic role management |
| 🤖 **AI Agent System** | ✅ Complete | Event-driven agent hierarchy (Admin, PM, Worker) based on the TrippleEffect model. |
| 🧠 **Memory & LLM** | ✅ Complete | Vector store, Ollama integration, constitutional filtering |
| 🛡️ **Constitutional Guardian** | ✅ Complete | Real-time monitoring, violation detection, educational remediation |
| 🌐 **Web Interface** | ✅ Complete | FastAPI server, React + WebGPU UI, real-time network visualization |
| 🗄️ **Database & Storage** | ✅ Complete | Constitutional compliance, vector search, encryption |
| ⚙️ **Configuration** | ✅ Complete | Pydantic V2 validation, constitutional compliance checks |
| 📊 **Logging System** | ✅ Complete | Constitutional audit trail, comprehensive violation tracking |
| 🧪 **Testing Framework** | ✅ Complete | 19/19 constitutional compliance + end-to-end integration tests |
| **🆕 Node Role Manager** | ✅ Complete | Dynamic master/slave assignment with constitutional elections |
| **🆕 WebGPU Renderer** | ✅ Complete | Hardware-accelerated network visualization with constitutional indicators |
| **🆕 Integration Testing** | ✅ Complete | End-to-end system testing with constitutional compliance validation |
| **🆕 Docker Deployment** | ✅ Complete | Production containers with security hardening and health checks |
| **🆕 Installation Automation** | ✅ Complete | Cross-platform setup with constitutional principle acceptance |

**🏗️ Advanced Architecture Achieved:**
- **Complete 3-Layer System**: Application, Service, and Infrastructure layers operational
- **Constitutional AI**: Full agent hierarchy with independent Guardian monitoring
- **P2P Decentralization**: No central authority, mesh networking ready
- **Production Quality**: Professional codebase with comprehensive error handling
- **Privacy-First Design**: Local-only processing, encrypted storage, user consent
- **Real-Time Interface**: React UI with WebSocket updates and constitutional monitoring

## 🛠️ Technical Implementation

### **Complete 3-Layer Architecture**

```
📁 HAI-Net Seed/
├── 🏛️ CONSTITUTION.md          # Immutable constitutional framework
├── 📋 PROJECT_PLAN.md          # Development roadmap and milestones
├── 📖 FUNCTIONS_INDEX.md       # Complete function reference
├── 📦 requirements.txt         # Python & React dependencies
├── 🔐 core/identity/           # DID generation & watermarking
├── 🌐 core/network/            # P2P, discovery, encryption
├── 🤖 core/ai/                 # Agents, LLM, memory, guardian
├── 🗄️ core/storage/            # Database & vector store
├── 🌐 core/web/                # FastAPI server & WebSocket
├── ⚙️ core/config/             # Constitutional validation
├── 📊 core/logging/            # Audit trail & compliance
├── 🌐 web/                     # React UI with Material-UI
└── 🧪 tests/                  # Constitutional compliance tests
```

### **Advanced Technology Stack**

- **Backend**: Python 3.9+, FastAPI, SQLite, asyncio, WebSocket
- **Frontend**: React 18+, TypeScript, Material-UI, WebGPU ready  
- **AI**: Ollama integration, vector search, constitutional filtering
- **Networking**: P2P communication, mDNS discovery, TLS 1.3 + Noise Protocol
- **Security**: Argon2id, ChaCha20, RSA cryptography, encrypted storage
- **Architecture**: 3-layer design, agent state machines, real-time updates

## 📖 Quick Start

### **🚀 One-Click Installation & Launch**

#### **Step 1: Clone Repository**
```bash
git clone https://github.com/gaborkukucska/hai-net-seed.git
cd hai-net-seed
```

#### **Step 2: Constitutional Installation**
```bash
# Run the constitutional installer (interactive)
./install.sh

# The installer will:
# ✅ Accept constitutional principles
# ✅ Install system dependencies  
# ✅ Create Python virtual environment
# ✅ Install all required packages
# ✅ Run constitutional compliance tests
# ✅ Set up Docker and system services
```

#### **Step 3: Launch HAI-Net**
```bash
# Interactive launch (recommended for first time)
./launch.sh

# Quick development start
./launch.sh --dev

# Docker production mode
./launch.sh --docker

# Run constitutional tests
./launch.sh --test
```

### **🎯 Launch Options**

The `./launch.sh` script provides multiple launch modes:

| Mode | Command | Description |
|------|---------|-------------|
| **🖥️ Development** | `./launch.sh --dev` | Full development mode with logging |
| **🌐 Web Only** | `./launch.sh --web` | Web interface only |
| **🐳 Docker** | `./launch.sh --docker` | Production Docker container |
| **🔧 Service** | `./launch.sh --service` | SystemD service management |
| **🧪 Test** | `./launch.sh --test` | Constitutional compliance tests |
| **🛠️ Debug** | `./launch.sh --debug` | Verbose logging and debugging |

### **✅ Expected Installation Output**
```bash
🏛️ HAI-Net Seed Framework - Constitutional Setup
✅ Constitutional Compliance: PASS (0 violations)
✅ Python 3.12.3 found
✅ Node.js found
✅ Constitutional compliance verified
✅ HAI-Net installation complete!
```

### **🌐 Web Interface Access**
After launching, access HAI-Net at:
- **Network Visualization**: http://localhost:8080 (WebGPU accelerated)
- **API Documentation**: http://localhost:8000/docs
- **Constitutional Dashboard**: http://localhost:8080/constitutional

### **🔧 Manual Installation (Advanced Users)**

If you prefer manual setup or need to customize the installation:

#### **Prerequisites**
- Python 3.9+ (3.12 recommended)
- Node.js 16+ (for React frontend)
- Git
- Docker (optional, for production)

#### **Manual Python Setup**
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Install network dependencies
pip install zeroconf netifaces psutil

# Test constitutional compliance
python -m pytest tests/test_constitutional_compliance.py -v
```

#### **Manual React Setup**
```bash
# Install and build web interface
cd web
npm install
npm run build
cd ..
```

#### **Manual Launch**
```bash
# Activate environment and start
source venv/bin/activate
python -m core.web.server
```

### **🆔 Create Your First Identity**
```python
from core.identity.did import IdentityManager

# Create constitutionally compliant identity
manager = IdentityManager()
identity = manager.create_identity(
    full_name="Your Name",
    date_of_birth="1990-01-01", 
    government_id="ID123456",
    passphrase="secure_passphrase_123",
    email="you@example.com"
)

print(f"Your HAI-Net DID: {identity['did']}")
```

### **🔍 Troubleshooting**
| Issue | Solution |
|-------|----------|
| **Port conflicts** | Change ports in `core/config/settings.py` |
| **Permission errors** | Run `chmod +x install.sh launch.sh` |
| **Constitutional violations** | Check logs for educational guidance |
| **Network issues** | Verify firewall allows port 4001 (P2P) |
| **Missing dependencies** | Re-run `./install.sh` |
| **Docker issues** | Ensure Docker is installed and user is in docker group |

## 🗺️ Development Roadmap

### **✅ Completed: Phase 0 - Foundation (Weeks 1-4)**
- ✅ **Week 1**: Core infrastructure, identity, config, logging *(COMPLETE)*
- ✅ **Week 2**: Networking (mDNS, P2P, encryption) *(COMPLETE)*
- ✅ **Week 3**: AI foundation (LLM integration, agent state machine) *(COMPLETE)*
- ✅ **Week 4**: UI foundation (FastAPI, React UI, WebSocket) *(COMPLETE)*

### **✅ Completed: Phase 1 - MVP (Weeks 5-8)**
- **Week 5-6**: ✅ Node role detection (Master/Slave), enhanced coordination *(COMPLETE)*
- **Week 7-8**: ✅ WebGPU visualization engine, end-to-end testing, Docker deployment *(COMPLETE)*
- **All Phase 1 goals achieved**: Constitutional AI network with hardware-accelerated visualization

### **📍 Current: Phase 2 - Alpha (Weeks 9-12)**
- **Ready to begin**: Advanced AI workflows, voice integration, mesh networking

### **🚀 Next Phases**
- **Phase 2**: Alpha with advanced AI workflows, voice services (Whisper/Piper), multi-hub mesh networking
- **Phase 3**: Beta with full AI marketplace, enhanced community governance, mobile deployment
- **Phase 4**: Production release with global constitutional AI network

[View Detailed Roadmap →](./helperfiles/PROJECT_PLAN.md)

## 🧠 Constitutional AI Agents

HAI-Net implements a sophisticated, **event-driven agent architecture** inspired by the TrippleEffect framework. This model enables complex, delegated workflows through a clear hierarchy and state management.

### Agent Hierarchy
The system uses a three-tier agent hierarchy:

```
👑 Admin Agent    - The user's primary AI counterpart. It receives user requests, handles top-level planning, and delegates tasks to Project Manager agents.
👔 PM (Project Manager) Agent - Manages the lifecycle of a specific project. It breaks down the Admin's plan into concrete tasks, spawns Worker agents, and monitors progress.
⚙️ Worker Agent   - A specialized agent that executes a single, well-defined task assigned by a PM agent.
🛡️ Guardian Agent  - An independent constitutional compliance monitor that oversees all agent actions.
```

### Event-Driven Execution
Agents operate asynchronously. Instead of executing tasks directly, an agent's `process_message` method yields a series of **events** (e.g., `tool_requests`, `final_response`). A central `AgentCycleHandler` consumes these events and orchestrates the corresponding actions, such as calling a tool or changing an agent's state. This decoupled design provides robustness and observability.

### Agent States
Agents operate on a detailed state machine, allowing for complex workflows. Key states include:
- **`PLANNING`**: The Admin or PM agent is creating a plan.
- **`MANAGE`**: The PM agent is actively monitoring its worker agents.
- **`WORK`**: A worker agent is executing its assigned task.
- **`WAIT`**: A worker agent has completed its task and is waiting for review.

*All agents operate under constitutional constraints, with every action logged for a complete audit trail.*

## 🌐 Network Architecture

### **Three-Layer System**
```
📱 Application Layer  - HAI-Net UI, AI Agents, User Tools
🔧 Service Layer      - AI Services, Resource Management, APIs  
🏗️ Infrastructure     - Mesh Network, Storage, Compute Pool
```

### **Resource Model**
- **🏠 Local Resources**: 100% dedicated to Local Hub users (never shared)
- **♻️ Surplus Resources**: Voluntary community sharing of idle compute
- **🌍 Environmental Focus**: Efficient resource use reduces global waste

## 🤝 Community & Governance

### **Decentralized Governance**
- **Consensus-based decisions** for technical changes
- **Community-driven development** with constitutional compliance
- **Fork-resistant architecture** prevents centralization
- **Educational approach** to violations (not punitive)

### **Real-World Community Focus**
- **In-person interaction priority** over digital-only connections
- **Local event promotion** and coordination
- **Skill sharing** and collaboration tools
- **Mutual aid** and community support systems

## 🔬 Testing & Compliance

**Constitutional Compliance Testing**:
```bash
# Run full constitutional compliance test suite
python tests/test_constitutional_compliance.py

# Expected output:
✅ Privacy First Principle: Verified
✅ Human Rights Protection: Verified  
✅ Decentralization Imperative: Verified
✅ Community Focus Principle: Verified
🎉 HAI-Net is Constitutionally Compliant!
```

**Test Coverage**:
- Privacy protection verification
- Human rights compliance checks
- Decentralization requirement testing  
- Community focus validation
- Constitutional violation detection

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| [🏛️ CONSTITUTION.md](./CONSTITUTION.md) | Immutable constitutional framework |
| [📋 PROJECT_PLAN.md](./helperfiles/PROJECT_PLAN.md) | Development roadmap and milestones |
| [🛠️ DEVELOPMENT_RULES.md](./helperfiles/DEVELOPMENT_RULES.md) | Development guidelines and standards |
| [📖 FUNCTIONS_INDEX.md](./helperfiles/FUNCTIONS_INDEX.md) | Complete function and class reference |

## 🤝 Contributing

HAI-Net welcomes community contributions that align with our constitutional principles:

1. **Read the Constitution**: Understand our core principles
2. **Follow Development Rules**: See `helperfiles/DEVELOPMENT_RULES.md`
3. **Constitutional Compliance**: All code must pass compliance tests
4. **Educational Approach**: Help others learn and improve

## 🌱 Environmental Impact

*"Every idle resource shared prevents unnecessary hardware production and reduces global energy waste. Join us in building a cooler planet!"*

- **Resource Efficiency**: Idle compute sharing reduces waste
- **Sustainable Architecture**: Optimized for minimal energy use
- **Community Benefit**: Shared resources support important projects
- **Environmental Tracking**: Monitor and measure impact

## 📞 Support & Community

- **Constitutional Questions**: See [CONSTITUTION.md](./CONSTITUTION.md)
- **Development Guidelines**: See [DEVELOPMENT_RULES.md](./helperfiles/DEVELOPMENT_RULES.md)  
- **Project Status**: See [PROJECT_PLAN.md](./helperfiles/PROJECT_PLAN.md)
- **Technical Reference**: See [FUNCTIONS_INDEX.md](./helperfiles/FUNCTIONS_INDEX.md)

## 📜 License

Open Source - Building technology that serves humanity.

---

*"Technology that serves humanity, communities that support each other, privacy that empowers individuals, and AI that enhances rather than replaces human connection."*

**🌟 HAI-Net: Where Constitutional AI Meets Human Community**
