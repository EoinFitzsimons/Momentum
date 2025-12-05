National College of Ireland

BSc (Honours) in Computing Software Development

 Academic Year 2025/2026

Student Name: Eoin Fitzsimons

Student Number: X23151374

Student Email: [x23151374@student.ncirl.ie](mailto:x23151374@student.ncirl.ie)

Project Title: Momentum - Multi-Discipline Motorsport Simulation System

Technical Report

Contents

[1 **Contents** 2](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414935)

[2 **Executive Summary** 8](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414936)

[3 **Introduction** 8](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414937)

[3.1 **Background** 8](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414938)

[3.2 **Aims** 9](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414939)

[3.3 **Technology** 9](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414940)

[3.4 **Structure** 10](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414941)

[4 **Requirements** 11](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414942)

[4.1 **Functional Requirements** 11](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414943)

[4.1.1 **HIGH Priority (Must Have - Core Gameplay):** 11](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414944)

[4.1.2 **MEDIUM Priority (Career Mode Depth):** 11](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414945)

[4.1.3 **LOW Priority (Polish & Advanced Features):** 12](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414946)

[5 **Use Cases** 12](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414947)

[5.1 **UC-1: Read Driver Details** 12](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414948)

[5.1.1 **Scope** 12](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414949)

[5.1.2 **Description** 12](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414950)

[5.1.3 **Actors** 13](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414951)

[5.1.4 **Use Case Diagram** 13](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414952)

[5.1.5 **Flow Description** 13](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414953)

[5.2 **UC-2: Read Race Configuration** 13](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414954)

[5.2.1 **Scope** 13](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414955)

[5.2.2 **Description** 13](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414956)

[5.2.3 **Actors** 13](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414957)

[5.2.4 **Use Case Diagram** 14](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414958)

[5.2.5 **Flow Description** 14](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414959)

[5.3 **UC-3: Create Race Result** 14](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414960)

[5.3.1 **Scope** 14](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414961)

[5.3.2 **Description** 14](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414962)

[5.3.3 **Actors** 14](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414963)

[5.3.4 **Flow Description** 14](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414964)

[5.4 **UC-4: Read Race Results** 15](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414965)

[5.4.1 **Scope** 15](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414966)

[5.4.2 **Description** 15](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414967)

[5.4.3 **Actors** 15](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414968)

[5.4.4 **Use Case Diagram** 15](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414969)

[5.4.5 **Flow Description** 15](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414970)

[5.5 **UC-5: Read Championship Details** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414971)

[5.5.1 **Scope** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414972)

[5.5.2 **Description** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414973)

[5.5.3 **Actors** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414974)

[5.5.4 **Use Case Diagram** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414975)

[5.5.5 **Flow Description** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414976)

[5.6 **UC-6: Update Championship Standings** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414977)

[5.6.1 **Scope** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414978)

[5.6.2 **Description** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414979)

[5.6.3 **Actors** 16](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414980)

[5.6.4 **Use Case Diagram** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414981)

[5.6.5 **Flow Description** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414982)

[5.7 **UC-7: Create Race Event** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414983)

[5.7.1 **Scope** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414984)

[5.7.2 **Description** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414985)

[5.7.3 **Actors** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414986)

[5.7.4 **Use Case Diagram** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414987)

[5.7.5 **Flow Description** 17](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414988)

[5.8 **UC-8: Read Race Schedule** 18](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414989)

[5.8.1 **Scope** 18](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414990)

[5.8.2 **Description** 18](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414991)

[5.8.3 **Actors** 18](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414992)

[5.8.4 **Use Case Diagram** 18](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414993)

[5.8.5 **Flow Description** 18](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414994)

[5.9 **UC-9: Update Race Status** 19](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414995)

[5.9.1 **Scope** 19](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414996)

[5.9.2 **Description** 19](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414997)

[5.9.3 **Actors** 19](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414998)

[5.9.4 **Use Case Diagram** 19](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215414999)

[5.9.5 **Flow Description** 19](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415000)

[5.10 **UC-10: Create Championship** 20](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415001)

[5.10.1 **Scope** 20](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415002)

[5.10.2 **Description** 20](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415003)

[5.10.3 **Actors** 20](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415004)

[5.10.4 **Use Case Diagram** 20](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415005)

[5.10.5 **Flow Description** 20](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415006)

[5.11 **UC-11: Read Team Details** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415007)

[5.11.1 **Scope** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415008)

[5.11.2 **Description** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415009)

[5.11.3 **Actors** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415010)

[5.11.4 **Use Case Diagram** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415011)

[5.11.5 **Flow Description** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415012)

[5.12 **UC-12: Create New Team** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415013)

[5.12.1 **Scope** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415014)

[5.12.2 **Description** 21](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415015)

[5.12.3 **Actors** 22](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415016)

[5.12.4 **Use Case Diagram** 22](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415017)

[5.12.5 **Flow Description** 22](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415018)

[5.13 **UC-13: Read Team Details (player team)** 22](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415019)

[5.13.1 **Scope** 22](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415020)

[5.13.2 **Description** 22](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415021)

[5.13.3 **Actors** 22](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415022)

[5.13.4 **Use Case Diagram** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415023)

[5.13.5 **Flow Description** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415024)

[5.14 **UC-14: Update Team Attributes** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415025)

[5.14.1 **Scope** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415026)

[5.14.2 **Description** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415027)

[5.14.3 **Actors** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415028)

[5.14.4 **Use Case Diagram** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415029)

[5.14.5 **Flow Description** 23](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415030)

[5.15 **UC-15: Read Available Drivers** 24](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415031)

[5.15.1 **Scope** 24](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415032)

[5.15.2 **Description** 24](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415033)

[5.15.3 **Actors** 24](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415034)

[5.15.4 **Use Case Diagram** 24](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415035)

[5.15.5 **Flow Description** 24](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415036)

[5.16 **UC-16: Update Driver Contract** 25](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415037)

[5.16.1 **Scope** 25](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415038)

[5.16.2 **Description** 25](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415039)

[5.16.3 **Actors** 25](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415040)

[5.16.4 **Use Case Diagram** 25](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415041)

[5.16.5 **Flow Description** 25](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415042)

[5.17 **UC-17: Read Available Staff** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415043)

[5.17.1 **Scope** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415044)

[5.17.2 **Description** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415045)

[5.17.3 **Actors** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415046)

[5.17.4 **Use Case Diagram** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415047)

[5.17.5 **Flow Description** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415048)

[5.18 **UC-18: Update Staff Contract** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415049)

[5.18.1 **Scope** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415050)

[5.18.2 **Description** 26](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415051)

[5.18.3 **Actors** 27](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415052)

[5.18.4 **Use Case Diagram** 27](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415053)

[5.18.5 **Flow Description** 27](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415054)

[5.19 **UC-19: Update Driver Skills/Age** 27](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415055)

[5.19.1 **Scope** 27](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415056)

[5.19.2 **Description** 27](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415057)

[5.19.3 **Actors** 27](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415058)

[5.19.4 **Use Case Diagram** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415059)

[5.19.5 **Flow Description** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415060)

[5.20 **UC-20: Update Team Budget** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415061)

[5.20.1 **Scope** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415062)

