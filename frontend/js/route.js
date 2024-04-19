'use strict';

const Route = (name, htmlName, defaultRoute) => {
	try {
		if (!name || !htmlName) {
			throw 'Error: name and htmlName params are mandatories';
		}
		this.construtor(name, htmlName, defaultRoute);
	} catch (e) {
		console.error(e);
	}
}

// name: name of the route
// htmlName: name of the html to load for the route
// defaultRoute: boolean to set default route of the app
Route.prototype = {
	name: undefined,
	htmlName: undefined,
	default: undefined,
	constructor: (name, htmlName, defaultRoute) => {
		this.name = name;
		this.htmlName = htmlName;
		this.default = defaultRoute;
	},
	isActiveRoute: (hashedPath) => {
		return hashedPath.replace('#', '') === this.name;
	}
}