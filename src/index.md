---
toc: false
---

<style>

.hero {
  display: flex;
  flex-direction: column;
  align-items: center;
  font-family: var(--sans-serif);
  margin: 4rem 0 8rem; text-wrap: balance;
  text-align: center;
}

.hero h1 {
  margin: 2rem 0;
  max-width: none;
  font-size: 14vw;
  font-weight: 900;
  line-height: 1;
  background: linear-gradient(30deg, var(--theme-foreground-muted), currentColor);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero h2 {
  margin: 0;
  max-width: 34em;
  font-size: 20px;
  font-style: initial;
  font-weight: 500;
  line-height: 1.5;
  color: var(--theme-foreground-muted);
}

@media (min-width: 640px) {
  .hero h1 {
    font-size: 70px;
  }
}

</style>

<div class="hero">
  <h1>Impacts SAAS &amp; IAAS</h1>
</div>

```js
console.log("Loading data")
const storage_impact_data = FileAttachment("data/storage_impact.csv").csv({typed: true})

const units = {"gwp": "kgCO2eq", "adpe": "kgSbeq", "adpf": "MJ", "ap": "", "ctue": "ctue", "ir": "kBqU235eq", "pm": "Disease occurence", "pocp": "kgNMVOCeq", "mips": "kg", "wp": "kg", "pe": "MJ", "fe": "MJ"}

const impact_criteria = view(Inputs.select(["gwp", "adpe", "adpf", "ap", "ctue", "ir", "pm", "pocp", "mips", "wp", "pe", "fe"], {unique: true, value: "1", label: "Impact criteria"}));
const size_gb = view(Inputs.select([1,10,100], {label: "Size in GB"}))
const service_type = view(Inputs.select(["Storage (1 year)"], {"label": "Service Type'"}))
const x_group = view(Inputs.select(["tier", "dc_location"], {value: "tier", label: "X grouping by"}))
const fx = view(Inputs.select(["dc_location", "tier"], {value: "dc_location", label: "fx grouping"}))
```

<h3>Impact of ${service_type}, size in GB: ${size_gb}, ${impact_criteria}, unit: ${units[impact_criteria]}</h3>
<div class="grid grid-cols-1">
  <div class="card">${
    resize((width) => Plot.plot({
      x: {axis: null},
      y: {tickFormat: "s", grid: true},
      color: {scheme: "spectral", legend: true},
      marks: [
        Plot.barY(storage_impact_data, {
          x: x_group,
          y: impact_criteria,
          fill: x_group,
          fx: fx,
          filter: (d) => d.service_type === service_type && d.size_gb === size_gb,
          sort: {x: null, color: null, fx: {value: "-y", reduce: "sum"}}
        }),
        Plot.ruleY([0])
      ]
    }))}
</div>
</div>