[5.20.2 **Description** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415063)

[5.20.3 **Actors** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415064)

[5.20.4 **Use Case Diagram** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415065)

[5.20.5 **Flow Description** 28](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415066)

[5.21 **UC-21: Create New Driver** 29](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415067)

[5.21.1 **Scope** 29](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415068)

[5.21.2 **Description** 29](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415069)

[5.21.3 **Actors** 29](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415070)

[5.21.4 **Use Case Diagram** 29](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415071)

[5.21.5 **Flow Description** 29](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415072)

[5.22 **UC-22: Create New Staff Member (staff generation)** 30](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415073)

[5.22.1 **Scope** 30](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415074)

[5.22.2 **Description** 30](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415075)

[5.22.3 **Actors** 30](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415076)

[5.22.4 **Use Case Diagram** 30](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415077)

[5.22.5 **Flow Description** 30](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415078)

[5.23 **UC-23: Delete Championship** 31](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415079)

[5.23.1 **Scope** 31](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415080)

[5.23.2 **Description** 31](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415081)

[5.23.3 **Actors** 31](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415082)

[5.23.4 **Use Case Diagram** 31](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415083)

[5.23.5 **Flow Description** 31](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415084)

[5.24 **UC-24: Create Custom Track** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415085)

[5.24.1 **Scope** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415086)

[5.24.2 **Description** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415087)

[5.24.3 **Actors** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415088)

[5.24.4 **Use Case Diagram** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415089)

[5.24.5 **Flow Description** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415090)

[5.25 **UC-25: Update Track Characteristics** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415091)

[5.25.1 **Scope** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415092)

[5.25.2 **Description** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415093)

[5.25.3 **Actors** 32](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415094)

[5.25.4 **Use Case Diagram** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415095)

[5.25.5 **Flow Description** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415096)

[5.26 **UC-26: Delete Track** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415097)

[5.26.1 **Scope** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415098)

[5.26.2 **Description** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415099)

[5.26.3 **Actors** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415100)

[5.26.4 **Use Case Diagram** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415101)

[5.26.5 **Flow Description** 33](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415102)

[5.27 **UC-27: Read Staff Performance Modifiers** 34](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415103)

[5.27.1 **Scope** 34](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415104)

[5.27.2 **Description** 34](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415105)

[5.27.3 **Actors** 34](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415106)

[5.27.4 **Use Case Diagram** 34](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415107)

[5.27.5 **Flow Description** 34](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415108)

[5.28 **UC-28: Update Driver Appearance** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415109)

[5.28.1 **Scope** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415110)

[5.28.2 **Description** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415111)

[5.28.3 **Actors** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415112)

[5.28.4 **Use Case Diagram** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415113)

[5.28.5 **Flow Description** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415114)

[5.29 **UC-29: Update Team Branding** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415115)

[5.29.1 **Scope** 35](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415116)

[5.29.2 **Description** 36](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415117)

[5.29.3 **Actors** 36](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415118)

[5.29.4 **Use Case Diagram** 36](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415119)

[5.29.5 **Flow Description** 36](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415120)

[6 **Data Requirements** 36](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415121)

[6.1 **User Requirements** 37](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415122)

[6.2 **Environmental Requirements** 38](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415123)

[6.3 **Usability Requirements** 39](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415124)

[7 **Design & Architecture** 39](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415125)

