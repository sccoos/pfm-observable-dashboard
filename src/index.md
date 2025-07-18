```js
// Import deck.gl components for interactive map
import L from "npm:leaflet";
import * as d3 from "npm:d3";

let shoreline_point_json = await FileAttachment("data/pfm_his_daily/computed_shoreline_points.json").json()
let site_markers_json = await FileAttachment("data/pfm_his_daily/site_markers.json").json()
let risk_thresholds = await FileAttachment("data/pfm_his_daily/risk_thresholds.json").json()
let model_extent = await FileAttachment("data/pfm_his_daily/LV4_model_extent.json").json()
let dye_contour_json = await loadContours()
let site_values_csv = await FileAttachment("data/pfm_his_daily/site_timeseries.csv").csv({typed: true})
const key_locations = site_values_csv.columns.slice(1)
let selected_location = ({selected: key_locations[0]})
const times = site_values_csv.map((d) => d3.timeParse("%Y-%m-%d %H:%M:%S%Z")(d.time));
site_values_csv = site_values_csv.map((d) => ({
  ...d,
  time: d3.timeParse("%Y-%m-%d %H:%M:%S%Z")(d.time)
}));
let contourKey = JSON.parse(dye_contour_json.all[0]).features.map(feature => ({
  range: feature.properties.title,
  color: feature.properties.fill
}));
async function loadContours() {
    let c0 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_0.json").json()
    let c1 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_1.json").json()
    let c2 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_2.json").json()
    let c3 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_3.json").json()
    let c4 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_4.json").json()
    return {
        all: [...c0, ...c1, ...c2, ...c3, ...c4]
    }
}

```
<link rel="stylesheet" href="index.css">
<div class="grid grid-cols-3 grid-rows-2" style="grid-auto-rows: auto;">

  <div class="card grid-colspan-1 grid-rowspan-1"><h1>Pathogen Forecast Model Phase 1</h1>

  <div class="warning" label="Phase 1 Release Notes:">
    This forecast updates at 6:30AM US/Pacific. The current forecast range is
  ${getFormattedDate(times[0])} - ${getFormattedDate(times[times.length-1])}    
      <hr/>
   Click "Play" below to view the animated forecast of percentage sewage in the ocean.  You can also use the scroll bar to move back and forth in time.  Click on the location circle on the map to see the detailed forecast at that location to the right.  
  </div>
  
```js
const keyframe = view(
    Scrubber(times, {
    delay: 100,
    loop: false
    })
);

function getCurrentSite(){
    return selected_location.selected
}

function getFormattedDate(time) {
    var iso = Date.parse(time)
    var formatDate = d3.timeFormat("%A %B %d, %Y %X") //%H:%M%p
    return formatDate(iso)
}

function getCurrentValue(keyframe, selected_location) {
    const d1_vals = site_values_csv.map((a) => parseFloat(a[selected_location]));
    const current_val = d1_vals[keyframe]
    return current_val
}

function getCurrentStatus(keyframe, selected_location) {
    const d1_vals = site_values_csv.map((a) => parseFloat(a[selected_location]));
    const current_val = d1_vals[keyframe]
    let status = ''
    let risk_high = risk_thresholds.high
    let risk_low = risk_thresholds.low

    // Low Risk
    if (current_val < risk_low) {
        status = 'green';
    // Medium Risk
    } else if (current_val < risk_high) {
        status = 'yellow';
    // High Risk
    } else {
        status = 'red';
    }
    return status
}

function buildSelectOptions(selected_location) {
  let loc_string = key_locations.map(
    loc => html`<option value="${loc}">${loc}</option>`
  );

  return loc_string
}

function siteClicked(e) {
  // e = event

  if (e.target.feature && e.target.feature.properties.label != null) {
    selected_location.selected = e.target.feature.properties.label;
    loc_sel.value = selected_location.selected
  } else {
    selected_location.selected = e.target.value;
  }
  const form = document.getElementById("date-scrub");
  form.i.dispatchEvent(new CustomEvent("input", {bubbles: true}));
}
let loc_sel = document.getElementById('location-select');
loc_sel.addEventListener('change', siteClicked);

function onEachFeature(feature, layer) {
    //bind click
    layer.on({
        click: siteClicked
    });
}
```
</div>
<div id = "site-ts" class="card grid-colspan-2 grid-rowspan-1" style="min-height: 200px; padding-bottom:20px; padding-left:30px;">
<h1 style="max-width:1100px">${buildStatusCard(getCurrentSite())}<select id="location-select" name="location-select">${buildSelectOptions(getCurrentSite())}</select></h1><h2>${getFormattedDate(times[keyframe])}</h2>
  ${resize((width, height) => Plot.plot({
    width: width,
    height: height*0.7,
    x: {
      type: 'time'
    },
    y: {
      tickFormat: (n) => `${+(10**(n) * 100).toFixed(6)}%`,
      grid: true,
      label: "Sewage percentage at shoreline"
    },
  marks: [
    Plot.axisX({ ticks: "8 hours" }),
    Plot.areaY(site_values_csv, {x: "time", y1: risk_thresholds.low, y2: -6, fill: "green", opacity: 0.2}),
    Plot.areaY(site_values_csv, {x: "time", y1: -1.5, y2: risk_thresholds.high, fill: "red", opacity: 0.2}),
    Plot.areaY(site_values_csv, {x: "time", y1: risk_thresholds.low, y2: risk_thresholds.high, fill: "yellow", opacity: 0.2}),
    Plot.ruleX(
      site_values_csv,
      { x: [times[keyframe]], py: getCurrentSite(), stroke: getCurrentStatus(keyframe, getCurrentSite()) }
    ),
    Plot.lineY(site_values_csv, { x: "time", y: getCurrentSite(), strokeWidth: 2 })
  ]
}))}

