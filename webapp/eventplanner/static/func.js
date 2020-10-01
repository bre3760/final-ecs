function modalLayout(page){
	$("#myModalContent").load(`${page}`,function(){
		$("#myModal").modal({show:true});
	});
}

function divLayout(div,page){
	$(`#${div}`).load(`${page}`,function(){});
	event.stopPropagation();
}

function accountSidebar(){
	$("#accountCollapse").animate({width:'toggle'},500);
	divLayout('user_info',"/account-info/");
	event.stopPropagation();
}

function accountUpdated(){
	divLayout('user_info',"/account-info/");
}

function createEventThumbnail(){
	create_event_thumbnail.setAttribute("src",URL.createObjectURL(new_thumbnail.files[0]));
}


function booking(pressed_btn){
	let tickets = document.getElementsByClassName("ticket_type");
	let nums = document.getElementsByClassName("num_booked_tickets");
	let booked_tickets = [];
	for (let i = 0; i < tickets.length; i++) {
		booked_tickets.push({ticket_id: tickets.item(i).id, booked_num: nums.item(i).value});
	}
	// booked_tickets = [ {ticket_id: 2, booked_num: 2}, {ticket_id: 12, booked_num: 45}]
	if (pressed_btn.id == "purchase_button") {
		// PURCHASE
		var myHeaders = new Headers();
	    myHeaders.append("Content-Type", "application/json");
	    var raw = JSON.stringify(booked_tickets);
	    var requestOptions = {
	      method: 'POST',
	      headers: myHeaders,
	      body: raw,
	      redirect: 'follow'
	    };
		fetch("/start-payment-flow", requestOptions)
	      .then(response => {
	        if (response.redirected) {
	            window.location.href = response.url;
	        }
	      })
	      .then(result => console.log(result))
	      .catch(error => console.log('error', error));
	} else if ( pressed_btn.id == "book_button") {
		// BOOK
		try{
		var myHeaders = new Headers();
	    myHeaders.append("Content-Type", "application/json");
	    var raw = JSON.stringify(booked_tickets);
	    var requestOptions = {
	      method: 'POST',
	      headers: myHeaders,
	      body: raw,
	      redirect: 'follow'
	    };
		fetch("/generate-booking/", requestOptions)
	      .then(response => {
	        if (response.redirected) {
	            window.location.href = response.url;
	        }
	      })
	      .then(result => console.log(result))
	      //.then(result => alert(result))
	      .catch(error => console.log('error', error));
		}catch(e){
			alert(e);
		}
	} // end else if
} // end func


function selectByType(type_int){
    $.ajax({
            async: false,
            timeout: 10000,
            url: `/events-by-type/`,
            method: "POST",
            headers: {
                    "Content-Type":"application/json"
            },
            data: {
                    "type":type_int
            },
            success:function(data){
                    alert(JSON.stringify(data));
            },
            error:function(data){
                    alert(JSON.stringify(data));
            }
    });
}

