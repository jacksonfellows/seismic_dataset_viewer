function loadArray(path, handler) {
	// Calls handler w/ a array.
	let client = new XMLHttpRequest();
	client.addEventListener("load", _ => {
		// More direct way to do this?
		handler(Array.from(new Float32Array(client.response)));
	});
	client.open("GET", path, true);
	client.responseType = "arraybuffer";
	client.send();
}

let sync = uPlot.sync("test");

let resetScalePlugin = {
	hooks: {
		ready: u => {			// u is a uPlot object.
			// Save original bounds.
			xMin = u.scales.x.min;
			xMax = u.scales.x.max;
			let over = u.over;

			function resetBounds(e) {
				e.stopPropagation(); // Stop click event from triggering on parent div.
				// Have to use sync object.
				for (let u_ of sync.plots) {
					u_.setScale("x", {min: xMin, max: xMax});
				}
			}

			// Add reset button.
			let buttonDiv = document.createElement("div");
			buttonDiv.style = "float: right;";
			let button = document.createElement("button");
			button.innerHTML = "🏠";
			buttonDiv.appendChild(button);
			button.onclick = resetBounds;
			over.appendChild(buttonDiv);
		}
	}
};

let picks = {};

function savePicks() {
	let client = new XMLHttpRequest();
	client.open("POST", `/save_picks/${CC.event_id}`, true);
	client.setRequestHeader("Content-Type", "application/json");
	client.send(JSON.stringify({picks: picks}));
}

function drawPick(u, pickX, strokeStyle) {
	let minYPos = u.valToPos(u.scales.y.min, "y", true);
	let maxYPos = u.valToPos(u.scales.y.max, "y", true);
	let xPos = u.valToPos(pickX, "x", true);
	let ctx = u.ctx;
	ctx.save();
	ctx.strokeStyle = strokeStyle;
	ctx.beginPath();
	ctx.moveTo(xPos, minYPos); ctx.lineTo(xPos, maxYPos);
	ctx.stroke();
	ctx.restore();
}

let pickPlugin = {
	hooks: {
		ready: u => {
			// Add clear pick button.
			let buttonDiv = document.createElement("div");
			buttonDiv.style = "float: right;";
			let button = document.createElement("button");
			button.innerHTML = "❌";
			buttonDiv.appendChild(button);
			button.onclick = e => {
				e.stopPropagation(); // Stop click event from triggering on parent div.
				delete picks[u.id];
				u.redraw();
			};
			u.over.appendChild(buttonDiv);

			u.over.onclick = e => {
				// Use offsetX not clientX!
				let pickX = u.posToVal(e.offsetX, "x");
				picks[u.id] = pickX;
				// Force a redraw so that we see the pick.
				u.redraw();
			};
		},
		draw: u => {
			let refPickX = CC.reference_picks[u.id];
			if (refPickX) drawPick(u, refPickX, "orange");
			let pickX = picks[u.id];
			if (pickX) drawPick(u, pickX, "red");
		}
	}
};

// bounds.current = current map bounds, bounds.old = map bounds before zooming in
let bounds = {};
let inFitBounds = false;		// Is Leaflet currently performing a map.fitBounds().
let deferFitBounds = false;		// Do have another map.fitBounds() to perform?

let mapPlugin = {
	hooks: {
		ready: u => {
			// Hacky.
			u.over.onmouseenter = e => {
				let refMarker = station_markers[getStationName(CC.reference_channel)];
				let marker = station_markers[getStationName(u.id)];
				bounds.old = bounds.current;
				bounds.current = new L.featureGroup([refMarker, marker]).getBounds().pad(0.2);
				if (inFitBounds) {
					deferFitBounds = true;
				} else {
					map.fitBounds(bounds.current);
				}
				L.DomUtil.addClass(marker._icon.children[0], "station-selected");
			};
			u.over.onmouseleave = e => {
				bounds.current = bounds.old;
				inFitBounds = true;
				map.fitBounds(bounds.current);
				L.DomUtil.removeClass(station_markers[getStationName(u.id)]._icon.children[0], "station-selected");
			};
		}
	}
};

let defaultOpts = {
	width: 800,
	height: 180,
	cursor: {
		sync: {
			key: sync.key,
		},
	},
	scales: {
		x: {
			auto: true,
			time: false,
		},
		y: {
			auto: true,
		}
	},
	series: [
		{},
		{
			stroke: "black",
			width: 1,
			points: {
				show: false
			},
		}
	],
	axes: [
		{
			labelSize: 0,
			size: 25,
			font: "10px sans-serif",
		},
		{
			font: "10px sans-serif",
		},
	],
	legend: {
		show: false,
	},
	plugins: [resetScalePlugin, pickPlugin, mapPlugin]
};

function loadPlot(channel, elem, opts) {
	path = `/xy/${CC.event_id}/${channel}`;
	loadArray(path, a => {
		let M = a.length / 2;
		let data = [a.slice(0, M), a.slice(M, a.length)];
		let opts_ = {...opts, ...defaultOpts};
		let u = new uPlot(opts_, data, elem);
		u.id = channel;			// Set an id so we can e.g. reference picks later.
		sync.sub(u);
	});
}

function getStationName(channel) {
	return channel.split(".").slice(0,2).join(".");
}

function loadChannels() {
	// Display channels in order of distance from reference station.
	let near_to_far = CC.channels.toSorted(
		(a, b) => CC.m_from_reference_station[getStationName(a)] - CC.m_from_reference_station[getStationName(b)]
	);
	let plotsDiv = document.getElementById("plots");
	for (let channel of near_to_far) {
		let pDiv = document.createElement("div");
		pDiv.classList.add("my-plot");
		plotsDiv.append(pDiv);
		loadPlot(channel, pDiv, {title: channel});
	}
}

let station_markers = {};
let map;

function setupMap() {
	map = L.map("map");
	map.attributionControl.setPrefix("Leaflet");
	// L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
	//	maxZoom: 19,
	//	attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>'
	// }).addTo(map);
	L.tileLayer('https://basemap.nationalmap.gov/arcgis/rest/services/USGSTopo/MapServer/tile/{z}/{y}/{x}', {
		maxZoom: 20,
		attribution: 'Tiles courtesy of the <a href="https://usgs.gov/">U.S. Geological Survey</a>'
	}).addTo(map);
	// Add stations.
	for (let station in CC.station_metadata) {
		m = CC.station_metadata[station];
		let icon = L.divIcon({className: null, html: `<div class="station-icon"></div><span>${station}</span>`});
		let marker = L.marker([m["latitude"], m["longitude"]], {icon: icon});
		marker.addTo(map);
		station_markers[station] = marker;
	}
	// Expand view to fit all markers.
	bounds.current = new L.featureGroup(Object.values(station_markers)).getBounds();
	map.fitBounds(bounds.current);
	// Mark reference station.
	L.DomUtil.addClass(station_markers[getStationName(CC.reference_channel)]._icon.children[0], "station-reference");
	// Add scale bar.
	L.control.scale().addTo(map);

	// :(
	map.on("mouseend zoomend", e => {
		if (deferFitBounds) {
			deferFitBounds = false;
			map.fitBounds(bounds.current);
		} else {
			inFitBounds = false;
		}
	});
}

window.onload = _ => {
	setupMap();
	loadChannels();
};
