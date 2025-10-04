# InfantMortalityRate
Interactive map of infant mortality rate(IMR) in Santa Catarina by municipal associations (FECAM). Python pipeline: extract municipality→association from PDF, dissolve municipal GeoJSON, join annual SIM/SINASC series, and visualize trends with a time slider in Plotly.

**Infant Mortality Rate (IMR)**  is the number of deaths of children under 1 year of age in a given year, divided by the total live births that year, multiplied by 1,000. It’s a core public-health indicator of prenatal, delivery, and neonatal care, as well as nutrition and sanitation.

The GeoJSON data of Santa Catarina was acquired from https://github.com/tbrugz/geodata-br/.