[7.1 **System Architecture Overview** 39](https://file+.vscode-resource.vscode-cdn.net/c%3A/Users/eoin0/.vscode/extensions/cweijan.vscode-office-3.5.4/out/webview/#_Toc215415126)

Executive Summary

Momentum is a comprehensive multi-discipline motorsport management simulation system developed as a final year Computer Science project. The system implements seven complete racing disciplines (Single Seater, Production/Touring, Rally/Stage, Urban/Street, Drag/Acceleration, Sprint/Rallycross, and Endurance) with realistic simulation mechanics implemented via an agent-based approach.

The project addresses the challenge of creating an engaging and realistic motorsport management game that balances complexity with accessibility. Unlike existing motorsport games that focus on a single discipline, Momentum provides a unified platform supporting multiple racing categories with cross-discipline driver and team management.

Key achievements include:

50+ driver attributes across 7 categories with dynamic career progression

40+ staff attributes across 25+ roles with budget-based team scaling

Multi-currency financial system with real-time exchange rates supporting EUR, USD, GBP, JPY, and CHF

Seven complete racing engines each with discipline-specific simulation logic

Agent-based simulation engine generating realistic, watchable race outcomes.

AI decision-making framework for realistic team and driver behaviours.

RESTful API architecture enabling frontend integration and scalability.

The system successfully demonstrates advanced software engineering principles including object-oriented design, database normalisation, API development, and statistical simulation. Performance testing shows sub-second race simulation times with realistic result distributions. The modular architecture enables easy expansion to additional disciplines or gameplay features.

Introduction

Background

Motorsport management simulation games have been a niche but dedicated gaming genre since the 1990s. However, most existing games focus on a single discipline (usually Formula 1) or lack the depth required for authentic simulation. Games like FootballManager have shown that deep statistical simulation can create compelling gameplay, but motorsport has remained underserved.

This project was undertaken to create a modern, multi-discipline motorsport simulation that:

Supports multiple racing disciplines rather than forcing players into a single category

Uses realistic statistical modelling based on motorsport data and driver attributes

Implements comprehensive team management including staff, budgets, and development

Provides an API-first architecture enabling multiple frontend implementations (Unity, Web, Mobile)

Demonstrates advanced computer science concepts including agent-based simulation, AI decision-making, and distributed architecture

The motivation stemmed from both personal interest in motorsport and the technical challenge of building a complex simulation system that balances realism with performance.

Aims

The primary objectives of the Momentum project are:

Technical Objectives:

Design and implement a multi-discipline racing simulation engine using an agent-based approach

Create a comprehensive data model supporting 50+ driver attributes and 40+ staff attributes

Develop seven discipline-specific racing engines with unique simulation characteristics

Implement a RESTful API for frontend integration and external system access

Build a multi-currency financial system with real-time exchange rate support

Create an AI decision-making framework for autonomous team and driver behaviours

Simulation Quality Objectives:

Generate statistically realistic race results with appropriate variance and upset potential

Model cross-discipline driver compatibility reflecting real-world skill transferability

Implement budget-based team scaling affecting performance and information access

Create fog-of-war information systems where data quality depends on staff capabilities

Software Engineering Objectives:

Apply object-oriented design patterns for maintainable and extensible code

Implement database normalisation for data integrity and performance

Create comprehensive unit and integration tests ensuring system reliability

Document code with clear API specifications and usage examples

Technology

The Momentum system is built using the following technology stack:

Backend (Python 3.8+):

FastAPI: Modern, high-performance web framework for building RESTful APIs

Automatic OpenAPI documentation generation

Asynchronous request handling for scalability

Built-in data validation using Pydantic models

SQLite: Embedded relational database for persistent storage

Zero-configuration deployment

ACID compliance for data integrity

Foreign key constraints for referential integrity

NumPy & SciPy: Scientific computing libraries for statistical simulation

stochastic sampling

Statistical distribution calculations

Performance optimisation for numerical operations

PyTorch: Machine learning framework for AI decision-making

Neural network models for strategy prediction

Gradient-based optimisation

Future expansion for deep learning features

Data Generation:

Faker Library: Generates culturally appropriate names with locale support

Custom name generation system with ethnic/regional distributions

Multi-currency exchange rate APIs for real-time financial data

Development Tools:

Git/GitHub: Version control and collaboration

VS Code: Primary development environment

Uvicorn: ASGI server for running FastAPI applications

Python-dotenv: Environment variable management for API keys

Architecture Approach: The system follows a layered architecture pattern:

API Layer: FastAPI endpoints handling HTTP requests/responses

Business Logic Layer: Simulation engines, AI systems, and management modules

Data Access Layer: Database models and repository patterns

Data Layer: SQLite database with normalised schema

This separation enables:

Independent testing of each layer

Easy replacement of components (e.g., switching databases)

Clear separation of concerns

Scalability through horizontal scaling of API servers

Structure

This technical report is organized as follows:

Section 2 - System: Provides comprehensive documentation of the system including requirements analysis, design decisions, implementation details, and testing procedures. This section is divided into:

Requirements (2.1): Functional, data, user, environmental, and usability requirements

Design & Architecture (2.2): System architecture, component design, and algorithm descriptions

Implementation (2.3): Key code modules, algorithms, and implementation challenges

Testing (2.4): Test strategy, test cases, and validation results

Evaluation (2.5): Performance analysis, user feedback, and system assessment

Section 3 - Conclusions: Summarizes the project outcomes, identifies strengths and limitations, and reflects on lessons learned.

Section 4 - Further Development: Outlines potential future enhancements and research directions.

Section 5 - References: Lists all academic papers, technical documentation, and resources used.

Section 6 - Appendices: Contains supplementary materials including project proposal, reflective journals, code samples, and test data.

Requirements

Functional Requirements

The following functional requirements are listed in priority order:

HIGH Priority (Must Have - Core Gameplay):

UC-1: Read Driver Details

UC-2: Read Race Configuration

UC-3: Create Race Result

MEDIUM Priority (Career Mode Depth):

UC-4: Read Race Results

UC-5: Read Championship Details

UC-6: Update Championship Standings

UC-7: Create Race Event

UC-8: Read Race Schedule

UC-9: Update Race Status

UC-12: Create Championship

UC-11: Read Team Details

UC-12: Create New Team

UC-13: Read Team Details (team screen)

UC-14: Update Team Attributes

UC-15: Read Available Drivers

UC-16: Update Driver Contract

UC-17: Read Available Staff

UC-18: Update Staff Contract

UC-19: Update Driver Skills/Age (includes recycling retired drivers)

UC-20: Update Team Budget

LOW Priority (Polish & Advanced Features):

UC-21: Create New Driver (not needed - recycle existing 1,781 drivers)

UC-22: Create New Staff Member (not needed - recycle existing 57,936 staff)

UC-23: Delete Championship

UC-24: Create Custom Track

UC-25: Update Track Characteristics

UC-26: Delete Track

UC-27: Read Staff Performance Modifiers

UC-28: Update Driver Appearance

UC-29: Update Team Branding

Use Cases

UC-1: Read Driver Details

Scope

Retrieve a complete driver profile with 50+ attributes across 7 categories (technical, mental, physical, racecraft, personality, discipline preferences) from the SQLite database for race simulation initialisation.

Description

The GUI or Simulation Service queries the database manager to retrieve a driver record containing all racing attributes, team assignment, and current status. The system returns the full driver object which is used to initialise the AI agent for real-time race simulation.

Actors

GUI - requests driver data for race setup screens and displays.

Simulation Service - requests driver profiles for real-time race engine initialisation.

Database Manager - executes SQL queries against the SQLite database and returns driver objects.

Use Case Diagram

The system has loaded the database; driver records exist with complete attribute sets.

Flow Description

Activation

This use case starts when the GUI loads the race setup screen or when the Simulation Service initialises a race session.

Main flow

The GUI or Simulation Service calls DatabaseManager.get_all_drivers() or get_driver(driver_id).

The Database Manager executes a SELECT query against the drivers table.

The system validates that driver records contain all required attributes (0-100 scale for skills).

The system returns Driver objects with full attribute payloads.

For race simulation, each driver is instantiated as an AI agent with decision-making capabilities.

Alternate flow

A1: Requested driverId does not exist - return None and GUI displays error message. A2: Database file not found - GUI displays connection error and prompts database regeneration.

Exceptional flow

E1: Database read failure or corruption - GUI catches exception, logs to logs/ directory, and displays user-friendly error with regeneration option. E2: Missing or invalid attributes - Database Manager logs warning and uses default values (50.0) for missing skills.

Termination

Client receives driver objects and proceeds with race initialisation or display rendering.

Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/45b13661-c338-4bc6-b69e-6eb8afada540)

UC-2: Read Race Configuration

Scope

Retrieve track information (175 circuits with IMA grading, surface types, characteristics) and race parameters from the SQLite database to configure the real-time race simulation engine.

Description

The GUI and Simulation Service query track records containing length, surface type, corners, and IMA characteristics. The system loads this data to initialise the track map with 100 evenly-spaced checkpoints, corner types (slow/medium/fast), and DRS zones for the physics engine.

Actors

GUI - requests track data for race setup and displays circuit information.

Simulation Service - loads track configuration to initialise the TrackMap and physics calculations.

Database Manager - queries the tracks table and returns Track objects.

Flow Description

Precondition

Database contains 175 circuit definitions imported from data/circuits_database.json.

Activation

Starts when the GUI loads the race setup screen and requests available tracks, or when the Simulation Service begins a race session.

Main flow

GUI calls DatabaseManager.get_all_tracks() or get_track(track_id).

Database Manager executes SELECT query against the tracks table.

System returns Track objects containing name, length (km), country, surface type, and IMA grading.

For simulation, the engine generates a TrackMap with corner sections and racing physics parameters.

The circuit is rendered in the GUI with 100 checkpoint markers at 1% intervals.

Alternate flow

A1: Invalid track_id requested - return None and GUI displays error or fallback message. A2: No tracks available in database - GUI prompts user to run scripts/import_circuits.py to populate track data.

Exceptional flow

E1: Database read error - GUI logs exception to logs/database_generation.log and displays connection error. E2: Missing track characteristics - System uses default values (medium corners, standard grip) and logs warning.

Termination

Caller receives track configuration and proceeds to simulation or display rendering.

Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/cb004c7e-2992-4fbc-ac11-53afd63a200a)

UC-3: Create Race Result

Scope

Persist race outcomes (positions, times, incidents) and trigger standings updates.

Description

Accept a race result payload from the Simulation Service or operator, validate it, persist the results atomically, and enqueue standings recalculation.

Actors

Simulation Service - submits generated race results.

Standings Service - recalculates standings from persisted results.

Flow Description

Precondition

Race event exists and is writable.

Activation

Starts when the simulation finishes or an operator submits results.

Main flow

The Simulation Service submits the result payload.

The system validates the payload and event state, stores race_results in a transaction, and marks the event complete.

The system enqueues a standings recalculation job and returns acknowledgement.

