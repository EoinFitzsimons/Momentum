Unity front-end quickstart for the Momentum backend

This small guide shows how to import the provided `UnityApiClient.cs` into a Unity project and test basic backend connectivity.

Prerequisites
- Unity 2020.3 LTS or newer (tested with 2021/2022). UnityWebRequest is used; any recent Unity will work.
- The Momentum backend running locally (FastAPI server or alternative) accessible at `http://localhost:8000`.

Files provided
- `UnityApiClient.cs` — MonoBehaviour that demonstrates GET /health and POST /simulate/race examples.

Steps
1. Open or create a Unity project.
2. In the Unity Editor, create a folder `Assets/Scripts` and copy `UnityApiClient.cs` into it.
3. In the Hierarchy create an empty GameObject and name it `ApiClient`.
4. Select `ApiClient`, click Add Component, and add the `UnityApiClient` script.
5. In the Inspector set `Base Url` to your backend, e.g. `http://localhost:8000`.
6. (Optional) Add a UI Button and hook its OnClick to the `ApiClient` GameObject, selecting `UnityApiClient.CheckHealth` or `UnityApiClient.SimulateRaceExample`.

Testing
- Start your backend server (e.g., `uvicorn simulation:app --reload --port 8000` in `Momentum/Python` if the FastAPI app is `simulation.py`).
- In Unity, press Play and click the button (or call methods via another script). Console logs will show responses.

Troubleshooting
- If you get CORS errors when calling localhost from Unity's editor, ensure your backend allows requests from the Editor (FastAPI + Starlette/fastapi needs CORSMiddleware configured). Add:

```py
from fastapi.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

- JsonUtility limitations: `JsonUtility` can't serialize `Dictionary<string, object>` or many dynamic structures. For complex payloads either:
  - Build raw JSON strings (shown in `SimulateRaceExample`) or
  - Use a JSON library such as `Newtonsoft.Json` (~Json.NET) compatible Unity port.

- Timeouts: UnityWebRequest default timeouts may be short for long-running simulations. Increase `uwr.timeout` before sending.

Next steps
- I can add a simple UI prefab (button + text field) and a small Unity scene demonstrating a simulated race result display.
- I can prepare a demo-ready backend endpoint (deterministic sample response) so the Unity client shows predictable data for your demo.

If you want me to create the Unity scene and prefab assets, say "create scene" and I'll add the minimal scripts and steps you can import into Unity.