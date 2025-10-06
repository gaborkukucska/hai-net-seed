<!-- # START OF FILE README.md -->
<!-- # IT IS CRITICAL THAT ALL AIs and LLMs FOLLOW THE DEVELOPMENT INSTRUCTIONS IN THE `helperfiles/DEVELOPMENT_RULES.md` FILE WHEN FURTHER DEVELOPING THIS FRAMEWORK!!! -->

# 🌐 HAI-Net Seed Framework

**Human-AI Network: A Constitutional Framework for Decentralized AI Collaboration**

[![Constitutional Compliance](https://img.shields.io/badge/Constitutional_Compliance-100%25-green.svg)](./CONSTITUTION.md)
[![Phase](https://img.shields.io/badge/Phase-1%20Core%20Workflow%20Implemented-yellow.svg)](./helperfiles/PROJECT_PLAN.md)
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

### 🟡 **Phase 1 In Progress: Core Agent Workflow Functional**

The foundational, event-driven agent workflow is now implemented and tested. This provides a stable base for building out the full feature set.

**Key Accomplishments:**
- **Automated Agent Hierarchy:** Implemented the full Admin -> PM -> Worker delegation workflow.
- **Event-Driven Architecture:** The core components (`AgentManager`, `AgentCycleHandler`, `WorkflowManager`) are functional and orchestrate agent actions.
- **State Machine:** Agents now correctly transition through states (`PLANNING`, `STARTUP`, `BUILD_TEAM_TASKS`, `WORK`, etc.) as part of the automated workflow.
- **End-to-End Integration Test:** A new test (`tests/test_automated_workflow.py`) validates the entire delegation process.

**Component Status:**

| Component | Status | Description |
|-----------|--------|-------------|
| 🤖 **AI Agent System** | ✅ Functional | The core automated workflow (Admin -> PM -> Worker) is operational. |
| 💬 **Chat Interface** | ✅ Functional | Audio-visual chat interface with Admin AI, voice features ready. |
| 🧪 **Testing Framework**| ✅ Functional | A robust testing framework with a mock LLM and an end-to-end workflow test is in place. |
| ⚙️ **Configuration** | ✅ Functional | Pydantic-based settings management is working. |
| 📊 **Logging System** | ✅ Functional | Constitutional logger is integrated. |
| 🌐 **Web Interface** | ✅ Functional | React UI with Material-UI, WebGPU network visualization, chat page. |
| 🎤 **Audio/TTS/STT** | 🟡 Infrastructure | Whisper, Coqui TTS packages integrated, voice UI ready for implementation. |
| 🔐 **Identity System** | 🟡 Placeholder | Core classes exist but are not integrated into the agent workflow. |
| 🌐 **P2P Networking** | 🟡 Placeholder | Core classes exist but are not integrated into the agent workflow. |
| 🗄️ **Database & Storage**| 🟡 Placeholder | Core classes exist but are not integrated into the agent workflow. |
| 🛡️ **Constitutional Guardian** | 🟡 Placeholder | Core class exists but is not integrated into the agent workflow. |

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
- **Audio**: OpenAI Whisper (STT), Coqui TTS (Text-to-Speech), PyAudio, librosa
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
- **Chat Interface**: http://localhost:8080/chat (Audio-visual Admin AI chat - **NEW!**)
- **Network Visualization**: http://localhost:8080/network (WebGPU accelerated)
- **Activity Feed**: http://localhost:8080/feed (Real-time AI activity)
- **Logs**: http://localhost:8080/logs (System logs and audit trail)
- **Settings**: http://localhost:8080/settings (Constitutional settings)
- **API Documentation**: http://localhost:8000/docs

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
- ✅ Core infrastructure and class structure established.

### **📍 Current: Phase 1 - Core Workflow Implementation (In Progress)**
- **✅ COMPLETE**: Implemented the full, event-driven, automated agent workflow.
  - ✅ Admin agent can create a plan, which automatically spawns a PM agent.
  - ✅ PM agent can break down the plan into tasks.
  - ✅ PM agent can request the creation of Worker agents for each task.
  - ✅ PM agent can assign tasks to workers using the `SendMessageTool`.
  - ✅ Worker agents can receive and execute tasks.
  - ✅ Added a comprehensive integration test (`test_automated_workflow.py`) to validate the entire flow.
  - ✅ Fixed critical frontend build issue by correcting the `web/public` directory structure.

**Next (Phase 1 Continued)**:
- [ ] **PRIORITY**: Fully integrate the frontend with the backend. Fix the UI build process and connect it to the agent system via WebSockets.
- [ ] **NEXT**: Integrate the `ConstitutionalGuardian` into the agent cycle to monitor all communications.
- [ ] Enhance the `MemoryManager` and integrate it with agents to provide long-term memory.
- [ ] Implement the P2P networking components to allow agents to discover each other.

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