Alternate flow

A1: Validation failure - return 400 with field-level errors. A2: Event already finalised - return 409 Conflict and provide adjustment options.

Exceptional flow

E1: Database write failure - return 500 and include diagnostic id.

Termination

Event status updated; standings update job queued.

Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/be6223d5-0ef3-4ddb-839e-69ea3a38bf61)

UC-4: Read Race Results

Scope

Retrieve historical race results from the database for display in the GUI, including final classification, lap times, and DNF information.

Description

The system queries completed race records to display historical results. Results include finishing positions, lap times, DNF reasons, and incident details for analysis and comparison.

Actors

GUI - requests and displays historical race results.

Database Manager - queries the race_results table and joins with driver/team data.

Flow Description

Precondition

Race results have been persisted to the database from previous simulations.

Activation

Starts when user navigates to race history screen or requests results for a specific event.

Main flow

GUI calls DatabaseManager.get_race_results(race_id) or get_championship_results(championship_id).

Database Manager executes SELECT query joining race_results, drivers, and teams tables.

System returns ordered list of results with driver names, positions, times, and DNF reasons.

GUI displays results in standings table format.

Alternate flow

A1: No results found for requested race - GUI displays "No results available" message. A2: Partial results due to incomplete race - GUI displays available data and marks as "Race Incomplete".

Exceptional flow

E1: Database read failure - GUI logs error and displays cached results if available from previous session. E2: Corrupt result data - System logs validation errors and displays partial data with warning.

Termination

GUI displays historical results and awaits user navigation.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/7f185133-6acc-4a55-82c5-9852b8a933f1)

UC-5: Read Championship Details

Scope

Retrieve championship information including season parameters, calendar of events, current standings, and points allocations across 7 racing disciplines.

Description

The system maintains championship records tracking season-long competitions. Each championship contains a calendar of races, points standings, and discipline-specific rules for the simulation.

Actors

GUI - displays championship standings, calendar, and season progress.

Game Loop - manages season progression and championship state (planned feature).

Database Manager - queries championship, standings, and calendar data.

Flow Description

Precondition

Championship has been created with discipline, season year, and initial calendar.

Activation

Starts when user navigates to championship screen or game loop initialises a season.

Main flow

GUI or Game Loop requests championship data via DatabaseManager.get_championship(championship_id).

System retrieves championship metadata (discipline, year, points system).

System queries calendar entries and aggregates standings from race results.

GUI displays championship overview with standings table and upcoming races.

Alternate flow

A1: Championship has no races yet - display empty calendar with option to schedule events. A2: Standings unavailable - calculate standings from existing race results or display zero points.

Exceptional flow

E1: Database query failure - GUI displays error and offers retry or cached data. E2: Invalid championship structure - System logs diagnostic and prompts database verification.

Termination

GUI displays championship view with standings and calendar; system awaits user interaction.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/457840f5-ecda-485e-88a3-d384cde1a308)

UC-6: Update Championship Standings

Scope

Recalculate and persist championship standings after results are recorded.

Description

Actors

Standings Service - triggers recalculation and consumes updated standings.

Admin - may invoke recalculation manually.

Flow Description

Precondition

Championship and results exist.

Activation

Starts when results are created or adjusted.

Main flow

Gather results for the championship.

Apply points system and compute standings.

Persist updated standings and notify consumers.

Alternate flow

A1: Partial update requested - return 202 Accepted with job id for async completion. A2: Concurrent updates - return 409 Conflict with current version.

Exceptional flow

E1: Points rules missing - return 500 and log for admin attention. E2: Persistence error - roll back and queue retry.

Termination

Standings persisted.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/8470d71c-8b8a-4883-a0de-21564aafda31)

UC-7: Create Race Event

Scope

Add a race event to a championship calendar (track, date, configuration).

Description

An admin or scheduler submits an event; the backend validates and persists the event record.

Actors

Admin - creates and manages race events.

Scheduler - schedules events programmatically.

Flow Description

Precondition

Championship exists and is editable.

Activation

Starts when an admin posts new event details.

Main flow

Validate dates and track availability.

Insert event record into races.

Return created resource.

Alternate flow

A1: Date/track conflict - return 409 Conflict with conflicts and alternatives. A2: Validation warning - return 200 with warnings and allow override.

Exceptional flow

E1: Database write failure - return 500 and persist request to retry queue. E2: External sync failure - create event in draft and return 202 Accepted with sync pending.

Termination

Calendar updated; notifications may be sent.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/44c0bccb-9ee5-458f-959e-0c9a72c489f9)

UC-8: Read Race Schedule

Scope

Retrieve championship calendar/schedule for UI display.

Description

Return ordered list of events with dates, tracks and statuses.

Actors

User / UI - requests the schedule for display.

Calendar Service - synchronises events externally when configured.

Flow Description

Precondition

Championship or season exists.

Activation

Starts when client opens the calendar screen.

Main flow

Validate championship/season.

Retrieve ordered events and metadata.

Return schedule to caller.

Alternate flow

A1: Championship not found - return 404 Not Found with guidance to create a championship first. A2: Championship exists but has no events - return empty schedule with a message suggesting adding events.

Exceptional flow

E1: Database read error - return 503 Service Unavailable with diagnostic id; offer cached schedule if available. E2: Permission or tenancy error - return 403.

Termination

Client displays schedule.

Post condition

System awaits next request.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/fce2606a-fdea-43df-b240-94b213867218)

UC-9: Update Race Status

Scope

Change a race event status (scheduled → in-progress → completed → cancelled).

Description

Update event lifecycle state and notify dependent systems.

Actors

Simulation/Service - updates status during simulation.

Admin - may manually change status.

Notification Service - receives lifecycle events.

Flow Description

Precondition

Event exists and caller has permission.

Activation

Starts when a service or admin posts a status update.

Main flow

Validate transition is allowed.

Update races.status accordingly.

Emit notifications/events.

Alternate flow

A1: Invalid lifecycle transition (e.g., completed → scheduled) - return 400 Bad Request with allowed transitions and current state. A2: Caller requests cancellation during in-progress - return 202 Accepted and initiate graceful abort procedures (safety checks, rollback attempts).

Exceptional flow

E1: Database write error or optimistic lock fail - return 500 and include current event state; schedule a background reconciliation job. E2: Notification subsystem failure - update status but record notification failure for later retry; return 200 with notificationsPending: true.

Termination

Event status updated and notifications sent.

Post condition

System awaits next lifecycle event.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/df66e449-eb6c-4464-bdfa-72217501a0c4)

UC-10: Create Championship

Scope

Create a new championship/season automatically on season rollover, with base rules and an empty calendar.

Description

On season rollover the Game Loop computes the next season parameters, instantiates a championship record with a ruleset and calendar placeholder, persists it, and notifies downstream systems (scheduling, AI, UI) that a new season is available.

Actors

Game Loop / Scheduler - triggers automatic season rollover and championship creation.

Policy Service - validates or supplies rulesets.

Event Scheduler - consumes the new championship to populate events.

Flow Description

Precondition

End-of-season tick reached; ruleset templates and calendar seeding configuration are available.

Activation

Triggered automatically by the Game Loop on season rollover (no manual admin intervention required).

