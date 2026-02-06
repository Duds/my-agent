# Capability Spec: Distributed Mesh Core

**Status:** Draft
**Priority:** Critical (Foundational)

## 1. Overview
The **Distributed Mesh** is the nervous system of the Agent, bridging the **Work Laptop** and **Home Mac Mini**. It allows the agent to exist ubiquitously while leveraging the specific hardware advantages of each node (e.g., M1 Neural Engine on Mac, Corporate Access on Laptop).

## 2. Core Architecture

### 2.1 Networking Layer: Tailscale (Virtual Private Mesh)
We will use **Tailscale** to create a secure, encrypted peer-to-peer mesh network.
*   **Why:** Zero-config NAT traversal, secure by default, DNS magic (`http://my-agent-mac`).
*   **Configuration:** All nodes join the same Tailnet.
*   **Addressing:** Nodes address each other via stable hostnames (e.g., `agent-home`, `agent-work`).

### 2.2 Node Identity
Each instance of the application starts with a specific identity defined in `.env`.
```env
# .env example
AGENT_NODE_ID="agent-work-laptop"
AGENT_ROLE="satellite" # or "primary"
MESH_PEERS=["agent-home-mini"]
```

### 2.3 RPC Layer (Remote Procedure Calls)
Nodes communicate via **FastAPI** endpoints secured to the Tailscale interface.
*   **Protocol:** HTTP/JSON (REST) for control messages; WebSocket for real-time streams (logs/interventions).
*   **Auth:** API Key shared via `secret` manager (or Tailscale identity headers).
*   **Router:** A `MeshRouter` class in Python will wrap local vs remote calls.
    ```python
    # Hypothetical usage
    response = await mesh.route(
        capability="llm_inference",
        payload={...},
        prefer_node="agent-home-mini" # Route heavy tasks to Mac
    )
    ```

### 2.4 State Synchronization
*   **Code & Config:** Synced via **Git** (GitHub/GitLab).
*   **Knowledge (Vector DB):** 
    *   *Phase 1:* Independent dbs per node (User syncing not critical immediately).
    *   *Phase 2:* Master-Slave replication or centralized ChromaDB on Home Mac.
*   **Files (Downloads/Projects):** **Syncthing** running purely on the specific directories we want to mirror (Search-free P2P sync).

## 3. Implementation Plan (Phased)

### Phase 1: "The Ping" (Connectivity)
1.  Install Tailscale on both machines.
2.  Create `core/mesh.py`: Basic discovery of peers.
3.  Add `/mesh/health` endpoint to FastAPI.
4.  Verify Work Laptop can `curl http://agent-home-mini:8000/mesh/health`.

### Phase 2: "The Brain Transplant" (Remote LLM)
1.  Home Mac hosts Ollama.
2.  Work Laptop configures `core/llm.py` to point `OLLAMA_HOST` to `http://agent-home-mini:11434`.
3.  Demonstrate Work Laptop asking Home Mac to generate text.

### Phase 3: "The Handover" (State)
1.  Setup Syncthing for `~/agent_data/`.
2.  Implement "Handoff" command: "Continue this conversation on home node."

## 4. Decision Log
*   **Decision:** Use Tailscale over OpenVPN/manual tunnels. (Reason: Ease of use, security).
*   **Decision:** Use HTTPS/REST for RPC over gRPC. (Reason: Simplified debugging, reuses existing FastAPI stack).
