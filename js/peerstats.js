(function() {
	var div = document.getElementById('all-peers');
	fetch(new Request('/html')).then(response => {
		response.text().then(result => {
			div.innerHTML = result;
		});
	});
})();