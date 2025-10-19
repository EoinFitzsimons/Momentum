using System;
using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;

// Minimal Unity API client for the Momentum FastAPI backend.
// Drop this into a GameObject in your Unity scene and set the baseUrl.
// Requires Unity 2020.3+ (or any Unity with UnityWebRequest support).

public class UnityApiClient : MonoBehaviour
{
    [Tooltip("Base URL of the Momentum backend, e.g. http://localhost:8000")]
    public string baseUrl = "http://localhost:8000";

    // Example: call GET /health
    public void CheckHealth()
    {
        StartCoroutine(GetRequest("/health", (success, text) => {
            if (success)
                Debug.Log("Health OK: " + text);
            else
                Debug.LogError("Health check failed: " + text);
        }));
    }

    // Example: call POST /simulate/race with a small payload (send raw JSON string)
    public void SimulateRaceExample()
    {
        // JsonUtility cannot serialize Dictionary<string, object> directly in Unity.
        // Use a raw JSON string for the example payload below.
        string json = "{\"discipline\": \"SINGLE_SEATER\", \"race_id\": 0, \"drivers\": [] }";

        StartCoroutine(PostJson("/simulate/race", json, (success, text) => {
            if (success)
                Debug.Log("Simulate race response: " + text);
            else
                Debug.LogError("Simulate race failed: " + text);
        }));
    }

    IEnumerator GetRequest(string path, Action<bool,string> callback)
    {
        var url = baseUrl.TrimEnd('/') + path;
        using (UnityWebRequest webRequest = UnityWebRequest.Get(url))
        {
            webRequest.timeout = 10;
            yield return webRequest.SendWebRequest();

#if UNITY_2020_1_OR_NEWER
            if (webRequest.result == UnityWebRequest.Result.ConnectionError || webRequest.result == UnityWebRequest.Result.ProtocolError)
#else
            if (webRequest.isNetworkError || webRequest.isHttpError)
#endif
            {
                callback(false, webRequest.error + " - " + webRequest.downloadHandler.text);
            }
            else
            {
                callback(true, webRequest.downloadHandler.text);
            }
        }
    }

    IEnumerator PostJson(string path, string json, Action<bool,string> callback)
    {
        var url = baseUrl.TrimEnd('/') + path;
        var uwr = new UnityWebRequest(url, "POST");
        byte[] bodyRaw = System.Text.Encoding.UTF8.GetBytes(json);
        uwr.uploadHandler = new UploadHandlerRaw(bodyRaw);
        uwr.downloadHandler = new DownloadHandlerBuffer();
        uwr.SetRequestHeader("Content-Type", "application/json");
        uwr.timeout = 30;

        yield return uwr.SendWebRequest();

#if UNITY_2020_1_OR_NEWER
        if (uwr.result == UnityWebRequest.Result.ConnectionError || uwr.result == UnityWebRequest.Result.ProtocolError)
#else
        if (uwr.isNetworkError || uwr.isHttpError)
#endif
        {
            callback(false, uwr.error + " - " + uwr.downloadHandler.text);
        }
        else
        {
            callback(true, uwr.downloadHandler.text);
        }
    }

    // Note: Unity's JsonUtility is limited. For complex payloads consider using a
    // third-party JSON library such as Newtonsoft.Json for Unity (recommended) or
    // construct raw JSON strings for small requests as shown above.
}
