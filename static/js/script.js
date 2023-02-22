function sleep(ms) {
      return new Promise(resolve => setTimeout(resolve, ms));
  }
getPage();
window.onhashChange = getPage;
function fetchPage(to_dir){
	sleep(2000);
	var loc_url = "/api/nx/home/request/home";
	switch(to_dir){
		case 'blogs':
			loc_url = "/api/nx/home/request/blogs";
			break;
		case 'messages':
			loc_url = "/api/nx/home/request/notifications";
			break;
		case 'settings':
			loc_url = "/api/nx/home/request/settings";
			break;
		default:
			break;
	}
	fetch(loc_url)
	    .then(function(response) {
		return response.text()
	    })
	    .then(function(html) {    
		document.getElementById("_main").innerHTML = html;
		
	    })
	    .catch(function(err) {  
		console.log(err);
		  
	    });
}
function getPage(){
	if(location.hash.includes('#')){
		console.log(location.hash);
		try{
			let to_dir = location.hash.replace("#",'');
			fetchPage(to_dir);
		}catch(err){
			console.log(err);
		}
	}else{
		fetchPage('home');	
	}
}