</div>
<div class="card grid-colspan-2" style="padding: 0;"><div id="map-SD" style="height: 100%; min-height: 400px; width: 100%; z-index: 1; position: relative;">
<div style="display: flex; flex-direction: column; justify-content: center; position: absolute; bottom: 5%; left: 65%; z-index: 9999; background-color: rgba(255, 255, 255, 0.0); pointer-events: none;">
<img style="padding: 1em" src = "https://s2020.s3.amazonaws.com/media/logo-scripps-ucsd-dark.png" width = "80%"></img>
<img style="padding: 1em" src = "https://sccoos.org/wp-content/uploads/2022/05/SCCOOS_logo-01.png" width = "80%"></img>
</div>
<div style="display: flex;
    flex-direction: column;
    justify-content: center;
    position: absolute;
    top: 5%;
    left:5%;
    height:80%;
    align-items: center; z-index: 9999; pointer-events: none;">
    <img style="padding: 1em" src = "https://falk.ucsd.edu/PFM_Forecast/colorbar_pcent_cropped.png" height = "80%"></img>

</div>
</div></div>
<div class="card grid-colspan-1" style="min-height: 60vh">
<p>
Forecasts of sewage at the ocean surface are provided for the San Diego/Tijuana border region.  
In the map on the left, colored contour lines represent the percentage of sewage at the ocean surface.  A value of 100% is pure sewage and a value of zero is pure ocean water.  Contours go from a high of 10% sewage to a low of 0.0005% sewage.  

The color at the shoreline indicates swimmer illness risk based on sewage percentage with
<ul>
  <li> Red indicates high risk representing greater than 0.1% sewage</li>
  <li> Yellow indicates moderate risk at values between 0.001% and 0.1% sewage</li>
  <li> Green indicates low risk at values less than 0.001% sewage</li>
</ul>

Four swimming locations from south to north – Playas de Tijuana, Imperial Beach Pier, Silver Strand, and Coronado, Avenida Lunar – are labeled with circles.  Click on the circle to see a more detailed forecast (shown above) at these locations. There is also a drop-down menu in the detailed forecast shown above.  In the graph above, sewage concentration is given in percentages with the high, moderate, and low swimmer risk indicated with the colored background.

Swimmer illness risk is based upon risk of illness from norovirus  <a href="https://agupubs.onlinelibrary.wiley.com/doi/full/10.1029/2021GH000490" target="_blank">Feddersen et al. (2021)</a>.  A value of 0.1% sewage corresponds to a 10% risk of swimmer illness and a value of 0.001% sewage corresponds to a 1% risk of swimmer illness.

The county’s official beach water quality conditions are reported by the County
of San Diego Beach & Bay Water Quality Monitoring Program. Current advisories, warnings,
and closures are updated daily and can be found at <a href="https://www.sdbeachinfo.com/">County of San Diego Beach Water Quality</a>. The County of San Diego also maintains the <a href="https://tjdashboard.netlify.app/">Tijuana River Valley Sewage Crisis Environmental Dashboard</a>.

