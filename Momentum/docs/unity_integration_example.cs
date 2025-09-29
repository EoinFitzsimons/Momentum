"""
Enhanced Unity integration examples for Momentum simulation.
Shows best practices for Unity ↔ Python FastAPI communication.
"""

using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Networking;
using Newtonsoft.Json;

namespace Momentum.API
{
    [System.Serializable]
    public class DriverData
    {
        public int id;
        public string name;
        public string nationality;
        public float skill;
        public float consistency;
        public float racecraft;
        public int career_wins;
        public int career_points;
    }

    [System.Serializable]
    public class DriversResponse
    {
        public DriverData[] drivers;
        public int count;
    }

    [System.Serializable]
    public class RaceSimulationRequest
    {
        public int race_id;
        public string weather_conditions;
        public Participant[] participants;
    }

    [System.Serializable]
    public class Participant
    {
        public int driver_id;
        public int team_id;
    }

    [System.Serializable]    
    public class RaceResult
    {
        public int driver_id;
        public int team_id;
        public int position;
        public int points;
        public bool fastest_lap;
    }

    [System.Serializable]
    public class RaceSimulationResponse
    {
        public int race_id;
        public string weather;
        public RaceResult[] results;
        public string simulation_status;
    }

    public class MomentumAPIClient : MonoBehaviour
    {
        [Header("API Configuration")]
        public string baseURL = "http://127.0.0.1:8000";
        
        [Header("Debug")]
        public bool enableLogging = true;

        // Get all drivers
        public IEnumerator GetDrivers(System.Action<DriversResponse> onSuccess, System.Action<string> onError)
        {
            string url = $"{baseURL}/drivers";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.SetRequestHeader("Content-Type", "application/json");
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        DriversResponse response = JsonConvert.DeserializeObject<DriversResponse>(request.downloadHandler.text);
                        onSuccess?.Invoke(response);
                        
                        if (enableLogging)
                            Debug.Log($"Successfully loaded {response.count} drivers");
                    }
                    catch (System.Exception e)
                    {
                        onError?.Invoke($"JSON parsing error: {e.Message}");
                    }
                }
                else
                {
                    onError?.Invoke($"API request failed: {request.error}");
                }
            }
        }

        // Simulate a race
        public IEnumerator SimulateRace(RaceSimulationRequest raceRequest, 
            System.Action<RaceSimulationResponse> onSuccess, System.Action<string> onError)
        {
            string url = $"{baseURL}/simulate/race";
            string jsonData = JsonConvert.SerializeObject(raceRequest);
            
            using (UnityWebRequest request = UnityWebRequest.Post(url, jsonData, "application/json"))
            {
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success)
                {
                    try
                    {
                        RaceSimulationResponse response = JsonConvert.DeserializeObject<RaceSimulationResponse>(request.downloadHandler.text);
                        onSuccess?.Invoke(response);
                        
                        if (enableLogging)
                            Debug.Log($"Race {response.race_id} simulation completed with {response.results.Length} results");
                    }
                    catch (System.Exception e)
                    {
                        onError?.Invoke($"JSON parsing error: {e.Message}");
                    }
                }
                else
                {
                    onError?.Invoke($"Simulation request failed: {request.error}");
                }
            }
        }

        // Health check
        public IEnumerator CheckAPIHealth(System.Action<bool> onComplete)
        {
            string url = $"{baseURL}/health";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url))
            {
                request.timeout = 5; // 5 second timeout
                
                yield return request.SendWebRequest();
                
                bool isHealthy = request.result == UnityWebRequest.Result.Success;
                onComplete?.Invoke(isHealthy);
                
                if (enableLogging)
                {
                    if (isHealthy)
                        Debug.Log("API health check: OK");
                    else
                        Debug.LogWarning($"API health check failed: {request.error}");
                }
            }
        }

        // Example usage method
        public void ExampleUsage()
        {
            // Get all drivers
            StartCoroutine(GetDrivers(
                onSuccess: (drivers) => {
                    Debug.Log($"Loaded {drivers.count} drivers");
                    foreach (var driver in drivers.drivers)
                    {
                        Debug.Log($"Driver: {driver.name} ({driver.nationality}) - Skill: {driver.skill:F2}");
                    }
                },
                onError: (error) => {
                    Debug.LogError($"Failed to load drivers: {error}");
                }
            ));

            // Simulate a race
            var raceRequest = new RaceSimulationRequest
            {
                race_id = 1,
                weather_conditions = "dry",
                participants = new Participant[]
                {
                    new Participant { driver_id = 1, team_id = 1 },
                    new Participant { driver_id = 2, team_id = 1 },
                    new Participant { driver_id = 3, team_id = 2 },
                    new Participant { driver_id = 4, team_id = 2 }
                }
            };

            StartCoroutine(SimulateRace(raceRequest,
                onSuccess: (result) => {
                    Debug.Log($"Race simulation completed!");
                    foreach (var raceResult in result.results)
                    {
                        Debug.Log($"Position {raceResult.position}: Driver {raceResult.driver_id} - {raceResult.points} points");
                    }
                },
                onError: (error) => {
                    Debug.LogError($"Race simulation failed: {error}");
                }
            ));
        }
    }
}

/*
Usage in Unity:

1. Add this script to a GameObject in your scene
2. Install Newtonsoft.Json via Package Manager (com.unity.nuget.newtonsoft-json)
3. Make sure your Python FastAPI server is running
4. Call methods via the API client:

    public class GameManager : MonoBehaviour
    {
        public MomentumAPIClient apiClient;
        
        void Start()
        {
            // Check if API is available
            StartCoroutine(apiClient.CheckAPIHealth(isHealthy => {
                if (isHealthy)
                {
                    Debug.Log("API connected successfully!");
                    apiClient.ExampleUsage();
                }
                else
                {
                    Debug.LogError("Cannot connect to Momentum API server!");
                }
            }));
        }
    }
*/