Main flow

Game Loop determines season rollover has occurred and computes seed parameters (year, discipline, ruleset template).

System requests/validates the ruleset from Policy Service.

System creates the championship record with initial metadata and an empty calendar.

System persists the championship atomically and emits events to Event Scheduler, AI and UI.

Alternate flow

A1: Ruleset validation fails - select fallback template and continue, or mark championship as requiresReview and emit admin notification.

Exceptional flow

E1: Database write failure - rollback and schedule a retry; emit diagnostic id to monitoring and place a recovery job in the maintenance queue.

Termination

Championship record created and downstream systems notified.

Post condition

Event Scheduler and AI begin populating events and participants for the new season.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/c1624be7-67eb-41cc-8e12-5b7554ba680a)

UC-11: Read Team Details

Scope

Retrieve complete team profile including budget (€130M cap for top-tier Single Seater), tier classification, headquarters, discipline specialisation, and assigned drivers.

Description

The system maintains 1,095 team records across 7 racing disciplines. Each team has budget constraints, tier classification (tier1/tier2/tier3), and performance multipliers that affect simulation outcomes.

Actors

GUI - displays team information on management screens.

Simulation Service - requests team data to calculate performance multipliers for race simulation.

Database Manager - queries the teams table and joins with driver assignments.

Flow Description

Precondition

Team records exist in database with complete attribute sets.

Activation

Starts when GUI loads team management screen or simulation engine initialises a race.

Main flow

GUI or Simulation Service calls DatabaseManager.get_team(team_id) or get_teams_by_discipline(discipline).

Database Manager executes SELECT query against teams table.

System retrieves team metadata including budget, tier, headquarters, and discipline.

For simulation, engine calculates team performance multiplier (0.55 to 0.95) based on tier and budget.

GUI displays team profile or simulation applies multipliers to driver performance.

Alternate flow

A1: Invalid team_id - return None and GUI displays "Team not found" error. A2: Team has no assigned drivers - display team info with empty roster.

Exceptional flow

E1: Database read failure - GUI logs error to logs/ and displays connection error with retry option. E2: Missing team attributes - System uses default values (tier2, €100M budget) and logs warning.

Termination

GUI displays team screen or simulation proceeds with team performance calculations.

Post condition

System awaits next team query or user action.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/9702954c-f9a1-4e32-ac44-7aa3bc3daaae)

UC-12: Create New Team

Scope

Create a new team record (initial roster, budget, HQ).

Description

Player or admin creates a team; the system allocates starting assets or placeholders.

Actors

Player/Admin - initiates team creation.

Provisioning Service - reserves starting resources.

Flow Description

Precondition

Requester authorised; required seed data available.

Activation

Starts when player/admin submits team creation.

Main flow

Validate request and reserve resources.

Insert team record and assign initial roster/placeholders.

Return created team.

Alternate flow

A1: Resource conflict (e.g., team name or HQ occupied) - return 409 Conflict with suggested alternatives and actions to resolve. A2: Missing seed data - return 422 Unprocessable Entity with details on required fields.

Exceptional flow

E1: Database transaction failure - return 500 and log the full request for replay. E2: External provisioning failure (e.g., storage) - create the team in pending state and notify admin.

Termination

Team visible in lists.

Post condition

System awaits next management action.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/42974461-0605-4fda-9710-9a0083d953d2)

UC-13: Read Team Details (player team)

Scope

Return player's own team with editable flags and affordances.

Description

Provide editable team data for the player's management screen.

Actors

Player - owner of the team and primary editor.

Auth Service - validates ownership and permissions.

Flow Description

Precondition

Player has a team.

Activation

Starts when player opens their team management screen.

Main flow

Validate player's identity and team ownership.

Return team data with editable flags.

Alternate flow

A1: Player has no team - return 404 Not Found with guidance to create or join a team and links to relevant endpoints.

Exceptional flow

E1: Database read error - return 503 Service Unavailable and include a diagnostic id. E2: Authorization check failure - return 403.

Termination

Player views editable team screen.

Post condition

System awaits further edits.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/eed368ee-b97b-4103-85f0-05b6f95dda9f)

UC-14: Update Team Attributes

Scope

Modify team attributes (budget allocation, HQ upgrades, staff assignments).

Description

Player or admin updates team settings which are validated and persisted.

Actors

Player/Admin - submits updates.

Finance Service - validates budget changes.

Flow Description

Precondition

Requester authorised and has sufficient resources.

Activation

Starts when client submits team updates.

Main flow

Validate changes and budget.

Persist updates.

Return updated resource.

Alternate flow

A1: Insufficient funds detected - return 422 Unprocessable Entity with required amount and suggestions (sponsor, loan, reduce spend). A2: Concurrent update to budget - return 409 Conflict with current balance and retry instructions.

Exceptional flow

E1: Database write/commit failure - return 500 and enqueue the update for manual reconciliation. E2: Audit/logging service failure - persist the change but flag audit missing; return 200 with auditPending: true.

Termination

Changes reflected on subsequent reads.

Post condition

System awaits next request.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/e30d1445-3b39-4486-b437-2bf58ba0df61)

UC-15: Read Available Drivers

Scope

Return list of uncontracted or transfer-available drivers for recruitment.

Description

Provide filtered and paginated driver pool for the market UI.

Actors

Player - browses and filters available drivers.

Team AI - automated consumer of driver listings.

Flow Description

Precondition

Driver pool exists.

Activation

Starts when user opens driver market.

Main flow

Apply filters/pagination.

Return driver list with availability flags.

Alternate flow

A1: Filter parameters return no matches - return 200 OK with empty list and suggestions to relax filters. A2: Partial data due to pagination limits - include hasMore: true and next-page token.

Exceptional flow

E1: Database query failure - return 503 Service Unavailable with diagnostic id; if cached pool exists return cached results marked stale: true. E2: Indexing/search service failure - fall back to simple DB query and note reduced fidelity.

Termination

Client displays candidate drivers.

Post condition

System awaits next query.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/900b80e8-3972-454e-9d81-bdedf5b27583)

UC-16: Update Driver Contract

Scope

Sign, renew or terminate driver contracts and update team roster and budget.

Description

Persist contract terms and adjust availability and team budgets.

Actors

Team Manager - negotiates and confirms driver contracts.

Admin - enforces or modifies contract rules when required.

Flow Description

Precondition

Driver and team exist; negotiation outcome determined.

Activation

Starts when contract terms are finalised and submitted.

Main flow

Validate budget and contract rules.

Persist contract and update roster/budget.

Return confirmation.

Alternate flow

A1: Budget shortfall during contract update - return 422 with required funding and options (defer, partial contract, renegotiate). A2: Contract already signed by another party - return 409 Conflict with current contract details.

Exceptional flow

E1: Database write error - rollback, return 500 and include reference id for support. E2: Payment gateway or external finance service failure - abort contract update, return 502 Bad Gateway and queue retry.

Termination

Driver assigned and availability updated.

Post condition

System awaits next contract action.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/e85e995e-2e5d-4b2f-8211-62f0f2f2ec98)

UC-17: Read Available Staff

Scope

Return list of available staff for hiring with roles and modifiers.

Description

