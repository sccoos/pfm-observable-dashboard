```js
// Import deck.gl components for interactive map
import L from "npm:leaflet";

//import * as d3 from "npm:d3-time-format";

//const contours = await FileAttachment("data/all_dye_contours.json").json()

let shore_points = await FileAttachment("data/all_shore_points.json").json()

async function loadDyes() {
    let dye_01 = await FileAttachment("data/dye_01_forecast_20250316.csv").csv()
    let dye_02 = await FileAttachment("data/dye_02_forecast_20250316.csv").csv()
    return {
        dye_01: dye_01,
        dye_02: dye_02
    }
}

async function loadContours() {
    let c0 = await FileAttachment("data/dye_01_contour_example_0.json").json()
    let c1 = await FileAttachment("data/dye_01_contour_example_1.json").json()
    let c2 = await FileAttachment("data/dye_01_contour_example_2.json").json()
    let c3 = await FileAttachment("data/dye_01_contour_example_3.json").json()
    let c4 = await FileAttachment("data/dye_01_contour_example_4.json").json()
    let c5 = await FileAttachment("data/dye_01_contour_example_5.json").json()
    let c6 = await FileAttachment("data/dye_01_contour_example_6.json").json()
    let c7 = await FileAttachment("data/dye_01_contour_example_7.json").json()
    return {
        arr: [...c0, ...c1, ...c2, ...c3, ...c4, ...c5, ...c6, ...c7]
    }
}

const all_dye = await loadDyes()
const all_contours = await loadContours()
const key_locations = ['PTJ', 'border', 'TJRE', 'IB pier', 'Silver Strand', 'HdC']
const key_lats = [32.52, 32.534, 32.552, 32.58, 32.625, 32.678]
const site_map = {
    'HdC': [32.678, -117.18],
    'Silver Strand': [32.625, -117.14],
    'IB pier': [32.58, -117.133],
    'TJRE': [32.552, -117.128],
    'border': [32.534, -117.122],
    'PTJ': [32.52, -117.121],
}

var greenIcon = new L.Icon({
  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41]
});

```

<div class="grid grid-cols-3 grid-rows-1">
  <div class="card grid-colspan-1"><h2>${getFormattedDate(keyframe)}</h2><h1>Pathogen Risk Forecast</h1>

```js
const times = all_dye.dye_01.map((d) => d.time)

const keyframe = view(
    Scrubber(times, {
    delay: 100,
    loop: false
    })
);

function getCurrentValue(location){
    const d1_vals = all_dye.dye_01.map((a) => parseFloat(a[location]));
    const d2_vals = all_dye.dye_02.map((a) => parseFloat(a[location]));
    const current_val = Math.log10((10 ** parseFloat(d1_vals[keyframe]))+(10 ** parseFloat(d1_vals[keyframe])))
    return current_val
}

function getFormattedDate(keyframe) {
    var iso = Date.parse(times[keyframe])
    var formatDate = d3.timeFormat("%A %B %d, %Y:  %X")
    return formatDate(iso)
}
```

${buildStatusCard(key_locations[5])}
${buildStatusCard(key_locations[4])}
${buildStatusCard(key_locations[3])}
${buildStatusCard(key_locations[2])}
${buildStatusCard(key_locations[1])}
${buildStatusCard(key_locations[0])}
</div>
    <div class="card grid-colspan-2"><div id="map-SD" style="height: 80vh; width: 100%;"></div></div>
</div>