This ocean forecast model is analogous to weather forecast models.  Forecasts are typically 5 days long, but may be as short as 3 days.  Occasionally if forecasts fail, the forecast date is a day behind. The dashed white rectangle box represents the region where the model is providing a forecast.  Outside of this box, no forecast is made. This model uses NOAA forecasts of Tijuana River flow and estimates San Antonio de los Buenos outflow at Punta Bandera MX.  Questions regarding the Pathogen Forecast Model should be addressed to <i>ffeddersen@ucsd.edu</i>.  

This forecast is experimental and may contain errors. Not for official use. Accuracy is not guaranteed. 

<span style="color: orange"><b>Funding provided by the State of California.</b></span>

<span style="color: orange"><b>A guide to the PFM dashboard can be found on youtube here</b></span>
</p>
</div>

```js
var map = L.map('map-SD').setView([32.58, -117.18], 11);
var basetile = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
    maxZoom: 19,
    attribution: '© OpenStreetMap contributors'
})

var basetileID = L.stamp(basetile)
basetile.addTo(map);

function renderJSONContours(keyframe, basetileID) {
    map.eachLayer(function(layer){
        if (L.stamp(layer) != basetileID)
        layer.removeFrom(map);
    });

    var model_bbox = L.geoJSON(JSON.parse(model_extent), {style: setBoundingBoxStyle})
    model_bbox.addTo(map);
    var curContour = L.geoJSON(JSON.parse(dye_contour_json.all[keyframe]), {style: setContourStyle})
    curContour.addTo(map);

    var shorelineJSON = new L.geoJSON(JSON.parse(shoreline_point_json[keyframe]), {
      pointToLayer: (feature, latlng) => {
          return new L.Circle(latlng, {radius: 90, fillOpacity: 1, color: feature.properties.risk});
      }
    }).addTo(map);

    var siteJSON = new L.geoJSON(JSON.parse(site_markers_json), {
      pointToLayer: (feature, latlng) => {
          return new L.circleMarker(latlng, {color: "white", weight: 1, fillColor: getCurrentStatus(keyframe, feature.properties.label), fillOpacity: 1}).addTo(map).bindTooltip(feature.properties.label,{permanent: true, direction: "right", offset: [10, -5], });
      },
      onEachFeature: onEachFeature
    }).addTo(map);

    return curContour;
}

function setBoundingBoxStyle(feature) {
  return {
    fillColor: '#FFFFFF',
    color: 'white',
    fillOpacity: 0,
    weight: 2,
    dashArray: '3',
    opacity: 0.7
  };
}

function setContourStyle(feature) {
  return {
    fillColor: feature.properties.fill,
    color: feature.properties.stroke,
    fillOpacity: feature.properties.fillOpacity,
    opacity: feature.properties.strokeOpacity
  };
}
```

```js
const curContour = renderJSONContours(keyframe, basetileID)
```


```js
function buildStatusCard(location) {
  
    const d1_vals = site_values_csv.map((a) => parseFloat(a[location]));
    const current_val = d1_vals[keyframe]

    let risk_high = risk_thresholds.high
    let risk_low = risk_thresholds.low
    var card;

    // Low Risk
    if (current_val < risk_low) {
        card = html`
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="20px" viewBox="0 0 500 500"><path fill="palegreen" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"/></svg>
        `;
    // Medium Risk
    } else if (current_val < risk_high) {
        card = html`
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="20px" viewBox="0 0 500 500"><path fill="gold" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zm0-384c13.3 0 24 10.7 24 24l0 112c0 13.3-10.7 24-24 24s-24-10.7-24-24l0-112c0-13.3 10.7-24 24-24zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg>
        `;
    // High Risk
    } else {
        card = html`
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="20px" viewBox="0 0 500 500"><path fill="firebrick" d="M256 32c14.2 0 27.3 7.5 34.5 19.8l216 368c7.3 12.4 7.3 27.7 .2 40.1S486.3 480 472 480L40 480c-14.3 0-27.6-7.7-34.7-20.1s-7-27.8 .2-40.1l216-368C228.7 39.5 241.8 32 256 32zm0 128c-13.3 0-24 10.7-24 24l0 112c0 13.3 10.7 24 24 24s24-10.7 24-24l0-112c0-13.3-10.7-24-24-24zm32 224a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/></svg>
        `;
    }
    return card;
}
```

