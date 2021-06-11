var myUserName = "{{ request.user.username }}";
var timeOptions = { hour12: true, hour: '2-digit', minute:'2-digit' };
var loc = window.location.href.split('/')[4];

// Sends a new request to update the message list
function getChat() {
    $.ajax({
        url: "get-chat/" +loc,
        dataType : "json",
        success: updateChatPage,
        error: updateError
    });
}

function updateChatPage(response) {
    if (typeof response === "object" && !Array.isArray(response)) {
        updateChatMessage(response)
    } else if (response.hasOwnProperty('error')) {
        displayError(response.error)
    } else {
        displayError(response)
    }
}

function updateError(xhr, status, error) {
    displayError('Status=' + xhr.status + ' (' + error + ')')
}

function displayError(message) {
    $("#error").html(message);
}

function updateChatMessage(response) {
    // Removes the old todolist items
    // $("li").remove()

    // Adds each new message
    $(response['chatmessages']).each(function() {
        
        console.log(response)
        let my_chat_message = "id_chatmessage_" + this.id   //this.id = message.id
        if (document.getElementById(my_chat_message) == null) {
            console.log(this)

            let date = new Date(this.message_creation_time)
            message_date = date.toLocaleDateString() + " " + date.toLocaleTimeString('en', timeOptions)

            // if (this.message_type == 't'){
            //     message_content = sanitize(this.message_text)
            // } else {
            //     message_content = this.message_image
            // }

            if (this.message_text == ''){
                text = '';
            } else {
                text = this.message_text
            }

            if (this.message_image == null){
                image = '';
            } else {
            //     image = '<a href=' + this.message_image + ' class="link" id="id_message_image_' + this.id + '">' + 'attached </a>'
                image = '<a href="get-image/'+ this.id + '" class="link" id="id_message_image_' + this.id + '">' + 'attached </a>'
            }


            // "incoming_msg"
            if (this.to_username == myUserName){
                // console.log(this)
                $("#chatmessage-list").append(
                    // no need {% for post in posts %}
                    '<li id="id_chatmessage_' + this.id + '">' +    //this.id = post.id
						'<div class="incoming_msg">' +
							'<div class="received_msg">' +
								'<div class="received_withd_msg">' +
									'<div class="received_withd_msg" id="id_message_text_' + this.id + '"><p>' + sanitize(this.message_text)  + 
                                        image +
                                    '</p></div>' +
                                    '<span class="time_date" id="id_post_date_time_' + this.id + '">' + message_date + '</span>' +
								'</div>' +
							'</div>' +
						'</div>' +
                    '</li>'
                )
            } else {    // "outgoing_msg", this.from_username == other_user.username
                $("#chatmessage-list").append(
                    // no need {% for post in posts %}
                    '<li id="id_chatmessage_' + this.id + '">' +    //this.id = post.id
                        '<div class="outgoing_msg">' +
							'<div class="sent_msg">' + 
								// 'Message from ' + this.from_username + ' to ' + this.to_username +
								    '<div class="sent_msg" id="id_message_text_' + this.id + '"><p>' + sanitize(this.message_text) +
                                        image +
                                    '</p></div>' +
								'<span class="time_date" id="id_post_date_time_' + this.id + '">' + message_date + '</span>' +
							'</div>' +
						'</div>' +
                    '</li>'
                )
            }

        }
    });
}

function sanitize(s) {
    // Be sure to replace ampersand first
    return s.replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
}


function getCSRFToken() {
    let cookies = document.cookie.split(";")
    for (let i = 0; i < cookies.length; i++) {
        let c = cookies[i].trim()
        if (c.startsWith("csrftoken=")) {
            return c.substring("csrftoken=".length, c.length)
        }
    }
    return "unknown";
}
