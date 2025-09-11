# Evaluierung des SQL-Agenten mit watsonx.orchestrate

**Datum:** 2025-09-11

## Methodik

Diese Evaluierung bewertet die Fähigkeit der SQL-Agenten innerhalb des watsonx.orchestrate-Frameworks, korrekte SQL-Abfragen aus natürlichsprachlichen Eingaben zu generieren. Jede generierte Abfrage wurde manuell mit einer erwarteten, korrekten Abfrage verglichen, um die syntaktische und logische Genauigkeit zu bestimmen.

## Zusammenfassung der Ergebnisse

- **Gesamtzahl der evaluierten Abfragen:** 240
- **Erfolgreiche Abfragen:** 39
- **Davon mit korrekter SQL Query:** 26
- **Fehlerhafte Abfragen:** 201
- **Erfolgsquote:** 16.25%
- **Genauigkeit (nur erfolgreiche Durchläufe):** 66.7%
- **Durchschnittliche Latenz (nur erfolgreiche Durchläufe):** 83.4 Sekunden


## Beispiele

### Korrekt generierte Abfrage

- **Frage:** "What are the monthly registrations for electric vehicles (EVs) since 2023?"
- **Generierte Abfrage:**
```sql
SELECT t.year_month, SUM(f.vehicle_count) AS ev_registrations FROM "FactRegisteredVehicles" AS f JOIN "DimTime" AS t ON f.time_key = t.time_key JOIN "DimVehicle" AS v ON f.vehicle_key = v.vehicle_key WHERE v.fuel_type = 'ELECTRIC' AND t.year_report >= 2023 GROUP BY t.year_month ORDER BY t.year_month;
```


### Fehlerhaft generierte Abfrage (Schema-Halluzination)
- **Frage:** "What about the sales in December? What body types were sold the most?"
- **Generierte Abfrage:**
```sql
SELECT body_type, COUNT(*) AS total_registrations FROM vehicle_registrations WHERE EXTRACT(YEAR FROM registration_date) = 2023 AND EXTRACT(MONTH FROM registration_date) = 12 GROUP BY body_type ORDER BY total_registrations DESC;
```
- **Fehler:** Der Agent hat eine nicht existierende Tabelle vehicle_registrations und falsche Spaltennamen halluziniert, anstatt das korrekte Sternschema mit JOINs zu verwenden.


---


## Latenz-Evaluierung des Multi-Agenten-Workflows mit watsonx.orchestrate

**Datum:** 2025-09-11

### Methodik

Diese Evaluierung misst die End-to-End-Latenz des gesamten Multi-Agenten-Workflows in watsonx.orchestrate für eine Reihe von Testanfragen. Jede der 10 Anfragen wurde mehrmals ausgeführt, um die Erfolgsrate und die durchschnittliche Latenzzeit für erfolgreiche Durchläufe zu ermitteln.

**Hinweis:** Aufgrund von Limitierungen der Plattform war es nicht möglich, die Latenz einzelner Agenten-Schritte zu messen. Es wird nur die Gesamtlatenz des Workflows berichtet.


## Latenztabelle erfolgreicher Durchläufe


| Lauf-ID | Frage                                                                                             | Gesamtlatenz (Sekunden) |
|:-----|:-----------------------------------------------------------------------------------------------------|:------------------------|
| 10   | "What are the monthly registrations for electric vehicles (EVs) since 2023?"                         | 78.9                    |
| 11   | "Provide a comparison of monthly registrations for petrol vs electric vehicles since 2023."          | 88.1                    |
| 13   | "Q1 2024 vs Q1 2023 comparison of total vehicle registrations?"                                      | 101.4                   |
| 14   | "Q1 2024 vs Q1 2023 comparison of total vehicle registrations for MERCEDES-BENZ?"                    | 85.0                    |
| 15   | "Provide a comparison of monthly registrations for petrol vs electric vehicles since 2023."          | 69.3                    |
| 16   | "Find the top regions for PORSCHE registrations"                                                     | 98.0                    |
| 18   | "Find the top regions for PORSCHE registrations"                                                     | 82.8                    |
| 19   | "What are the monthly registrations in total since 2023?"                                            | 84.5                    |
| 21   | "Q1 2024 vs Q1 2023 comparison of total vehicle registrations for BMW?"                              | 88.8                    |
| 22   | "Find the top regions for MERCEDES-BENZ registrations"                                               | 70.0                    |
| 23   | "Q1 2024 vs Q1 2023 comparison of total vehicle registrations for AUDI?"                             | 76.2                    |
| 104  | "Find the top regions for AUDI registrations"                                                        | 81.1                    |
| 106  | "Which districts register the most electric vehicles?"                                               | 80.5                    |
| 109  | "Find the top regions for BMW registrations"                                                         | 71.8                    |
| 111  | "What are the monthly registration trends for BMW, AUDI, and MERCEDES-BENZ by body type since 2023?" | 91.5                    |
| 112  | "Year-over-year comparison of SUV registrations from 2023 to 2024?"                                  | 81.9                    |
| 115  | "What is the growth rate among body types from 2023 to 2024?"                                        | 75.8                    |
| 119  | "Q1 2024 vs Q1 2023 comparison of total vehicle registrations for BMW?"                              | 94.6                    |
| 123  | "What are the top 3 body types registered in 2024?"                                                  | 79.1                    |
| 127  | "What are the top 5 car brands by total registrations in 2024?"                                      | 65.8                    |
| 133  | "Provide a comparison of monthly registrations for SUVs vs Sedans since 2023."                       | 95.4                    |
| 135  | "Which fuel type showed the highest growth rate from 2023 to 2024?"                                  | 83.3                    |
| 144  | "Which country has the highest vehicle registrations?"                                               | 74.4                    |
| 145  | "Which country has the highest vehicle registrations?"                                               | 89.6                    |
| 149  | "What are the top 5 car brands by total registrations in 2024?"                                      | 99.2                    |
| 155  | "Which fuel type showed the highest growth rate from 2023 to 2024?"                                  | 105.3                   |
| 158  | "What are the year-over-year growth trends for electric vehicles (2023 vs 2024)?"                    | 90.3                    |
| 163  | "Show me a waterfall chart of year-over-year petrol vehicle registration changes from 2023 to 2024?" | 92.5                    |
| 165  | "What are the monthly registration trends for BMW, AUDI, and MERCEDES-BENZ by body type since 2023?" | 85.2                    |
| 173  | "Which country has the highest vehicle registrations?"                                               | 62.9                    |
| 182  | "What are the year-over-year growth trends for electric vehicles (2023 vs 2024)?"                    | 73.7                    |
| 183  | "What are the top 3 body types registered in 2024?"                                                  | 68.7                    |
| 190  | "Find the top regions for MERCEDES-BENZ registrations"                                               | 93.2                    |
| 193  | "Find the top regions for PORSCHE registrations"                                                     | 67.5                    |
| 210  | "Which districts register the most electric vehicles?"                                               | 110.1                   |
| 222  | "What are the top 5 car brands by total registrations in 2024?"                                      | 82.1                    |
| 229  | "Monthly registrations for ELECTRIC and PATROL vehicles for 2023 and 2024"                           | 77.6                    |
| 237  | "Compare England vs Scotland vehicle body type preferences"                                          | 96.7                    |
| 238  | "Find the top regions for BMW registrations"                                                         | 86.4                    |