```js
var map = L.map('map-SD').setView([32.6, -117.2], 11);
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

    var curContour = L.geoJSON(JSON.parse(all_contours.arr[keyframe]), {style: setContourStyle})
    curContour.addTo(map);

    var geoJson = new L.geoJSON(JSON.parse(shore_points[keyframe]), {
      pointToLayer: (feature, latlng) => {
          return new L.Circle(latlng, {radius: 45, fillOpacity: 1, color: feature.properties.risk});
      }
    }).addTo(map);

    // var curPoints = L.geoJSON(JSON.parse(shore_points[keyframe]), {style: setContourStyle})
    // curPoints.addTo(map)

    for (let site of key_locations) {
        let markerCol;
        let risk_high = -3
        let risk_med = -5
        let risk_low = -5.5
        const d1_vals = all_dye.dye_01.map((a) => parseFloat(a[site]));
        const d2_vals = all_dye.dye_02.map((a) => parseFloat(a[site]));
        const current_val = Math.log10((10 ** parseFloat(d1_vals[keyframe]))+(10 ** parseFloat(d1_vals[keyframe])))
        if (current_val < risk_med) {
            markerCol = "palegreen"
        } else if (current_val < risk_high) {
            markerCol = "gold"
        } else{
            markerCol = "firebrick"
        }
        
        L.circleMarker(site_map[site], {color: "white", weight: 1, fillColor: markerCol, fillOpacity: 1}).addTo(map).bindTooltip(site,{permanent: true, direction: "right", offset: [10, -5]})
    }

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
  
    const d1_vals = all_dye.dye_01.map((a) => parseFloat(a[location]));
    const d2_vals = all_dye.dye_02.map((a) => parseFloat(a[location]));
    const current_val = Math.log10((10 ** parseFloat(d1_vals[keyframe]))+(10 ** parseFloat(d1_vals[keyframe])))

    let risk_high = -3
    let risk_med = -5
    let risk_low = -5.5

    const cur_plot = Plot.plot({
        y: {
            grid: true
        },
        marks: [
            Plot.ruleX([keyframe]),
            Plot.lineY(d1_vals, { x: "time", y: location})
        ]
    })
    var card;

    // Low Risk
    if (current_val < risk_med) {
        card = html`
            <div class="card grid grid-cols-3" style = "height: 48px; text-align: center;">
            <div style = "color: palegreen"><h2>${location}</h2></div><div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 2400"><path fill="palegreen" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zM369 209L241 337c-9.4 9.4-24.6 9.4-33.9 0l-64-64c-9.4-9.4-9.4-24.6 0-33.9s24.6-9.4 33.9 0l47 47L335 175c9.4-9.4 24.6-9.4 33.9 0s9.4 24.6 0 33.9z"/></svg></div><div>${current_val.toFixed(2)}</div>
            </div>
        `;
    // Medium Risk
    } else if (current_val < risk_high) {
        card = html`
            <div class="card grid grid-cols-3" style = "height: 48px; text-align: center;">
            <div style = "color: gold"><h2>${location}</h2></div><div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 2400"><path fill="gold" d="M256 512A256 256 0 1 0 256 0a256 256 0 1 0 0 512zm0-384c13.3 0 24 10.7 24 24l0 112c0 13.3-10.7 24-24 24s-24-10.7-24-24l0-112c0-13.3 10.7-24 24-24zM224 352a32 32 0 1 1 64 0 32 32 0 1 1 -64 0z"/></svg></div><div>${current_val.toFixed(2)}</div>
            </div>
        `;
    // High Risk
    } else {
        card = html`
            <div class="card grid grid-cols-3" style = "height: 48px; text-align: center;">
            <div style = "color: firebrick"><h2>${location}</h2></div><div><svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2400 2400"><path fill="firebrick" d="M256 32c14.2 0 27.3 7.5 34.5 19.8l216 368c7.3 12.4 7.3 27.7 .2 40.1S486.3 480 472 480L40 480c-14.3 0-27.6-7.7-34.7-20.1s-7-27.8 .2-40.1l216-368C228.7 39.5 241.8 32 256 32zm0 128c-13.3 0-24 10.7-24 24l0 112c0 13.3 10.7 24 24 24s24-10.7 24-24l0-112c0-13.3-10.7-24-24-24zm32 224a32 32 0 1 0 -64 0 32 32 0 1 0 64 0z"/></svg></div><div>${current_val.toFixed(2)}</div>
            </div>
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
  const form = html`<form style="font: 12px var(--sans-serif); font-variant-numeric: tabular-nums; justify-content: center; display: flex; height: 33px; align-items: center;">
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
    if (event && event.isTrusted && running()) stop();
    form.value = form.i.valueAsNumber;
    form.o.value = format(values[form.i.valueAsNumber], form.i.valueAsNumber, values);
  };
  form.b.onclick = () => {
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