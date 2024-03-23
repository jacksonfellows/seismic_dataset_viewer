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

// Mapping of id -> {min: xMin, max: xMax}.
let originalBounds = {};

function resetBounds() {
	for (let u_ of sync.plots) {
		u_.setScale("x", originalBounds[u_.id]);
	}
}

let resetScalePlugin = {
	hooks: {
		ready: u => {			// u is a uPlot object.
			// Save original bounds.
			originalBounds[u.id] = {min: u.scales.x.min, max: u.scales.x.max};

			// Add reset button.
			let buttonDiv = document.createElement("div");
			buttonDiv.style = "float: right;";
			let button = document.createElement("button");
			button.innerHTML = "🏠";
			buttonDiv.appendChild(button);
			button.onclick = e => {
				e.stopPropagation(); // Stop click event from triggering on parent div.
				resetBounds();
			};
			u.over.appendChild(buttonDiv);
		}
	}
};

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
		draw: u => {
			for (let pick of CC["picks"]) {
				let pickX = pick["pick_s"];
				if (pickX) drawPick(u, pickX, pick["color"]);
			}
		}
	}
};


let defaultOpts = {
	...getPlotSize(),
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
};

let normalOpts = {
	...defaultOpts,
	plugins: [resetScalePlugin, pickPlugin],
};

function loadComponent(elem, component) {
	let path = `/xy/${CC["trace_name"]}/${component}`;
	loadArray(path, a => {
		let M = a.length / 2;
		let data = [a.slice(0, M), a.slice(M, a.length)];
		let u = new uPlot({title: component, ...normalOpts}, data, elem);
		sync.sub(u);
	});
}

function loadComponents() {
	let plotsDiv = document.getElementById("plots");
	for (let component of CC["components"]) {
		let pDiv = document.createElement("div");
		pDiv.classList.add("my-plot");
		plotsDiv.append(pDiv);
		loadComponent(pDiv, component);
	}
}

window.onload = loadComponents;

function getPlotSize() {
	let totalWidth = window.innerWidth;
	let plotWidth = totalWidth - 20;
	return {width: plotWidth, height: 180};
}

function resizePlots() {
	let newSize = getPlotSize();
	sync.plots.forEach(u => u.setSize(newSize));
}

window.onresize = resizePlots;

// Keybindings.
document.onkeypress = e => {
	if (e.key == "g") {
		resetBounds();
	}
};
