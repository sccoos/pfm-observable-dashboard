```js
// Import deck.gl components for interactive map
import L from "npm:leaflet";

import * as d3 from "npm:d3-time-format";

let shoreline_point_json = await FileAttachment("data/pfm_his_daily/computed_shoreline_points.json").json()
let site_markers_json = await FileAttachment("data/pfm_his_daily/site_markers.json").json()
let risk_thresholds = await FileAttachment("data/pfm_his_daily/risk_thresholds.json").json()
let dye_contour_json = await loadContours()
let site_values_csv = await FileAttachment("data/pfm_his_daily/site_timeseries.csv").csv({typed: true})
const key_locations = site_values_csv.columns.slice(1)
let selected_location = ({selected: key_locations[0]})
const times = site_values_csv.map((d) => d3.timeParse("%Y-%m-%d %H:%M:%S%Z")(d.time));
site_values_csv = site_values_csv.map((d) => ({
  ...d,
  time: d3.timeParse("%Y-%m-%d %H:%M:%S%Z")(d.time)
}));


async function loadContours() {
    let c0 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_0.json").json()
    let c1 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_1.json").json()
    let c2 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_2.json").json()
    let c3 = await FileAttachment("data/pfm_his_daily/computed_dye_contours_3.json").json()
    return {
        all: [...c0, ...c1, ...c2, ...c3]
    }
}

```

<div class="grid grid-cols-3 grid-rows-2" style="grid-auto-rows: auto;">

  <div class="card grid-colspan-1 grid-rowspan-1"><h1>Pathogen Risk Forecast [beta]</h1>
  
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

function getFormattedDate(keyframe) {
    var iso = Date.parse(times[keyframe])
    var formatDate = d3.timeFormat("%A %B %d, %Y %X")
    return formatDate(iso)
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

function siteClicked(e) {
  // e = event
  selected_location.selected = e.target.feature.properties.label
  const form = document.getElementById("date-scrub");
  form.i.dispatchEvent(new CustomEvent("input", {bubbles: true}))
}

function onEachFeature(feature, layer) {
    //bind click
    layer.on({
        click: siteClicked
    });
}
```
<div class="warning" label="Beta Release Notes:">This forecast is highly-experimental and is in limited beta release: not for official use.<hr/>The current forecast range is: mdy-mdy. Site last updated: mdy</div>
</div>

<div id = "site-ts" class="card grid-colspan-2 grid-rowspan-1">
<h1>${buildStatusCard(getCurrentSite())}</h1><h2>${getFormattedDate(keyframe)}</h2>
  ${resize((width, height) => Plot.plot({
    width: width,
    height: height*0.7,
  marks: [
    Plot.axisX({ ticks: "8 hours" }),
    Plot.ruleX(
      site_values_csv,
      { x: [times[keyframe]], py: getCurrentSite(), stroke: getCurrentStatus(keyframe, getCurrentSite()) }
    ),
    Plot.tip(
      site_values_csv,
      { x: [times[keyframe]], py: getCurrentSite(), stroke: getCurrentStatus(keyframe, getCurrentSite()) }
    ),
    Plot.lineY(site_values_csv, { x: "time", y: getCurrentSite() })
  ]
}))}

</div>
<div class="card grid-colspan-2" style="padding: 0;"><div id="map-SD" style="height: 66vh; width: 100%;"></div></div>
<div class="card grid-colspan-1">
<p>
Colored contour lines represent the fraction of raw wastewater forecasted to be at the ocean surface.  A value of 1 is pure sewage (black) and a value of zero (light yellow) is pure ocean water.  Click “Play” or use the scroll-bar to the left to see the forecast.

Values are presented in powers of 10, such that 10-1 is 1:10 dilution or 10% raw sewage, 10-3 is 1:1000 dilution, 10-4 is 1:10,000 dilution, etc.

Shoreline color represents swimmer risk based on wastewater fraction:  red is high risk, yellow is moderate risk, and green is low risk.   

Four swimming locations south to north – Playas Tijuana, Imperial Beach Pier, Silver Strand, and Hotel del Coronado – are labeled with coordinates.  Click on those locations to see a more detailed forecast. 

Additional information is available at http://URL

*Questions should be addressed to EMAIL

Funding provided by the State of California.
</p>
<div style = "text-align: center">
<img src = "https://s2020.s3.amazonaws.com/media/logo-scripps-ucsd-dark.png" width = "45%"></img>
<img src = "https://sccoos.org/wp-content/uploads/2022/05/SCCOOS_logo-01.png" width = "45%"></img>
</div>
</div>

```js
var map = L.map('map-SD').setView([32.58, -117.2], 11);
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

    var curContour = L.geoJSON(JSON.parse(dye_contour_json.all[keyframe]), {style: setContourStyle})
    curContour.addTo(map);

    var shorelineJSON = new L.geoJSON(JSON.parse(shoreline_point_json[keyframe]), {
      pointToLayer: (feature, latlng) => {
          return new L.Circle(latlng, {radius: 90, fillOpacity: 1, color: feature.properties.risk});
      }
    }).addTo(map);

    var siteJSON = new L.geoJSON(JSON.parse(site_markers_json), {
      pointToLayer: (feature, latlng) => {
          return new L.circleMarker(latlng, {color: "white", weight: 1, fillColor: getCurrentStatus(keyframe, feature.properties.label), fillOpacity: 1}).addTo(map).bindTooltip(feature.properties.label,{permanent: true, direction: "right", offset: [10, -5]});
      },
      onEachFeature: onEachFeature
    }).addTo(map);

    return curContour;
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
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="20px" viewBox="0 0 500 500"><path fill="palegreen" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"/></svg>${location}
        `;
    // Medium Risk
    } else if (current_val < risk_high) {
        card = html`
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="20px" viewBox="0 0 500 500"><path fill="gold" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zm0-384c13.3 0 24 10.7 24 24l0 112c0 13.3-10.7 24-24 24s-24-10.7-24-24l0-112c0-13.3 10.7-24 24-24zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg>${location}
        `;
    // High Risk
    } else {
        card = html`
            <svg xmlns="http://www.w3.org/2000/svg" width="24px" height="20px" viewBox="0 0 500 500"><path fill="firebrick" d="M256 32c14.2 0 27.3 7.5 34.5 19.8l216 368c7.3 12.4 7.3 27.7 .2 40.1S486.3 480 472 480L40 480c-14.3 0-27.6-7.7-34.7-20.1s-7-27.8 .2-40.1l216-368C228.7 39.5 241.8 32 256 32zm0 128c-13.3 0-24 10.7-24 24l0 112c0 13.3 10.7 24 24 24s24-10.7 24-24l0-112c0-13.3-10.7-24-24-24zm32 224a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/></svg>${location}
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
    if ((event && event.isTrusted && running()) || (event && event && event.explicitOriginalTarget.classList[0] == "leaflet-interactive" && running())) stop();
    form.value = form.i.valueAsNumber;
    form.o.value = format(values[form.i.valueAsNumber], form.i.valueAsNumber, values);
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
```