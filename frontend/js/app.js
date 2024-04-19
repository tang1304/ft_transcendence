'use strict';

(function () {
	function init() {
		const router = new Router([
			new Route('login', 'login.html', true),
			new Route('register', 'register.html'),
		])
	}
	init();
}());

// https://accreditly.io/articles/creating-single-page-applications-with-vanilla-javascript
// https://www.youtube.com/watch?v=6BozpmSjk-Y&list=PLw5h0DiJ-9PBXb6SnjLxAQH6ecMYz3Wjs