Provide paginated staff pool for recruitment screens.

Actors

Player - requests staff listings.

HR Service - provides staff filters and pools.

Flow Description

Precondition

Staff pool exists.

Activation

Starts when player opens staff hiring screen.

Main flow

Apply filters and paginate.

Return staff list with core stats and cost.

Alternate flow

A1: No staff matching filters - return 200 OK with empty list and filter suggestions. A2: Partial availability (some staff on contract) - return available subset with availability: limited flag.

Exceptional flow

E1: Database or search index failure - return 503 Service Unavailable and provide cached results if available. E2: Data corruption in staff records detected - return 500 and set a maintenance flag.

Termination

Client displays staff candidates.

Post condition

System awaits next request.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/13376327-11d5-4d34-baaa-ce42d071c8fc)

UC-18: Update Staff Contract

Scope

Hire, fire or renegotiate staff contracts and persist changes to team resources.

Description

Assign staff to teams, record salary and update budgets.

Actors

Player - initiates hiring/renegotiation.

Team Manager - manages staff assignments.

Flow Description

Precondition

Staff profile exists and is available.

Activation

Starts when hiring/renegotiation action is confirmed.

Main flow

Validate terms and budget.

Persist contract and update team state.

Return confirmation.

Alternate flow

A1: Insufficient funds - return 422 Unprocessable Entity with required funding detail and rollback any provisional assignments. A2: Candidate no longer available at confirmation - return 409 Conflict and provide alternatives.

Exceptional flow

E1: Database write failure - rollback and return 500 with support reference. E2: Concurrent contract update detected - return 409 with current contract state and instructions to retry.

Termination

Staff assigned and salary deducted from budget.

Post condition

System awaits further HR actions.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/502bfbfa-4a69-4fcd-8df6-00ab91f3e9c7)

UC-19: Update Driver Skills/Age

Scope

Periodic update of driver attributes (ageing, progression/regression) and handle retirements/recycling.

Description

Perform end-of-season or scheduled updates to driver skills and ages; mark retirees and optionally regenerate/recycle entities.

Actors

Scheduler (Game Loop) - triggers seasonal maintenance jobs.

Admin - may invoke manual progression runs.

Flow Description

Precondition

Driver population present.

Activation

Starts at season end or scheduled tick.

Main flow

System iterates drivers and adjusts skills and ages.

Flag retired drivers and recycle or replace per policy.

Persist updates.

Alternate flow

A1: Emergency update due to injury or incident - apply immediate decrement to affected driver(s), mark as underReview, and notify teams. A2: Player-triggered training boost - apply progression rules and mark a cooldown period.

Exceptional flow

E1: Batch update failure during season tick - return 500, log affected driver ids and schedule a retry job. E2: Constraint violation (e.g., negative attribute) - abort update for affected records and flag for manual review.

Termination

Driver records updated for next season.

Post condition

System awaits next scheduled update.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/bc050843-d1bd-43a2-a260-ddcc67642b69)

UC-20: Update Team Budget

Scope

Adjust team budget for income/expenses, sponsor payouts and race fees.

Description

Apply transactions affecting a team's budget and persist them.

Actors

Finance System - posts transactions affecting team budgets.

Game Loop - triggers periodic income/expense events.

Flow Description

Precondition

Team exists.

Activation

Starts when a transaction affecting budget occurs.

Main flow

Validate transaction and atomicity.

Update team budget.

Return updated balance.

Alternate flow

A1: Insufficient funds for debit - reject the transaction with 402 Payment Required (or 422) and suggest corrective actions (sponsor, loan, adjust expenses). A2: Pending transactions that affect available balance - return 409 Conflict with pending transaction list.

Exceptional flow

E1: Database write failure - return 500 and enqueue transaction for replay.

Termination

Team budget updated and awaiting next transaction.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/276a0200-49d8-42ce-a2f4-08115facef14)

UC-21: Create New Driver

Scope

Add a driver to the hireable pool by recycling an existing placeholder or generating a new driver profile when pool thresholds require expansion.

Description

Maintain and expand the hireable driver pool to support roster growth, replacement of retired drivers, and content variety. The system prefers recycling deactivated driver records when suitable; otherwise the Generator Service creates a new driver profile validated against uniqueness and configured policy constraints.

Actors

Admin - requests manual creation.

System - scheduled or policy-driven generator.

Generator Service - produces seeded attribute payloads for new drivers.

Flow Description

Precondition

Driver pool is below configured threshold or an explicit admin request to create a driver is received; seeding and generation configuration are available.

Activation

Triggered by POST /api/drivers/generate from an admin or by an automated roster expansion job.

Main flow

Validate request and policy constraints (pool thresholds, allowed classes).

Attempt to select a recycle candidate from the deactivated pool; if none available, call Generator Service to create attributes.

Validate generated attributes (unique name, valid age, discipline suitability).

Persist the driver record inside a transaction and mark availability.

Return 201 Created with the driver resource.

Alternate flow

A1: Recycle candidate unavailable - generate new attributes and continue. A2: Minor validation warnings - persist with a warnings field and return 201 Created. A3: Name or identity conflict - mutate the attribute (rename) and retry up to configured attempts; on exhaustion return 409 Conflict with guidance.

Exceptional flow

E1: Database write failure - rollback and return 500 with diagnostic id for support. E2: Generator Service unavailable - return 503 Service Unavailable and schedule a retry job. E3: Policy or configuration violation - return 422 Unprocessable Entity with policy details.

Termination

Driver record created and visible in the hireable pool.

Post condition

Driver returned in subsequent listing endpoints and system awaits next generation task.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/be1a48a3-3266-4b00-b9d9-684b6a65c9d8)

UC-22: Create New Staff Member (staff generation)

Scope

Generate new staff when required (optional).

Description

Create or recycle staff records for hireable pool expansion.

Actors

Admin/System - triggers staff generation or pool maintenance.

Flow Description

Precondition

Staff pool needs expansion.

Activation

Triggered by admin or scheduled regeneration.

Main flow

Generate staff attributes and persist.

Return created staff record.

Alternate flow

A1: Attribute conflict or duplicate identity - alter generated attributes (name, hometown) and retry generation automatically. A2: Pool constraints prevent generation - return 422 with explanation (e.g., max drivers reached).

Exceptional flow

E1: Database write failure - return 500 and record the attempted generation for retry. E2: Resource exhaustion (temp files, quota) - return 503 and back off generation.

Termination

Staff visible in hiring pool.

Post condition

System awaits next generation.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/d636222d-6123-4448-b31a-06d880cc70c6)

UC-23: Delete Championship

Scope

Remove or archive a championship (admin only).

Description

Delete or archive championship and related resources according to retention policy.

Actors

Admin - authorised to delete or archive championships.

Flow Description

Precondition

Admin authorised and backup policy confirmed.

Activation

Starts when admin confirms deletion.

Main flow

Perform integrity checks.

Delete or archive resources.

Return confirmation.

Alternate flow

A1: Referential integrity prevents deletion - return 409 Conflict with list of dependent resources and suggested cleanup steps. A2: Admin chooses archive instead of delete - archive resources and return 200 OK with archived: true flag.

Exceptional flow

