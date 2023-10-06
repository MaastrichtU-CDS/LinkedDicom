# Example queries

The following example queries are listed below:

* **[RTSTRUCT.sparql](RTSTRUCT.sparql)** Find the structure names for all patients in various RTSTRUCT files
* **[RTSTRUCT_CT.sparql](RTSTRUCT_CT.sparql)** Similar as `RTSTRUCT.sparql` however now with the referenced CT information
* **[RT_package.sparql](RT_package.sparql)** Query which fetches the RT Dose -> Plan -> Structure -> CT (series) reference

## Specific DVH queries
* **[dose_overview.sparql](dose_overview.sparql)** Query the general/generic dose information
* **[dvh_curve.sparql](dvh_curve.sparql)** Give a DVH curve points for a specific structure
* **[dvh_d_point.sparql](dvh_d_point.sparql)** Query a specific DVH-d point (d30)
* **[dvh_v_point.sparql](dvh_v_point.sparql)** Query a specific DVH-v point (v10)