```js
function Scrubber(values, {
  format = value => value,
  initial = 0,
  direction = 1,
  delay = null,
  autoplay = false,
  loop = true,
  loopDelay = 300,
  alternate = false
} = {}) {
  values = Array.from(values);
  const form = html`<form id="date-scrub" style="font: 12px var(--sans-serif); font-variant-numeric: tabular-nums; justify-content: center; display: flex; height: 33px; align-items: center;">
  <button name=b type=button style="margin-right: 0.4em; width: 5em;"></button>
  <label style="display: flex; align-items: center;">
    <input name=i type=range min=0 max=${values.length - 1} value=${initial} step=1">
    <output name=o style="margin-left: 0.4em;"></output>
  </label>
</form>`;
  let frame = null;
  let timer = null;
  let interval = null;
  function start() {
    form.b.textContent = "Pause";
    if (delay === null) frame = requestAnimationFrame(tick);
    else interval = setInterval(tick, delay);
  }
  function stop() {
    form.b.textContent = "Play";
    if (frame !== null) cancelAnimationFrame(frame), frame = null;
    if (timer !== null) clearTimeout(timer), timer = null;
    if (interval !== null) clearInterval(interval), interval = null;
  }
  function running() {
    return frame !== null || timer !== null || interval !== null;
  }
  function tick() {
    if (form.i.valueAsNumber === (direction > 0 ? values.length - 1 : direction < 0 ? 0 : NaN)) {
      if (!loop) return stop();
      if (alternate) direction = -direction;
      if (loopDelay !== null) {
        if (frame !== null) cancelAnimationFrame(frame), frame = null;
        if (interval !== null) clearInterval(interval), interval = null;
        timer = setTimeout(() => (step(), start()), loopDelay);
        return;
      }
    }
    if (delay === null) frame = requestAnimationFrame(tick);
    step();
  }
  function step() {
    form.i.valueAsNumber = (form.i.valueAsNumber + direction + values.length) % values.length;
    form.i.dispatchEvent(new CustomEvent("input", {bubbles: true}));
  }

  form.i.oninput = event => {
    if ((event && event.isTrusted && running())) stop();
    form.value = form.i.valueAsNumber;
    form.o.value = d3.timeFormat("%m/%d/%y %H:%M")(values[form.i.valueAsNumber]);
  };
  form.b.onclick = event => {
    if (running()) return stop();
    direction = alternate && form.i.valueAsNumber === values.length - 1 ? -1 : 1;
    form.i.valueAsNumber = (form.i.valueAsNumber + direction) % values.length;
    form.i.dispatchEvent(new CustomEvent("input", {bubbles: true}));
    start();
  };
  form.i.oninput();
  if (autoplay) start();
  else stop();
  Inputs.disposal(form).then(stop);
  return form;
}

function legend({
  color,
  title,
  tickSize = 6,
  width = 36 + tickSize,
  height = 320,
  marginTop = 20,
  marginRight = 10 + tickSize,
  marginBottom = 20,
  marginLeft = 5,
  ticks = height / 64,
  tickFormat,
  tickValues
} = {}) {
  const svg = d3
    .create("svg")
    .attr("width", width)
    .attr("height", height)
    .attr("viewBox", [0, 0, width, height])
    .style("color", "white")
    .style("overflow", "visible")
    .style("display", "block");

  let tickAdjust = (g) =>
    g.selectAll(".tick line").attr("x1", marginLeft - width + marginRight);
  let x;

  x = d3
    .scaleBand()
    .domain(color.domain())
    .rangeRound([height - marginBottom, marginTop]);

  svg
    .append("g")
    .selectAll("rect")
    .data(color.domain())
    .join("rect")
    .attr("y", x)
    .attr("x", marginLeft)
    .attr("height", Math.max(0, x.bandwidth() - 1))
    .attr("width", width - marginLeft - marginRight)
    .attr("fill", color);

  tickAdjust = () => {};

  svg
    .append("g")
    .attr("transform", `translate(${width - marginRight},0)`)
    .call(
      d3
        .axisRight(x)
        .ticks(ticks, typeof tickFormat === "string" ? tickFormat : undefined)
        .tickFormat(typeof tickFormat === "function" ? tickFormat : undefined)
        .tickSize(tickSize)
        .tickValues(tickValues)
    )
    .call(tickAdjust)
    .call((g) => g.select(".domain").remove())
    .call((g) =>
      g
        .append("text")
        .attr("x", marginLeft - width + marginRight)
        .attr("y", 0)
        .attr("fill", "currentColor")
        .attr("text-anchor", "start")
        .attr("font-weight", "bold")
        .attr("class", "title")
        .text(title)
    );

  return svg.node();
}
```