E1: Database cascade failure - return 500 and halt operation; create a rollback plan and notify admin. E2: Backup/restore service failure during deletion - abort and recommend manual intervention.

Termination

Championship removed or archived.

Post condition

System awaits next admin action.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/ea150dc8-5b14-43a8-87a8-6511a8580393)

UC-24: Create Custom Track

Scope

Add a custom track with characteristics for use in events.

Description

Designer or admin submits track metadata and layout which becomes available for events.

Actors

Designer/Admin - submits track definitions and layout files.

Flow Description

Precondition

Creator authorised.

Activation

Starts when track creation form is submitted.

Main flow

Validate track data.

Insert track record.

Return created track resource.

Alternate flow

A1: Invalid or incomplete track layout submitted - return 400 Bad Request with field-level errors and validation hints. A2: Duplicate track name or coordinates - return 409 Conflict with resolution options.

Exceptional flow

E1: Database write failure - return 500 and log the payload for manual replay. E2: Geometry parsing failure - return 422 Unprocessable Entity with parsing error details.

Termination

Track available for event creation.

Post condition

System awaits next track management action.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/733dbfc5-4692-4e94-a84f-ab6efc3cf8ec)

UC-25: Update Track Characteristics

Scope

Modify track parameters (surface, length, grip) for balancing.

Description

Admin updates track metadata and future events use revised parameters.

Actors

Admin - submits track updates.

Flow Description

Precondition

Track exists and is editable.

Activation

Starts when admin submits updates.

Main flow

Validate and persist updates.

Return updated resource.

Alternate flow

A1: Track is scheduled in upcoming events - return 409 Conflict and offer archive or force options with explicit confirmation. A2: Minor characteristic change allowed - apply change with warnings indicating affected events.

Exceptional flow

E1: Database write failure - return 500 and queue the request for admin review. E2: Constraint violation due to dependent events - return 409 and detail the blocking events.

Termination

Track updated for future events.

Post condition

System awaits next management action.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/f7f7a824-4126-4998-9bb3-04c32086f94a)

UC-26: Delete Track

Scope

Remove custom or unused tracks with checks for scheduled use.

Description

Admin removes track or archives it if scheduled in future.

Actors

Admin - initiates deletion or archiving of tracks.

Flow Description

Precondition

Admin confirmed deletion policy.

Activation

Starts when deletion requested.

Main flow

Check for scheduled events.

If none, delete; else archive or return 409.

Alternate flow

A1: Track has scheduled events - automatically archive and return 200 OK with archived: true when admin confirms, or return 409 if admin cancels.

Exceptional flow

E1: DB transaction failure during delete/archive - return 500 and log for manual reconciliation. E2: File storage deletion error (assets) - mark record archived and flag cleanup pending.

Termination

Track removed or archived.

Post condition

System awaits further track management.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/a48acafc-f752-47be-9757-4e635c488b52)

UC-27: Read Staff Performance Modifiers

Scope

Return computed staff modifiers used by the simulation for team performance.

Description

Provide staff-based modifiers (mechanic efficiency, strategist value) to the Simulation Service.

Actors

Simulation Service - requests computed modifiers for a team.

Flow Description

Precondition

Staff members assigned or available.

Activation

Starts when simulation requests modifiers for a team.

Main flow

Aggregate staff attributes for team.

Return modifier set to simulator.

Alternate flow

A1: Missing or partial staff assignments - return default modifiers and mark incomplete: true in response. A2: Requested team has no staff assigned - return 200 OK with defaults and a recommendation to hire staff for full modifiers.

Exceptional flow

E1: Database read failure - return 503 Service Unavailable and include diagnostic id. E2: Aggregation error while computing modifiers - return 500 and provide fallback default values.

Termination

Simulation applies modifiers.

Post condition

System awaits next modifier request.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/22fbf516-6b02-4f7b-8cca-c9f29d08b2d6)

UC-28: Update Driver Appearance

Scope

Change cosmetic appearance for a driver (helmet, livery) - non-gameplay affecting.

Description

Player edits and saves driver appearance assets which are stored and served to UI.

Actors

Player - creates or edits appearance assets.

Storage Service - stores and serves asset files.

Flow Description

Precondition

Player owns or is authorised to edit driver appearance.

Activation

Starts when player submits appearance changes.

Main flow

Validate assets.

Persist appearance metadata and files.

Return confirmation.

Alternate flow

A1: Invalid asset format or too large - return 400 Bad Request with accepted formats and size limits. A2: Asset conflicts (same filename) - return 409 Conflict and provide renaming options.

Exceptional flow

E1: File storage error (S3/local) - return 500 and queue asset upload for retry; return a reference id to the client. E2: Virus/validation rejection - return 422 Unprocessable Entity with reason.

Termination

Appearance updated for reads.

Post condition

System awaits further edits.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/29727000-fac9-46cc-bf70-5e8a0fc850fd)

UC-29: Update Team Branding

Scope

Update team visual branding assets and metadata (logos, colours).

Description

Player or admin uploads branding assets and updates team metadata for display in UI.

Actors

Player/Admin - uploads branding assets.

Storage/DB - stores branding files and metadata.

Flow Description

Precondition

Requester authorised; assets valid.

Activation

Starts when branding upload is submitted.

Main flow

Validate assets and metadata.

Persist files and update team record.

Return confirmation.

Alternate flow

A1: Invalid branding assets - return 400 Bad Request with clear validation errors and accepted file types. A2: Asset name conflicts - return 409 Conflict with suggested renames.

Exceptional flow

E1: File store or DB failure - return 500 and persist metadata change to a pending queue. E2: Permission or quota error - return 403 or 429 as appropriate with remediation steps.

Termination

Branding served to UI.

Post condition

System awaits next update.

Use Case Diagram

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/3a7202c7-bc50-4913-9c0e-b8591f4ceb5e)

Data Requirements

Database Schema:

The system requires persistent storage for the following entities:

Drivers Table

Primary Key: **driver_id** (INTEGER)

50+ attribute columns (REAL, 0.0-100.0 range)

Biographical data: name, nationality, birth_date, age

Career statistics: races, wins, podiums, championships

Constraints: CHECK constraints on attribute ranges

Teams Table

Primary Key: **team_id** (INTEGER)

Budget (REAL), discipline (TEXT), tier (INTEGER)

Performance attributes: innovation, risk_appetite, management_quality

Career statistics: championships, total_wins

Staff Table

Primary Key: **staff_id** (INTEGER)

Foreign Key: **team_id** references Teams

40+ attribute columns for role-specific skills

Contract data: salary, contract_end_date, job_satisfaction

Tracks Table

Primary Key: **track_id** (INTEGER)

Physical characteristics: length, corners, elevation_change

Surface data: surface_type, grip_level

Challenge ratings: technical_challenge, overtaking_difficulty

Championships Table

Primary Key: **championship_id** (INTEGER)

Series configuration: discipline, points_system, race_count

Races Table

Primary Key: **race_id** (INTEGER)

Foreign Keys: championship_id, track_id

Conditions: weather, temperature, track_condition

RaceResults Table

Primary Key: **result_id** (INTEGER)

Foreign Keys: race_id, driver_id, team_id

Performance data: position, fastest_lap, points_earned

