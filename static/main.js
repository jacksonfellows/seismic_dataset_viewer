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

let myPlugin = {
	hooks: {
		ready: u => {			// u is a uPlot object.
			// Save original bounds.
			xMin = u.scales.x.min;
			xMax = u.scales.x.max;
			let over = u.over;

			function resetBounds(e) {
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

let opts = {
	width: 1200,
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
	plugins: [myPlugin]
};

function loadPlot(path) {
	loadArray(path, a => {
		let M = a.length / 2;
		let data = [a.slice(0, M), a.slice(M, a.length)];
		let plot = new uPlot(opts, data, document.getElementById("plots"));
		sync.sub(plot);
	});
}

window.onload = _ => {
	loadPlot("/xy/0");
	loadPlot("/xy/1");
	loadPlot("/xy/2");
	loadPlot("/xy/3");
	loadPlot("/xy/4");
	loadPlot("/xy/5");
	loadPlot("/xy/6");
};