Data Integrity:

Foreign key constraints enforce referential integrity

CHECK constraints validate attribute ranges

UNIQUE constraints prevent duplicate entries

NOT NULL constraints on critical fields

Performance Optimisation:

Indexes on frequently queried fields (driver_id, team_id)

Composite indexes on race lookups (championship_id, race_id)

Query optimisation for large result sets

![](blob:vscode-webview://1knau8j0787evpd56fvmreg35b7l4dfq1uquc2t84ulekvo44mee/ff1a3fd2-14b2-4e8b-b77b-027277ec320b)

User Requirements

Environmental Requirements

Hardware Requirements:

Minimum: 2GB RAM, 500MB disk space, 1GHz dual-core CPU

Recommended: 4GB RAM, 1GB disk space, 2GHz quad-core CPU

Software Requirements:

Operating System: Windows 10+, macOS 10.14+, Linux (Ubuntu 20.04+)

Python: Version 3.8 or higher

Database: SQLite 3.7+

Network: Internet connection for currency exchange rates (optional)

Deployment Requirements:

Development: Local uvicorn server on localhost:8000

Production: ASGI-compatible server (uvicorn, gunicorn)

Database: File-based SQLite (momentum.db)

API Keys: Optional for external services (currency rates)

Scalability Considerations:

API can run multiple worker processes

Database can migrate to PostgreSQL/MySQL for multi-user scenarios

Stateless design enables horizontal scaling

Usability Requirements

Design & Architecture

System Architecture Overview

The Momentum system follows a layered architecture pattern with clear separation of concerns. The architecture is designed for modularity, testability, and future expansion.

**┌─────────────────────────────────────────────────────────────┐**
│                     CLIENT LAYER                            │
│  (Unity Frontend / Web Client / Mobile App / API Consumer)  │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                      API LAYER (**FastAPI**)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  /drivers   │  │   /teams    │  │ /simulate   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│  Request Validation │ Response Formatting │ Error Handling  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              BUSINESS LOGIC LAYER                            │
│  ┌──────────────────────────────────────────────────┐       │
│  │         Multi-Discipline Simulator               │       │
│  │  ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐ ┌──────┐  │       │
│  │  │Single│ │Touring│ │Rally │ │Street│ │ Drag │  │       │
│  │  │Seater│ │  Car │ │ Stage│ │ Race │ │ Race │  │       │
│  │  └──────┘ └──────┘ └──────┘ └──────┘ └──────┘  │       │
│  │  ┌──────┐ ┌──────┐                              │       │
│  │  │Rally │ │**Endur**-│                              │       │
│  │  │cross │ │ **ance** │                              │       │
│  │  └──────┘ └──────┘                              │       │
│  └──────────────────────────────────────────────────┘       │
│                                                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │   Staff     │  │  Currency   │  │     AI      │         │
│  │ Management  │  │   System    │  │   Engine    │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              DATA ACCESS LAYER                               │
│  ┌──────────────────┐  ┌──────────────────┐                │
│  │ **DatabaseManager**  │  │  **DatabaseFactory** │                │
│  └──────────────────┘  └──────────────────┘                │
│           ORM Mapping │ Query Builder │ Connection Pool     │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   DATA LAYER (SQLite)                        │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐          │
│  │ Drivers │ │  Teams  │ │  Staff  │ │ Tracks  │          │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘          │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐                      │
│  │  Races  │ │ Results │ │  Champ  │                      │
│  └─────────┘ └─────────┘ └─────────┘                      │
└─────────────────────────────────────────────────────────────┘

Implementation

Describe the main algorithms/classes/functions used in the code. Consider to show and explain interesting code snippets where appropriate.

Graphical User Interface (GUI)

Provide screenshots of key screens and explain what can be seen in each one.

Testing

Describe any testing tools, test plans and test specifications used in the project.  Provide evidence for and results of all Unit, Integration and End User testing that is carried out.

Evaluation

How was the system evaluated and what are the results? This may consist of usage data. It may also include performance evaluations, scalability, correctness, etc. depending on the focus of the project.  Quantative results may be reported in tables or figures.

Conclusions

Describe the advantages/disadvantages, strengths and limitations of the project

Further Development or Research

With additional time and resources, which direction would this project take?

Bibliography

There are no sources in the current document.

Appendices

This section should contain information that is supplementary to the main body of the report.

Project Proposal

Ethics Approval Application (only if required)

Reflective Journals

Invention Disclosure Form (Remove if not completed)

Please fill in the following sections, if you think your idea is innovative:

1. Title of Invention

2. Inventors

| Name | School/Research Institute | Affiliation with Institute (i.e. department, student, staff, visitor) | Address, contact phone no., e-mail | % Contribution to the Invention |
| ---- | ------------------------- | --------------------------------------------------------------------- | ---------------------------------- | ------------------------------- |
|      |                           |                                                                       |                                    |                                 |
|      |                           |                                                                       |                                    |                                 |
|      |                           |                                                                       |                                    |                                 |
|      |                           |                                                                       |                                    |                                 |

3. Contribution to the Invention

Each contributor/potential inventor should write a paragraph relating to his/her contribution and include a signature and date at the end of the paragraph.

4. Description of Invention

 (Please highlight the novelty/patentable aspect. Attach extra sheets if necessary including diagrams where appropriate).  What is novel, the ‘inventive step’? For more information on patents, please look at [http://www.patentsoffice.ie/en/patents.aspx](http://www.patentsoffice.ie/en/patents.aspx)

5. Why is this invention more advantageous than present technology?

What is its novel or unusual features? What problems does it solve? What are the problems associated with these technologies, products or processes?  Explain how this invention overcomes these problems (i.e. what are its advantages).

6. What is the current stage of development / testing of the invention?
7. List the names of companies which you think would be interested in using, developing or marketing this invention

8. Funding Partner(s)

| Government Agency & Department |  |
| ------------------------------ | - |
| % Support                      |  |
| Contract/Grant No.             |  |
| Contact Name                   |  |
| Phone No.                      |  |
| Address                        |  |

| Industry orotherSponsor |  |
| ----------------------- | - |
| % Support               |  |
| Contract/Grant No.      |  |
| Contact Name            |  |
| Phone No.               |  |
| Address                 |  |

9. Where was the research carried out?

10. What is the potential commercial application of this invention?

11. Was there transfer of any materials/information to or from other institutions regarding this invention?

If so please give details and provide signed agreements where relevant.

12. Have any third parties any rights to this invention?

If yes, give names and addresses and a brief explanation of involvement.

13. Are there any existing or planned disclosures regarding this invention?

 Please give details.

14. Has any patent application been made? Yes/No

If yes, give date: _______________ Application No.: _______________

 Name of patent agent:  _________________________________________

 Please supply copy of specification.

15. Is a model or prototype available? Has the invention been demonstrated practically?

I/we acknowledge that I/we have read, understood and agree with this form and the Institute’s Intellectual Property and Procedures and that all the information provided in this disclosure is complete and correct.

I/we shall take all reasonable precautions to protect the integrity and confidentiality of the IP in question.

Inventor: ______________________________ _______________________

  Signature Date

---

Signature

Other materials used

Any other reference material used in the project for example evaluation surveys etc.
